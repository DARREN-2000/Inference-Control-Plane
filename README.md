# Inference Control Plane

Inference Control Plane is a fully async FastAPI gateway for LLM inference with model routing, Redis caching, Redis-based rate limiting, request logging, and observability.

This repository now includes a production-oriented Next.js frontend in `frontend/` for dashboarding, playground requests, and operator workflows.

## Capabilities

- API key authentication with DB lookup and Redis auth cache
- Per-key and per-user rate limiting
- Prompt and model response caching with TTL
- Routing by priority, token estimate, or explicit model override
- Fallback model path on upstream failure
- Request log persistence in PostgreSQL
- Usage summary by tenant and user
- Prometheus metrics and OpenTelemetry tracing
- Liveness and readiness health checks

## Project Structure

```text
app/
	main.py
	api/
	core/
	db/
	models/
	observability/
	schemas/
	services/
frontend/
 	src/
prometheus/
	prometheus.yml
Dockerfile
docker-compose.yml
```

## Local Development

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

## Testing and Quality

Backend tests:

```bash
pip install -r requirements.txt -r requirements-dev.txt
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
make lint-frontend
make build-frontend
make migrate
make migration m="describe change"
```

## Docker Compose

Start all services (API, PostgreSQL, Redis, Prometheus):

```bash
docker compose up --build
```

The app container applies migrations with `alembic upgrade head` before starting the API process.

Stop all services:

```bash
docker compose down
```

Service URLs:

- API: http://localhost:8000
- Prometheus: http://localhost:9090

## Frontend (Next.js + Tailwind)

1. Open a second terminal.
2. Prepare frontend environment:

```bash
cd frontend
cp .env.example .env.local
```

3. Run the UI:

```bash
npm install
npm run dev
```

4. Open http://localhost:3000

## API Endpoints

- POST /api/v1/generate
	- Header: x-api-key
	- Body:
		- prompt: string
		- user_id: string
		- priority: low | high (optional, default low)
		- model_override: string (optional)

- GET /api/v1/usage/summary?user_id=<user_id>
	- Header: x-api-key

- GET /api/v1/usage/logs?user_id=<user_id>&limit=<1-100>
	- Header: x-api-key

Legacy unversioned paths continue to work for backward compatibility.

- GET /health/live
- GET /health/ready
- GET /metrics

## Quick Request Example

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

## Notes

- Database schema is managed with Alembic migrations.
- A default API key is seeded from DEFAULT_API_KEY.
- In production, override DEFAULT_API_KEY and store secrets securely.