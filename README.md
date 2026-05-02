<p align="center">
	<picture>
		<source media="(prefers-color-scheme: dark)" srcset="docs/assets/readme-hero-dark.svg">
		<source media="(prefers-color-scheme: light)" srcset="docs/assets/readme-hero-light.svg">
		<img src="docs/assets/readme-hero-light.svg" alt="Live flow of LLM traffic through auth, routing, cache, limits, logs, and metrics." width="100%" draggable="false"/>
	</picture>
</p>

<h1 align="center">Inference Control Plane</h1>

<p align="center">
	<strong>Always-on LLM gateway with live routing, cache, limits, and observability.</strong>
</p>

<p align="center">
	<a href="#quickstart"><img src="https://img.shields.io/badge/Quickstart-Run%20locally-0A7C5A?style=for-the-badge" alt="Quickstart"/></a>
	<a href="#api"><img src="https://img.shields.io/badge/API-Endpoints-2563EB?style=for-the-badge" alt="API Endpoints"/></a>
	<a href="docs/ARCHITECTURE.md"><img src="https://img.shields.io/badge/Architecture-Read-334155?style=for-the-badge" alt="Architecture"/></a>
	<a href="frontend/README.md"><img src="https://img.shields.io/badge/Frontend-Next.js-111827?style=for-the-badge" alt="Frontend"/></a>
</p>

<div align="center">

[![stars](https://img.shields.io/github/stars/DARREN-2000/Inference-Control-Plane?style=flat-square)](https://github.com/DARREN-2000/Inference-Control-Plane)
[![license](https://img.shields.io/github/license/DARREN-2000/Inference-Control-Plane?style=flat-square)](LICENSE)
[![backend](https://img.shields.io/badge/backend-FastAPI-0B7285?style=flat-square)](https://fastapi.tiangolo.com/)
[![frontend](https://img.shields.io/badge/frontend-Next.js-111827?style=flat-square)](https://nextjs.org/)
[![observability](https://img.shields.io/badge/observability-OpenTelemetry-6D28D9?style=flat-square)](https://opentelemetry.io/)

</div>

<p align="center">
	Inference Control Plane is a fully async FastAPI gateway for LLM inference with model routing,
	Redis caching, Redis-based rate limiting, request logging, and observability.
	A production-focused Next.js frontend in the <a href="frontend/README.md">frontend</a> folder
	supports dashboarding, playground requests, and operator workflows.
</p>

## Why it feels live
- Redis-backed caching and limits keep the hot path fast for every request.
- Routing decisions can change per request based on priority, token estimates, or overrides.
- Logs, metrics, and traces are emitted for each request and shared across services.
- PostgreSQL stores request logs and usage summaries for operators.

## Request flow
1. `POST /api/v1/generate` receives a request and validates the API key.
2. Rate limits are enforced per key and per user.
3. A cache lookup is attempted for prompt and model responses.
4. The router selects the target model or fallback path.
5. The response is returned and the request log is persisted.
6. Metrics and traces are emitted for observability.

## Quickstart
Start the full stack with Docker Compose:

```bash
docker compose up --build
```

Service URLs:
- API: http://localhost:8000
- Prometheus: http://localhost:9090

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

2. Run the UI:

```bash
npm install
npm run dev
```

3. Open http://localhost:3000

## API
- `POST /api/v1/generate`
	- Header: `x-api-key`
	- Body:
		- `prompt`: string
		- `user_id`: string
		- `priority`: low | high (optional, default low)
		- `model_override`: string (optional)

- `GET /api/v1/usage/summary?user_id=<user_id>`
	- Header: `x-api-key`

- `GET /api/v1/usage/logs?user_id=<user_id>&limit=<1-100>`
	- Header: `x-api-key`

Legacy unversioned paths continue to work for backward compatibility:
- `GET /health/live`
- `GET /health/ready`
- `GET /metrics`

## Quick request example
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

## Configuration
See the default settings in `.env.example`. Highlights:
- `DATABASE_URL` and `REDIS_URL` configure data stores.
- `CACHE_TTL_SECONDS` and `RATE_LIMIT_WINDOW_SECONDS` control hot-path behavior.
- `LLM_MODE` can be set to `simulated` for local testing.

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

## License
Apache-2.0. See [LICENSE](LICENSE).