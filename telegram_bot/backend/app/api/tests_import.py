"""
Tests Import Endpoints — JSON orqali quiz yuklash
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_admin_user
from app.database import get_async_db
from app.models.user import User
from app.schemas.tests_import import (
    ImportTestsPayload,
    TestImportPreviewResponse,
    TestImportResultResponse,
)
from app.services.tests_import_service import TestsImportService

router = APIRouter(prefix="/tests/import", tags=["tests-import"])

import_service = TestsImportService()


@router.post(
    "/json/preview",
    response_model=TestImportPreviewResponse,
    summary="JSON test'ni validatsiya qilish",
)
async def preview_json_import(
    payload: ImportTestsPayload,
    current_user: User = Depends(get_current_admin_user),
):
    """JSON payload ni validatsiya qiladi. Bazaga yozmaydi."""
    return await import_service.validate(payload)


@router.post(
    "/json/confirm",
    response_model=TestImportResultResponse,
    summary="Validatsiya qilingan JSON ni DB ga saqlash",
)
async def confirm_json_import(
    payload: ImportTestsPayload,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Validatsiya qilingan ma'lumotni bazaga yozadi."""
    preview = await import_service.validate(payload)
    if not preview.valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Validatsiya xatolari",
                "errors": [e.model_dump() for e in preview.errors],
            },
        )

    result = await import_service.save(payload, db)

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Saqlashda xato", "errors": result.errors},
        )

    return result