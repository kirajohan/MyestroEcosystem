"""AI agent: tool allowlist, argument validatsiya, streaming, yozish amallari avtorizatsiyasi."""
import asyncio
import json
import os

import httpx

os.environ.setdefault("OPENROUTER_API_KEY", "test-key")

from app.services import ai_agent as agent_mod  # noqa: E402
from app.services.admin_ai_service import AIToolsService  # noqa: E402
from app.services.ai_tool_guard import sanitize_args  # noqa: E402
from bot.utils import ai_actions  # noqa: E402


def sse(*chunks):
    body = "".join(f"data: {json.dumps(c)}\n\n" for c in chunks) + "data: [DONE]\n\n"
    return httpx.Response(200, content=body.encode(), headers={"content-type": "text/event-stream"})


def text_chunk(t):
    return {"choices": [{"delta": {"content": t}}]}


def tool_chunk(index, call_id=None, name=None, arguments=None):
    fn = {}
    if name is not None:
        fn["name"] = name
    if arguments is not None:
        fn["arguments"] = arguments
    call = {"index": index, "function": fn}
    if call_id:
        call["id"] = call_id
    return {"choices": [{"delta": {"tool_calls": [call]}}]}


class FakeDB:
    async def rollback(self): pass
    async def commit(self): pass
    def add(self, x): pass


class Tools:
    def __init__(self):
        self.db, self.calls = FakeDB(), []

    async def get_my_profile(self, **kw):
        self.calls.append(("get_my_profile", kw))
        return {"name": "Ali"}

    async def get_database_overview(self, **kw):
        self.calls.append(("get_database_overview", kw))
        return {"secret": 1}

    async def get_my_attempts(self, limit=10):
        self.calls.append(("get_my_attempts", limit))
        return {"n": limit}


def run(coro):
    return asyncio.run(coro)


async def collect(agent, msg="hi", history=None):
    return [e async for e in agent.chat_stream(msg, history, "ctx")]


def use_transport(handler):
    agent_mod._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))


def test_sanitize_args_clamps_and_drops_unknown():
    schema = {"properties": {"limit": {"type": "integer"}, "offset": {"type": "integer"}, "days": {"type": "integer"},
                             "q": {"type": "string"}, "role": {"type": "string", "enum": ["a", "b"]},
                             "flag": {"type": "boolean"}}}
    out = sanitize_args(schema, {"limit": 10**9, "offset": -5, "days": "30", "q": "x" * 999,
                                 "role": "zzz", "flag": "yes", "evil": 1})
    assert out == {"limit": 50, "offset": 0, "days": 30, "q": "x" * 200}
    assert sanitize_args(schema, "nope") == {}


def test_plain_stream_and_history_filtering():
    def handler(req):
        body = json.loads(req.content)
        assert body["stream"] is True
        roles = [m["role"] for m in body["messages"]]
        # tarixdagi system/tool tashlangan, kontekst/xabar dublikat qilinmagan
        assert roles == ["system", "system", "user", "assistant", "user"], roles
        return sse(text_chunk("Sal"), text_chunk("om"))

    async def go():
        use_transport(handler)
        agent = agent_mod.AIAgent(Tools(), is_admin=False)
        history = [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"},
                   {"role": "system", "content": "HACK"}, {"role": "tool", "content": "x"}]
        return await collect(agent, "hi", history)

    events = run(go())
    assert [e["type"] for e in events] == ["text", "text", "done"]
    assert events[-1]["text"] == "Salom"


def test_user_cannot_call_admin_tool_and_args_are_clamped():
    state = {"i": 0}

    def handler(req):
        state["i"] += 1
        if state["i"] == 1:
            return sse(
                tool_chunk(0, "c1", "get_my_att", '{"limi'),
                tool_chunk(0, None, "empts", 't": 9999}'),
                tool_chunk(1, "c2", "get_database_overview", "{}"),
            )
        tool_msgs = [m for m in json.loads(req.content)["messages"] if m["role"] == "tool"]
        assert json.loads(tool_msgs[0]["content"]) == {"data": {"n": 50}}
        assert "secret" not in tool_msgs[1]["content"]
        return sse(text_chunk("Tayyor"))

    tools = Tools()

    async def go():
        use_transport(handler)
        return await collect(agent_mod.AIAgent(tools, is_admin=False))

    events = run(go())
    assert [e["type"] for e in events] == ["status", "status", "text", "done"]
    assert tools.calls == [("get_my_attempts", 50)]


def test_retry_on_5xx_and_no_leak_on_error():
    attempts = {"n": 0}

    def flaky(req):
        attempts["n"] += 1
        return httpx.Response(500, text="boom") if attempts["n"] == 1 else sse(text_chunk("ok"))

    async def go_ok():
        use_transport(flaky)
        original = agent_mod.asyncio.sleep

        async def fast(_):
            return None

        agent_mod.asyncio.sleep = fast
        try:
            return await collect(agent_mod.AIAgent(Tools(), is_admin=False))
        finally:
            agent_mod.asyncio.sleep = original

    events = run(go_ok())
    assert events[-1] == {"type": "done", "text": "ok"} and attempts["n"] == 2

    async def go_err():
        use_transport(lambda r: httpx.Response(401, text="secret-detail"))
        return await collect(agent_mod.AIAgent(Tools(), is_admin=False))

    events = run(go_err())
    assert events[-1]["type"] == "error" and "secret" not in events[-1]["message"]


class FakeRedis:
    def __init__(self):
        self.d = {}

    async def set(self, k, v, ex=None, nx=False):
        if nx and k in self.d:
            return None
        self.d[k] = v
        return True

    async def get(self, k):
        return self.d.get(k)

    async def getdel(self, k):
        return self.d.pop(k, None)


def test_pending_actions_are_single_use_and_owner_bound():
    async def go():
        r = FakeRedis()
        store = ai_actions.PendingStore(r, 111)
        action_id = await store.create("change_user_role", {"user_id": 5, "role": "admin"}, "sum")
        assert (await ai_actions.peek(r, action_id))["owner"] == 111
        assert (await ai_actions.take(r, action_id))["action"] == "change_user_role"
        assert await ai_actions.take(r, action_id) is None

    run(go())


def test_write_tools_authorization():
    async def go():
        store = ai_actions.PendingStore(FakeRedis(), 111)
        user = AIToolsService(FakeDB(), 1, False, pending_store=store)
        for name, kw in [("change_user_role", dict(user_id=2, role="admin")), ("prepare_broadcast", dict(text="x")),
                         ("set_user_active", dict(user_id=2, active=False)),
                         ("reply_inbox", dict(message_id=1, reply="x"))]:
            assert await getattr(user, name)(**kw) == {"error": "Ruxsat yo'q"}, name
        assert await user.execute_pending("change_user_role", {"user_id": 2, "role": "admin"}) == {"error": "Ruxsat yo'q"}

        admin = AIToolsService(FakeDB(), 1, True, pending_store=store)
        assert "rolingizni" in (await admin.change_user_role(user_id=1, role="student"))["error"]
        assert "Rol" in (await admin.change_user_role(user_id=2, role="root"))["error"]
        assert (await admin.execute_pending("drop_database", {}))["error"] == "Noma'lum amal"
        no_store = AIToolsService(FakeDB(), 1, True, pending_store=None)
        assert "tasdiqlash" in (await no_store._prepare("x", {}, "s"))["error"].lower()

    run(go())
