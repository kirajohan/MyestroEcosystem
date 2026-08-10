"""Schemas for AI chat context and message history."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class ChatMessage(BaseModel):
    """Single message in chat history (OpenRouter format)."""
    role: str = Field(..., description="'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message text")
    
    class Config:
        examples = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]


class ChatHistory(BaseModel):
    """Full chat history with context for OpenRouter."""
    messages: List[ChatMessage] = Field(
        ..., 
        description="List of messages in conversation order"
    )
    system_prompt: Optional[str] = Field(
        None,
        description="System prompt with context summary (if generated)"
    )
    
    def to_openrouter_format(self) -> Dict[str, Any]:
        """Convert to OpenRouter API format."""
        result = {
            "messages": [{"role": m.role, "content": m.content} for m in self.messages]
        }
        if self.system_prompt:
            result["messages"].insert(0, {
                "role": "system",
                "content": self.system_prompt
            })
        return result


class AIMemorySessionResponse(BaseModel):
    """Response for AI memory session info."""
    session_id: UUID
    user_id: int
    title: Optional[str]
    language: str
    cefr_level: Optional[str]
    message_count: int
    is_active: bool
    context_summary: Optional[str]
    created_at: datetime
    last_activity_at: datetime
    expires_at: datetime
    
    class Config:
        from_attributes = True


class ChatQueryWithMemoryRequest(BaseModel):
    """Request for AI query with memory context."""
    user_id: int = Field(..., description="User ID for session lookup")
    message: str = Field(..., description="User's message")
    system_prompt: Optional[str] = Field(
        None,
        description="Custom system prompt (overrides default)"
    )
    model: Optional[str] = Field(
        None,
        description="Specific model to use (overrides default)"
    )
    temperature: Optional[float] = Field(
        0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature"
    )
    max_tokens: Optional[int] = Field(
        1024,
        ge=100,
        le=4000,
        description="Max tokens in response"
    )


class ChatQueryWithMemoryResponse(BaseModel):
    """Response from AI query with memory."""
    response: str = Field(..., description="AI response")
    session_id: UUID = Field(..., description="Session ID used")
    model_used: str = Field(..., description="Model that generated response")
    tokens_used: Optional[int] = Field(None, description="Tokens consumed")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    context_messages_count: int = Field(..., description="Number of context messages sent")
    
    class Config:
        from_attributes = True