#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / "state" / "latest.json"
PROMPT_FILE = ROOT / "config" / "digest-prompt.md"
DIGESTS_DIR = ROOT / "digests"
TELEGRAM_FILE = ROOT / "telegram.md"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def parse_json(text: str) -> dict:
    cleaned = strip_code_fence(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            return json.loads(cleaned[start:end + 1])
        raise


def validate_result(data: dict) -> None:
    required = {
        "title": str,
        "period": str,
        "full_digest": str,
        "telegram_messages": list,
        "published_titles": list,
        "source_urls": list,
    }
    for key, expected in required.items():
        if key not in data:
            raise ValueError(f"Missing field: {key}")
        if not isinstance(data[key], expected):
            raise ValueError(f"Invalid type for {key}")

    if len(data["full_digest"].strip()) < 300:
        raise ValueError("full_digest is suspiciously short")
    if not data["telegram_messages"]:
        raise ValueError("telegram_messages is empty")
    for i, message in enumerate(data["telegram_messages"], start=1):
        if not isinstance(message, str):
            raise ValueError(f"telegram_messages[{i}] must be string")
        if not message.strip():
            raise ValueError(f"telegram_messages[{i}] is empty")
        if len(message) > 3500:
            raise ValueError(f"telegram_messages[{i}] exceeds 3500 chars")


def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is not configured")

    model = os.getenv("OPENAI_MODEL", "gpt-5.6-terra").strip()
    state = load_state()
    now = utc_now()

    previous_run = state.get("last_run_utc")
    if previous_run:
        period_start = previous_run
    else:
        period_start = (now - timedelta(days=7)).isoformat()

    previous_titles = state.get("published_titles", [])[-50:]

    base_prompt = PROMPT_FILE.read_text(encoding="utf-8")
    run_context = f"""
КОНТЕКСТ ТЕКУЩЕГО ЗАПУСКА

Текущее время UTC: {now.isoformat()}
Начало периода: {period_start}

Темы, уже опубликованные в предыдущих выпусках:
{json.dumps(previous_titles, ensure_ascii=False, indent=2)}

Не повторяй их без существенного нового развития после начала текущего периода.
"""

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=model,
        tools=[{"type": "web_search"}],
        input=base_prompt + "\n\n" + run_context,
    )

    raw = response.output_text
    data = parse_json(raw)
    validate_result(data)

    date_slug = now.strftime("%Y-%m-%d")
    DIGESTS_DIR.mkdir(parents=True, exist_ok=True)

    full_path = DIGESTS_DIR / f"{date_slug}.md"
    full_text = (
        f"# {data['title']}\n\n"
        f"**Период:** {data['period']}\n\n"
        f"{data['full_digest'].strip()}\n"
    )
    full_path.write_text(full_text, encoding="utf-8")
    # Human-readable preview. The sender reads telegram.json instead.
    TELEGRAM_FILE.write_text(
        ("\n\n---\n\n".join(m.strip() for m in data["telegram_messages"])) + "\n",
        encoding="utf-8",
    )
    (ROOT / "telegram.json").write_text(
        json.dumps(
            {"parse_mode": "MarkdownV2", "messages": data["telegram_messages"]},
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    merged_titles = (previous_titles + [str(x) for x in data["published_titles"]])[-100:]
    new_state = {
        "last_run_utc": now.isoformat(),
        "last_period": data["period"],
        "last_digest_file": str(full_path.relative_to(ROOT)),
        "published_titles": merged_titles,
        "source_urls": data["source_urls"][-30:],
        "model": model,
    }
    STATE_FILE.write_text(
        json.dumps(new_state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Generated {full_path.relative_to(ROOT)}")
    print(f"Telegram messages: {len(data['telegram_messages'])}")
    print(f"Telegram chars: {sum(len(m) for m in data['telegram_messages'])}")
    print(f"Topics: {len(data['published_titles'])}")
    print(f"Sources: {len(data['source_urls'])}")


if __name__ == "__main__":
    main()
