"""
Exam Scoring Service — Markazlashtirilgan baholash tizimi.
Listening/Reading: auto-scoring
Writing/Speaking: AI evaluation
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exam import (
    ExamAttempt, ExamAttemptBlock, ExamItem, ExamOption,
    ExamAnswer, Exam, ExamBlock
)
from app.services.exam_ai_service import evaluate_writing

logger = logging.getLogger(__name__)


async def auto_score_listening_reading(
    attempt_id: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Listening va Reading uchun avtomatik baholash.
    To'g'ri javoblarni answer_key bilan solishtiradi.
    """
    # Attempt'ni olish
    attempt_stmt = select(ExamAttempt).where(ExamAttempt.id == attempt_id)
    attempt_result = await db.execute(attempt_stmt)
    attempt = attempt_result.scalar_one_or_none()
    
    if not attempt:
        return {"error": "Attempt topilmadi", "scored": 0}
    
    # Barcha javoblarni olish
    answers_stmt = select(ExamAnswer).where(ExamAnswer.attempt_id == attempt_id)
    answers_result = await db.execute(answers_stmt)
    answers = answers_result.scalars().all()
    
    scored_count = 0
    total_auto_score = 0.0
    
    for answer in answers:
        # Item'ni olish
        item_stmt = select(ExamItem).where(ExamItem.id == answer.item_id)
        item_result = await db.execute(item_stmt)
        item = item_result.scalar_one_or_none()
        
        if not item:
            continue
        
        # Faqat Listening/Reading uchun
        if item.item_type not in ["listening_question", "reading_question"]:
            continue
        
        # answer_key'ni olish
        answer_key = item.answer_key or {}
        correct_option_ids = answer_key.get("correct_option_ids", [])
        
        if not correct_option_ids:
            continue
        
        # Foydalanuvchi javobini tekshirish
        user_selected = answer.selected_options or []
        
        # To'g'ri javoblar soni
        correct_count = len([opt_id for opt_id in user_selected if opt_id in correct_option_ids])
        total_correct = len(correct_option_ids)
        
        # Ball hisoblash
        if total_correct > 0:
            score_ratio = correct_count / total_correct
            auto_score = float(item.max_score) * score_ratio
        else:
            auto_score = 0.0
        
        # Javobni yangilash
        answer.auto_score = auto_score
        answer.final_score = auto_score
        answer.ai_status = "completed"
        
        total_auto_score += auto_score
        scored_count += 1
    
    await db.commit()
    
    logger.info(f"✅ Auto-scored {scored_count} items for attempt {attempt_id}")
    
    return {
        "scored": scored_count,
        "total_auto_score": total_auto_score
    }


