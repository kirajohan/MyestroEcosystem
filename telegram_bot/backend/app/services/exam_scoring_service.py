"""
Exam Scoring Service — Markazlashtirilgan baholash tizimi.
Listening/Reading: auto-scoring
Writing/Speaking: AI evaluation
"""

import logging
import os
from typing import Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.exam import (
    ExamAttempt, ExamAttemptBlock, ExamItem, ExamOption,
    ExamAnswer, Exam, ExamBlock
)
from app.services.exam_ai_service import evaluate_writing, evaluate_speaking
from app.services.exam.transcription_service import transcribe_audio

logger = logging.getLogger(__name__)


async def auto_score_listening_reading(
    attempt_id: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Listening va Reading uchun avtomatik baholash.
    """
    attempt_stmt = select(ExamAttempt).where(ExamAttempt.id == attempt_id)
    attempt_result = await db.execute(attempt_stmt)
    attempt = attempt_result.scalar_one_or_none()
    
    if not attempt:
        return {"error": "Attempt topilmadi", "scored": 0}
    
    answers_stmt = select(ExamAnswer).where(ExamAnswer.attempt_id == attempt_id)
    answers_result = await db.execute(answers_stmt)
    answers = answers_result.scalars().all()
    
    scored_count = 0
    total_auto_score = 0.0
    
    for answer in answers:
        item_stmt = select(ExamItem).where(ExamItem.id == answer.item_id)
        item_result = await db.execute(item_stmt)
        item = item_result.scalar_one_or_none()
        
        if not item:
            continue
        
        if item.item_type not in ["listening_question", "reading_question"]:
            continue
        
        answer_key = item.answer_key or {}
        correct_option_ids = answer_key.get("correct_option_ids", [])
        
        if not correct_option_ids:
            continue
        
        user_selected = answer.selected_options or []
        correct_count = len([opt_id for opt_id in user_selected if opt_id in correct_option_ids])
        total_correct = len(correct_option_ids)
        
        if total_correct > 0:
            score_ratio = correct_count / total_correct
            auto_score = float(item.max_score) * score_ratio
        else:
            auto_score = 0.0
        
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
    attempt_stmt = select(ExamAttempt).options(selectinload(ExamAttempt.exam)).where(ExamAttempt.id == attempt_id)
    attempt_result = await db.execute(attempt_stmt)
    attempt = attempt_result.scalar_one_or_none()
    
    if not attempt:
        return {"error": "Attempt topilmadi", "triggered": 0}
    
    cefr_level = attempt.exam.cefr_level or "B1"
    
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
        if not answer.text_answer or not answer.text_answer.strip():
            continue
        
        word_count = len(answer.text_answer.strip().split())
        if word_count < 5:
            logger.info(f"⚠️ Skipping AI for answer {answer.id}: only {word_count} words")
            continue
        
        item_stmt = select(ExamItem).where(ExamItem.id == answer.item_id)
        item_result = await db.execute(item_stmt)
        item = item_result.scalar_one_or_none()
        
        if not item:
            continue
        
        answer.ai_status = "processing"
        await db.commit()
        
        try:
            ai_result = await evaluate_writing(
                task_instruction=item.question_text or item.title or "",
                student_text=answer.text_answer,
                cefr_level=cefr_level,
                min_words=item.min_words,
                max_words=item.max_words,
                max_score=float(item.max_score or 1.0),
            )
            
            if "error" not in ai_result:
                normalized_score = ai_result.get("overall_score_normalized")
                
                if normalized_score is None:
                    ai_score_100 = ai_result.get("overall_score", 0)
                    normalized_score = (ai_score_100 / 100.0) * float(item.max_score or 1.0)
                
                answer.ai_score = normalized_score
                answer.final_score = normalized_score
                answer.ai_status = "completed"
                answer.feedback = ai_result
                
                logger.info(f"✅ Writing AI score saved: {normalized_score}/{item.max_score}")            
            else:
                answer.ai_status = "error"
                answer.feedback = {"error": ai_result.get("error")}
        
        except Exception as e:
            logger.error(f"❌ Writing AI evaluation failed for answer {answer.id}: {e}")
            answer.ai_status = "error"
            answer.feedback = {"error": str(e)}
        
        await db.commit()
        triggered_count += 1
    
    return {
        "triggered": triggered_count,
        "total_writing": len(writing_answers)
    }


async def trigger_speaking_evaluation(
    attempt_id: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Speaking javoblari uchun Transkripsiya va AI evaluation'ni ishga tushirish.
    """
    attempt_stmt = select(ExamAttempt).options(selectinload(ExamAttempt.exam)).where(ExamAttempt.id == attempt_id)
    attempt_result = await db.execute(attempt_stmt)
    attempt = attempt_result.scalar_one_or_none()
    
    if not attempt:
        return {"error": "Attempt topilmadi", "triggered": 0}
    
    cefr_level = attempt.exam.cefr_level or "B1"
    
    answers_stmt = (
        select(ExamAnswer)
        .join(ExamItem, ExamAnswer.item_id == ExamItem.id)
        .where(
            ExamAnswer.attempt_id == attempt_id,
            ExamItem.item_type == "speaking_task"
        )
    )
    answers_result = await db.execute(answers_stmt)
    speaking_answers = answers_result.scalars().all()
    
    triggered_count = 0
    
    for answer in speaking_answers:
        # 1. Transkript borligini tekshirish
        if not answer.transcript_text or not answer.transcript_text.strip():
            # Agar transkript yo'q bo'lsa, audio_url dan transkripsiya qilishga harakat qilamiz
            if answer.audio_url:
                logger.info(f"🎤 No transcript for answer {answer.id}, transcribing from audio...")
                
                # Audio fayl yo'lini aniqlash
                # audio_url format: /media/exam/audio/xxx.webm yoki to'liq URL
                audio_path = answer.audio_url
                if audio_path.startswith("/media/"):
                    # Local fayl
                    audio_path = f"/app{audio_path}"  # Docker ichida
                elif audio_path.startswith("http"):
                    # URL dan yuklab olish kerak (hozircha skip)
                    logger.warning(f"⚠️ HTTP audio URL not supported yet: {audio_path}")
                    answer.ai_status = "error"
                    answer.feedback = {"error": "HTTP audio URL not supported. Please use local storage."}
                    await db.commit()
                    continue
                else:
                    # Noto'g'ri format
                    answer.ai_status = "error"
                    answer.feedback = {"error": f"Invalid audio URL format: {audio_path}"}
                    await db.commit()
                    continue
                
                # Transkripsiya qilish
                transcription_result = await transcribe_audio(audio_path, language="en")
                
                if transcription_result["success"]:
                    answer.transcript_text = transcription_result["transcript"]
                    logger.info(f"✅ Transcription successful: {transcription_result['word_count']} words")
                else:
                    logger.error(f"❌ Transcription failed: {transcription_result['error']}")
                    answer.ai_status = "error"
                    answer.feedback = {"error": f"Transcription failed: {transcription_result['error']}"}
                    await db.commit()
                    continue
            else:
                # Audio ham yo'q
                answer.ai_status = "error"
                answer.feedback = {"error": "No audio file provided"}
                await db.commit()
                continue
        
        # 2. Item'ni olish
        item_stmt = select(ExamItem).where(ExamItem.id == answer.item_id)
        item_result = await db.execute(item_stmt)
        item = item_result.scalar_one_or_none()
        
        if not item:
            continue
        
        # 3. AI status'ni "processing" qilish
        answer.ai_status = "processing"
        await db.commit()
        
        try:
            # 4. AI evaluation chaqirish
            ai_result = await evaluate_speaking(
                task_instruction=item.question_text or item.title or "",
                transcript_text=answer.transcript_text,
                cefr_level=cefr_level,
                duration_sec=item.answer_time_sec,
                max_score=float(item.max_score or 1.0),
            )
            
            if "error" not in ai_result:
                normalized_score = ai_result.get("overall_score_normalized")
                if normalized_score is None:
                    ai_score_100 = ai_result.get("overall_score", 0)
                    normalized_score = (ai_score_100 / 100.0) * float(item.max_score or 1.0)
                
                answer.ai_score = normalized_score
                answer.final_score = normalized_score
                answer.ai_status = "completed"
                answer.feedback = ai_result
                
                logger.info(f"✅ Speaking AI score saved: {normalized_score}/{item.max_score}")            
            else:
                answer.ai_status = "error"
                answer.feedback = {"error": ai_result.get("error")}
        
        except Exception as e:
            logger.error(f"❌ Speaking AI evaluation failed for answer {answer.id}: {e}")
            answer.ai_status = "error"
            answer.feedback = {"error": str(e)}
        
        await db.commit()
        triggered_count += 1
    
    return {
        "triggered": triggered_count,
        "total_speaking": len(speaking_answers)
    }


async def calculate_final_scores(
    attempt_id: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Yakuniy ballarni hisoblash va attempt'ni yakunlash.
    """
    attempt_stmt = select(ExamAttempt).where(ExamAttempt.id == attempt_id)
    attempt_result = await db.execute(attempt_stmt)
    attempt = attempt_result.scalar_one_or_none()
    
    if not attempt:
        return {"error": "Attempt topilmadi"}
    
    answers_stmt = select(ExamAnswer).where(ExamAnswer.attempt_id == attempt_id)
    answers_result = await db.execute(answers_stmt)
    answers = answers_result.scalars().all()
    answers_map = {ans.item_id: ans for ans in answers}
    
    total_score = 0.0
    max_possible = 0.0
    completed_ai = 0
    pending_ai = 0
    items_map = {}
    
    for answer in answers:
        item_stmt = select(ExamItem).where(ExamItem.id == answer.item_id)
        item_result = await db.execute(item_stmt)
        item = item_result.scalar_one_or_none()
        if not item:
            continue
        items_map[item.id] = item
        
        max_possible += float(item.max_score or 0)
        total_score += float(answer.final_score or 0)
        
        if item.item_type in ["writing_task", "speaking_task"]:
            if answer.ai_status == "completed":
                completed_ai += 1
            elif answer.ai_status in ["pending", "processing"]:
                pending_ai += 1

    # ExamAttemptBlock holatini va ballini yangilash
    ab_stmt = select(ExamAttemptBlock).where(ExamAttemptBlock.attempt_id == attempt_id)
    ab_result = await db.execute(ab_stmt)
    attempt_blocks = ab_result.scalars().all()
    
    for ab in attempt_blocks:
        ab.status = "completed"
        ab.completed_at = func.now()
        
        block_score = 0.0
        for item_id, item in items_map.items():
            if item.block_id == ab.block_id:
                ans = answers_map.get(item_id)
                if ans and ans.final_score is not None:
                    block_score += float(ans.final_score or 0)
        ab.score = block_score

    attempt.total_score = total_score
    
    if pending_ai == 0:
        attempt.status = "completed"
        attempt.completed_at = func.now()
    else:
        attempt.status = "scoring"
    
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
    Asosiy submit funksiyasi — barcha scoring jarayonlarini ketma-ket bajaradi.
    """
    logger.info(f"🚀 Starting submit and score process for attempt {attempt_id}")
    
    # 1. Auto-score Listening/Reading
    auto_result = await auto_score_listening_reading(attempt_id, db)
    logger.info(f"Auto-scoring result: {auto_result}")
    
    # 2. Trigger Writing AI evaluation
    writing_result = await trigger_writing_evaluation(attempt_id, db)
    logger.info(f"Writing evaluation result: {writing_result}")
    
    # 3. Trigger Speaking AI evaluation (YANGI)
    speaking_result = await trigger_speaking_evaluation(attempt_id, db)
    logger.info(f"Speaking evaluation result: {speaking_result}")
    
    # 4. Calculate final scores
    final_result = await calculate_final_scores(attempt_id, db)
    logger.info(f"Final result: {final_result}")
    
    return {
        "attempt_id": attempt_id,
        "auto_scoring": auto_result,
        "writing_evaluation": writing_result,
        "speaking_evaluation": speaking_result,
        "final": final_result
    }