"""
AI javobini Telegram HTML'ga xavfsiz aylantirish.

- `to_telegram_html(text)`      — to'liq javob (Markdown qoldiqlari + HTML) → toza, to'g'ri joylashgan HTML
- `to_partial_html(text)`       — oqim paytidagi tugallanmagan matn → doim yaroqli HTML
- `split_html(html, limit)`     — yaroqli HTML'ni teg-xavfsiz bo'laklarga bo'lish
- `strip_html(html)`            — HTML'siz oddiy matn (parse xatosi bo'lsa fallback)

Faqat Telegram qo'llab-quvvatlaydigan teglar o'tkaziladi; qolgani escape yoki olib tashlanadi.
"""
import html as _html
import re
from typing import List, Tuple

_TAG_RE = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9-]*)((?:\s[^<>]*)?)/?>")
_ENTITY_RE = re.compile(r"&(?:amp|lt|gt|quot|#\d{1,6}|#x[0-9a-fA-F]{1,6});")
_HREF_RE = re.compile(r"""href\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.IGNORECASE)

# alias -> Telegram tegi
_ALLOWED = {
    "b": "b", "strong": "b",
    "i": "i", "em": "i",
    "u": "u", "ins": "u",
    "s": "s", "strike": "s", "del": "s",
    "code": "code",
    "pre": "pre",
    "a": "a",
    "blockquote": "blockquote",
    "tg-spoiler": "tg-spoiler",
}
_HEADING_RE = re.compile(r"^h[1-6]$")
_SAFE_SCHEMES = ("http://", "https://", "tg://")


# ───────────────────────────────────────────────────────────
# Markdown qoldiqlarini HTML'ga o'tkazish (kod bloklari himoyalanadi)
# ───────────────────────────────────────────────────────────

def _markdown_to_html(text: str) -> str:
    stash: List[str] = []

    def _stash(html_piece: str) -> str:
        stash.append(html_piece)
        return f"\x00{len(stash) - 1}\x00"

    # ```kod``` bloklari
    def _fence(m: "re.Match") -> str:
        return _stash(f"<pre>{_html.escape(m.group(1).strip(chr(10)), quote=False)}</pre>")

    text = re.sub(r"```[\w+-]*\n?(.*?)```", _fence, text, flags=re.S)
    # `inline`
    text = re.sub(r"`([^`\n]+)`", lambda m: _stash(f"<code>{_html.escape(m.group(1), quote=False)}</code>"), text)

    # Sarlavhalar
    def _heading(m: "re.Match") -> str:
        level = len(m.group(1))
        title = m.group(2).strip()
        if level == 1:
            return f"\n📌 <b>{title.upper()}</b>\n"
        if level == 2:
            return f"\n🔹 <b>{title}</b>\n"
        return f"\n▫️ <b>{title}</b>\n"

    text = re.sub(r"^(#{1,6})\s+(.+)$", _heading, text, flags=re.M)

    # **qalin**, *kursiv*
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<b><i>\1</i></b>", text, flags=re.S)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text, flags=re.S)
    text = re.sub(r"(?<![\*\w])\*(?![\*\s])([^\*\n]+?)(?<![\*\s])\*(?![\*\w])", r"<i>\1</i>", text)

    # Ro'yxat belgilari
    text = re.sub(r"^[ \t]*[-*][ \t]+", "• ", text, flags=re.M)

    return re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], text)


# ───────────────────────────────────────────────────────────
# Tozalash: allowlist + to'g'ri joylashtirish + escape
# ───────────────────────────────────────────────────────────

def _escape_text(s: str) -> str:
    """`<`, `>` va entity bo'lmagan `&` ni escape qiladi (mavjud entity'lar saqlanadi)."""
    out: List[str] = []
    pos = 0
    for m in _ENTITY_RE.finditer(s):
        out.append(_raw_escape(s[pos:m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(_raw_escape(s[pos:]))
    return "".join(out)


def _raw_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _open_tag(name: str, attrs: str) -> str:
    """Ochuvchi teg satri; `a` uchun faqat xavfsiz href. None qaytsa teg tashlanadi."""
    if name != "a":
        return f"<{name}>"
    m = _HREF_RE.search(attrs or "")
    href = (m.group(1) or m.group(2) or "").strip() if m else ""
    href = _html.unescape(href)
    if not href.lower().startswith(_SAFE_SCHEMES):
        return ""
    return f'<a href="{_html.escape(href, quote=True)}">'


def clean_html(text: str) -> str:
    """Yaroqsiz teglarni olib tashlaydi/escape qiladi, ochiq teglarni yopadi, nesting'ni to'g'rilaydi."""
    out: List[str] = []
    stack: List[Tuple[str, str]] = []  # (nom, ochuvchi teg satri)
    pos = 0

    def close_all_down_to(index: int) -> None:
        # stack[index:] ni yopadi va stack'dan chiqaradi; qaytaradi: qayta ochiladiganlar
        reopen = stack[index + 1:]
        for name, _ in reversed(stack[index:]):
            out.append(f"</{name}>")
        del stack[index:]
        for name, opener in reopen:
            out.append(opener)
            stack.append((name, opener))

    for m in _TAG_RE.finditer(text):
        out.append(_escape_text(text[pos:m.start()]))
        pos = m.end()
        closing, raw_name, attrs = m.group(1) == "/", m.group(2).lower(), m.group(3)

        if raw_name == "br":
            out.append("\n")
            continue
        if raw_name in ("p", "div", "ul", "ol", "tr"):
            if closing:
                out.append("\n")
            continue
        if raw_name == "li":
            if not closing:
                out.append("\n• ")
            continue
        if _HEADING_RE.match(raw_name):
            out.append("</b>\n" if closing else "\n<b>")
            if closing and stack and stack[-1][0] == "b":
                stack.pop()
            elif not closing:
                stack.append(("b", "<b>"))
            continue

        name = _ALLOWED.get(raw_name)
        if name is None:
            continue  # noma'lum teg: matni qoladi, teg tashlanadi

        if not closing:
            opener = _open_tag(name, attrs)
            if not opener:
                continue
            out.append(opener)
            stack.append((name, opener))
        else:
            idx = next((i for i in range(len(stack) - 1, -1, -1) if stack[i][0] == name), None)
            if idx is None:
                continue  # ochilmagan teg yopilishi — tashlanadi
            if idx == len(stack) - 1:
                out.append(f"</{name}>")
                stack.pop()
            else:
                close_all_down_to(idx)
                # close_all_down_to yopilgan elementni ham chiqargan; qayta ochilganlar qoladi

    out.append(_escape_text(text[pos:]))
    for name, _ in reversed(stack):
        out.append(f"</{name}>")
    return "".join(out)


