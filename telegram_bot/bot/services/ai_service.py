import logging
import httpx
from bot.utils.backend_http import BackendClient
from bot.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Service to manage AI operations."""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.api_url = "https://openrouter.ai/api/v1"
        self.client = None
    
    async def health_check(self) -> bool:
        """Check if AI service is available."""
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY not set - AI service disabled")
            return False
        
        logger.info(f"Testing OpenRouter API with key length: {len(self.api_key)}")
        
        try:
            async with BackendClient(timeout=5) as client:
                # Try with Bearer token
                response = await client.get(
                    f"{self.api_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                
                logger.info(f"OpenRouter response status: {response.status_code}")
                
                if response.status_code == 200:
                    logger.info("✅ OpenRouter API health check PASSED")
                    return True
                else:
                    logger.warning(f"OpenRouter health check returned {response.status_code}: {response.text[:300]}")
                    
                    # Try alternative endpoint
                    logger.info("Trying alternative endpoint...")
                    response2 = await client.get(
                        f"{self.api_url}/auth/key",
                        headers={"Authorization": f"Bearer {self.api_key}"}
                    )
                    logger.info(f"Alternative endpoint status: {response2.status_code}")
                    return response2.status_code == 200
                    
        except Exception as e:
            logger.error(f"AI health check failed: {e}")
            return False


ai_service = AIService()

