
from __future__ import annotations
from typing import Optional
from fastapi import Query
from sqlalchemy import func
from app.models.exam import Exam
from app.services.exam_scoring_service import submit_and_score_attempt
from datetime import datetime, timezone
from app.services.exam_ai_service import evaluate_writing
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.session_deps import get_current_user_from_session
from app.database import get_async_db
from app.models.exam import ExamAttempt, ExamAttemptBlock, ExamBlock, ExamItem, ExamAnswer
from app.models.user import User
import logging
logger = logging.getLogger(__name__)
router = APIRouter()


async def get_user_attempt(attempt_id: int, user_id: int, db: AsyncSession) -> ExamAttempt:
    """Attempt faqat shu user'niki bo'lishi kerak."""
    stmt = select(ExamAttempt).where(
        ExamAttempt.id == attempt_id,
        ExamAttempt.user_id == user_id,
    )
    result = await db.execute(stmt)
    attempt = result.scalar_one_or_none()

    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt topilmadi")
    return attempt


def check_deadline(attempt: ExamAttempt):
    """Agar vaqt tugagan bo'lsa, attempt'ni submitted qilish."""
    if attempt.deadline and attempt.status == "in_progress":
        now = datetime.now(timezone.utc)
        if attempt.deadline < now:
            attempt.status = "submitted"
            attempt.submitted_at = now

