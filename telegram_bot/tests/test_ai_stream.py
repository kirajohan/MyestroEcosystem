"""StreamRenderer: edit va draft rejimlari, flood-control, parse xatolari, Stop, draft fallback, rate-limiter."""
import asyncio
import time

from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.methods import EditMessageText

from bot.utils import ai_stream
from bot.utils.ai_html import strip_html
from bot.utils.ai_stream import StreamRenderer

_TEXTS = {"ai.thinking_short": "Thinking", "ai.stopped": "⏹ To'xtatildi.", "ai.timeout": "timeout", "ai.error": "ERR"}


def _fast(monkeypatch, mode="edit"):
    monkeypatch.setattr(ai_stream, "get_text", lambda k, lang="uz", **kw: _TEXTS.get(k, k))
    monkeypatch.setattr(ai_stream, "BASE_INTERVAL", 0.12)
    monkeypatch.setattr(ai_stream, "MAX_INTERVAL", 0.5)
    monkeypatch.setattr(ai_stream, "DRAFT_INTERVAL", 0.08)
    monkeypatch.setattr(ai_stream, "TYPING_REFRESH", 100)
    monkeypatch.setattr(ai_stream, "_draft_broken", False)
    monkeypatch.setattr(ai_stream, "_BUCKET", ai_stream._TokenBucket(500, 100))
    monkeypatch.setattr(ai_stream.settings, "AI_STREAM_MODE", mode, raising=False)


def _bad(msg):
    return TelegramBadRequest(method=EditMessageText(text="x"), message=msg)


class FakeBot:
    def __init__(self, draft_error=None):
        self.drafts, self.draft_error = [], draft_error

    async def send_chat_action(self, *a, **k):
        pass

    async def send_message_draft(self, chat_id, draft_id, text, parse_mode="HTML"):
        if self.draft_error:
            raise self.draft_error
        self.drafts.append((draft_id, text))
        return True


class FakeChat:
    id = 1


class Store:
    def __init__(self, fail_parse=0, flood_at=(), draft_error=None):
        self.msgs, self.fail_parse, self.flood_at, self.edits = [], fail_parse, set(flood_at), 0
        self.bot = FakeBot(draft_error)
        self.edit_times = []

    def new(self, text, markup):
        m = FakeMsg(self, text, markup, len(self.msgs))
        self.msgs.append(m)
        return m

    def edit(self, m, text, markup, parse_mode):
        self.edits += 1
        if self.edits in self.flood_at:
            self.flood_at.discard(self.edits)
            raise TelegramRetryAfter(method=EditMessageText(text="x"), message="flood", retry_after=1)
        if self.fail_parse and parse_mode == "default" and "<b>" in text:
            self.fail_parse -= 1
            raise _bad("Bad Request: can't parse entities: boom")
        if m.text == text and m.markup == markup:
            raise _bad("Bad Request: message is not modified")
        m.text, m.markup = text, markup
        self.edit_times.append(time.monotonic())


class FakeMsg:
    def __init__(self, store, text, markup, mid):
        self.store, self.text, self.markup, self.mid = store, text, markup, mid
        self.bot, self.chat, self.deleted = store.bot, FakeChat(), False

    async def answer(self, text, reply_markup=None, parse_mode="default"):
        return self.store.new(text, reply_markup)

    async def edit_text(self, text, reply_markup=None, parse_mode="default"):
        self.store.edit(self, text, reply_markup, parse_mode)

    async def delete(self):
        self.deleted = True


def _origin(store):
    return FakeMsg(store, "", None, -1)


async def _gen(chunks, delay):
    for c in chunks:
        await asyncio.sleep(delay)
        yield {"type": "text", "delta": c}
    yield {"type": "done", "text": "".join(chunks)}


