# ──────────────────────────────────────────────────────────────────
# Tribesence — Production Dockerfile
# Django 4.2 · Python 3.12-slim · Gunicorn · WhiteNoise static files
# ──────────────────────────────────────────────────────────────────

# ── Stage 1: dependency builder ────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# System deps needed to compile any C-extension wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies into a prefix we can COPY later
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --prefix=/install --no-cache-dir -r requirements.txt \
 && pip install --prefix=/install --no-cache-dir \
        gunicorn \
        whitenoise


# ── Stage 2: runtime image ─────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=tribesence.settings \
    PORT=8000

WORKDIR /app

# Only the packages copied from the builder — no build tools in prod
COPY --from=builder /install /usr/local

# Application source
COPY . .

# ── Collect static files (WhiteNoise will serve them) ──────────────
RUN python manage.py collectstatic --noinput

# ── Run migrations then start Gunicorn ─────────────────────────────
# entrypoint.sh handles ordering so the CMD stays clean
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "tribesence.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--threads", "2", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]