@router.get("/me", summary="Mening attempt tarixim")
async def list_my_attempts(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user_from_session),
):
    """
    Foydalanuvchining attempt tarixini qaytaradi.
    status bo'yicha filter qilish mumkin:
    created, in_progress, submitted, scoring, completed, failed
    """

    filters = [ExamAttempt.user_id == current_user.id]

    if status_filter:
        filters.append(ExamAttempt.status == status_filter)

    stmt = (
        select(ExamAttempt, Exam)
        .join(Exam, Exam.id == ExamAttempt.exam_id)
        .where(*filters)
        .order_by(ExamAttempt.created_at.desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    rows = result.all()

    items = []

    for attempt, exam in rows:
        # Shu attempt examining maksimal ballini hisoblaymiz
        max_score_stmt = (
            select(func.coalesce(func.sum(ExamItem.max_score), 0))
            .join(ExamBlock, ExamBlock.id == ExamItem.block_id)
            .where(ExamBlock.exam_id == attempt.exam_id)
        )
        max_score_result = await db.execute(max_score_stmt)
        max_score = float(max_score_result.scalar() or 0)

        total_score = float(attempt.total_score or 0)

        percentage = 0
        if max_score > 0:
            percentage = round((total_score / max_score) * 100, 1)

        items.append(
            {
                "attempt_id": attempt.id,
                "exam_id": exam.id,
                "exam_title": exam.title,
                "exam_type": exam.exam_type,
                "cefr_level": exam.cefr_level,
                "status": attempt.status,
                "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
                "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
                "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
                "deadline": attempt.deadline.isoformat() if attempt.deadline else None,
                "total_score": total_score,
                "max_score": max_score,
                "percentage": percentage,
                "cefr_estimate": attempt.cefr_estimate,
            }
        )

    active_attempts = [
        item for item in items
        if item["status"] in ["created", "in_progress", "submitted", "scoring"]
    ]

    completed_attempts = [
        item for item in items
        if item["status"] == "completed"
    ]

    return {
        "items": items,
        "total": len(items),
        "active_count": len(active_attempts),
        "completed_count": len(completed_attempts),
    }

@router.get("/{attempt_id}", summary="Attempt holati")
async def get_attempt(
    attempt_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user_from_session),
):
    """Attempt holatini qaytaradi (block'lar bilan)."""

    attempt = await get_user_attempt(attempt_id, current_user.id, db)
    check_deadline(attempt)

    ab_stmt = select(ExamAttemptBlock).where(
        ExamAttemptBlock.attempt_id == attempt_id
    )
    ab_result = await db.execute(ab_stmt)
    attempt_blocks = ab_result.scalars().all()

    block_ids = [ab.block_id for ab in attempt_blocks]
    blocks_map = {}
    if block_ids:
        blocks_stmt = select(ExamBlock).where(ExamBlock.id.in_(block_ids))
        blocks_result = await db.execute(blocks_stmt)
        blocks_map = {b.id: b for b in blocks_result.scalars().all()}

    await db.commit()

    return {
        "id": attempt.id,
        "exam_id": attempt.exam_id,
        "status": attempt.status,
        "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
        "deadline": attempt.deadline.isoformat() if attempt.deadline else None,
        "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
        "total_score": attempt.total_score,
        "cefr_estimate": attempt.cefr_estimate,
        "blocks": [
            {
                "attempt_block_id": ab.id,
                "block_id": ab.block_id,
                "block_type": blocks_map.get(ab.block_id).block_type if blocks_map.get(ab.block_id) else None,
                "title": blocks_map.get(ab.block_id).title if blocks_map.get(ab.block_id) else None,
                "status": ab.status,
                "score": ab.score,
            }
            for ab in attempt_blocks
        ],
    }


@router.get(
    "/{attempt_id}/blocks/{block_id}",
    summary="Block savollari (to'g'ri javoblarsiz)",
)
async def get_attempt_block(
    attempt_id: int,
    block_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user_from_session),
):
    """
    Block ichidagi savollarni qaytaradi.
    ⚠️ XAVFSIZLIK: answer_key va is_correct QAYTARILMAYDI!
    """

    attempt = await get_user_attempt(attempt_id, current_user.id, db)
    check_deadline(attempt)

    if attempt.status not in ["in_progress", "submitted"]:
        raise HTTPException(status_code=400, detail="Attempt faol emas")

    # Block topish (faqat shu exam'ga tegishli)
    block_stmt = (
        select(ExamBlock)
        .where(
            ExamBlock.id == block_id,
            ExamBlock.exam_id == attempt.exam_id,
        )
        .options(selectinload(ExamBlock.items).selectinload(ExamItem.options))
    )
    block_result = await db.execute(block_stmt)
    block = block_result.scalar_one_or_none()

    if not block:
        raise HTTPException(status_code=404, detail="Block topilmadi")

    # Attempt block'ni in_progress qilish
    ab_stmt = select(ExamAttemptBlock).where(
        ExamAttemptBlock.attempt_id == attempt_id,
        ExamAttemptBlock.block_id == block_id,
    )
    ab_result = await db.execute(ab_stmt)
    attempt_block = ab_result.scalar_one_or_none()

    if attempt_block and attempt_block.status == "pending":
        attempt_block.status = "in_progress"
        attempt_block.started_at = datetime.now(timezone.utc)
        await db.commit()

    # Items tayyorlash (answer_key YO'Q, is_correct YO'Q)
    sorted_items = sorted(block.items, key=lambda i: i.order)

    items_response = []
    for item in sorted_items:
        item_data = {
            "id": item.id,
            "item_type": item.item_type,
            "title": item.title,
            "instruction": item.instruction,
            "question_text": item.question_text,
            "passage_text": item.passage_text,
            "audio_url": item.audio_url,
            "min_words": item.min_words,
            "max_words": item.max_words,
            "max_score": item.max_score,
            "order": item.order,
        }

        # Options — faqat id, text, order (is_correct YO'Q!)
        if item.options:
            sorted_options = sorted(item.options, key=lambda o: o.order)
            item_data["options"] = [
                {
                    "id": opt.id,
                    "text": opt.text,
                    "order": opt.order,
                }
                for opt in sorted_options
            ]
        else:
            item_data["options"] = []

        items_response.append(item_data)

    return {
        "attempt_id": attempt.id,
        "block_id": block.id,
        "block_type": block.block_type,
        "title": block.title,
        "instructions": block.instructions,
        "passage_text": block.passage_text,       # ← YANGI
        "audio_url": block.audio_url,             # ← YANGI
        "time_limit_sec": block.time_limit_sec,
        "items": items_response,
    }

