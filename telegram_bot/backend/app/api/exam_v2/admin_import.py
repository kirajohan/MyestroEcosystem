"""
Admin Import Endpoints — JSON orqali imtihon yuklash
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_admin_user
from app.database import get_async_db
from app.models.user import User
from app.schemas.exam_import import (
    ImportExam, ImportPreviewResponse,
    ImportConfirmRequest, ImportResultResponse
)
from app.services.exam_import_service import ExamImportService

router = APIRouter(prefix="/admin/import", tags=["admin-import"])

import_service = ExamImportService()


@router.post(
    "/json/preview",
    response_model=ImportPreviewResponse,
    summary="JSON faylni validatsiya qilish",
)
async def preview_json_import(
    payload: ImportExam,
    current_user: User = Depends(get_current_admin_user),
):
    """
    JSON ma'lumotni validatsiya qiladi.
    Xatolar va ogohlantirishlarni qaytaradi.
    Saqlamaydi — faqat ko'rib chiqish uchun.
    """
    result = await import_service.validate(payload)
    return result


@router.post(
    "/json/confirm",
    response_model=ImportResultResponse,
    summary="Validatsiya qilingan JSON ni DB ga saqlash",
)
async def confirm_json_import(
    request: ImportConfirmRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Validatsiya qilingan ma'lumotni bazaga yozadi.
    Avval /json/preview chaqirilishi tavsiya etiladi.
    """
    # Qayta validatsiya (xavfsizlik uchun)
    preview = await import_service.validate(request.data)
    if not preview.valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Validatsiya xatolari",
                "errors": [e.model_dump() for e in preview.errors],
            },
        )

    result = await import_service.save(request.data, db)

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Saqlashda xato", "errors": result.errors},
        )

    return result