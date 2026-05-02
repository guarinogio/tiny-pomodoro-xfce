#!/usr/bin/env bash
set -euo pipefail

python3 -m py_compile tiny_pomodoro.py tiny_pomodoro/*.py

python3 - <<'PY'
from tiny_pomodoro.config import DEFAULTS
required = [
    "timer_title", "work_minutes", "timer_hours", "timer_minutes",
    "timer_seconds", "timer_shutdown", "compact_mode",
    "dim_when_inactive", "inactive_opacity"
]
missing = [k for k in required if k not in DEFAULTS]
if missing:
    raise SystemExit(f"Missing config keys: {missing}")
print("Smoke test OK")
PY
