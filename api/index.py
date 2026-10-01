"""Vercel serverless entry point.

Vercel's Python runtime imports THIS module and serves its ASGI `app`.
Everything else stays untouched - the same FastAPI app powers local,
Vercel and Cloud Run.
"""
import os
import sys

# api/index.py sits one level below the project root; make `app` importable.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from app.main import app  # noqa: E402

# Vercel looks for the ASGI callable named `app` in this module.
