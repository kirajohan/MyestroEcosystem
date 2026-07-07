from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.ai_service import ask_ai, analyze_error_logs
from app.models.logs import ErrorLog
from sqlalchemy.orm import Session as DBSession
from app.database import get_db

router = APIRouter(prefix="/ai-assistant", tags=["ai_assistant"])


class AIQueryRequest(BaseModel):
    prompt: str
    chat_history: Optional[List[Dict[str, str]]] = None
    system_prompt: Optional[str] = None


class AIQueryResponse(BaseModel):
    response: str


@router.get("/query", response_model=AIQueryResponse)
async def query_ai(
    prompt: str,
    db: DBSession = Depends(get_db),
):
    result = await ask_ai(prompt)
    return AIQueryResponse(response=result)


@router.post("/analyze-logs")
async def analyze_logs(
    db: DBSession = Depends(get_db),
):
    logs = db.query(ErrorLog).filter(ErrorLog.is_fixed == False).limit(10).all()
    log_data = [
        {
            "id": log.id,
            "error_type": log.error_type,
            "error_message": log.error_message,
            "service": log.service,
        }
        for log in logs
    ]
    results = await analyze_error_logs(log_data)

    for item in results:
        log_id = item.get("id")
        if not log_id:
            continue
        matching_log = db.query(ErrorLog).filter(
            ErrorLog.id == log_id
        ).first()
        if matching_log:
            matching_log.cause = item.get("cause")
            matching_log.solution = item.get("solution")
    db.commit()

    return {"analyzed": len(results), "results": results}
