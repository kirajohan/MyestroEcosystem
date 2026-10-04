"""
Maestro Exam — Admin API endpoints.

Bu endpointlar faqat admin huquqiga ega foydalanuvchilar uchun.
"""

# from __future__ import annota
from typing import Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_current_admin_user
from app.database import get_async_db, get_db
from app.models.exam import Exam, ExamBlock, ExamItem, ExamOption
from app.models.exam_enums import CEFRLevel, ExamType
from app.models.user import User
from app.schemas.exam import (
    ExamCreate,
    ExamRead,
    ExamListResponse,
    ExamListItem,
    ExamUpdate,
)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

logger = logging.getLogger(__name__)


router = APIRouter()


@router.get(
    "/exams",
    response_model=ExamListResponse,
    summary="Barcha examlar ro'yxati (admin)",
)
async def list_exams_admin(
    exam_type: Optional[ExamType] = Query(default=None),
    cefr_level: Optional[str] = Query(default=None),
    is_published: Optional[bool] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Admin uchun barcha examlar ro'yxati."""

    filters = []
    if exam_type:
        filters.append(Exam.exam_type == exam_type.value)
    if cefr_level:
        filters.append(Exam.cefr_level == cefr_level)
    if is_published is not None:
        filters.append(Exam.is_published == is_published)

    count_stmt = select(func.count(Exam.id))
    if filters:
        count_stmt = count_stmt.where(*filters)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one() or 0

    stmt = select(Exam).order_by(Exam.created_at.desc()).limit(limit).offset(offset)
    if filters:
        stmt = stmt.where(*filters)

    result = await db.execute(stmt)
    exams = result.scalars().all()

    return ExamListResponse(
        total=total,
        items=[
            ExamListItem(
                id=exam.id,
                code=exam.code,
                title=exam.title,
                description=exam.description,
                exam_type=exam.exam_type,
                cefr_level=exam.cefr_level,
                time_limit_sec=exam.time_limit_sec,
            )
            for exam in exams
        ],
    )

@router.post("/exams", response_model=ExamRead, status_code=status.HTTP_201_CREATED, summary="Yangi exam yaratish")
async def create_exam(
    payload: ExamCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user),
):
    existing = await db.execute(select(Exam).where(Exam.code == payload.code))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bu kod allaqachon mavjud: {payload.code}",
        )

    # ✅ MUHIM: Enum qiymatlarini string ga o'tkazamiz
    exam = Exam(
        code=payload.code,
        title=payload.title,
        description=payload.description,
        exam_type=payload.exam_type.value if hasattr(payload.exam_type, 'value') else str(payload.exam_type),
        cefr_level=payload.cefr_level.value if payload.cefr_level and hasattr(payload.cefr_level, 'value') else payload.cefr_level,
        time_limit_sec=payload.time_limit_sec,
        is_published=payload.is_published,
        scoring_config=payload.scoring_config,
    )

    db.add(exam)
    await db.commit()
    await db.refresh(exam)
    return exam