@router.post("/{attempt_id}/answers", summary="Javoblarni saqlash (autosave)")
async def save_answers(
    attempt_id: int,
    payload: dict,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user_from_session),
):
    """
    Javoblarni saqlaydi (autosave uchun).
    ⚠️ AI evaluation BU YERDA EMAS — faqat submit_attempt'da!
    
    Payload formati:
    {
        "answers": [
            {"item_id": 1, "selected_options": [5, 6]},  // Reading/Listening
            {"item_id": 2, "text_answer": "My essay..."}  // Writing
        ]
    }
    """
    attempt = await get_user_attempt(attempt_id, current_user.id, db)
    check_deadline(attempt)

    if attempt.status not in ["in_progress", "created"]:
        raise HTTPException(status_code=400, detail="Attempt faol emas")

    answers_data = payload.get("answers", [])
    saved_count = 0

    for ans in answers_data:
        item_id = ans.get("item_id")
        selected_options = ans.get("selected_options")
        text_answer = ans.get("text_answer")

        if not item_id:
            continue

        # Item mavjudligini va shu attempt'ga tegishli ekanligini tekshirish
        item_stmt = (
            select(ExamItem)
            .join(ExamBlock, ExamBlock.id == ExamItem.block_id)
            .where(
                ExamItem.id == item_id,
                ExamBlock.exam_id == attempt.exam_id,
            )
        )
        item_result = await db.execute(item_stmt)
        item = item_result.scalar_one_or_none()

        if not item:
            continue

        # Answer topish yoki yaratish
        answer_stmt = select(ExamAnswer).where(
            ExamAnswer.attempt_id == attempt_id,
            ExamAnswer.item_id == item_id,
        )
        answer_result = await db.execute(answer_stmt)
        answer = answer_result.scalar_one_or_none()

        if not answer:
            answer = ExamAnswer(
                attempt_id=attempt_id,
                item_id=item_id,
            )
            db.add(answer)

        # Javobni yangilash
        if selected_options is not None:
            answer.selected_options = selected_options
        if text_answer is not None:
            answer.text_answer = text_answer

        saved_count += 1

    await db.commit()

    return {"saved": saved_count, "status": "ok"}


@router.post("/{attempt_id}/submit", summary="Imtihonni yakunlash")
async def submit_attempt(
    attempt_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user_from_session),
):
    """
    Imtihonni yakunlaydi va scoring'ni ishga tushiradi.
    
    Jarayon:
    1. Attempt status'ni "submitted" qilish
    2. Listening/Reading auto-scoring
    3. Writing/Speaking AI evaluation trigger
    4. Yakuniy ballarni hisoblash
    
    Return:
    - status: "completed" yoki "scoring"
    - total_score
    - pending_ai: AI hali tugatmagan javoblar soni
    """
    attempt = await get_user_attempt(attempt_id, current_user.id, db)
    check_deadline(attempt)

    if attempt.status not in ["in_progress", "created"]:
        raise HTTPException(
            status_code=400,
            detail=f"Attempt allaqachon yakunlangan: {attempt.status}"
        )

    # 1. Attempt'ni "submitted" qilish
    attempt.status = "submitted"
    attempt.submitted_at = func.now()
    await db.commit()

    logger.info(f"📝 Attempt {attempt_id} submitted by user {current_user.id}")

    # 2. Scoring service'ni chaqirish
    try:
        result = await submit_and_score_attempt(attempt_id, db)
        
        return {
            "attempt_id": attempt_id,
            "status": result["final"]["status"],
            "total_score": result["final"]["total_score"],
            "max_possible": result["final"]["max_possible"],
            "percentage": result["final"]["percentage"],
            "scored_items": result["auto_scoring"]["scored"],
            "pending_ai": result["final"]["pending_ai"],
            "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None
        }
    
    except Exception as e:
        logger.error(f"❌ Scoring failed for attempt {attempt_id}: {e}")
        
        # Xato bo'lsa ham, attempt'ni "scoring" holatida qoldirish
        attempt.status = "scoring"
        await db.commit()
        
        return {
            "attempt_id": attempt_id,
            "status": "scoring",
            "error": str(e),
            "message": "Scoring jarayoni davom etmoqda"
        }


