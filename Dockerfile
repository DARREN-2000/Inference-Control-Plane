FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip uv

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini
COPY .env.example ./.env.example

RUN uv sync --frozen --no-dev

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home appuser

COPY --chown=appuser:appuser --from=builder /app/.venv /app/.venv
COPY --chown=appuser:appuser --from=builder /app/src ./src
COPY --chown=appuser:appuser --from=builder /app/alembic ./alembic
COPY --chown=appuser:appuser --from=builder /app/alembic.ini ./alembic.ini
COPY --chown=appuser:appuser --from=builder /app/README.md ./README.md
COPY --chown=appuser:appuser --from=builder /app/.env.example ./.env.example
COPY --chown=appuser:appuser scripts ./scripts

RUN sed -i 's/\r$//' ./scripts/start.sh && chmod +x ./scripts/start.sh

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD curl -fsS http://localhost:8000/health/live || exit 1

CMD ["sh", "./scripts/start.sh"]
