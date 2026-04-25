# Architecture

## Overview

Inference Control Plane is split into backend API, frontend dashboard, and observability components.

- Backend: FastAPI async gateway in `app/`
- Frontend: Next.js dashboard in `frontend/`
- Data stores: PostgreSQL (system of record), Redis (cache/rate-limit state)
- Metrics: Prometheus scrape from `/metrics`

## Backend Layers

- API layer: request parsing, auth dependency wiring
- Services layer: inference flow, routing, caching, usage aggregation
- Data layer: SQLAlchemy models and async session handling
- Observability layer: logs, traces, and metrics

## Request Flow

1. `POST /api/v1/generate` receives a request.
2. API key is validated and loaded from cache/DB.
3. Per-key and per-user limits are enforced.
4. Cache lookup is attempted.
5. Model is selected using routing rules.
6. LLM response is generated with fallback on provider failure.
7. Request log is persisted and metrics are emitted.

## Schema Management

Database schema changes are managed with Alembic migrations in `alembic/`.
Runtime schema auto-creation is intentionally disabled.
