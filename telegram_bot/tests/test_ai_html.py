"""ai_html: sanitizer, oqim (partial) va bo'lish — natija doim yaroqli Telegram HTML bo'lishi kerak."""
import re
from html.parser import HTMLParser

from bot.utils.ai_html import split_html, strip_html, to_partial_html, to_telegram_html


class _Validator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.error = [], None

    def handle_starttag(self, tag, attrs):
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.error = f"mismatch {tag} vs {self.stack}"
        else:
            self.stack.pop()


def is_valid(html: str) -> bool:
    v = _Validator()
    v.feed(html)
    return v.error is None and not v.stack


CASES = [
    "**bold** and *it* and `code` __init__ <b>x</b>",
    "<b>bold <i>nested</b> after</i> end",
    "1 < 2 & 3 > 2 &amp; ok <script>alert(1)</script>",
    '<a href="javascript:alert(1)">bad</a> <a href="https://x.uz/?a=1&b=2">good</a>',
    "# Title\n## Sub\n- a\n- b\n```py\nif a<b: print('x')\n```",
    "line<br>two<p>para</p><ul><li>one</li><li>two</li></ul>",
    "<b>unclosed bold",
    "text </b> stray close",
    "<pre>code <b>x</b></pre>",
]


def test_full_output_is_valid_html():
    for case in CASES:
        assert is_valid(to_telegram_html(case)), case


def test_dangerous_content_removed():
    out = to_telegram_html(CASES[3])
    assert "javascript:" not in out
    assert 'href="https://x.uz/?a=1&amp;b=2"' in out
    assert "<script" not in to_telegram_html(CASES[2])


def test_every_prefix_is_valid_for_streaming():
    for case in CASES:
        for i in range(len(case) + 1):
            assert is_valid(to_partial_html(case[:i])), (case[:i], to_partial_html(case[:i]))


def test_split_respects_limit_and_keeps_tags_valid():
    long = "<b>" + ("word " * 500 + "\n") * 6 + "</b> tail &amp; end " + "x" * 5000
    html = to_telegram_html(long)
    parts = split_html(html, 1000)
    assert len(parts) > 1
    assert all(len(p) <= 1000 for p in parts)
    assert all(is_valid(p) for p in parts)

    def text(s):
        return re.sub(r"\s", "", re.sub(r"<[^>]+>", "", s))

    assert text("".join(parts)) == text(html)


def test_strip_html():
    assert strip_html("<b>a &amp; b</b>") == "a & b"
