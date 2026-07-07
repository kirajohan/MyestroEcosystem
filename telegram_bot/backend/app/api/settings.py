"""Settings router — global AI toggle endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.settings import SystemSetting
from app.schemas.user import SystemSettingResponse, SystemSettingUpdateRequest

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/ai", response_model=SystemSettingResponse)
def get_global_ai_status(
    db: Session = Depends(get_db),
):
    """Get global AI toggle status."""
    setting = db.query(SystemSetting).filter(SystemSetting.key == "ai_global_enabled").first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting


@router.get("/ai-public")
def get_ai_global_status_public(db: Session = Depends(get_db)):
    """Get global AI toggle status (Public/Bot — no auth required)."""
    setting = db.query(SystemSetting).filter(SystemSetting.key == "ai_global_enabled").first()
    if not setting:
        return {"value": "true"}
    return {"value": setting.value}


@router.put("/ai", response_model=SystemSettingResponse)
def toggle_global_ai(
    request: SystemSettingUpdateRequest,
    db: Session = Depends(get_db),
):
    """Toggle global AI on/off."""
    if request.value not in ("true", "false"):
        raise HTTPException(status_code=400, detail="Value must be 'true' or 'false'")

    setting = db.query(SystemSetting).filter(SystemSetting.key == "ai_global_enabled").first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    setting.value = request.value
    db.commit()
    db.refresh(setting)
    return setting
