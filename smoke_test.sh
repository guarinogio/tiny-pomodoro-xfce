#!/usr/bin/env bash
set -euo pipefail

python3 -m py_compile tiny_pomodoro.py tiny_pomodoro/*.py
python3 -m pytest -q

echo "Smoke test OK"