@router.get("/{attempt_id}/result", summary="Imtihon natijasi (to'liq)")
async def get_attempt_result(
    attempt_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user_from_session),
):
    """
    Yakunlangan attempt'ning to'liq natijasini qaytaradi.
    ✅ Reading/Listening uchun to'g'ri javoblar (is_correct) qaytariladi.
    ✅ AI feedback ham qaytariladi.
    """
    attempt = await get_user_attempt(attempt_id, current_user.id, db)
    check_deadline(attempt)

    if attempt.status not in ["submitted", "scoring", "completed"]:
        raise HTTPException(status_code=400, detail="Attempt hali yakunlanmagan")

    # Exam ma'lumotlarini olish
    exam_stmt = select(Exam).where(Exam.id == attempt.exam_id)
    exam_result = await db.execute(exam_stmt)
    exam = exam_result.scalar_one_or_none()

    if not exam:
        raise HTTPException(status_code=404, detail="Exam topilmadi")

    # Attempt blocks
    ab_stmt = select(ExamAttemptBlock).where(
        ExamAttemptBlock.attempt_id == attempt_id
    )
    ab_result = await db.execute(ab_stmt)
    attempt_blocks = ab_result.scalars().all()

    if not attempt_blocks:
        raise HTTPException(status_code=404, detail="Attempt block'lar topilmadi")

    # Block'lar va ularning items'larini olish
    block_ids = [ab.block_id for ab in attempt_blocks]
    blocks_stmt = (
        select(ExamBlock)
        .where(ExamBlock.id.in_(block_ids))
        .options(selectinload(ExamBlock.items).selectinload(ExamItem.options))
    )
    blocks_result = await db.execute(blocks_stmt)
    blocks = blocks_result.scalars().all()
    blocks_map = {b.id: b for b in blocks}

    # Attempt answers (barcha javoblar)
    answers_stmt = select(ExamAnswer).where(
        ExamAnswer.attempt_id == attempt_id
    )
    answers_result = await db.execute(answers_stmt)
    answers = answers_result.scalars().all()
    answers_map = {a.item_id: a for a in answers}

    # Umumiy ball hisoblash
    max_score_stmt = (
        select(func.coalesce(func.sum(ExamItem.max_score), 0))
        .join(ExamBlock, ExamBlock.id == ExamItem.block_id)
        .where(ExamBlock.exam_id == attempt.exam_id)
    )
    max_score_result = await db.execute(max_score_stmt)
    max_possible = float(max_score_result.scalar() or 0)

    total_score = float(attempt.total_score or 0)
    percentage = round((total_score / max_possible) * 100, 1) if max_possible > 0 else 0

    # Blocks response tuzish
    blocks_response = []
    for ab in attempt_blocks:
        block = blocks_map.get(ab.block_id)
        if not block:
            continue

        # Items tayyorlash (ENDI to'g'ri javoblar bilan!)
        sorted_items = sorted(block.items, key=lambda i: i.order)
        items_response = []

        for item in sorted_items:
            answer = answers_map.get(item.id)
            
            # Options (to'g'ri javoblar bilan — Result sahifasi uchun)
            options_response = []
            if item.options:
                sorted_options = sorted(item.options, key=lambda o: o.order)
                options_response = [
                    {
                        "id": opt.id,
                        "text": opt.text,
                        "order": opt.order,
                        "is_correct": opt.is_correct,  # ✅ Endi qaytariladi!
                    }
                    for opt in sorted_options
                ]

            # correct_option_ids
            correct_option_ids = [
                opt.id for opt in item.options if opt.is_correct
            ] if item.options else []

            # Answer response
            answer_response = None
            if answer:
                answer_response = {
                    "id": answer.id,
                    "selected_options": answer.selected_options,
                    "text_answer": answer.text_answer,
                    "audio_url": answer.audio_url,
                    "transcript_text": answer.transcript_text,
                    "auto_score": answer.auto_score,
                    "ai_score": answer.ai_score,
                    "final_score": answer.final_score,
                    "ai_status": answer.ai_status or "pending",
                    "feedback": answer.feedback,
                }

            items_response.append({
                "id": item.id,
                "item_type": item.item_type,
                "title": item.title,
                "instruction": item.instruction,
                "question_text": item.question_text,
                "order": item.order,
                "max_score": item.max_score,
                "min_words": item.min_words,
                "max_words": item.max_words,
                "correct_option_ids": correct_option_ids,
                "options": options_response,
                "answer": answer_response,
            })

        blocks_response.append({
            "block_id": block.id,
            "block_type": block.block_type,
            "title": block.title,
            "score": ab.score or 0,
            "status": ab.status,
            "items": items_response,
        })

    return {
        "attempt_id": attempt.id,
        "exam_id": exam.id,
        "exam_title": exam.title,
        "exam_type": exam.exam_type,
        "status": attempt.status,
        "total_score": total_score,
        "percentage": percentage,
        "cefr_estimate": attempt.cefr_estimate,
        "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
        "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
        "blocks": blocks_response,
    }