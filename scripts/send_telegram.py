#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

SAFE_LIMIT = 3500


def escape_markdown_v2(text: str) -> str:
    # Preserve only very simple authoring conventions from telegram-draft.md:
    # **bold** -> *bold*
    # `code` -> `code`
    # [text](url) -> [text](url)
    #
    # Everything else is escaped for Telegram MarkdownV2.

    placeholders = {}

    def stash(value: str) -> str:
        key = f"@@PH{len(placeholders)}@@"
        placeholders[key] = value
        return key

    # Links first.
    def link_repl(m):
        label = m.group(1)
        url = m.group(2)
        esc_label = re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', label)
        esc_url = url.replace("\\", "\\\\").replace(")", "\\)")
        return stash(f"[{esc_label}]({esc_url})")

    text = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', link_repl, text)

    # Inline code.
    def code_repl(m):
        code = m.group(1).replace("\\", "\\\\").replace("`", "\\`")
        return stash(f"`{code}`")

    text = re.sub(r'`([^`\n]+)`', code_repl, text)

    # Bold from standard Markdown **text**.
    def bold_repl(m):
        inner = re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', m.group(1))
        return stash(f"*{inner}*")

    text = re.sub(r'\*\*(.+?)\*\*', bold_repl, text)

    # Escape remaining Telegram MarkdownV2 special chars.
    text = re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

    # Restore protected constructs.
    for key, value in placeholders.items():
        text = text.replace(key, value)

    return text


def split_text(text: str, limit: int = SAFE_LIMIT) -> list[str]:
    paragraphs = text.strip().split("\n")
    chunks, current = [], []

    for paragraph in paragraphs:
        candidate = "\n".join(current + [paragraph]) if current else paragraph

        if len(candidate) <= limit:
            current.append(paragraph)
            continue

        if current:
            chunks.append("\n".join(current).strip())
            current = []

        remaining = paragraph
        while len(remaining) > limit:
            cut = remaining.rfind(" ", 0, limit)
            if cut < limit // 2:
                cut = limit
            chunks.append(remaining[:cut].strip())
            remaining = remaining[cut:].strip()

        if remaining:
            current = [remaining]

    if current:
        chunks.append("\n".join(current).strip())

    return [c for c in chunks if c]


def send(token: str, chat_id: str, text: str) -> int:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps(
        {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "MarkdownV2",
            "disable_web_page_preview": True,
        },
        ensure_ascii=False,
    ).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram HTTP {exc.code}: {body}") from exc

    if not result.get("ok"):
        raise RuntimeError(f"Telegram API error: {result}")

    return int(result["result"]["message_id"])


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: send_telegram.py <draft.md>")

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not configured")
    if not chat_id:
        raise SystemExit("TELEGRAM_CHAT_ID is not configured")

    raw = open(sys.argv[1], "r", encoding="utf-8").read().strip()
    rendered = escape_markdown_v2(raw)
    chunks = split_text(rendered)

    print(f"Publishing {len(chunks)} Telegram message(s)")

    for i, chunk in enumerate(chunks, start=1):
        message_id = send(token, chat_id, chunk)
        print(f"Sent {i}/{len(chunks)} message_id={message_id}")
        if i < len(chunks):
            time.sleep(1)


if __name__ == "__main__":
    main()
