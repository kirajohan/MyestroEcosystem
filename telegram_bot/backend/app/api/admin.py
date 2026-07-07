from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.services.ai_service import ask_ai

router = APIRouter(prefix="/admin", tags=["admin"])


class AIChatRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None


class AIChatResponse(BaseModel):
    response: str


@router.post("/ai-chat", response_model=AIChatResponse)
async def admin_ai_chat(
    data: AIChatRequest,
):
    result = await ask_ai(
        data.prompt,
        system_prompt=data.system_prompt or "You are a helpful admin assistant for Myestro platform.",
    )
    return AIChatResponse(response=result)
