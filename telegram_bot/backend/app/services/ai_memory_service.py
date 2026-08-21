"""AI Memory Service — manages chat history, context, and OpenRouter queries."""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID
import time

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.models.conversation import Message, ConversationThread
from app.models.ai_memory import AIMemorySession
from app.models.user import User
from app.schemas.chat_context import ChatMessage, ChatHistory, ChatQueryWithMemoryResponse
from app.services.ai_service import ask_ai
from app.config import settings

logger = logging.getLogger(__name__)

# Memory management constants
REDIS_MEMORY_TTL = 7200  # 2 hours cache for active sessions
MAX_MEMORY_MESSAGES = 10  # Send last 10 messages to OpenRouter
SUMMARY_THRESHOLD = 15   # Generate summary when > 15 messages
SLIDING_WINDOW_SIZE = 12  # Include last 12 for summary generation


class AIMemoryService:
    """Manages AI conversation memory, context, and chat history."""
    
    def __init__(self, db_session: AsyncSession, redis_client: redis.Redis):
        self.db = db_session
        self.redis = redis_client
    
    # ═══════════════════════════════════════════════════════════════════
    # SESSION MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════
    
    async def get_or_create_session(
        self, 
        user_id: int,
        language: str = "uz",
        cefr_level: Optional[str] = None
    ) -> AIMemorySession:
        """Get active session or create new one."""
        
        # Check if active session exists
        stmt = select(AIMemorySession).where(
            and_(
                AIMemorySession.user_id == user_id,
                AIMemorySession.is_active == True
            )
        )
        result = await self.db.execute(stmt)
        existing_session = result.scalar_one_or_none()
        
        if existing_session and not existing_session.is_expired():
            # Update last_activity
            existing_session.last_activity_at = datetime.utcnow()
            await self.db.commit()
            return existing_session
        
        # Create new session
        new_session = AIMemorySession.create_new(
            user_id=user_id,
            language=language,
            cefr_level=cefr_level
        )
        self.db.add(new_session)
        await self.db.commit()
        await self.db.refresh(new_session)
        
        logger.info(f"Created new AI session {new_session.session_id} for user {user_id}")
        return new_session
    
    async def cleanup_expired_sessions(self) -> int:
        """Delete expired sessions (cleanup task for scheduler)."""
        stmt = select(AIMemorySession).where(
            AIMemorySession.expires_at < datetime.utcnow()
        )
        result = await self.db.execute(stmt)
        expired_sessions = result.scalars().all()
        
        count = 0
        for session in expired_sessions:
            await self.db.delete(session)
            count += 1
        
        await self.db.commit()
        logger.info(f"Cleaned up {count} expired AI sessions")
        return count
    
    # ═══════════════════════════════════════════════════════════════════
    # THREAD MANAGEMENT (FIX: thread_id NULL xatosini oldini olish)
    # ═══════════════════════════════════════════════════════════════════
    
    async def _get_or_create_thread(self, user_id: int) -> ConversationThread:
        """
        Get the active conversation thread for a user, or create a new one.
        This fixes the 'thread_id NULL' database error.
        """
        # Try to find an existing active thread
        stmt = select(ConversationThread).where(
            and_(
                ConversationThread.user_id == user_id,
                ConversationThread.is_active == True
            )
        ).order_by(desc(ConversationThread.created_at)).limit(1)
        
        result = await self.db.execute(stmt)
        thread = result.scalar_one_or_none()
        
        if thread:
            logger.debug(f"Using existing thread {thread.id} for user {user_id}")
            return thread
        
        # Create new thread if none exists
        logger.info(f"Creating new conversation thread for user {user_id}")
        new_thread = ConversationThread(
            user_id=user_id,
            title="AI Chat",
            is_active=True,
            cefr_level="A1"
        )
        self.db.add(new_thread)
        await self.db.commit()
        await self.db.refresh(new_thread)
        
        return new_thread
    
    # ═══════════════════════════════════════════════════════════════════
    # REDIS CACHE OPERATIONS
    # ═══════════════════════════════════════════════════════════════════
    
    def _get_redis_key(self, session_id: UUID) -> str:
        """Redis key for session messages."""
        return f"ai_chat:{session_id}:messages"
    
    def _get_summary_key(self, session_id: UUID) -> str:
        """Redis key for session summary."""
        return f"ai_chat:{session_id}:summary"
    
    async def _get_redis_messages(self, session_id: UUID) -> List[ChatMessage]:
        """Get messages from Redis cache."""
        try:
            redis_key = self._get_redis_key(session_id)
            cached_json = await self.redis.get(redis_key)
            
            if not cached_json:
                return []
            
            messages_data = json.loads(cached_json)
            return [
                ChatMessage(role=m["role"], content=m["content"])
                for m in messages_data
                if isinstance(m, dict) and "role" in m and "content" in m
            ]
        except Exception as e:
            logger.error(f"Error retrieving Redis messages: {e}")
            return []
    
    async def _save_to_redis(self, session_id: UUID, messages: List[ChatMessage]) -> None:
        """Save messages to Redis cache."""
        try:
            redis_key = self._get_redis_key(session_id)
            messages_json = json.dumps([
                {"role": m.role, "content": m.content}
                for m in messages
            ])
            await self.redis.setex(
                redis_key,
                REDIS_MEMORY_TTL,
                messages_json
            )
        except Exception as e:
            logger.error(f"Error saving to Redis: {e}")
    
    async def _get_redis_summary(self, session_id: UUID) -> Optional[str]:
        """Get context summary from Redis."""
        try:
            summary_key = self._get_summary_key(session_id)
            summary = await self.redis.get(summary_key)
            if not summary:
                return None
            
            # ✅ FIX: Agar bytes bo'lsa decode qiladi, agar string bo'lsa to'g'ridan-to'g'ri qaytaradi
            return summary.decode() if isinstance(summary, bytes) else summary
        except Exception as e:
            logger.error(f"Error retrieving summary from Redis: {e}")
            return None
        
    # ═══════════════════════════════════════════════════════════════════
    # MESSAGE HISTORY BUILDING
    # ═══════════════════════════════════════════════════════════════════
    
    async def get_chat_history(
        self,
        session_id: UUID,
        limit: int = MAX_MEMORY_MESSAGES
    ) -> List[ChatMessage]:
        """Get chat history: first check Redis cache, then PostgreSQL."""
        
        # 1. Try Redis cache (fast path)
    # 1. Try Redis cache (fast path)
        redis_messages = await self._get_redis_messages(session_id)
        if redis_messages:
            return redis_messages   # ← ESKI KESHNI QAYTARADI! Yangi xabarlar yo'q!
        
            # 2. Fall back to PostgreSQL (slow path)
        logger.debug(f"Cache miss, loading from PostgreSQL for session {session_id}")
        stmt = select(Message).where(
            Message.session_id == session_id
        ).order_by(
            desc(Message.created_at)
        ).limit(limit)
        
        result = await self.db.execute(stmt)
        messages_db = result.scalars().all()
        
        # Reverse to get chronological order
        messages = [
            ChatMessage(role=m.role, content=m.content)
            for m in reversed(messages_db)
        ]
        
        # Cache in Redis for future queries
        if messages:
            await self._save_to_redis(session_id, messages)
        
        return messages
    
    async def build_context_for_query(
        self,
        session_id: UUID,
        user_message: str,
        system_prompt: Optional[str] = None,
        use_summary: bool = True
    ) -> ChatHistory:
        """Build full chat context for OpenRouter API."""
        
        # Get message count to determine if we need summary
        stmt = select(Message).where(Message.session_id == session_id)
        result = await self.db.execute(stmt)
        all_messages_db = result.scalars().all()
        total_message_count = len(all_messages_db)
        
        # Get chat history (last 10)
        history_messages = await self.get_chat_history(session_id, limit=MAX_MEMORY_MESSAGES)
        
        # Generate summary if needed
        summary = None
        if use_summary and total_message_count > SUMMARY_THRESHOLD:
            logger.debug(f"Session has {total_message_count} messages, generating summary...")
            summary = await self._generate_or_get_summary(
                session_id,
                all_messages_db[-SLIDING_WINDOW_SIZE:]
            )
        
        # Build system prompt with summary
        if not system_prompt:
            system_prompt = self._build_system_prompt(summary)
        
        # Add user's current message
        all_messages = history_messages + [ChatMessage(role="user", content=user_message)]
        
        return ChatHistory(
            messages=all_messages,
            system_prompt=system_prompt
        )
    
    async def _generate_or_get_summary(
        self,
        session_id: UUID,
        recent_messages: List[Message]
    ) -> str:
        """Generate summary using AI or get from cache."""
        
        # Check if summary exists in Redis
        cached_summary = await self._get_redis_summary(session_id)
        if cached_summary:
            logger.debug("Using cached summary")
            return cached_summary
        
        # Build summary request
        convo_text = "\n".join([
            f"{m.role}: {m.content[:200]}"
            for m in recent_messages
        ])
        
        summary_prompt = f"""Summarize this conversation in 2-3 sentences. Focus on:
- Main topics discussed
- User's learning level/goals
- Any corrections or key points

Conversation:
{convo_text}"""
        
        try:
            summary = await ask_ai(
                prompt=summary_prompt,
                system_prompt="You are a conversation summarizer. Be concise and factual.",
                temperature=0.3,
                max_tokens=200
            )
            
            # Cache summary for 24 hours
            summary_key = self._get_summary_key(session_id)
            await self.redis.setex(summary_key, 86400, summary)
            
            logger.info(f"Generated summary for session {session_id}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Previous conversation context"
    
    def _build_system_prompt(self, summary: Optional[str] = None) -> str:
        """Build system prompt with optional summary."""
        base_prompt = """You are Myestro Teacher, an AI English tutor specializing in:
        - Teaching English from A1 to C2 levels
        - IELTS, TOEFL, CEFR exam preparation
        - Practical conversation and grammar correction
        - Vocabulary and pronunciation improvement

Provide clear, supportive, and educational responses. Correct mistakes gently."""
        
        if summary:
            base_prompt += f"\n\n[Context from previous chat]: {summary}"
        
        return base_prompt
    
    # ═══════════════════════════════════════════════════════════════════
    # QUERY & RESPONSE HANDLING (BARCHA XATOLAR TUZATILGAN)
    # ═══════════════════════════════════════════════════════════════════
    async def query_with_memory(
        self,
        user_id: int,
        user_message: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> ChatQueryWithMemoryResponse:
        """
        Main method: Query AI with full memory context.
        """
        start_time = time.time()
        
        # 1. Get or create session
        session = await self.get_or_create_session(user_id)
        logger.info(f"Using session {session.session_id} for user {user_id}")
        
        # 2. Get or create thread (FIX: thread_id NULL xatosini oldini olish)
        thread = await self._get_or_create_thread(user_id)
        
        # 3. Build context
        chat_history = await self.build_context_for_query(
            session.session_id,
            user_message,
            system_prompt=system_prompt
        )
        
        context_message_count = len(chat_history.messages)
        logger.debug(f"Built context with {context_message_count} messages")
        
        # 🔍 DEBUG: Chat history ni log qilish
        logger.info(f"=== DEBUG: Chat History ===")
        logger.info(f"Total messages in history: {len(chat_history.messages)}")
        for idx, msg in enumerate(chat_history.messages):
            logger.info(f"Message {idx + 1}: role={msg.role}, content={msg.content[:100]}...")
        logger.info(f"=== END DEBUG ===")
        
        # 4. FIX: Convert Pydantic ChatMessage objects to dicts before sending to AI
        chat_history_dicts = [
            {"role": msg.role, "content": msg.content} 
            for msg in chat_history.messages
        ]
        
        # 🔍 DEBUG: Dict formatini ham log qilish
        logger.info(f"Sending to AI: {len(chat_history_dicts)} messages in chat_history")
        
        # 5. Query AI (with fixed chat_history format)
        try:
            ai_response = await ask_ai(
                prompt=user_message,
                chat_history=chat_history_dicts,  # ✅ Endi dict formatida
                system_prompt=chat_history.system_prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            logger.error(f"AI query failed: {e}")
            ai_response = "Kechirasiz, AI javob bera olmayapti. Iltimos, keyinroq urinib ko'ring."
        
        processing_time = int((time.time() - start_time) * 1000)
        
        # 6. Save messages to storage (with valid thread_id)
        await self._save_messages_to_storage(
            session_id=session.session_id,
            thread_id=thread.id,  # ✅ Endi NULL emas
            user_id=user_id,
            user_message=user_message,
            ai_response=ai_response,
            model_used=model or "gpt-4o-mini",
            tokens_used=None,
            processing_time_ms=processing_time
        )
        
        # 7. FIX: Refresh session object to prevent MissingGreenlet error
        await self.db.refresh(session)
        
        # Update session activity
        session.last_activity_at = datetime.utcnow()
        session.message_count += 2
        await self.db.commit()
        await self.db.refresh(session)
        
        # Update Redis cache
        # 7. Update Redis cache
        # Update Redis cache — avval eski keshni o'chirish shart
        await self.redis.delete(self._get_redis_key(session.session_id))
        updated_history = await self.get_chat_history(session.session_id)
        await self._save_to_redis(session.session_id, updated_history)
        
        # 8. Return response
        return ChatQueryWithMemoryResponse(
            response=ai_response,
            session_id=session.session_id,
            model_used=model or "gpt-4o-mini",
            tokens_used=None,
            processing_time_ms=processing_time,
            context_messages_count=context_message_count
        )
        
    async def _save_messages_to_storage(
        self,
        session_id: UUID,
        thread_id: Optional[int],
        user_id: int,
        user_message: str,
        ai_response: str,
        model_used: str,
        tokens_used: Optional[int],
        processing_time_ms: int
    ) -> None:
        """Save user and AI messages to PostgreSQL."""
        
        try:
            # User message
            user_msg = Message(
                session_id=session_id,
                thread_id=thread_id,
                user_id=user_id,
                role="user",
                content=user_message,
                content_type="text",
                source="api",
                is_in_memory=True
            )
            
            # AI message
            ai_msg = Message(
                session_id=session_id,
                thread_id=thread_id,
                user_id=user_id,
                role="assistant",
                content=ai_response,
                content_type="text",
                ai_model=model_used,
                tokens_used=tokens_used,
                processing_time_ms=processing_time_ms,
                source="api",
                is_in_memory=True
            )
            
            self.db.add(user_msg)
            self.db.add(ai_msg)
            await self.db.commit()
            
            logger.debug(f"Saved messages to PostgreSQL for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error saving messages to storage: {e}")
            await self.db.rollback()
    
    # ═══════════════════════════════════════════════════════════════════
    # CLEANUP & MAINTENANCE
    # ═══════════════════════════════════════════════════════════════════
    
    async def clear_session_memory(self, session_id: UUID) -> bool:
        """Clear Redis cache for session (soft delete)."""
        try:
            redis_key = self._get_redis_key(session_id)
            summary_key = self._get_summary_key(session_id)
            
            await self.redis.delete(redis_key)
            await self.redis.delete(summary_key)
            
            logger.info(f"Cleared memory for session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing session memory: {e}")
            return False