def to_telegram_html(text: str) -> str:
    """To'liq AI javobi → Telegram uchun xavfsiz HTML."""
    if not text:
        return ""
    return re.sub(r"\n{3,}", "\n\n", clean_html(_markdown_to_html(text))).strip()


# ───────────────────────────────────────────────────────────
# Oqim (partial)
# ───────────────────────────────────────────────────────────

def _hold_back(text: str) -> str:
    """Oxiridagi tugallanmagan teg/entity/Markdown belgisini vaqtincha ko'rsatmaslik."""
    # tugallanmagan HTML teg: "<b", '<a href="ht'
    lt = text.rfind("<")
    if lt != -1 and text.find(">", lt) == -1:
        text = text[:lt]
    # tugallanmagan entity: "&am"
    text = re.sub(r"&#?[A-Za-z0-9]{0,10}$", "", text)
    # ``` bloki ochiq
    if text.count("```") % 2:
        text = text[:text.rfind("```")]
    # yolg'iz ` (fence'lardan tashqari)
    singles = [m.start() for m in re.finditer(r"```.*?```|`", text, flags=re.S) if m.group(0) == "`"]
    if len(singles) % 2:
        text = text[:singles[-1]]
    # ochiq **
    if text.count("**") % 2:
        text = text[:text.rfind("**")]
    return text


def to_partial_html(text: str) -> str:
    """Tugallanmagan matn → yaroqli HTML (ochiq teglar yopiladi)."""
    return to_telegram_html(_hold_back(text))


# ───────────────────────────────────────────────────────────
# Bo'lish va fallback
# ───────────────────────────────────────────────────────────

def split_html(html: str, limit: int = 4000) -> List[str]:
    """
    Yaroqli HTML'ni har biri o'zi yaroqli bo'lgan bo'laklarga bo'ladi.
    Satr oxirlarida bo'lishga harakat qiladi; ochiq teglar bo'lak oxirida yopilib, keyingisida qayta ochiladi.
    """
    if len(html) <= limit:
        return [html]

    # Tokenlar: teglar va matn (matn satrlarga bo'linadi)
    tokens: List[Tuple[str, str]] = []  # ("tag"|"text", qiymat)
    pos = 0
    for m in re.finditer(r"</?[a-zA-Z][^<>]*>", html):
        if m.start() > pos:
            for part in re.split(r"(?<=\n)", html[pos:m.start()]):
                if part:
                    tokens.append(("text", part))
        tokens.append(("tag", m.group(0)))
        pos = m.end()
    if pos < len(html):
        for part in re.split(r"(?<=\n)", html[pos:]):
            if part:
                tokens.append(("text", part))

    chunks: List[str] = []
    stack: List[Tuple[str, str]] = []
    cur: List[str] = []
    cur_len = 0

    def closing_len() -> int:
        return sum(len(n) + 3 for n, _ in stack)

    def flush() -> None:
        nonlocal cur, cur_len
        body = "".join(cur)
        if re.sub(r"<[^>]+>", "", body).strip():
            chunks.append(body + "".join(f"</{n}>" for n, _ in reversed(stack)))
        cur = [o for _, o in stack]
        cur_len = sum(len(o) for _, o in stack)

    cur = []
    for kind, value in tokens:
        if kind == "tag":
            is_close = value.startswith("</")
            name = re.match(r"</?([a-zA-Z0-9-]+)", value).group(1).lower()
            if cur_len + len(value) + closing_len() + (0 if is_close else len(name) + 3) > limit:
                flush()
            cur.append(value)
            cur_len += len(value)
            if is_close:
                if stack and stack[-1][0] == name:
                    stack.pop()
            else:
                stack.append((name, value))
            continue

        text = value
        while text:
            room = limit - cur_len - closing_len()
            if len(text) <= room:
                cur.append(text)
                cur_len += len(text)
                break
            if room < 50 and cur_len > sum(len(o) for _, o in stack):
                flush()
                continue
            cut = max(room, 1)
            # entity ichida kesmaslik
            amp = text.rfind("&", 0, cut)
            if amp != -1 and text.find(";", amp, cut) == -1 and amp > 0:
                cut = amp
            cur.append(text[:cut])
            cur_len += cut
            text = text[cut:]
            flush()

    flush()
    return chunks or [""]


def strip_html(html: str) -> str:
    """HTML teglarsiz oddiy matn (Telegram parse xatosi uchun fallback)."""
    return _html.unescape(re.sub(r"<[^>]+>", "", html))
