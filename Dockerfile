# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Argus AI - web tier image
# Serves the UI, authentication, SQLite-backed reports and the alerts
# dashboard under a production WSGI server (gunicorn).
#
# Layer order is tuned for fast rebuilds: the user + dependency layers are
# cached and only re-run when requirements.txt changes; editing app code only
# rebuilds the tiny COPY layers.
# ---------------------------------------------------------------------------
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ARGUS_HOST=0.0.0.0 \
    ARGUS_PORT=5000 \
    ARGUS_DATA_DIR=/data \
    ARGUS_DB_PATH=/data/patient.db

# Non-root user + writable data dir (cached layer — never changes)
RUN useradd --create-home --uid 10001 argus \
    && mkdir -p /data \
    && chown argus:argus /data

WORKDIR /app

# Dependencies (cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Application code (only these small layers rebuild on a code change)
COPY --chown=argus:argus backend/ ./backend/
COPY --chown=argus:argus frontend/ ./frontend/

USER argus
VOLUME ["/data"]
EXPOSE 5000

# Container health check. Honors $PORT (injected by hosts like Render).
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os,urllib.request,sys; p=os.environ.get('PORT','5000'); sys.exit(0) if urllib.request.urlopen(f'http://127.0.0.1:{p}/health').status==200 else sys.exit(1)"

# Production WSGI server. Shell form so ${PORT} is expanded at runtime;
# defaults to 5000 for local `docker run` / compose.
# --preload imports the app once in the master before forking workers, so DB
# init + demo seeding run exactly once (no cross-worker race).
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --preload --timeout 120 backend.api_server:app"]
