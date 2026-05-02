<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/readme-hero-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="docs/assets/readme-hero-light.svg">
    <img src="docs/assets/readme-hero-light.svg" alt="Live flow of LLM traffic through auth, routing, cache, limits, logs, and metrics." width="100%" draggable="false"/>
  </picture>
</p>

<h1 align="center">Inference Control Plane</h1>

<p align="center">
  <strong>Control LLM traffic in real time.</strong>
</p>

<p align="center">
  <strong>Star us</strong> -> <a href="https://github.com/DARREN-2000/Inference-Control-Plane">GitHub</a> |
  <a href="docs/ARCHITECTURE.md">Architecture</a> |
  <a href="docs/OPERATIONS.md">Operations</a> |
  <a href="frontend/README.md">Frontend</a>
</p>

<p align="center">
  Production-ready FastAPI gateway for LLM inference: routing, caching, limits, and observability.
  Every request is logged, metered, and traced for operator-grade visibility.
</p>

<p align="center">
  <b>Routing</b> | <b>Cache</b> | <b>Rate limits</b> | <b>Logs</b> | <b>Metrics</b>
</p>

<p align="center">
  <a href="#get-started">Get started</a> |
  <a href="#request-flow">Request flow</a> |
  <a href="#api">API</a> |
  <a href="#observability">Observability</a>
</p>

<div align="center">

[![stars](https://img.shields.io/github/stars/DARREN-2000/Inference-Control-Plane?style=flat-square)](https://github.com/DARREN-2000/Inference-Control-Plane)
[![license](https://img.shields.io/github/license/DARREN-2000/Inference-Control-Plane?style=flat-square)](LICENSE)
[![backend](https://img.shields.io/badge/backend-FastAPI-0B7285?style=flat-square)](https://fastapi.tiangolo.com/)
[![frontend](https://img.shields.io/badge/frontend-Next.js-111827?style=flat-square)](https://nextjs.org/)
[![observability](https://img.shields.io/badge/observability-OpenTelemetry-6D28D9?style=flat-square)](https://opentelemetry.io/)

</div>

<br/>

## Get started
Run the full stack with Docker Compose:

```bash
docker compose up --build
```

Service URLs:
- API: http://localhost:8000
- Prometheus: http://localhost:9090
- Frontend: http://localhost:3000

Send a request:

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

## Why this control plane
- Fast hot path backed by Redis for caching and rate limits.
- Per-request routing with priority and model overrides.
- PostgreSQL request logs with usage summaries for operators.
- OpenTelemetry traces and Prometheus metrics on every request.
- A Next.js dashboard for live workflows and playground requests.

## Request flow
1. `POST /api/v1/generate` validates the API key.
2. Per-key and per-user rate limits are enforced.
3. Cache lookup checks for a matching response.
4. Router selects the target model or fallback path.
5. The response is returned and a request log is written.
6. Metrics and traces are emitted.

## Local development
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
See [CONTRIBUTING.md](CONTRIBUTING.md).

## License
Apache-2.0. See [LICENSE](LICENSE).