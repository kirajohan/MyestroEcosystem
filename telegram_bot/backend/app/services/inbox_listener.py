"""Inbox listener — Listen to Redis pub/sub and broadcast to WebSocket."""

import asyncio
import json
import logging
import redis.asyncio as redis

from app.config import settings
from app.websocket.admin_ws import broadcast_inbox_update

logger = logging.getLogger(__name__)


async def start_inbox_listener():
    """Start listening to Redis pub/sub for inbox events."""
    logger.info("📨 Starting inbox listener...")
    
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)
    pubsub = r.pubsub()
    
    await pubsub.subscribe("inbox:new_message")
    
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    logger.info(f"📨 Inbox event received: {data}")
                    
                    # Broadcast to all connected admin WebSocket clients
                    await broadcast_inbox_update("new_message", data)
                    
                except Exception as e:
                    logger.error(f"Error processing inbox event: {e}")
    except Exception as e:
        logger.error(f"Inbox listener error: {e}")
    finally:
        await pubsub.unsubscribe("inbox:new_message")
        await pubsub.close()
        await r.close()