#!/usr/bin/env bash
# SAHAYI one-command demo launcher
set -e
if [ ! -d ".venv" ]; then
  echo "📦 Creating virtualenv…"
  python -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate
pip install -q -r requirements.txt
echo ""
echo "🌿 SAHAYI live on http://localhost:8000"
echo "   Open the dashboard, tap Auto-play, and let Lakshmi's journey run."
echo ""
uvicorn app.main:app --host 0.0.0.0 --port 8000
