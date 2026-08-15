#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

TELEGRAM_MAX = 4096


def load_payload(path: str) -> tuple[str, list[str]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    parse_mode = data.get("parse_mode", "MarkdownV2")
    messages = data.get("messages", [])

    if not isinstance(messages, list) or not messages:
        raise SystemExit("telegram.json does not contain messages")

    for i, message in enumerate(messages, start=1):
        if not isinstance(message, str) or not message.strip():
            raise SystemExit(f"Message {i} is empty or invalid")
        if len(message) > TELEGRAM_MAX:
            raise SystemExit(
                f"Message {i} is {len(message)} chars; Telegram limit is {TELEGRAM_MAX}"
            )

    return parse_mode, messages


def send(token: str, chat_id: str, text: str, parse_mode: str) -> int:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps(
        {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
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
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not configured")
    if not chat_id:
        raise SystemExit("TELEGRAM_CHAT_ID is not configured")
    if len(sys.argv) != 2:
        raise SystemExit("Usage: send_telegram.py <telegram.json>")

    parse_mode, messages = load_payload(sys.argv[1])
    print(f"Publishing {len(messages)} Telegram message(s) using {parse_mode}")

    for i, message in enumerate(messages, start=1):
        message_id = send(token, chat_id, message, parse_mode)
        print(f"Sent {i}/{len(messages)} message_id={message_id}")
        if i < len(messages):
            time.sleep(1)


if __name__ == "__main__":
    main()
