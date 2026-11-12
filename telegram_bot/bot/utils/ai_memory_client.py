"""Bot client for AI memory service (backend communication)."""

import logging
from typing import Dict, Any, Optional
import httpx
from bot.utils.backend_http import BackendClient

logger = logging.getLogger(__name__)


class AIMemoryClient:
    """Client for communicating with backend AI memory service."""
    
    def __init__(self, backend_url: str, http_client: Optional[httpx.AsyncClient] = None):
        self.backend_url = backend_url.rstrip("/")
        self.http_client = http_client
        self._default_client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get HTTP client (use provided or create default)."""
        if self.http_client:
            return self.http_client
        
        if not self._default_client:
            self._default_client = BackendClient(
                timeout=30.0,
                limits=httpx.Limits(max_keepalive_connections=5)
            )
        
        return self._default_client
    
    async def query_with_memory(
        self,
        user_id: int,
        message: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """
        Query AI with memory context.
        
        Returns:
        {
            "response": str,
            "session_id": uuid,
            "model_used": str,
            "tokens_used": int,
            "processing_time_ms": int,
            "context_messages_count": int
        }
        """
        
        try:
            client = await self._get_client()
            
            payload = {
                "user_id": user_id,
                "message": message,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            if system_prompt:
                payload["system_prompt"] = system_prompt
            if model:
                payload["model"] = model
            
            response = await client.post(
                f"{self.backend_url}/ai-assistant/query-with-memory",
                json=payload
            )
            
            response.raise_for_status()
            return response.json()
            
        except httpx.TimeoutException:
            logger.error(f"Timeout querying AI service for user {user_id}")
            raise Exception("AI service timeout")
        
        except httpx.HTTPError as e:
            logger.error(f"HTTP error in AI query: {e}")
            raise Exception(f"AI service error: {e}")
        
        except Exception as e:
            logger.error(f"Error in query_with_memory: {e}", exc_info=True)
            raise
    
    async def clear_memory(self, user_id: int) -> Dict[str, Any]:
        """Clear AI memory for user."""
        
        try:
            client = await self._get_client()
            
            response = await client.post(
                f"{self.backend_url}/ai-assistant/session/{user_id}/clear"
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Error clearing memory for user {user_id}: {e}")
            raise
    
    async def get_session_info(self, user_id: int) -> Dict[str, Any]:
        """Get user's current AI session info."""
        
        try:
            client = await self._get_client()
            
            response = await client.get(
                f"{self.backend_url}/ai-assistant/session/{user_id}"
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting session for user {user_id}: {e}")
            raise
    
    async def close(self):
        """Close HTTP client connection."""
        if self._default_client:
            await self._default_client.aclose()
            self._default_client = None