"""
Exam Scoring Service — Markazlashtirilgan baholash tizimi.
✅ [BE-02.2] N+1 muammosi hal qilingan — selectinload ishlatilgan
✅ [BE-04.1] Aniq holatlar — skip/error/timeout uchun
✅ [BE-02.1] Transaction optimizatsiyasi
"""

import logging
import traceback
from typing import Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.exam import (
    ExamAttempt, ExamAttemptBlock, ExamItem,
    ExamAnswer, Exam, ExamBlock
)
from app.services.exam_ai_service import evaluate_writing, evaluate_speaking
from app.services.exam.transcription_service import transcribe_audio

logger = logging.getLogger(__name__)

# Minimal so'z talabi (hardcoded — keyinroq item.min_words bilan almashtiriladi)
MIN_WORDS_FOR_AI = 5


# ═══════════════════════════════════════════════════════════
# 1. AUTO-SCORE (Tez, sinxron, N+1'siz)
# ═══════════════════════════════════════════════════════════

async def auto_score_attempt(
    attempt_id: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Faqat Listening/Reading uchun avtomatik baholash.
    ✅ N+1 yo'q — barcha items va options bitta query'da yuklangan.
    ✅ answer_key bo'sh bo'lsa, options.is_correct dan olinadi.
    """
    logger.info(f"🤖 Auto-scoring attempt {attempt_id}")

    # ✅ Javob berilmagan item'lar uchun bo'sh answer yaratish
    # (aks holda natija sahifasida "AI baholanmoqda" abadiy qoladi)
    attempt = await db.get(ExamAttempt, attempt_id)
    if attempt:
        existing_ids = set(
            (await db.execute(
                select(ExamAnswer.item_id).where(ExamAnswer.attempt_id == attempt_id)
            )).scalars().all()
        )
        all_items = (await db.execute(
            select(ExamItem)
            .join(ExamBlock, ExamBlock.id == ExamItem.block_id)
            .where(ExamBlock.exam_id == attempt.exam_id)
        )).scalars().all()
        for it in all_items:
            if it.id not in existing_ids:
                db.add(ExamAnswer(attempt_id=attempt_id, item_id=it.id))
        await db.flush()

    # ✅ Bitta query: answers + items + options
    answers_stmt = (
        select(ExamAnswer)
        .options(
            selectinload(ExamAnswer.item).selectinload(ExamItem.options)
        )
        .where(ExamAnswer.attempt_id == attempt_id)
    )
    answers_result = await db.execute(answers_stmt)
    answers = answers_result.scalars().all()
    
    scored_count = 0
    pending_ai = 0
    total_score = 0.0
    max_possible = 0.0
    
    for answer in answers:
        item = answer.item
        
        if not item:
            continue
        
        max_possible += float(item.max_score or 0)
        
        # Listening/Reading — auto-score
        if item.item_type in ["listening_question", "reading_question"]:
            
            # ✅ 1. Avval answer_key dan
            correct_option_ids = []
            if item.answer_key and item.answer_key.get("correct_option_ids"):
                correct_option_ids = item.answer_key["correct_option_ids"]
            
            # ✅ 2. answer_key bo'sh bo'lsa, options.is_correct dan
            if not correct_option_ids and item.options:
                correct_option_ids = [
                    opt.id for opt in item.options if opt.is_correct
                ]
            
            if correct_option_ids:
                user_selected = answer.selected_options or []
                correct_count = len([
                    opt for opt in user_selected 
                    if opt in correct_option_ids
                ])
                total_correct = len(correct_option_ids)
                
                if total_correct > 0:
                    score_ratio = correct_count / total_correct
                    auto_score = float(item.max_score) * score_ratio
                else:
                    auto_score = 0.0
                
                answer.auto_score = auto_score
                answer.final_score = auto_score
                answer.ai_status = "completed"
                total_score += auto_score
                scored_count += 1
            else:
                # To'g'ri javob topilmadi — 0 ball, lekin completed
                answer.auto_score = 0.0
                answer.final_score = 0.0
                answer.ai_status = "completed"
        
        # Writing/Speaking — AI kerak
        elif item.item_type in ["writing_task", "speaking_task"]:
            has_content = (
                bool((answer.text_answer or "").strip())
                if item.item_type == "writing_task"
                else bool((answer.transcript_text or "").strip() or answer.audio_url)
            )
            answer.auto_score = None
            answer.ai_score = None
            answer.final_score = 0.0
            if not has_content:
                # Bo'sh javob — AI'ga yuborilmaydi, 0 ball
                answer.ai_status = "completed"
                answer.ai_score = 0.0
                answer.feedback = {
                    "skipped": True,
                    "reason": "Javob berilmagan.",
                    "overall_score_normalized": 0.0,
                }
            else:
                answer.ai_status = "pending"
                pending_ai += 1
    
    await db.commit()
    
    logger.info(f"✅ Auto-scored {scored_count} items, {pending_ai} pending AI")
    
    return {
        "scored": scored_count,
        "pending_ai": pending_ai,
        "total_score": total_score,
        "max_possible": max_possible,
        "percentage": round((total_score / max_possible * 100), 1) if max_possible > 0 else 0
    }


# ═══════════════════════════════════════════════════════════
# 2. BACKGROUND AI EVALUATION
# ═══════════════════════════════════════════════════════════

async def process_ai_evaluation_background(attempt_id: int):
    """Background task: Writing/Speaking AI evaluation."""
    from app.database import async_session_maker
    
    logger.info(f"🤖 Background AI evaluation started for attempt {attempt_id}")
    
    try:
        async with async_session_maker() as db:
            # Writing evaluation
            logger.info(f"📝 Starting writing evaluation for attempt {attempt_id}")
            writing_result = await trigger_writing_evaluation(attempt_id, db)
            logger.info(f"✅ Writing evaluation completed: {writing_result}")
            
            # Speaking evaluation
            logger.info(f"🎤 Starting speaking evaluation for attempt {attempt_id}")
            speaking_result = await trigger_speaking_evaluation(attempt_id, db)
            logger.info(f"✅ Speaking evaluation completed: {speaking_result}")
            
            # Final scores
            logger.info(f"🧮 Calculating final scores for attempt {attempt_id}")
            final_result = await calculate_final_scores(attempt_id, db)
            logger.info(f"✅ Final scores calculated: {final_result}")
            
            logger.info(f"✅ Background AI evaluation completed for attempt {attempt_id}")
            
    except Exception as e:
        logger.error(f"❌ Background AI evaluation failed for attempt {attempt_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Xato bo'lsa: kutilayotgan javoblarni "error" qilib, attempt'ni baribir yakunlash
        # (aks holda foydalanuvchi uchun "AI baholanmoqda" abadiy qoladi)
        try:
            async with async_session_maker() as db:
                stuck = (await db.execute(
                    select(ExamAnswer).where(
                        ExamAnswer.attempt_id == attempt_id,
                        ExamAnswer.ai_status.in_(["pending", "processing"]),
                    )
                )).scalars().all()
                for a in stuck:
                    a.ai_status = "error"
                    a.feedback = {"error": f"Evaluation failed: {e}"}
                await db.commit()
                await calculate_final_scores(attempt_id, db)
        except Exception as e2:
            logger.error(f"❌ Failed to mark attempt as failed: {e2}")
            logger.error(f"Traceback: {traceback.format_exc()}")


# ═══════════════════════════════════════════════════════════
# 3. WRITING EVALUATION (N+1'siz, error isolation)
# ═══════════════════════════════════════════════════════════

async def trigger_writing_evaluation(
    attempt_id: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """Writing javoblari uchun AI evaluation."""
    logger.info(f"📝 trigger_writing_evaluation called for attempt {attempt_id}")
    
    attempt_stmt = select(ExamAttempt).options(selectinload(ExamAttempt.exam)).where(ExamAttempt.id == attempt_id)
    attempt_result = await db.execute(attempt_stmt)
    attempt = attempt_result.scalar_one_or_none()
    
    if not attempt:
        logger.error(f"❌ Attempt {attempt_id} not found")
        return {"error": "Attempt topilmadi", "triggered": 0, "skipped": 0}
    
    cefr_level = attempt.exam.cefr_level or "B1"
    logger.info(f"📚 CEFR level: {cefr_level}")
    
    # ✅ Bitta query: answers + items
    answers_stmt = (
        select(ExamAnswer)
        .options(selectinload(ExamAnswer.item))
        .join(ExamItem, ExamAnswer.item_id == ExamItem.id)
        .where(
            ExamAnswer.attempt_id == attempt_id,
            ExamItem.item_type == "writing_task"
        )
    )
    answers_result = await db.execute(answers_stmt)
    writing_answers = answers_result.scalars().all()
    
    logger.info(f"📝 Found {len(writing_answers)} writing answers")
    
    triggered_count = 0
    skipped_count = 0
    
    for answer in writing_answers:
        logger.info(f"📝 Processing writing answer {answer.id}")
        
        item = answer.item
        if not item:
            logger.error(f"❌ Item not found for answer {answer.id}")
            answer.ai_status = "error"
            answer.feedback = {"error": "Item not found"}
            await db.commit()
            continue

        text = (answer.text_answer or "").strip()
        word_count = len(text.split()) if text else 0

        # ✅ SKIP: juda qisqa javob
        if word_count < MIN_WORDS_FOR_AI:
            answer.ai_status = "completed"
            answer.ai_score = 0.0
            answer.final_score = 0.0
            answer.feedback = {
                "skipped": True,
                "reason": f"Javob juda qisqa ({word_count} so'z). Baholash uchun kamida {MIN_WORDS_FOR_AI} so'z kerak.",
                "overall_score_normalized": 0.0,
            }
            await db.commit()
            logger.info(f"⚠️ Answer {answer.id} skipped: {word_count} words → 0 ball")
            skipped_count += 1
            continue
        
        # ✅ AI evaluation
        answer.ai_status = "processing"
        await db.commit()
        
        try:
            logger.info(f"🤖 Calling evaluate_writing for answer {answer.id} ({word_count} words)")
            
            ai_result = await evaluate_writing(
                task_instruction=item.question_text or item.title or "",
                student_text=answer.text_answer,
                cefr_level=cefr_level,
                min_words=item.min_words,
                max_words=item.max_words,
                max_score=float(item.max_score or 1.0),
            )
            
            logger.info(f"✅ evaluate_writing returned for answer {answer.id}")
            
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
                triggered_count += 1
            else:
                logger.error(f"❌ AI returned error for answer {answer.id}: {ai_result.get('error')}")
                answer.ai_status = "error"
                answer.feedback = {"error": ai_result.get("error")}
        
        except Exception as e:
            logger.error(f"❌ Writing AI evaluation failed for answer {answer.id}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            answer.ai_status = "error"
            answer.feedback = {"error": str(e)}
        
        await db.commit()
    
    logger.info(f"✅ trigger_writing_evaluation completed: {triggered_count} evaluated, {skipped_count} skipped")
    
    return {
        "triggered": triggered_count,
        "skipped": skipped_count,
        "total_writing": len(writing_answers)
    }


# ═══════════════════════════════════════════════════════════
# 4. SPEAKING EVALUATION (N+1'siz, error isolation)
# ═══════════════════════════════════════════════════════════

async def trigger_speaking_evaluation(
    attempt_id: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """Speaking javoblari uchun AI evaluation."""
    logger.info(f"🎤 trigger_speaking_evaluation called for attempt {attempt_id}")
    
    attempt_stmt = select(ExamAttempt).options(selectinload(ExamAttempt.exam)).where(ExamAttempt.id == attempt_id)
    attempt_result = await db.execute(attempt_stmt)
    attempt = attempt_result.scalar_one_or_none()
    
    if not attempt:
        logger.error(f"❌ Attempt {attempt_id} not found")
        return {"error": "Attempt topilmadi", "triggered": 0}
    
    cefr_level = attempt.exam.cefr_level or "B1"
    logger.info(f"📚 CEFR level: {cefr_level}")
    
    # ✅ Bitta query: answers + items
    answers_stmt = (
        select(ExamAnswer)
        .options(selectinload(ExamAnswer.item))
        .join(ExamItem, ExamAnswer.item_id == ExamItem.id)
        .where(
            ExamAnswer.attempt_id == attempt_id,
            ExamItem.item_type == "speaking_task"
        )
    )
    answers_result = await db.execute(answers_stmt)
    speaking_answers = answers_result.scalars().all()
    
    logger.info(f"🎤 Found {len(speaking_answers)} speaking answers")
    
    triggered_count = 0
    
    for answer in speaking_answers:
        logger.info(f"🎤 Processing speaking answer {answer.id}")
        
        # Transkript tekshirish
        if not answer.transcript_text or not answer.transcript_text.strip():
            if answer.audio_url:
                logger.info(f"🎤 No transcript for answer {answer.id}, transcribing from audio...")
                
                audio_path = answer.audio_url
                if audio_path.startswith("/media/"):
                    audio_path = f"/app{audio_path}"
                elif audio_path.startswith("http"):
                    logger.warning(f"⚠️ HTTP audio URL not supported yet: {audio_path}")
                    answer.ai_status = "error"
                    answer.feedback = {"error": "HTTP audio URL not supported."}
                    await db.commit()
                    continue
                else:
                    logger.error(f"❌ Invalid audio URL format: {audio_path}")
                    answer.ai_status = "error"
                    answer.feedback = {"error": f"Invalid audio URL format: {audio_path}"}
                    await db.commit()
                    continue
                
                try:
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
                except Exception as e:
                    logger.error(f"❌ Transcription exception for answer {answer.id}: {e}")
                    answer.ai_status = "error"
                    answer.feedback = {"error": f"Transcription exception: {str(e)}"}
                    await db.commit()
                    continue
            else:
                # Bo'sh javob — AI'ga yuborilmaydi, 0 ball
                logger.info(f"⚠️ No audio for answer {answer.id} → 0 ball, AI skipped")
                answer.ai_status = "completed"
                answer.ai_score = 0.0
                answer.final_score = 0.0
                answer.feedback = {
                    "skipped": True,
                    "reason": "Javob berilmagan (audio yo'q).",
                    "overall_score_normalized": 0.0,
                }
                await db.commit()
                continue
        
        item = answer.item
        
        if not item:
            logger.error(f"❌ Item not found for answer {answer.id}")
            answer.ai_status = "error"
            answer.feedback = {"error": "Item not found"}
            await db.commit()
            continue
        
        # ✅ AI evaluation
        answer.ai_status = "processing"
        await db.commit()
        
        try:
            logger.info(f"🤖 Calling evaluate_speaking for answer {answer.id}")
            
            ai_result = await evaluate_speaking(
                task_instruction=item.question_text or item.title or "",
                transcript_text=answer.transcript_text,
                cefr_level=cefr_level,
                duration_sec=item.answer_time_sec,
                max_score=float(item.max_score or 1.0),
            )
            
            logger.info(f"✅ evaluate_speaking returned for answer {answer.id}")
            
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
                triggered_count += 1
            else:
                logger.error(f"❌ AI returned error for answer {answer.id}: {ai_result.get('error')}")
                answer.ai_status = "error"
                answer.feedback = {"error": ai_result.get("error")}
        
        except Exception as e:
            logger.error(f"❌ Speaking AI evaluation failed for answer {answer.id}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            answer.ai_status = "error"
            answer.feedback = {"error": str(e)}
        
        await db.commit()
    
    logger.info(f"✅ trigger_speaking_evaluation completed: {triggered_count}/{len(speaking_answers)}")
    
    return {
        "triggered": triggered_count,
        "total_speaking": len(speaking_answers)
    }


# ═══════════════════════════════════════════════════════════
# 5. FINAL SCORES (N+1'siz)
# ═══════════════════════════════════════════════════════════

async def calculate_final_scores(
    attempt_id: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """Yakuniy ballarni hisoblash."""
    logger.info(f"🧮 calculate_final_scores called for attempt {attempt_id}")
    
    attempt_stmt = select(ExamAttempt).where(ExamAttempt.id == attempt_id)
    attempt_result = await db.execute(attempt_stmt)
    attempt = attempt_result.scalar_one_or_none()
    
    if not attempt:
        logger.error(f"❌ Attempt {attempt_id} not found")
        return {"error": "Attempt topilmadi"}
    
    # ✅ Bitta query: answers + items
    answers_stmt = (
        select(ExamAnswer)
        .options(selectinload(ExamAnswer.item))
        .where(ExamAnswer.attempt_id == attempt_id)
    )
    answers_result = await db.execute(answers_stmt)
    answers = answers_result.scalars().all()
    answers_map = {ans.item_id: ans for ans in answers}
    
    total_score = 0.0
    max_possible = 0.0
    completed_ai = 0
    pending_ai = 0
    error_ai = 0
    items_map = {}
    
    for answer in answers:
        item = answer.item
        
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
            elif answer.ai_status == "error":
                error_ai += 1

    logger.info(f"📊 Scores: {completed_ai} completed, {pending_ai} pending, {error_ai} errors")

    # ExamAttemptBlock yangilash
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
        logger.info(f"✅ Attempt {attempt_id} marked as completed")
    else:
        attempt.status = "scoring"
        logger.info(f"⏳ Attempt {attempt_id} remains in scoring ({pending_ai} pending)")
    
    await db.commit()
    
    return {
        "total_score": total_score,
        "max_possible": max_possible,
        "percentage": round((total_score / max_possible * 100), 1) if max_possible > 0 else 0,
        "completed_ai": completed_ai,
        "pending_ai": pending_ai,
        "error_ai": error_ai,
        "status": attempt.status
    }