async def trigger_writing_evaluation(
    attempt_id: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Writing javoblari uchun AI evaluation'ni ishga tushirish.
    """
    # Barcha Writing javoblarni topish
    answers_stmt = (
        select(ExamAnswer)
        .join(ExamItem, ExamAnswer.item_id == ExamItem.id)
        .where(
            ExamAnswer.attempt_id == attempt_id,
            ExamItem.item_type == "writing_task"
        )
    )
    answers_result = await db.execute(answers_stmt)
    writing_answers = answers_result.scalars().all()
    
    triggered_count = 0
    
    for answer in writing_answers:
        # Matn borligini tekshirish
        if not answer.text_answer or not answer.text_answer.strip():
            continue
        
        # So'zlar sonini tekshirish (min 5 so'z MVP uchun)
        word_count = len(answer.text_answer.strip().split())
        if word_count < 5:
            logger.info(f"⚠️ Skipping AI for answer {answer.id}: only {word_count} words")
            continue
        
        # Item'ni olish
        item_stmt = select(ExamItem).where(ExamItem.id == answer.item_id)
        item_result = await db.execute(item_stmt)
        item = item_result.scalar_one_or_none()
        
        if not item:
            continue
        
        # AI status'ni "processing" qilish
        answer.ai_status = "processing"
        await db.commit()
        
        # AI evaluation chaqirish
        logger.info(f"🤖 Evaluating writing for answer {answer.id}, attempt {attempt_id}")
        
        try:
            ai_result = await evaluate_writing(
                task_instruction=item.question_text or item.title or "",
                student_text=answer.text_answer,
                cefr_level="B1",  # TODO: exam'dan olish kerak
                min_words=item.min_words,
                max_words=item.max_words,
            )
            
            # Natijani saqlash
            if "error" not in ai_result:
                answer.ai_score = ai_result.get("overall_score", 0)
                answer.final_score = ai_result.get("overall_score", 0)
                answer.ai_status = "completed"
                answer.feedback = ai_result
                logger.info(f"✅ AI evaluation saved for answer {answer.id}: score={answer.ai_score}")
            else:
                answer.ai_status = "error"
                answer.feedback = {"error": ai_result.get("error")}
                logger.error(f"❌ AI error for answer {answer.id}: {ai_result.get('error')}")
        
        except Exception as e:
            logger.error(f"❌ AI evaluation failed for answer {answer.id}: {e}")
            answer.ai_status = "error"
            answer.feedback = {"error": str(e)}
        
        await db.commit()
        triggered_count += 1
    
    return {
        "triggered": triggered_count,
        "total_writing": len(writing_answers)
    }


async def calculate_final_scores(
    attempt_id: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Yakuniy ballarni hisoblash va attempt'ni yakunlash.
    """
    # Attempt'ni olish
    attempt_stmt = select(ExamAttempt).where(ExamAttempt.id == attempt_id)
    attempt_result = await db.execute(attempt_stmt)
    attempt = attempt_result.scalar_one_or_none()
    
    if not attempt:
        return {"error": "Attempt topilmadi"}
    
    # Barcha javoblarni olish
    answers_stmt = select(ExamAnswer).where(ExamAnswer.attempt_id == attempt_id)
    answers_result = await db.execute(answers_stmt)
    answers = answers_result.scalars().all()
    
    # Umumiy ball
    total_score = 0.0
    max_possible = 0.0
    completed_ai = 0
    pending_ai = 0
    
    for answer in answers:
        # Item'ni olish
        item_stmt = select(ExamItem).where(ExamItem.id == answer.item_id)
        item_result = await db.execute(item_stmt)
        item = item_result.scalar_one_or_none()
        
        if not item:
            continue
        
        max_possible += float(item.max_score or 0)
        total_score += float(answer.final_score or 0)
        
        # AI status tekshirish
        if item.item_type in ["writing_task", "speaking_task"]:
            if answer.ai_status == "completed":
                completed_ai += 1
            elif answer.ai_status in ["pending", "processing"]:
                pending_ai += 1
    
    # Attempt'ni yangilash
    attempt.total_score = total_score
    
    # Agar hamma AI tugagan bo'lsa, "completed" qilish
    if pending_ai == 0:
        attempt.status = "completed"
        attempt.completed_at = func.now()
        logger.info(f"✅ Attempt {attempt_id} completed: score={total_score}/{max_possible}")
    else:
        attempt.status = "scoring"
        logger.info(f"⏳ Attempt {attempt_id} still scoring: {pending_ai} AI jobs pending")
    
    await db.commit()
    
    return {
        "total_score": total_score,
        "max_possible": max_possible,
        "percentage": round((total_score / max_possible * 100), 1) if max_possible > 0 else 0,
        "completed_ai": completed_ai,
        "pending_ai": pending_ai,
        "status": attempt.status
    }


async def submit_and_score_attempt(
    attempt_id: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Asosiy submit funksiyasi — barcha scoring'larni ketma-ket bajaradi.
    """
    logger.info(f"🚀 Starting submit for attempt {attempt_id}")
    
    # 1. Auto-score Listening/Reading
    auto_result = await auto_score_listening_reading(attempt_id, db)
    logger.info(f"Auto-scoring result: {auto_result}")
    
    # 2. Trigger Writing AI evaluation
    writing_result = await trigger_writing_evaluation(attempt_id, db)
    logger.info(f"Writing evaluation result: {writing_result}")
    
    # 3. Calculate final scores
    final_result = await calculate_final_scores(attempt_id, db)
    logger.info(f"Final result: {final_result}")
    
    return {
        "attempt_id": attempt_id,
        "auto_scoring": auto_result,
        "writing_evaluation": writing_result,
        "final": final_result
    }