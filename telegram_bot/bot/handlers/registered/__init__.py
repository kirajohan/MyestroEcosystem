"""Registered user handlers."""

from .menu import router as menu_router
from .ai_chat import router as ai_chat_router
from .academy import router as academy_router
from .profile import router as profile_router

__all__ = ["menu_router", "ai_chat_router", "academy_router", "profile_router"]