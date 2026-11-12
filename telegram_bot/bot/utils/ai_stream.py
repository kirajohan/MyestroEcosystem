"""
Telegram'da silliq oqim (streaming) chiqarish.

LLM tokenlari bufer'ga yig'iladi; alohida sikl xabarni davriy yangilaydi. Ikki rejim (AI_STREAM_MODE):
  - "edit"  (standart): `edit_text` ~1 s da bir marta (flood-control chegarasiga mos).
  - "draft": Telegram `sendMessageDraft` (private chat) — mijozda silliq ko'rinadi, ~0.4 s. Draft'da tugma
            bo'lmagani uchun Stop tugmasi alohida kichik xabarda turadi; yakunda javob yangi xabar sifatida
            yuboriladi va kichik xabar o'chiriladi. Draft xato bersa, avtomatik "edit" ga o'tadi.
Barcha oqimlar Telegram'ga umumiy token-bucket orqali boradi (bot bo'yicha ~30 so'rov/s chegarasi).
Har kadr yaroqli HTML, 4096 dan oshsa teg-xavfsiz bo'laklarga bo'linadi.
"""
import asyncio
import html as _html
import logging
import random
import time
from typing import Any, AsyncIterator, Dict, List, Optional

from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError, TelegramRetryAfter
from aiogram.types import InlineKeyboardMarkup, Message

from bot.config import settings
from bot.utils.ai_html import split_html, strip_html, to_partial_html, to_telegram_html
from bot.utils.i18n import get_text

logger = logging.getLogger(__name__)

BASE_INTERVAL = 1.0        # kadrlar orasidagi minimal vaqt (sek)
MAX_INTERVAL = 4.0         # flood-control bo'lsa maksimal
SOFT_LIMIT = 150.0         # umumiy oqim vaqti (sek) — oshsa, mavjud matn bilan yakunlanadi
LIVE_CHUNK = 3800          # oqim paytida bir xabar uchun belgi limiti
FINAL_CHUNK = 4000         # yakuniy bo'laklash limiti (Telegram: 4096)
CURSOR = " ▍"
TYPING_REFRESH = 4.0
DRAFT_INTERVAL = float(getattr(settings, "AI_STREAM_DRAFT_INTERVAL", 0.4))
TG_RATE = float(getattr(settings, "AI_TG_RATE", 25.0))   # bot bo'yicha barcha oqimlar uchun so'rov/s
SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

_STATUS_TEXT = {
    "read": {
        "uz": "🔎 Ma'lumotlar olinmoqda",
        "ru": "🔎 Получаю данные",
        "en": "🔎 Fetching data",
    },
    "write": {
        "uz": "📝 Amal tayyorlanmoqda",
        "ru": "📝 Готовлю действие",
        "en": "📝 Preparing action",
    },
}
_WRITE_PREFIXES = ("create_", "delete_", "set_", "change_", "deactivate_", "reply_", "close_", "prepare_")


class _TokenBucket:
    """Umumiy rate-limiter: barcha oqimlar Telegram'ga shu orqali boradi."""

    def __init__(self, rate: float, burst: float):
        self.rate, self.burst = rate, burst
        self.tokens, self.stamp = burst, time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            while True:
                now = time.monotonic()
                self.tokens = min(self.burst, self.tokens + (now - self.stamp) * self.rate)
                self.stamp = now
                if self.tokens >= 1:
                    self.tokens -= 1
                    return
                await asyncio.sleep((1 - self.tokens) / self.rate)


_BUCKET = _TokenBucket(TG_RATE, burst=max(5.0, TG_RATE / 2))
_active_streams = 0
_draft_broken = False   # draft ishlamasa (eski API/mijoz) jarayon davomida "edit" ga o'tamiz


def _status_label(tool: str, lang: str) -> str:
    kind = "write" if tool.startswith(_WRITE_PREFIXES) else "read"
    return _STATUS_TEXT[kind].get(lang) or _STATUS_TEXT[kind]["en"]


