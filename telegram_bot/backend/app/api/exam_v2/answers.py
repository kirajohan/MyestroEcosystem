"""
Maestro Exam — User Answers endpoints.

POST /api/v2/exam/attempts/{id}/answers   → javob saqlash
POST /api/v2/exam/attempts/{id}/submit    → yakunlash + auto-scoring
GET  /api/v2/exam/attempts/{id}/result    → natija
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.session_deps import get_current_user_from_session
from app.database import get_async_db
from app.models.exam import (
    Exam, ExamAttempt, ExamAttemptBlock, ExamBlock,
    ExamItem, ExamOption, ExamAnswer,
)
from app.models.user import User

router = APIRouter()


# ═══════════════════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════════════════

class AnswerSubmit(BaseModel):
    item_id: int
    selected_options: Optional[List[int]] = None   # [option_id, ...]
    text_answer: Optional[str] = None


class AnswerSubmitList(BaseModel):
    answers: List[AnswerSubmit]


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

async def get_user_attempt(attempt_id: int, user_id: int, db: AsyncSession) -> ExamAttempt:
    stmt = select(ExamAttempt).where(
        ExamAttempt.id == attempt_id,
        ExamAttempt.user_id == user_id,
    )
    result = await db.execute(stmt)
    attempt = result.scalar_one_or_none()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt topilmadi")
    return attempt


def check_deadline(attempt: ExamAttempt) -> bool:
    """Vaqt tugaganmi? True = tugagan."""
    if attempt.deadline and datetime.now(timezone.utc) > attempt.deadline:
        return True
    return False


async def auto_score_item(item: ExamItem, answer: ExamAnswer, db: AsyncSession) -> float:
    """
    Auto-scoring: item.options dagi is_correct dan foydalanadi.
    answer_key bo'sh bo'lsa ham ishlaydi.
    """
    if not answer.selected_options:
        return 0.0

    # 1. Avval answer_key dan urinib ko'ramiz
    correct_ids = set()
    if item.answer_key and item.answer_key.get("correct_option_ids"):
        correct_ids = set(item.answer_key.get("correct_option_ids", []))
    
    # 2. Agar answer_key bo'sh bo'lsa, options.is_correct dan olamiz
    if not correct_ids and item.options:
        correct_ids = {opt.id for opt in item.options if opt.is_correct}

    # 3. Agar baribir topilmasa, DB dan so'raymiz
    if not correct_ids:
        opts_stmt = select(ExamOption).where(
            ExamOption.item_id == item.id,
            ExamOption.is_correct == True,
        )
        opts_result = await db.execute(opts_stmt)
        correct_ids = {opt.id for opt in opts_result.scalars().all()}

    if not correct_ids:
        return 0.0

    selected_ids = set(answer.selected_options)

    # To'liq moslik kerak
    if correct_ids == selected_ids:
        return float(item.max_score or 1.0)

    return 0.0

# ═══════════════════════════════════════════════════════════════
# POST /answers — Javob saqlash
# ═══════════════════════════════════════════════════════════════

@router.post("/{attempt_id}/answers", summary="Javob saqlash (autosave)")
async def save_answers(
    attempt_id: int,
    payload: AnswerSubmitList,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user_from_session),
):
    """
    Foydalanuvchi javoblarni saqlaydi (har bir autosave da chaqiriladi).
    Agar item uchun javob allaqachon bor bo'lsa — yangilanadi.
    """

    attempt = await get_user_attempt(attempt_id, current_user.id, db)

    if attempt.status not in ["in_progress", "created"]:
        raise HTTPException(status_code=400, detail="Attempt faol emas")

    if check_deadline(attempt):
        # Vaqt tugagan, lekin saqlangan javoblarni qabul qilamiz (so'nggi soniyalarda)
        pass

    saved_count = 0
    updated_count = 0

    for ans_data in payload.answers:
        # Item topish (faqat shu exam'ga tegishli)
        item_stmt = (
            select(ExamItem)
            .join(ExamBlock)
            .where(
                ExamItem.id == ans_data.item_id,
                ExamBlock.exam_id == attempt.exam_id,
            )
        )
        item_result = await db.execute(item_stmt)
        item = item_result.scalar_one_or_none()

        if not item:
            continue  # Item topilmasa, o'tkazib yuboramiz


            # YANGI: Reading/Listening uchun auto-scoring
            if item.item_type in ("reading_question", "listening_question"):
                score_result = await ScoringService.score_answer(
                    db=db,
                    item_id=item.id,
                    selected_option_ids=payload.selected_options or [],
                )
                auto_score = score_result["auto_score"]
            else:
                auto_score = None

            # Answer yaratish/yangilash
            # ...
            answer.auto_score = auto_score
            
            await db.commit()
            
            return {
                "answer_id": answer.id,
                "auto_score": auto_score,
                "is_correct": score_result.get("is_correct") if auto_score is not None else None,
            }
        
        # Mavjud javob bormi?
        existing_stmt = select(ExamAnswer).where(
            ExamAnswer.attempt_id == attempt_id,
            ExamAnswer.item_id == ans_data.item_id,
        )
        existing_result = await db.execute(existing_stmt)
        existing = existing_result.scalar_one_or_none()

        if existing:
            # Yangilash
            existing.selected_options = ans_data.selected_options
            existing.text_answer = ans_data.text_answer
            existing.updated_at = datetime.now(timezone.utc)
            updated_count += 1
        else:
            # Yangi yaratish
            answer = ExamAnswer(
                attempt_id=attempt_id,
                item_id=ans_data.item_id,
                selected_options=ans_data.selected_options,
                text_answer=ans_data.text_answer,
                ai_status="pending",
            )
            db.add(answer)
            saved_count += 1

    await db.commit()

    return {
        "saved": saved_count,
        "updated": updated_count,
        "total": saved_count + updated_count,
    }


# ═══════════════════════════════════════════════════════════════
# POST /submit — Yakunlash + Auto-Scoring
# ═══════════════════════════════════════════════════════════════

@router.post("/{attempt_id}/submit", summary="Imtihonni yakunlash")
async def submit_attempt(
    attempt_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user_from_session),
):
    """
    Imtihonni yakunlaydi va Reading/Listening uchun auto-scoring qiladi.
    Writing/Speaking keyinroq AI orqali tekshiriladi.
    """

    attempt = await get_user_attempt(attempt_id, current_user.id, db)

    if attempt.status not in ["in_progress", "created"]:
        raise HTTPException(
            status_code=400,
            detail=f"Attempt allaqachon yakunlangan (status: {attempt.status})"
        )

    now = datetime.now(timezone.utc)

    # 1. Barcha javoblarni olish
    answers_stmt = (
        select(ExamAnswer)
        .where(ExamAnswer.attempt_id == attempt_id)
    )
    answers_result = await db.execute(answers_stmt)
    answers = answers_result.scalars().all()

    # 2. Barcha item'larni olish (answer_key bilan)
    items_stmt = (
        select(ExamItem)
        .join(ExamBlock)
        .where(ExamBlock.exam_id == attempt.exam_id)
        .options(selectinload(ExamItem.options))
    )
    items_result = await db.execute(items_stmt)
    items = items_result.scalars().all()
    items_map = {item.id: item for item in items}

    # 3. Auto-scoring (Reading/Listening)
    total_score = 0.0
    max_possible = 0.0
    scored_items = 0
    pending_ai = 0

    answers_map = {ans.item_id: ans for ans in answers}

    for item in items:
        max_possible += float(item.max_score or 0)
        answer = answers_map.get(item.id)

        if item.item_type in ["reading_question", "listening_question"]:
            # Auto-scoring
            if answer:
                score = await auto_score_item(item, answer, db)                
                answer.auto_score = score
                answer.final_score = score
                total_score += score
            scored_items += 1

        elif item.item_type in ["writing_task", "speaking_task"]:
            # AI scoring kerak (hozircha 0)
            if answer:
                answer.ai_status = "pending"
                answer.final_score = 0.0
            pending_ai += 1

    # 4. Attempt'ni yangilash
    attempt.status = "completed" if pending_ai == 0 else "scoring"
    attempt.submitted_at = now
    attempt.completed_at = now if pending_ai == 0 else None
    attempt.total_score = total_score

    # 5. Har bir attempt_block'ni yakunlash
    ab_stmt = select(ExamAttemptBlock).where(
        ExamAttemptBlock.attempt_id == attempt_id
    )
    ab_result = await db.execute(ab_stmt)
    attempt_blocks = ab_result.scalars().all()

    for ab in attempt_blocks:
        ab.status = "completed"
        ab.completed_at = now
        
        # Block bo'yicha ball hisoblash
        block_items = [it for it in items if it.block_id == ab.block_id]
        block_score = 0.0
        for it in block_items:
            ans = answers_map.get(it.id)
            if ans and ans.final_score is not None:
                block_score += ans.final_score
        ab.score = block_score

    await db.commit()
    await db.refresh(attempt)

    return {
        "attempt_id": attempt.id,
        "status": attempt.status,
        "total_score": attempt.total_score,
        "max_possible": max_possible,
        "percentage": round((attempt.total_score / max_possible * 100) if max_possible else 0, 1),
        "scored_items": scored_items,
        "pending_ai": pending_ai,
        "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
    }


# ═══════════════════════════════════════════════════════════════
# GET /result — Natija
# ═══════════════════════════════════════════════════════════════

@router.get("/{attempt_id}/result", summary="Natijani olish")
async def get_result(
    attempt_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user_from_session),
):
    """Attempt natijasini to'liq qaytaradi (block'lar va javoblar bilan)."""

    attempt = await get_user_attempt(attempt_id, current_user.id, db)

    if attempt.status not in ["completed", "scoring", "submitted"]:
        raise HTTPException(
            status_code=400,
            detail="Attempt hali yakunlanmagan"
        )

    # Exam
    exam_stmt = select(Exam).where(Exam.id == attempt.exam_id)
    exam_result = await db.execute(exam_stmt)
    exam = exam_result.scalar_one_or_none()

    # Blocks
    ab_stmt = (
        select(ExamAttemptBlock)
        .where(ExamAttemptBlock.attempt_id == attempt_id)
    )
    ab_result = await db.execute(ab_stmt)
    attempt_blocks = ab_result.scalars().all()

    block_ids = [ab.block_id for ab in attempt_blocks]
    blocks_stmt = select(ExamBlock).where(ExamBlock.id.in_(block_ids))
    blocks_result = await db.execute(blocks_stmt)
    blocks_map = {b.id: b for b in blocks_result.scalars().all()}

    # Items (answer_key BILAN — natijada ko'rsatish uchun)
    items_stmt = (
        select(ExamItem)
        .where(ExamItem.block_id.in_(block_ids))
        .options(selectinload(ExamItem.options))
    )
    items_result = await db.execute(items_stmt)
    items = items_result.scalars().all()

    # Javoblar
    answers_stmt = select(ExamAnswer).where(ExamAnswer.attempt_id == attempt_id)
    answers_result = await db.execute(answers_stmt)
    answers = answers_result.scalars().all()
    answers_map = {ans.item_id: ans for ans in answers}

    # Block'lar bo'yicha guruhlash
    blocks_data = []
    for ab in attempt_blocks:
        block = blocks_map.get(ab.block_id)
        if not block:
            continue

        block_items = [it for it in items if it.block_id == ab.block_id]
        items_data = []

        for item in sorted(block_items, key=lambda i: i.order):
            answer = answers_map.get(item.id)
            
            # To'g'ri javob ID larini aniqlash
            correct_option_ids = []
            if item.answer_key:
                correct_option_ids = item.answer_key.get("correct_option_ids", [])

            options_list = item.options if hasattr(item, 'options') else []
            items_data.append({
                "id": item.id,
                "item_type": item.item_type,
                "title": item.title,
                "instruction": item.instruction,
                "question_text": item.question_text,
                "max_score": float(item.max_score or 1),
                "order": item.order,
                # ═══ SPEAKING UCHUN YANGI ═══
                "preparation_time_sec": item.preparation_time_sec or 30,
                "answer_time_sec": item.answer_time_sec or 60,
                # ═══ WRITING UCHUN ═══
                "min_words": item.min_words,
                "max_words": item.max_words,
                "options": [
                    {
                        "id": opt.id,
                        "text": opt.text,
                        "order": opt.order,
                    }
                    for opt in options_list
                ],
            })

        blocks_data.append({
            "block_id": ab.block_id,
            "block_type": block.block_type,
            "title": block.title,
            "score": ab.score,
            "status": ab.status,
            "items": items_data,
        })

    # CEFR estimate (oddiy formula)
    percentage = 0
    if attempt.total_score is not None:
        max_score_stmt = select(func.sum(ExamItem.max_score)).where(
            ExamItem.block_id.in_(block_ids)
        )
        max_result = await db.execute(max_score_stmt)
        max_score = max_result.scalar() or 0
        if max_score > 0:
            percentage = (attempt.total_score / max_score) * 100

    cefr_estimate = "A1"
    if percentage >= 85: cefr_estimate = "C1"
    elif percentage >= 70: cefr_estimate = "B2"
    elif percentage >= 55: cefr_estimate = "B1"
    elif percentage >= 40: cefr_estimate = "A2"

    return {
        "attempt_id": attempt.id,
        "exam_id": attempt.exam_id,
        "exam_title": exam.title if exam else None,
        "exam_type": exam.exam_type if exam else None,
        "status": attempt.status,
        "total_score": attempt.total_score,
        "percentage": round(percentage, 1),
        "cefr_estimate": cefr_estimate,
        "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
        "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
        "blocks": blocks_data,
    }


# ═══════════════════════════════════════════════════════════
# SPEAKING AUDIO UPLOAD
# ═══════════════════════════════════════════════════════════

from fastapi import UploadFile, File
from app.services.exam.media_servicea import MediaService
from app.models.exam import ExamItem, ExamAnswer, ExamAIJob, ExamMedia
from sqlalchemy import select


@router.post(
    "/{attempt_id}/answers/{item_id}/audio",
    summary="Speaking audio yuklash",
)
async def upload_speaking_audio(
    attempt_id: int,
    item_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user_from_session),
):
    """
    Speaking task uchun audio faylni yuklaydi.

    Jarayon:
    1. Attempt va Item tekshiriladi
    2. Audio validation qilinadi (format, hajm)
    3. Fayl saqlanadi
    4. Answer yaratiladi/yangilanadi
    5. Transcribe AI job yaratiladi
    """

    # ── 1. Attempt tekshirish ─────────────────────────────
    attempt = await db.get(ExamAttempt, attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attempt topilmadi")

    if attempt.status not in ("in_progress", "created"):
        raise HTTPException(
            status_code=400,
            detail="Attempt yakunlangan, audio yuklab bo'lmaydi",
        )

    # ── 2. Item tekshirish (speaking task ekanligini) ─────
    item = await db.get(ExamItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item topilmadi")

    if item.item_type != "speaking_task":
        raise HTTPException(
            status_code=400,
            detail="Bu item speaking task emas",
        )

    # ── 3. Audio faylni saqlash ───────────────────────────
    saved = await MediaService.save_exam_audio(
        file=file,
        attempt_id=attempt_id,
        item_id=item_id,
    )

    # ── 4. Answer topish yoki yaratish ────────────────────
    result = await db.execute(
        select(ExamAnswer).where(
            ExamAnswer.attempt_id == attempt_id,
            ExamAnswer.item_id == item_id,
        )
    )
    answer = result.scalar_one_or_none()

    if answer:
        # Mavjud answer'ni yangilash
        answer.audio_url = saved["url"]
        answer.audio_file_id = saved["file_id"]
        answer.ai_status = "pending"
    else:
        # Yangi answer yaratish
        answer = ExamAnswer(
            attempt_id=attempt_id,
            item_id=item_id,
            audio_url=saved["url"],
            audio_file_id=saved["file_id"],
            ai_status="pending",
        )
        db.add(answer)
        await db.flush()
        await db.refresh(answer)

    # ── 5. ExamMedia yozuv qo'shish ───────────────────────
    media = ExamMedia(
        owner_type="answer",
        owner_id=answer.id,
        file_type="audio",
        file_name=saved["file_name"],
        file_path=saved["file_path"],
        mime_type=saved["mime_type"],
        size_bytes=saved["size_bytes"],
    )
    db.add(media)

    # ── 6. Transcribe AI job yaratish ─────────────────────
    ai_job = ExamAIJob(
        attempt_id=attempt_id,
        answer_id=answer.id,
        job_type="transcribe",
        status="pending",
        provider="whisper",
        request_payload={
            "audio_url": saved["url"],
            "file_id": saved["file_id"],
        },
    )
    db.add(ai_job)

    await db.commit()

    return {
        "status": "ok",
        "answer_id": answer.id,
        "audio": {
            "file_id": saved["file_id"],
            "url": saved["url"],
            "size_bytes": saved["size_bytes"],
            "mime_type": saved["mime_type"],
        },
        "ai_job": {
            "id": ai_job.id,
            "type": ai_job.job_type,
            "status": ai_job.status,
        },
    }
