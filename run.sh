#!/usr/bin/env bash
# ─────────────────────────────────────────────
# run.sh — Start the SecureBank Flask dev server
# ─────────────────────────────────────────────
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

# Activate virtual environment if present
if [ -f "$ROOT/venv/bin/activate" ]; then
  source "$ROOT/venv/bin/activate"
fi

# Seed the DB (no-op if customers already exist)
cd "$ROOT/BACKEND"
python seed.py

# Launch Flask
export FLASK_APP=app.py
export FLASK_DEBUG=1
exec flask run
