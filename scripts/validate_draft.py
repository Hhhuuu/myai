#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("Usage: validate_draft.py <draft.md>")

path = Path(sys.argv[1])
if not path.exists():
    raise SystemExit("Draft file not found")

text = path.read_text(encoding="utf-8").strip()

if not text:
    raise SystemExit("Draft is empty")

if "PASTE TELEGRAM POST HERE" in text:
    raise SystemExit("Replace the template text before publishing")

print(f"Draft OK: {len(text)} chars")
