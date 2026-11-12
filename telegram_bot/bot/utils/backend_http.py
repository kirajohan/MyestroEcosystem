"""
Backend'ga so'rov yuboruvchi httpx klienti: faqat backend hostiga `X-Internal-Key` qo'shadi.

Boshqa hostlarga (OpenRouter, Telegram va h.k.) kalit HECH QACHON ketmaydi.
INTERNAL_API_KEY bo'sh bo'lsa — sarlavha qo'shilmaydi (backend ham himoyani o'chiq tutadi).
"""
import os
from typing import Set
from urllib.parse import urlparse

import httpx

from bot.config import settings

INTERNAL_KEY_HEADER = "X-Internal-Key"


def _backend_hosts() -> Set[str]:
    urls = [
        getattr(settings, "BACKEND_URL", ""),
        getattr(settings, "API_BASE_URL", ""),
        os.getenv("BACKEND_API_URL", ""),
        os.getenv("BACKEND_INTERNAL_URL", ""),
    ]
    hosts = set()
    for u in urls:
        host = urlparse(u).hostname if u else None
        if host:
            hosts.add(host.lower())
    return hosts


_HOSTS = _backend_hosts()


class BackendClient(httpx.AsyncClient):
    """httpx.AsyncClient bilan bir xil; backend hostiga servis kalitini avtomatik qo'shadi."""

    async def send(self, request: httpx.Request, **kwargs):
        key = settings.INTERNAL_API_KEY
        if key and (request.url.host or "").lower() in _HOSTS:
            request.headers[INTERNAL_KEY_HEADER] = key
        return await super().send(request, **kwargs)