class StreamRenderer:
    def __init__(
        self,
        message: Message,
        lang: str,
        header: str = "",
        stop_markup: Optional[InlineKeyboardMarkup] = None,
    ):
        self.message = message
        self.lang = lang
        self.header = header
        self.stop_markup = stop_markup

        self.msgs: List[Message] = []
        self.shown: List[str] = []

        self.raw = ""
        self.final: Optional[str] = None
        self.error: Optional[str] = None
        self.status: Optional[str] = None

        # get_text sinxron (Redis cache) — event loop'ni bloklamaslik uchun bir marta olamiz
        self._t_thinking = get_text("ai.thinking_short", lang)

        self.mode = "draft" if str(getattr(settings, "AI_STREAM_MODE", "edit")).lower() == "draft" and not _draft_broken else "edit"
        self.draft_id = random.randint(1, 2**31 - 1)
        self.base = DRAFT_INTERVAL if self.mode == "draft" else BASE_INTERVAL
        self.interval = self.base
        self._ok_streak = 0
        self._frame = 0
        self._stopped = False

    # ───────────────────────────────────────────────────────
    # Boshlash / placeholder
    # ───────────────────────────────────────────────────────
    async def start(self) -> None:
        text = self._thinking_text()
        await _BUCKET.acquire()
        sent = await self.message.answer(text, reply_markup=self.stop_markup)
        self.msgs = [sent]
        self.shown = [text]

    def _thinking_text(self) -> str:
        spin = SPINNER[self._frame % len(SPINNER)]
        dots = "." * (self._frame % 3 + 1)
        base = self._t_thinking
        status = f"\n<i>{_html.escape(self.status)}…</i>" if self.status else ""
        return f"{spin} {_html.escape(base)}{dots}{status}"

    # ───────────────────────────────────────────────────────
    # Asosiy sikl
    # ───────────────────────────────────────────────────────
    async def run(self, events: AsyncIterator[Dict[str, Any]], soft_limit: float = SOFT_LIMIT) -> str:
        """Hodisalarni iste'mol qiladi, oqimni chiqaradi va yakuniy xom javobni qaytaradi."""
        if not self.msgs:
            await self.start()

        global _active_streams
        _active_streams += 1
        producer = asyncio.create_task(self._consume(events))
        typing = asyncio.create_task(self._typing_loop())
        deadline = time.monotonic() + soft_limit
        timed_out = False
        last_tick = 0.0

        try:
            while True:
                done, _ = await asyncio.wait({producer}, timeout=0.25)
                if done:
                    break
                now = time.monotonic()
                if now > deadline:
                    timed_out = True
                    break
                # Faol oqimlar ko'p bo'lsa har biri sekinroq yangilanadi: jami ≈ TG_RATE dan oshmasin
                if now - last_tick >= max(self.interval, _active_streams / TG_RATE):
                    await self._tick()
                    last_tick = time.monotonic()

            if timed_out:
                producer.cancel()
                await asyncio.gather(producer, return_exceptions=True)
            else:
                await producer  # _consume ichidagi kutilmagan xatolarni ko'taradi

            return await self._finalize(timed_out)
        except asyncio.CancelledError:
            await self.mark_stopped()
            raise
        finally:
            _active_streams -= 1
            typing.cancel()
            if not producer.done():
                producer.cancel()
            await asyncio.gather(producer, typing, return_exceptions=True)

    async def _consume(self, events: AsyncIterator[Dict[str, Any]]) -> None:
        async for ev in events:
            kind = ev.get("type")
            if kind == "text":
                self.status = None
                self.raw += ev["delta"]
            elif kind == "reset":
                self.raw = ""
            elif kind == "status":
                self.status = _status_label(ev.get("tool", ""), self.lang)
            elif kind == "done":
                self.final = ev.get("text", "")
            elif kind == "error":
                self.error = ev.get("message") or get_text("ai.error", self.lang)

    async def _typing_loop(self) -> None:
        try:
            while True:
                try:
                    await self.message.bot.send_chat_action(self.message.chat.id, "typing")
                except Exception:
                    pass
                await asyncio.sleep(TYPING_REFRESH)
        except asyncio.CancelledError:
            pass

    # ───────────────────────────────────────────────────────
    # Kadr (oqim paytida)
    # ───────────────────────────────────────────────────────
    async def _tick(self) -> None:
        if self.mode == "draft":
            await self._tick_draft()
            return
        if not self.raw:
            self._frame += 1
            await self._ensure_text(0, self._thinking_text(), self.stop_markup, final=False)
            return

        rendered = self.header + to_partial_html(self.raw)
        if not rendered.strip():
            return
        chunks = split_html(rendered, LIVE_CHUNK)
        last = len(chunks) - 1
        for i, chunk in enumerate(chunks):
            if i == last:
                await self._ensure_text(i, chunk + CURSOR, self.stop_markup, final=False)
            else:
                await self._ensure_text(i, chunk, None, final=False)

    async def _tick_draft(self) -> None:
        if not self.raw:
            self._frame += 1
            await self._draft(self._thinking_text())
            return
        rendered = self.header + to_partial_html(self.raw)
        if not rendered.strip():
            return
        # Draft bitta xabar: juda uzun bo'lsa oxirgi bo'lak ko'rsatiladi (to'liq javob yakunda bo'laklab yuboriladi)
        await self._draft(split_html(rendered, LIVE_CHUNK)[-1] + CURSOR)

    async def _draft(self, text: str) -> bool:
        """sendMessageDraft; xato bo'lsa "edit" rejimiga o'tadi."""
        global _draft_broken
        await _BUCKET.acquire()
        try:
            await self.message.bot.send_message_draft(
                chat_id=self.message.chat.id, draft_id=self.draft_id, text=text, parse_mode="HTML"
            )
            self._reward()
            return True
        except TelegramRetryAfter as e:
            self._penalize(e.retry_after)
            await asyncio.sleep(e.retry_after + 0.3)
            return False
        except TelegramBadRequest as e:
            low = str(e).lower()
            if "can't parse entities" in low or "can't find end" in low:
                try:
                    await self.message.bot.send_message_draft(
                        chat_id=self.message.chat.id, draft_id=self.draft_id, text=strip_html(text), parse_mode=None
                    )
                    return True
                except Exception:
                    return False
            logger.warning(f"[AI-STREAM] draft rad etildi, 'edit' rejimiga o'tilmoqda: {e}")
        except (AttributeError, TypeError) as e:
            logger.warning(f"[AI-STREAM] draft qo'llab-quvvatlanmaydi: {e}")
        except TelegramNetworkError:
            return False
        except Exception:
            logger.exception("[AI-STREAM] draft kutilmagan xato, 'edit' rejimiga o'tilmoqda")
        _draft_broken = True
        self.mode, self.base = "edit", BASE_INTERVAL
        self.interval = max(self.interval, self.base)
        return False

    async def _ensure_text(self, index: int, text: str, markup, final: bool) -> bool:
        """index-dagi xabar kerakli matnda bo'lishini ta'minlaydi (yo'q bo'lsa yangisini yuboradi)."""
        if index >= len(self.msgs):
            msg = await self._send_new(text, markup)
            if msg is None:
                return False
            self.msgs.append(msg)
            self.shown.append(text)
            return True
        if self.shown[index] == text:
            return True
        ok = await self._edit(self.msgs[index], text, markup)
        if ok:
            self.shown[index] = text
        return ok

    # ───────────────────────────────────────────────────────
    # Telegram bilan ishlash (flood-control, parse xatolari)
    # ───────────────────────────────────────────────────────
    def _penalize(self, retry_after: float) -> None:
        self._ok_streak = 0
        self.interval = min(MAX_INTERVAL, max(self.interval * 1.5, float(retry_after)))
        logger.warning(f"[AI-STREAM] flood-control: retry_after={retry_after}s, interval={self.interval:.1f}s")

    def _reward(self) -> None:
        self._ok_streak += 1
        if self._ok_streak >= 6 and self.interval > self.base:
            self.interval = max(self.base, self.interval * 0.85)
            self._ok_streak = 0

    async def _edit(self, msg: Message, text: str, markup) -> bool:
        for attempt in range(2):
            await _BUCKET.acquire()
            try:
                await msg.edit_text(text, reply_markup=markup)
                self._reward()
                return True
            except TelegramRetryAfter as e:
                self._penalize(e.retry_after)
                await asyncio.sleep(e.retry_after + 0.3)
                continue
            except TelegramBadRequest as e:
                low = str(e).lower()
                if "message is not modified" in low:
                    return True
                if "can't parse entities" in low or "can't find end" in low or "unsupported start tag" in low:
                    logger.warning(f"[AI-STREAM] HTML parse xatosi, oddiy matn bilan: {e}")
                    try:
                        await msg.edit_text(strip_html(text), reply_markup=markup, parse_mode=None)
                        return True
                    except TelegramBadRequest as e2:
                        if "message is not modified" in str(e2).lower():
                            return True
                        return False
                    except Exception:
                        return False
                logger.warning(f"[AI-STREAM] edit rad etildi: {e}")
                return False
            except TelegramNetworkError as e:
                logger.warning(f"[AI-STREAM] tarmoq xatosi: {e}")
                await asyncio.sleep(0.5)
                continue
            except Exception:
                logger.exception("[AI-STREAM] kutilmagan edit xatosi")
                return False
        return False

    async def _send_new(self, text: str, markup) -> Optional[Message]:
        for attempt in range(3):
            await _BUCKET.acquire()
            try:
                return await self.message.answer(text, reply_markup=markup)
            except TelegramRetryAfter as e:
                self._penalize(e.retry_after)
                await asyncio.sleep(e.retry_after + 0.3)
            except TelegramBadRequest as e:
                logger.warning(f"[AI-STREAM] yangi xabar parse xatosi, oddiy matn: {e}")
                try:
                    return await self.message.answer(strip_html(text), reply_markup=markup, parse_mode=None)
                except Exception:
                    return None
            except TelegramNetworkError:
                await asyncio.sleep(0.5)
            except Exception:
                logger.exception("[AI-STREAM] yangi xabar yuborilmadi")
                return None
        return None

    # ───────────────────────────────────────────────────────
    # Yakun / to'xtatish
    # ───────────────────────────────────────────────────────
    async def _finalize(self, timed_out: bool) -> str:
        answer = self.final if self.final is not None else self.raw
        footer = ""

        if self.error and not answer.strip():
            html_text = _html.escape(self.error)
            answer = ""
        elif timed_out:
            html_text = self.header + to_telegram_html(answer)
            footer = "\n\n" + get_text("ai.timeout", self.lang)
        elif not answer.strip():
            html_text = get_text("ai.error", self.lang)
        else:
            html_text = self.header + to_telegram_html(answer)

        chunks = split_html(html_text + footer, FINAL_CHUNK)

        if self.mode == "draft":
            # Draft -> yakuniy xabar(lar) yangi xabar sifatida (Telegram oqimi shunday tugaydi), keyin Stop xabari o'chadi
            sent_any = False
            for i, chunk in enumerate(chunks):
                msg = await self._send_new(chunk, None)
                sent_any = sent_any or msg is not None
                if i < len(chunks) - 1:
                    await asyncio.sleep(0.15)
            if sent_any:
                for extra in self.msgs:
                    try:
                        await extra.delete()
                    except Exception:
                        pass
            else:
                await self._ensure_text(0, chunks[0], None, final=True)
            return answer

        for i, chunk in enumerate(chunks):
            ok = False
            for _ in range(3):
                ok = await self._ensure_text(i, chunk, None, final=True)
                if ok:
                    break
                await asyncio.sleep(0.5)
            if not ok:
                logger.error(f"[AI-STREAM] yakuniy bo'lak {i} yuborilmadi")
            if i < len(chunks) - 1:
                await asyncio.sleep(0.15)

        # ortiqcha (oqim paytida ochilgan, endi kerak bo'lmagan) xabarlarni o'chirish
        for extra in self.msgs[len(chunks):]:
            try:
                await extra.delete()
            except Exception:
                pass

        return answer

    async def fail(self, html_text: str) -> None:
        """Kutilmagan xato: placeholder/oxirgi xabarni xato matniga almashtiradi (tugma olib tashlanadi)."""
        if self._stopped:
            return
        self._stopped = True
        if not self.msgs:
            await self._send_new(html_text, None)
            return
        # Allaqachon ko'rsatilgan javob bo'lsa, uni xato bilan almashtirmaymiz (faqat "edit" rejimida)
        if self.raw and self.mode == "edit":
            await self._ensure_text(len(self.msgs) - 1, self.shown[-1].removesuffix(CURSOR), None, final=True)
        else:
            await self._ensure_text(len(self.msgs) - 1, html_text, None, final=True)

    async def mark_stopped(self) -> None:
        """Stop bosilganda: chiqqan matn saqlanadi, oxiriga '⏹' qo'shiladi, tugma olib tashlanadi."""
        if self._stopped or not self.msgs:
            return
        self._stopped = True
        stopped = get_text("ai.stopped", self.lang)
        try:
            if self.raw:
                chunks = split_html(self.header + to_partial_html(self.raw), LIVE_CHUNK)
                text = chunks[-1] + "\n\n" + stopped
                index = len(chunks) - 1
            else:
                text, index = stopped, len(self.msgs) - 1
            index = min(index, len(self.msgs) - 1)
            await self._ensure_text(index, text, None, final=True)
        except Exception:
            logger.exception("[AI-STREAM] to'xtatish belgisi yozilmadi")
