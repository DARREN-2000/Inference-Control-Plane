<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/readme-hero-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="docs/assets/readme-hero-light.svg">
    <img src="docs/assets/readme-hero-light.svg" alt="Live flow of LLM traffic through auth, routing, cache, limits, logs, and metrics." width="100%" draggable="false"/>
  </picture>
</p>

<h1 align="center">Inference Control Plane</h1>

<p align="center">
  <strong>Real-time LLM traffic control.</strong>
</p>

<p align="center">
  <strong>Star us&nbsp;⭐&nbsp;→</strong>&nbsp;<a href="https://github.com/DARREN-2000/Inference-Control-Plane" title="Star on GitHub">GitHub</a> &nbsp;·&nbsp;
  <a href="docs/ARCHITECTURE.md" title="Read the architecture guide">Architecture</a> &nbsp;·&nbsp;
  <a href="docs/OPERATIONS.md" title="Operations guide">Operations</a> &nbsp;·&nbsp;
  <a href="frontend/README.md" title="Frontend docs">Frontend</a>
</p>

<p align="center">Production-ready FastAPI gateway for LLM inference — <em>routing, caching, rate limits, and observability.</em><br/>Every request is logged, metered, and traced for operator-grade visibility.</p>

<p align="center">
  <b>Routing</b> &nbsp;·&nbsp; <b>Cache hits</b> &nbsp;·&nbsp; <b>Rate limits</b> &nbsp;·&nbsp; <b>Live logs</b> &nbsp;·&nbsp; <b>Metrics</b>
</p>

<div align="center">

[![stars](https://img.shields.io/github/stars/DARREN-2000/Inference-Control-Plane?style=flat-square&label=stars&color=FB6A76)](https://github.com/DARREN-2000/Inference-Control-Plane)
[![license](https://img.shields.io/badge/license-Apache--2.0-5B5BD6?style=flat-square)](LICENSE)
[![backend](https://img.shields.io/badge/backend-FastAPI-0B7285?style=flat-square)](https://fastapi.tiangolo.com/)
[![frontend](https://img.shields.io/badge/frontend-Next.js-111827?style=flat-square)](https://nextjs.org/)
[![observability](https://img.shields.io/badge/observability-OpenTelemetry-6D28D9?style=flat-square)](https://opentelemetry.io/)
[![python](https://img.shields.io/badge/python-3.9%2B-3572A5?style=flat-square)](https://www.python.org/)

</div>

<br/>

<br/>

<h3 align="center">Get started in 2 minutes</h3>

Run the full stack with Docker Compose:

```bash
docker compose up --build
```

Service URLs:
- **API**: http://localhost:8000
- **Prometheus**: http://localhost:9090
- **Frontend**: http://localhost:3000

<p align="center">Send a test request:</p>

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -H "x-api-key: dev-inference-key" \
  -d '{
    "prompt": "Explain token bucket rate limiting.",
    "user_id": "user-123",
    "priority": "low"
  }'
```

<br/><br/>## Why this control plane

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/readme-system-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="docs/assets/readme-system-light.svg">
    <img src="docs/assets/readme-system-light.svg" alt="System overview: auth, routing, cache, rate limits, logging, and metrics" width="100%"/>
  </picture>
</p>

- **Sub-second response cache** backed by Redis for instant hits on repeated requests.
- **Intelligent routing** with priority queuing and dynamic model fallbacks.
- **Request audit log** in PostgreSQL with per-user and per-API-key usage summaries.
- **Full observability** — OpenTelemetry traces and Prometheus metrics on every request.
- **Live dashboard** — Next.js UI for real-time workflows, playground requests, and monitoring.

<br/><br/>## Request flow

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/readme-routing-light.svg">
    <source media="(prefers-color-scheme: light)" srcset="docs/assets/readme-routing-light.svg">
    <img src="docs/assets/readme-routing-light.svg" alt="Request routing flow: auth → policy → router → model selection → cache → metrics" width="100%"/>
  </picture>
</p>

1. `POST /api/v1/generate` **validates** the API key and principals.
2. **Rate limits** are enforced per key and per user (token bucket).
3. **Cache lookup** checks Redis for a matching prior response.
4. **Router** selects the target model or a fallback path based on priorities.
5. **Response** is returned; request metadata is logged to PostgreSQL.
6. **Metrics & traces** are emitted to Prometheus and your OpenTelemetry collector.

<br/><br/>## Local development
### Backend
1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy environment defaults:

```bash
cp .env.example .env
```

4. Start PostgreSQL and Redis locally.
5. Apply database migrations:

```bash
alembic upgrade head
```

6. Run the API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
1. Prepare frontend environment:

```bash
cd frontend
cp .env.example .env.local
```

2. Install dependencies and run the UI:

```bash
npm install
npm run dev
```

3. Open http://localhost:3000

## API
| Method | Path | Description |
| --- | --- | --- |
| POST | /api/v1/generate | Generate an LLM response |
| GET | /api/v1/usage/summary?user_id=... | Usage summary for a user |
| GET | /api/v1/usage/logs?user_id=...&limit=1-100 | Request log entries |

Headers:
- `x-api-key`

Legacy unversioned paths remain available:
- `GET /health/live`
- `GET /health/ready`
- `GET /metrics`

## Configuration
See the default settings in [.env.example](.env.example). Highlights:
- `DATABASE_URL` and `REDIS_URL` configure data stores.
- `CACHE_TTL_SECONDS` and `RATE_LIMIT_WINDOW_SECONDS` tune hot-path behavior.
- `LLM_MODE` can be set to `simulated` for local testing.

## Observability
- Prometheus metrics: `GET /metrics`
- OpenTelemetry traces: configured via `OTLP_ENDPOINT`
- Structured logs include request id, user id, model selection, and latency.

## Deployment
- Docker Compose for local and demo environments.
- Kubernetes manifests in `deploy/kubernetes`.

## Testing and quality
Backend checks:

```bash
pip install -r requirements.txt -r requirements-dev.txt
ruff check app tests
pytest
```

Frontend checks:

```bash
cd frontend
npm run lint
npm run build
```

Optional shortcuts:

```bash
make install-dev
make test
make lint-backend
make lint-frontend
make build-frontend
make migrate
make migration m="describe change"
make quality
```

## Docs
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/OPERATIONS.md](docs/OPERATIONS.md)
- [deploy/kubernetes/README.md](deploy/kubernetes/README.md)
- [frontend/README.md](frontend/README.md)

## Contributing

Every contribution makes Inference Control Plane better — from bug reports and feature requests to code and docs.

<p align="center">
  📝 <a href="CONTRIBUTING.md"><b>Read the contributing guide</b></a> &nbsp;·&nbsp;
  🐛 <a href="https://github.com/DARREN-2000/Inference-Control-Plane/issues"><b>Open an issue</b></a> &nbsp;·&nbsp;
  💬 <a href="https://github.com/DARREN-2000/Inference-Control-Plane/discussions"><b>Start a discussion</b></a>
</p>

<br/><br/>

## License

Apache-2.0 · See [LICENSE](LICENSE)