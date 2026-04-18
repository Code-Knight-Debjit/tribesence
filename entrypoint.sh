#!/bin/sh
# ──────────────────────────────────────────────────────────────────
# entrypoint.sh — run migrations, then hand off to CMD (Gunicorn)
# ──────────────────────────────────────────────────────────────────
set -e

echo "▶ Applying database migrations…"
python manage.py migrate --noinput

echo "▶ Starting server…"
exec "$@"