@router.get(
    "/exams/{exam_id}",
    response_model=ExamRead,
    summary="Exam tafsilotlari",
)
async def get_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Exam tafsilotlarini qaytaradi."""

    stmt = (
        select(Exam)
        .where(Exam.id == exam_id)
        .options(selectinload(Exam.blocks))
    )
    result = await db.execute(stmt)
    exam = result.scalar_one_or_none()

    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam topilmadi",
        )

    return exam


@router.put(
    "/exams/{exam_id}",
    response_model=ExamRead,
    summary="Exam tahrirlash",
)
async def update_exam(
    exam_id: int,
    payload: ExamUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Exam ma'lumotlarini yangilaydi."""

    stmt = select(Exam).where(Exam.id == exam_id)
    result = await db.execute(stmt)
    exam = result.scalar_one_or_none()

    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam topilmadi",
        )

    if payload.code and payload.code != exam.code:
        existing = await db.execute(
            select(Exam).where(Exam.code == payload.code, Exam.id != exam_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bu kod allaqachon mavjud: {payload.code}",
            )

    update_data = payload.model_dump(exclude_unset=True)
    
    # ✅ MUHIM: Enum'larni .value bilan yangilaymiz
    if "exam_type" in update_data and payload.exam_type:
        update_data["exam_type"] = payload.exam_type.value
    
    if "cefr_level" in update_data and payload.cefr_level:
        update_data["cefr_level"] = payload.cefr_level.value

    for field, value in update_data.items():
        setattr(exam, field, value)

    await db.commit()
    await db.refresh(exam)

    return exam
# ═══════════════════════════════════════════════════════════════
# BLOCKS CRUD
# ═══════════════════════════════════════════════════════════════

@router.get(
    "/exams/{exam_id}/blocks",
    summary="Exam blocklarini olish",
)
async def list_exam_blocks(
    exam_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Exam ichidagi barcha blocklarni qaytaradi."""
    stmt = (
        select(ExamBlock)
        .where(ExamBlock.exam_id == exam_id)
        .order_by(ExamBlock.order.asc())
    )
    result = await db.execute(stmt)
    blocks = result.scalars().all()
    return [
        {
            "id": b.id,
            "exam_id": b.exam_id,
            "block_type": b.block_type,
            "title": b.title,
            "description": b.description,
            "instructions": b.instructions,
            "passage_text": b.passage_text,       # ← YANGI
            "audio_url": b.audio_url,             # ← YANGI
            "audio_duration_sec": b.audio_duration_sec,  # ← YANGI
            "order": b.order,
            "time_limit_sec": b.time_limit_sec,
            "config": b.config,
            "created_at": b.created_at.isoformat() if b.created_at else None,
        }
        for b in blocks
    ]

# ═══════════════════════════════════════════════════════════════
# ITEMS (QUESTIONS / TASKS) CRUD
# ═══════════════════════════════════════════════════════════════

@router.get(
    "/blocks/{block_id}",
    summary="Block tafsilotlari (items bilan)",
)
async def get_block(
    block_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Block tafsilotlarini qaytaradi (items va options bilan)."""
    stmt = (
        select(ExamBlock)
        .where(ExamBlock.id == block_id)
        .options(selectinload(ExamBlock.items).selectinload(ExamItem.options))
    )
    result = await db.execute(stmt)
    block = result.scalar_one_or_none()
    
    if not block:
        raise HTTPException(status_code=404, detail="Block topilmadi")
    
    return {
        "id": block.id,
        "exam_id": block.exam_id,
        "block_type": block.block_type,
        "title": block.title,
        "description": block.description,
        "instructions": block.instructions,
        "passage_text": block.passage_text,
        "audio_url": block.audio_url,
        "audio_duration_sec": block.audio_duration_sec,
        "order": block.order,
        "time_limit_sec": block.time_limit_sec,
        "config": block.config,
        "created_at": block.created_at.isoformat() if block.created_at else None,
        "items": [
            {
                "id": item.id,
                "item_type": item.item_type,
                "title": item.title,
                "instruction": item.instruction,
                "question_text": item.question_text,
                "passage_text": item.passage_text,
                "audio_url": item.audio_url,
                "audio_duration_sec": item.audio_duration_sec,
                "transcript_text": item.transcript_text,
                "min_words": item.min_words,
                "max_words": item.max_words,
                "preparation_time_sec": item.preparation_time_sec,
                "answer_time_sec": item.answer_time_sec,
                "max_score": item.max_score,
                "order": item.order,
                "config": item.config,
                "answer_key": item.answer_key,
                "rubric_id": item.rubric_id,
                "options": [
                    {
                        "id": opt.id,
                        "text": opt.text,
                        "is_correct": opt.is_correct,
                        "order": opt.order,
                    }
                    for opt in sorted(item.options, key=lambda o: o.order)
                ] if item.options else [],
            }
            for item in sorted(block.items, key=lambda i: i.order)
        ],
    }

@router.post(
    "/blocks/{block_id}/items",
    status_code=status.HTTP_201_CREATED,
    summary="Block ichiga yangi savol qo'shish",
)
async def create_item(
    block_id: int,
    payload: dict,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Block ichiga yangi item yaratadi (options bilan birga)."""
    from app.models.exam import ExamBlock, ExamItem, ExamOption
    
    # Block mavjudligini tekshirish
    block_stmt = select(ExamBlock).where(ExamBlock.id == block_id)
    block_result = await db.execute(block_stmt)
    block = block_result.scalar_one_or_none()
    
    if not block:
        raise HTTPException(status_code=404, detail="Block topilmadi")
    
    # Keyingi order raqamini topish
    max_order_stmt = select(func.max(ExamItem.order)).where(
        ExamItem.block_id == block_id
    )
    max_order_result = await db.execute(max_order_stmt)
    max_order = max_order_result.scalar() or 0
    next_order = max_order + 1
    
    # Enum qiymatlarni string ga o'tkazish
    item_type = payload.get("item_type")
    if hasattr(item_type, "value"):
        item_type = item_type.value
    
    # Default item_type block_type ga mos
    if not item_type:
        item_type = f"{block.block_type}_question" if block.block_type in ["listening", "reading"] else f"{block.block_type}_task"
    
    # Item yaratish
    item = ExamItem(
        block_id=block_id,
        item_type=item_type,
        title=payload.get("title", f"Question {next_order}"),
        instruction=payload.get("instruction"),
        question_text=payload.get("question_text"),
        passage_text=payload.get("passage_text"),
        audio_url=payload.get("audio_url"),
        audio_duration_sec=payload.get("audio_duration_sec"),
        transcript_text=payload.get("transcript_text"),
        min_words=payload.get("min_words"),
        max_words=payload.get("max_words"),
        preparation_time_sec=payload.get("preparation_time_sec"),
        answer_time_sec=payload.get("answer_time_sec"),
        max_score=payload.get("max_score", 1.0),
        order=payload.get("order", next_order),
        config=payload.get("config"),
        answer_key=payload.get("answer_key"),
        rubric_id=payload.get("rubric_id"),
    )
    
    db.add(item)
    await db.flush()  # item.id olish uchun
    
    # ✅ YANGI: Options'larni yaratish
    options_data = payload.get("options", [])
    created_options = []
    
    for idx, opt_data in enumerate(options_data):
        if not opt_data.get("text", "").strip():
            continue  # Bo'sh variantlarni o'tkazib yuborish
        
        option = ExamOption(
            item_id=item.id,
            text=opt_data["text"],
            is_correct=opt_data.get("is_correct", False),
            order=opt_data.get("order", idx + 1),
        )
        db.add(option)
        created_options.append(option)
    
    await db.commit()
    await db.refresh(item)
    
    return {
        "id": item.id,
        "block_id": item.block_id,
        "item_type": item.item_type,
        "title": item.title,
        "order": item.order,
        "options_count": len(created_options),
    }

@router.put(
    "/items/{item_id}",
    summary="Savolni tahrirlash",
)
async def update_item(
    item_id: int,
    payload: dict,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Savol ma'lumotlarini yangilaydi (options bilan birga)."""
    from app.models.exam import ExamItem, ExamOption
    
    stmt = select(ExamItem).where(ExamItem.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Savol topilmadi")
    
    # Item maydonlarini yangilash
    updatable = [
        "title", "instruction", "question_text", "passage_text",
        "audio_url", "audio_duration_sec", "transcript_text",
        "min_words", "max_words", "preparation_time_sec", "answer_time_sec",
        "max_score", "order", "config", "answer_key", "rubric_id",
    ]
    
    for field in updatable:
        if field in payload:
            setattr(item, field, payload[field])
    
    if "item_type" in payload:
        it = payload["item_type"]
        item.item_type = it.value if hasattr(it, "value") else it
    
    # ✅ YANGI: Options'larni yangilash
    if "options" in payload:
        # Eski options'larni o'chirish
        old_opts_stmt = select(ExamOption).where(ExamOption.item_id == item_id)
        old_opts_result = await db.execute(old_opts_stmt)
        for old_opt in old_opts_result.scalars().all():
            await db.delete(old_opt)
        
        await db.flush()
        
        # Yangi options'larni yaratish
        options_data = payload.get("options", [])
        for idx, opt_data in enumerate(options_data):
            if not opt_data.get("text", "").strip():
                continue
            
            option = ExamOption(
                item_id=item_id,
                text=opt_data["text"],
                is_correct=opt_data.get("is_correct", False),
                order=opt_data.get("order", idx + 1),
            )
            db.add(option)
    
    await db.commit()
    await db.refresh(item)
    
    return {"id": item.id, "updated": True}


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Savolni o'chirish",
)
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Savol va uning barcha variantlarini o'chiradi."""
    from app.models.exam import ExamItem, ExamOption
    
    stmt = select(ExamItem).where(ExamItem.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Savol topilmadi")
    
    try:
        # Options o'chirish
        opts_stmt = select(ExamOption).where(ExamOption.item_id == item_id)
        opts_result = await db.execute(opts_stmt)
        for opt in opts_result.scalars().all():
            await db.delete(opt)
        
        # Item o'chirish
        await db.delete(item)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Savol o'chirishda xato: {str(e)}"
        )
    
    return None


# ═══════════════════════════════════════════════════════════════
# OPTIONS (VARIANTLAR) CRUD
# ═══════════════════════════════════════════════════════════════

@router.post(
    "/items/{item_id}/options",
    status_code=status.HTTP_201_CREATED,
    summary="Savolga variant qo'shish",
)
async def create_option(
    item_id: int,
    payload: dict,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Savolga yangi variant qo'shadi."""
    from app.models.exam import ExamItem, ExamOption
    
    # Item mavjudligini tekshirish
    item_stmt = select(ExamItem).where(ExamItem.id == item_id)
    item_result = await db.execute(item_stmt)
    item = item_result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Savol topilmadi")
    
    # Keyingi order raqamini topish
    max_order_stmt = select(func.max(ExamOption.order)).where(
        ExamOption.item_id == item_id
    )
    max_order_result = await db.execute(max_order_stmt)
    max_order = max_order_result.scalar() or 0
    next_order = max_order + 1
    
    option = ExamOption(
        item_id=item_id,
        text=payload.get("text", ""),
        is_correct=payload.get("is_correct", False),
        order=payload.get("order", next_order),
    )
    
    db.add(option)
    await db.commit()
    await db.refresh(option)
    
    return {
        "id": option.id,
        "item_id": option.item_id,
        "text": option.text,
        "is_correct": option.is_correct,
        "order": option.order,
    }


@router.put(
    "/options/{option_id}",
    summary="Variantni tahrirlash",
)
async def update_option(
    option_id: int,
    payload: dict,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Variant ma'lumotlarini yangilaydi."""
    from app.models.exam import ExamOption
    
    stmt = select(ExamOption).where(ExamOption.id == option_id)
    result = await db.execute(stmt)
    option = result.scalar_one_or_none()
    
    if not option:
        raise HTTPException(status_code=404, detail="Variant topilmadi")
    
    updatable = ["text", "is_correct", "order"]
    for field in updatable:
        if field in payload:
            setattr(option, field, payload[field])
    
    await db.commit()
    await db.refresh(option)
    
    return {"id": option.id, "updated": True}


@router.delete(
    "/options/{option_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Variantni o'chirish",
)
async def delete_option(
    option_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Variantni o'chiradi."""
    from app.models.exam import ExamOption
    
    stmt = select(ExamOption).where(ExamOption.id == option_id)
    result = await db.execute(stmt)
    option = result.scalar_one_or_none()
    
    if not option:
        raise HTTPException(status_code=404, detail="Variant topilmadi")
    
    await db.delete(option)
    await db.commit()
    return None

@router.post(
    "/exams/{exam_id}/blocks",
    status_code=status.HTTP_201_CREATED,
    summary="Yangi block yaratish",
)
async def create_block(
    exam_id: int,
    payload: dict,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Exam ichida yangi block yaratadi."""
    
    # 1. Exam mavjudligini tekshirish
    exam_stmt = select(Exam).where(Exam.id == exam_id)
    exam_result = await db.execute(exam_stmt)
    exam = exam_result.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam topilmadi")
    
    # 2. Block type ni olish va tekshirish
    block_type = payload.get("block_type")
    if hasattr(block_type, "value"):
        block_type = block_type.value
    
    # ✅ MUHIM: block_type "full" bo'la olmaydi! Faqat skill nomlari bo'lishi kerak.
    valid_block_types = ["listening", "reading", "writing", "speaking"]
    if not block_type or block_type not in valid_block_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Noto'g'ri block_type. Quyidagilardan biri bo'lishi kerak: {', '.join(valid_block_types)}"
        )
    
    # 3. Keyingi order raqamini topish
    max_order_stmt = select(func.max(ExamBlock.order)).where(
        ExamBlock.exam_id == exam_id
    )
    max_order_result = await db.execute(max_order_stmt)
    max_order = max_order_result.scalar() or 0
    next_order = max_order + 1
    
    # 4. Block yaratish
    block = ExamBlock(
        exam_id=exam_id,
        block_type=block_type,  # ✅ Endi faqat to'g'ri qiymat tushadi
        title=payload.get("title", f"{block_type.capitalize()} Section"),
        description=payload.get("description"),
        instructions=payload.get("instructions"),
        passage_text=payload.get("passage_text"),
        audio_url=payload.get("audio_url"),
        audio_duration_sec=payload.get("audio_duration_sec"),
        order=payload.get("order", next_order),
        time_limit_sec=payload.get("time_limit_sec", 0),
        config=payload.get("config"),
    )
    
    db.add(block)
    await db.commit()
    await db.refresh(block)
    
    return {
        "id": block.id,
        "exam_id": block.exam_id,
        "block_type": block.block_type,
        "title": block.title,
        "order": block.order,
    }

@router.put(
    "/blocks/{block_id}",
    summary="Block tahrirlash",
)
async def update_block(
    block_id: int,
    payload: dict,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Block ma'lumotlarini yangilaydi."""
    stmt = select(ExamBlock).where(ExamBlock.id == block_id)
    result = await db.execute(stmt)
    block = result.scalar_one_or_none()
    
    if not block:
        raise HTTPException(status_code=404, detail="Block topilmadi")
    
    # Yangilanishi mumkin bo'lgan maydonlar
    updatable = [
        "title", "description", "instructions",
        "passage_text", "audio_url", "audio_duration_sec",  # ← YANGI
        "order", "time_limit_sec", "config"
    ]   
    for field in updatable:
        if field in payload:
            setattr(block, field, payload[field])
    
    if "block_type" in payload:
        bt = payload["block_type"]
        block.block_type = bt.value if hasattr(bt, "value") else bt
    
    await db.commit()
    await db.refresh(block)
    return {"id": block.id, "updated": True}


@router.delete(
    "/blocks/{block_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Block o'chirish",
)
async def delete_block(
    block_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Block va uning barcha item/option/attempt_block larini o'chiradi."""
    from app.models.exam import ExamBlock, ExamItem, ExamOption, ExamAttemptBlock, ExamAnswer

    # 1. Block topish
    stmt = select(ExamBlock).where(ExamBlock.id == block_id)
    result = await db.execute(stmt)
    block = result.scalar_one_or_none()

    if not block:
        raise HTTPException(status_code=404, detail="Block topilmadi")

    try:
        # 2. Attempt blocks o'chirish (agar imtihon topshirilgan bo'lsa)
        ab_stmt = select(ExamAttemptBlock).where(ExamAttemptBlock.block_id == block_id)
        ab_result = await db.execute(ab_stmt)
        attempt_blocks = ab_result.scalars().all()
        
        for ab in attempt_blocks:
            # Avval shu attempt block'ga tegishli javoblarni o'chirish
            items_stmt = select(ExamItem.id).where(ExamItem.block_id == block_id)
            items_result = await db.execute(items_stmt)
            item_ids = [row[0] for row in items_result.all()]
            
            if item_ids:
                answers_stmt = select(ExamAnswer).where(
                    ExamAnswer.attempt_id == ab.attempt_id,
                    ExamAnswer.item_id.in_(item_ids)
                )
                answers_result = await db.execute(answers_stmt)
                for answer in answers_result.scalars().all():
                    await db.delete(answer)
            
            # Attempt block o'chirish
            await db.delete(ab)

        # 3. Options o'chirish
        items_stmt = select(ExamItem.id).where(ExamItem.block_id == block_id)
        items_result = await db.execute(items_stmt)
        item_ids = [row[0] for row in items_result.all()]
        
        if item_ids:
            opts_stmt = select(ExamOption).where(ExamOption.item_id.in_(item_ids))
            opts_result = await db.execute(opts_stmt)
            for opt in opts_result.scalars().all():
                await db.delete(opt)

        # 4. Items o'chirish
        if item_ids:
            items_stmt2 = select(ExamItem).where(ExamItem.id.in_(item_ids))
            items_result2 = await db.execute(items_stmt2)
            for item in items_result2.scalars().all():
                await db.delete(item)

        # 5. Block o'chirish
        await db.delete(block)
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Block o'chirishda xato: {str(e)}"
        )

    return None
    
@router.delete(
    "/exams/{exam_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exam o'chirish",
)
async def delete_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Exam va unga bog'liq barcha ma'lumotlarni o'chiradi."""
    
    from app.models.exam import ExamBlock, ExamItem, ExamOption, ExamAttempt
    
    # 1. Exam mavjudligini tekshirish
    stmt = select(Exam).where(Exam.id == exam_id)
    result = await db.execute(stmt)
    exam = result.scalar_one_or_none()

    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam topilmadi",
        )

    try:
        # 2. CASCADE bilan bog'liq ma'lumotlarni o'chirish
        # Avval options (eng chuqur daraja)
        options_stmt = select(ExamOption).join(ExamItem).join(ExamBlock).where(
            ExamBlock.exam_id == exam_id
        )
        options_result = await db.execute(options_stmt)
        options = options_result.scalars().all()
        for option in options:
            await db.delete(option)
        
        # 3. Items o'chirish
        items_stmt = select(ExamItem).join(ExamBlock).where(ExamBlock.exam_id == exam_id)
        items_result = await db.execute(items_stmt)
        items = items_result.scalars().all()
        for item in items:
            await db.delete(item)
        
        # 4. Blocks o'chirish
        blocks_stmt = select(ExamBlock).where(ExamBlock.exam_id == exam_id)
        blocks_result = await db.execute(blocks_stmt)
        blocks = blocks_result.scalars().all()
        for block in blocks:
            await db.delete(block)
        
        # 5. Attempts o'chirish (agar bo'lsa)
        attempts_stmt = select(ExamAttempt).where(ExamAttempt.exam_id == exam_id)
        attempts_result = await db.execute(attempts_stmt)
        attempts = attempts_result.scalars().all()
        for attempt in attempts:
            await db.delete(attempt)
        
        # 6. Exam'ning o'zini o'chirish
        await db.delete(exam)
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Exam o'chirishda xatolik: {str(e)}",
        )

    return None


# app/api/exam_v2/admin.py ichiga qo'shing

from fastapi import HTTPException
from sqlalchemy import select
@router.post("/bulk-import", summary="JSON orqali ommaviy exam yuklash")
async def bulk_import_exam(
    payload: dict,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user),
):
    try:
        exam_data = payload.get("exam")
        if not exam_data:
            raise HTTPException(status_code=400, detail="'exam' maydoni majburiy")
        
        existing_exam = await db.execute(select(Exam).where(Exam.code == exam_data.get("code")))
        if existing_exam.scalar_one_or_none():
            raise HTTPException(status_code=400, detail=f"Bu kod allaqachon mavjud: {exam_data.get('code')}")
        
        exam = Exam(
            code=exam_data.get("code"),
            title=exam_data.get("title"),
            description=exam_data.get("description"),
            exam_type=exam_data.get("exam_type"),
            cefr_level=exam_data.get("cefr_level"),
            time_limit_sec=exam_data.get("time_limit_sec", 0),
            is_published=exam_data.get("is_published", False),
        )
        db.add(exam)
        await db.flush()
        
        blocks_created = 0
        items_created = 0
        options_created = 0
        
        for block_data in payload.get("blocks", []):
            block = ExamBlock(
                exam_id=exam.id,
                block_type=block_data.get("block_type"),
                title=block_data.get("title"),
                description=block_data.get("description"),
                instructions=block_data.get("instructions"),
                passage_text=block_data.get("passage_text"),
                audio_url=block_data.get("audio_url"),
                audio_duration_sec=block_data.get("audio_duration_sec"),
                order=block_data.get("order", 1),
                time_limit_sec=block_data.get("time_limit_sec", 0),
                config=block_data.get("config"),
            )
            db.add(block)
            await db.flush()
            blocks_created += 1
            
            for item_data in block_data.get("items", []):
                options_data = item_data.pop("options", [])
                
                item = ExamItem(
                    block_id=block.id,
                    item_type=item_data.get("item_type"),
                    title=item_data.get("title"),
                    instruction=item_data.get("instruction"),
                    question_text=item_data.get("question_text"),
                    passage_text=item_data.get("passage_text"),
                    audio_url=item_data.get("audio_url"),
                    audio_duration_sec=item_data.get("audio_duration_sec"),
                    transcript_text=item_data.get("transcript_text"),
                    min_words=item_data.get("min_words"),
                    max_words=item_data.get("max_words"),
                    preparation_time_sec=item_data.get("preparation_time_sec"),
                    answer_time_sec=item_data.get("answer_time_sec"),
                    max_score=item_data.get("max_score", 1.0),
                    order=item_data.get("order", 1),
                    config=item_data.get("config"),
                )
                db.add(item)
                await db.flush()  # 1. Item ID olish uchun flush
                items_created += 1
                
                created_options = []
                for opt_data in options_data:
                    option = ExamOption(
                        item_id=item.id,
                        text=opt_data.get("text"),
                        is_correct=opt_data.get("is_correct", False),
                        order=opt_data.get("order", 1),
                    )
                    db.add(option)
                    created_options.append(option)
                
                await db.flush()  # 2. Option ID lar olish uchun flush
                
                # ✅ YANGI QO'SHILDI: is_correct=True bo'lgan variantlarning ID larini answer_key ga yozish
                correct_ids = [opt.id for opt in created_options if opt.is_correct]
                if correct_ids:
                    item.answer_key = {"correct_option_ids": correct_ids}
                
                options_created += len(created_options)
        
        await db.commit()
        
        return {
            "status": "success",
            "message": f"✅ Exam '{exam.title}' muvaffaqiyatli yuklandi!",
            "exam_id": exam.id,
            "exam_code": exam.code,
            "stats": {
                "blocks_created": blocks_created,
                "items_created": items_created,
                "options_created": options_created,
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Bulk import xatosi: {e}")
        raise HTTPException(status_code=400, detail=f"Import xatosi: {str(e)}")


# telegram_bot/backend/app/api/exam_v2/admin.py


# [BE-01.3] DTO: Faqat kerakli maydonni qabul qilish
class ExamPublishUpdate(BaseModel):
    is_published: bool

router = APIRouter(prefix="/admin", tags=["exam-admin"])

# ... boshqa endpointlar ...

@router.patch("/exams/{exam_id}/publish")
async def update_exam_publish_status(
    exam_id: int,
    payload: ExamPublishUpdate,
    db: AsyncSession = Depends(get_db), # get_db dependency sizda qanday nomlangan bo'lsa
    current_user: User = Depends(get_current_admin_user) # Admin auth dependency
):
    """Examning is_published holatini o'zgartirish"""
    # 1. Examni topish
    result = await db.execute(select(Exam).where(Exam.id == exam_id))
    exam = result.scalar_one_or_none()
    
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Exam topilmadi"
        )

    # 2. Holatni yangilash
    exam.is_published = payload.is_published
    
    # 3. Saqlash ([BE-02.1] Transaction chegarasi)
    await db.commit()
    await db.refresh(exam)

    # 4. Qaytarish
    return {
        "id": exam.id,
        "code": exam.code,
        "is_published": exam.is_published,
        "message": "Exam holati muvaffaqiyatli yangilandi"
    }