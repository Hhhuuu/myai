#!/usr/bin/env python3
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import sys

ROOT = Path(__file__).resolve().parents[1]
PUBLISHED = ROOT / "published"

if len(sys.argv) != 2:
    raise SystemExit("Usage: archive_post.py <draft.md>")

source = Path(sys.argv[1])
text = source.read_text(encoding="utf-8").strip()

now = datetime.now(timezone.utc)
digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]
filename = f"{now.strftime('%Y-%m-%d_%H-%M-%S')}_{digest}.md"

PUBLISHED.mkdir(parents=True, exist_ok=True)
target = PUBLISHED / filename
target.write_text(text + "\n", encoding="utf-8")

print(f"Archived as {target.relative_to(ROOT)}")
