"""Placeholder registry for bot services.

This module fetches placeholder definitions from the backend API via HTTP
and caches them to avoid repeated requests. Falls back to default values
if the backend is unreachable.

Since bot and backend run in separate Docker containers, we cannot import
backend modules directly. Instead, we use HTTP calls to get placeholder data.
"""

import time
import logging
from typing import Dict, List, Optional, Any

import httpx

logger = logging.getLogger(__name__)

# Backend API configuration
BACKEND_URL = "http://backend:8000"
PLACEHOLDERS_ENDPOINT = f"{BACKEND_URL}/placeholders/registry"

# Cache configuration
_CACHE_TTL_SECONDS = 3600  # 1 hour

# In-memory cache
_cache: Dict[str, any] = {
    "registry": None,
    "safe_fields": None,
    "timestamp": 0,
}


def _is_cache_valid() -> bool:
    """Check if cached data is still valid."""
    if _cache["registry"] is None:
        return False
    return (time.time() - _cache["timestamp"]) < _CACHE_TTL_SECONDS


async def _fetch_placeholders_from_backend() -> Optional[Dict]:
    """Fetch placeholders from backend API.
    
    Returns:
        Dict with PLACEHOLDER_REGISTRY and SAFE_USER_FIELDS, or None if failed
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(PLACEHOLDERS_ENDPOINT)
            response.raise_for_status()
            data = response.json()
            
            # Backend returns: {
            #   "PLACEHOLDER_REGISTRY": {"{id}": "{id}", "{email}": "{email}", ...},
            #   "SAFE_USER_FIELDS": ["id", "email", ...]
            # }
            placeholder_dict = data.get("PLACEHOLDER_REGISTRY", {})
            safe_fields = data.get("SAFE_USER_FIELDS", [])
            
            # Return as-is (dict format as per task specification)
            return {
                "PLACEHOLDER_REGISTRY": placeholder_dict,
                "SAFE_USER_FIELDS": safe_fields,
            }
    except Exception as e:
        logger.error(f"Failed to fetch placeholders from backend: {e}")
        return None


async def get_placeholders_from_backend() -> Dict[str, str]:
    """Get placeholder registry from backend with caching.
    
    Returns:
        Dict mapping placeholder keys to their values (e.g., {"{full_name}": "{full_name}"})
    """
    # Return cached data if valid
    if _is_cache_valid():
        logger.debug("Returning cached placeholder registry")
        return _cache["registry"]
    
    # Fetch from backend
    logger.info("Fetching placeholder registry from backend...")
    data = await _fetch_placeholders_from_backend()
    
    if data and data.get("PLACEHOLDER_REGISTRY"):
        # Update cache - store as dict
        _cache["registry"] = data["PLACEHOLDER_REGISTRY"]
        _cache["safe_fields"] = data.get("SAFE_USER_FIELDS", [])
        _cache["timestamp"] = time.time()
        logger.info(f"Cached {len(_cache['registry'])} placeholders from backend")
        return _cache["registry"]
    else:
        # Backend fetch failed - use fallback
        logger.warning("Backend unavailable, using fallback placeholders")
        return _get_fallback_placeholders_dict()


def _get_fallback_placeholders_dict() -> Dict[str, str]:
    """Return fallback placeholder definitions if backend is unreachable.
    
    Returns dict mapping placeholder keys to their values.
    """
    return {
        "{id}": "{id}",
        "{email}": "{email}",
        "{full_name}": "{full_name}",
        "{role}": "{role}",
        "{cefr_level}": "{cefr_level}",
        "{target_level}": "{target_level}",
        "{avatar_url}": "{avatar_url}",
        "{phone}": "{phone}",
        "{lang}": "{lang}",
        "{learning_lang}": "{learning_lang}",
        "{telegram_id}": "{telegram_id}",
        "{telegram_username}": "{telegram_username}",
        "{auth_provider}": "{auth_provider}",
        "{provider_user_id}": "{provider_user_id}",
        "{is_active}": "{is_active}",
        "{is_verified}": "{is_verified}",
        "{profile_completed}": "{profile_completed}",
        "{last_login_at}": "{last_login_at}",
        "{location}": "{location}",
        "{ai_enabled}": "{ai_enabled}",
        "{created_at}": "{created_at}",
        "{updated_at}": "{updated_at}",
    }


async def get_safe_user_fields() -> List[str]:
    """Get list of safe user field names for placeholders.
    
    Returns:
        List of field names (without {}) that are safe to use in placeholders
    """
    # Ensure we have placeholders loaded
    if _cache["safe_fields"] is None or not _is_cache_valid():
        await get_placeholders_from_backend()
    
    return _cache.get("safe_fields") or [
        "id", "email", "full_name", "role", "cefr_level", "target_level",
        "avatar_url", "phone", "lang", "learning_lang", "telegram_id",
        "telegram_username", "auth_provider", "provider_user_id",
        "is_active", "is_verified", "profile_completed", "last_login_at",
        "location", "ai_enabled", "created_at", "updated_at"
    ]


def get_placeholders() -> Dict[str, str]:
    """Synchronous wrapper to get placeholders (for compatibility).
    
    Note: This returns cached data. For fresh data, use get_placeholders_from_backend().
    """
    if _cache["registry"] is None:
        # Return fallback synchronously (will be updated async later)
        return _get_fallback_placeholders_dict()
    return _cache["registry"]


# Default PLACEHOLDER_REGISTRY for synchronous imports
# This is used by code that imports PLACEHOLDER_REGISTRY directly
PLACEHOLDER_REGISTRY = _get_fallback_placeholders_dict()


# Export public API
__all__ = [
    'PLACEHOLDER_REGISTRY',
    'get_placeholders',
    'get_placeholders_from_backend',
    'get_safe_user_fields',
]