def _words(n):
    return [("**Sarlavha %d** " % (i // 40) if i % 40 == 0 else "") + "so'z%d " % i for i in range(n)]


def test_edit_mode_long_stream_with_flood_and_parse_errors(monkeypatch):
    _fast(monkeypatch)
    store = Store(fail_parse=2, flood_at=(3,))
    r = StreamRenderer(_origin(store), "uz", header="🤖 <b>AI</b>\n\n", stop_markup="STOP")
    words = _words(800)
    out = asyncio.run(r.run(_gen(words, 0.002)))
    assert out == "".join(words)
    live = [m for m in store.msgs if not m.deleted]
    assert len(live) >= 2
    assert all(m.markup is None for m in live)           # Stop tugmasi yakunda yo'q
    assert all(len(m.text) <= 4096 for m in live)
    joined = "".join(strip_html(m.text) for m in live)
    assert "so'z799" in joined and "so'z0" in joined and "▍" not in joined
    gaps = [b - a for a, b in zip(store.edit_times, store.edit_times[1:])]
    assert min(gaps) >= 0.03


def test_stop_keeps_partial_text(monkeypatch):
    _fast(monkeypatch)
    store = Store()
    r = StreamRenderer(_origin(store), "uz", stop_markup="STOP")

    async def slow():
        for i in range(100):
            await asyncio.sleep(0.05)
            yield {"type": "text", "delta": "abc%d " % i}

    async def go():
        task = asyncio.create_task(r.run(slow()))
        await asyncio.sleep(0.8)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    asyncio.run(go())
    live = [m for m in store.msgs if not m.deleted][-1]
    assert "abc" in live.text and "To'xtatildi" in live.text and live.markup is None


def test_tool_status_then_text_and_error(monkeypatch):
    _fast(monkeypatch)
    store = Store()
    r = StreamRenderer(_origin(store), "uz", stop_markup="STOP")

    async def g():
        yield {"type": "status", "tool": "list_users"}
        await asyncio.sleep(0.5)
        yield {"type": "text", "delta": "Natija <b>5</b> ta"}
        yield {"type": "done", "text": "Natija <b>5</b> ta"}

    asyncio.run(r.run(g()))
    assert strip_html(store.msgs[0].text).endswith("Natija 5 ta")

    store = Store()
    r = StreamRenderer(_origin(store), "uz", stop_markup="STOP")

    async def err():
        yield {"type": "error", "message": "⚠️ AI bilan aloqada xatolik."}

    out = asyncio.run(r.run(err()))
    assert out == "" and "xatolik" in store.msgs[0].text and store.msgs[0].markup is None


def test_draft_mode_streams_via_drafts_then_sends_final_and_removes_placeholder(monkeypatch):
    _fast(monkeypatch, mode="draft")
    store = Store()
    r = StreamRenderer(_origin(store), "uz", header="🤖 <b>AI</b>\n\n", stop_markup="STOP")
    words = _words(200)
    out = asyncio.run(r.run(_gen(words, 0.003)))
    assert out == "".join(words)
    assert r.mode == "draft"
    assert len(store.bot.drafts) >= 2
    assert len({d[0] for d in store.bot.drafts}) == 1          # bitta draft_id
    assert store.edits == 0                                    # edit ishlatilmagan
    placeholder, *finals = store.msgs
    assert placeholder.deleted                                 # Stop xabari o'chirilgan
    assert finals and all(not m.deleted and m.markup is None for m in finals)
    assert "so'z199" in "".join(strip_html(m.text) for m in finals)


def test_draft_failure_falls_back_to_edit_mode(monkeypatch):
    _fast(monkeypatch, mode="draft")
    store = Store(draft_error=_bad("Bad Request: method not found"))
    r = StreamRenderer(_origin(store), "uz", stop_markup="STOP")
    words = _words(120)
    out = asyncio.run(r.run(_gen(words, 0.004)))
    assert out == "".join(words)
    assert r.mode == "edit" and ai_stream._draft_broken is True
    live = [m for m in store.msgs if not m.deleted]
    assert "so'z119" in "".join(strip_html(m.text) for m in live)
    assert all(m.markup is None for m in live)


def test_token_bucket_limits_rate():
    async def go():
        bucket = ai_stream._TokenBucket(rate=50, burst=5)
        t0 = time.monotonic()
        for _ in range(30):
            await bucket.acquire()
        return time.monotonic() - t0

    elapsed = asyncio.run(go())
    assert elapsed >= 0.4          # 30 so'rov: 5 burst + 25/50 = ~0.5 s
