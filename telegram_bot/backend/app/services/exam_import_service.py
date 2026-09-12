"""
Exam Import Service — JSON ma'lumotni parse, validate va DB ga saqlash
"""
import logging
from typing import Dict, Any, List, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exam import Exam, ExamBlock, ExamItem, ExamOption
from app.schemas.exam_import import (
    ImportExam, ImportValidationError, ImportPreviewResponse,
    ImportResultResponse
)

logger = logging.getLogger(__name__)


class ExamImportService:
    """JSON import servisi"""

    # ─────────────────────────────────────────────
    # VALIDATION
    # ─────────────────────────────────────────────
    async def validate(self, data: ImportExam) -> ImportPreviewResponse:
        """Ma'lumotni validatsiya qiladi, preview qaytaradi"""
        errors: List[ImportValidationError] = []
        warnings: List[str] = []

        # 1. Block code unikalligi
        block_codes = [b.block_code for b in data.blocks]
        duplicates = set([c for c in block_codes if block_codes.count(c) > 1])
        for dup in duplicates:
            errors.append(ImportValidationError(
                location="blocks",
                message=f"block_code '{dup}' takrorlangan"
            ))

        # 2. Item → Block referens
        valid_block_codes = set(block_codes)
        for idx, item in enumerate(data.items):
            if item.block_code not in valid_block_codes:
                errors.append(ImportValidationError(
                    location=f"items[{idx}].block_code",
                    message=f"'{item.block_code}' blocks ichida topilmadi"
                ))

        # 3. MCQ uchun options tekshiruvi
        for idx, item in enumerate(data.items):
            if item.item_type in ("listening_question", "reading_question"):
                if len(item.options) < 2:
                    warnings.append(
                        f"items[{idx}] '{item.title}': MCQ uchun kamida 2 ta variant kerak "
                        f"(hozir: {len(item.options)})"
                    )
                correct_count = sum(1 for o in item.options if o.is_correct)
                if correct_count == 0 and len(item.options) > 0:
                    warnings.append(
                        f"items[{idx}] '{item.title}': to'g'ri javob belgilanmagan"
                    )

        # 4. Writing word limit
        for idx, item in enumerate(data.items):
            if item.item_type == "writing_task":
                if item.min_words and item.max_words and item.min_words > item.max_words:
                    errors.append(ImportValidationError(
                        location=f"items[{idx}]",
                        message=f"min_words ({item.min_words}) > max_words ({item.max_words})"
                    ))

        # 5. Listening block audio tekshiruvi
        for block in data.blocks:
            if block.block_type == "listening" and not block.audio_url:
                warnings.append(
                    f"Block '{block.title}' (listening): audio_url bo'sh"
                )

        # 6. Reading block passage tekshiruvi
        for block in data.blocks:
            if block.block_type == "reading" and not block.passage_text:
                warnings.append(
                    f"Block '{block.title}' (reading): passage_text bo'sh"
                )

        # 7. Options soni
        total_options = sum(len(item.options) for item in data.items)

        is_valid = len(errors) == 0

        return ImportPreviewResponse(
            valid=is_valid,
            exam_title=data.title,
            exam_type=data.exam_type,
            cefr_level=data.cefr_level,
            blocks_count=len(data.blocks),
            items_count=len(data.items),
            options_count=total_options,
            errors=errors,
            warnings=warnings,
            parsed_data=data if is_valid else None,
        )

    # ─────────────────────────────────────────────
    # SAVE TO DB
    # ─────────────────────────────────────────────
    async def save(self, data: ImportExam, db: AsyncSession) -> ImportResultResponse:
        """Validatsiya qilingan ma'lumotni DB ga saqlaydi"""
        try:
            # 1. Exam yaratish
            exam = Exam(
                code=data.code,
                title=data.title,
                description=data.description or "",
                exam_type=data.exam_type,
                cefr_level=data.cefr_level,
                time_limit_sec=data.time_limit_sec,
                is_published=data.is_published,
            )
            db.add(exam)
            await db.flush()  # exam.id olish uchun

            logger.info(f"✅ Exam created: id={exam.id}, code={data.code}")

            # 2. Blocks yaratish
            block_map: Dict[str, int] = {}  # block_code → db_id
            blocks_created = 0

            for block_data in sorted(data.blocks, key=lambda b: b.order):
                block = ExamBlock(
                    exam_id=exam.id,
                    block_type=block_data.block_type,
                    title=block_data.title,
                    instructions=block_data.instructions,
                    passage_text=block_data.passage_text,
                    audio_url=block_data.audio_url,
                    order=block_data.order,
                    time_limit_sec=block_data.time_limit_sec,
                )
                db.add(block)
                await db.flush()
                block_map[block_data.block_code] = block.id
                blocks_created += 1

            logger.info(f"✅ {blocks_created} blocks created")

            # 3. Items yaratish
            items_created = 0
            options_created = 0

            for item_data in sorted(data.items, key=lambda i: i.order):
                block_id = block_map.get(item_data.block_code)
                if not block_id:
                    continue  # validatsiyada allaqachon xato aniqlangan

                # answer_key tayyorlash
                correct_ids = [
                    idx + 1
                    for idx, opt in enumerate(item_data.options)
                    if opt.is_correct
                ]
                answer_key = {"correct_option_ids": correct_ids} if correct_ids else None

                item = ExamItem(
                    block_id=block_id,
                    item_type=item_data.item_type,
                    title=item_data.title,
                    instruction=item_data.instruction,
                    question_text=item_data.question_text,
                    passage_text=item_data.passage_text,
                    audio_url=item_data.audio_url,
                    min_words=item_data.min_words,
                    max_words=item_data.max_words,
                    preparation_time_sec=item_data.preparation_time_sec,
                    answer_time_sec=item_data.answer_time_sec,
                    max_score=item_data.max_score,
                    order=item_data.order,
                    answer_key=answer_key,
                )
                db.add(item)
                await db.flush()
                items_created += 1

                # 4. Options yaratish
                for opt_data in sorted(item_data.options, key=lambda o: o.order):
                    option = ExamOption(
                        item_id=item.id,
                        text=opt_data.text,
                        is_correct=opt_data.is_correct,
                        order=opt_data.order,
                    )
                    db.add(option)
                    options_created += 1

            await db.commit()

            logger.info(
                f"✅ Import complete: exam={exam.id}, "
                f"blocks={blocks_created}, items={items_created}, options={options_created}"
            )

            return ImportResultResponse(
                success=True,
                exam_id=exam.id,
                blocks_created=blocks_created,
                items_created=items_created,
                options_created=options_created,
            )

        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Import failed: {e}", exc_info=True)
            return ImportResultResponse(
                success=False,
                errors=[str(e)],
            )