# Operations Runbook

## Local Preflight

```bash
make install-dev
make migrate
make test
make lint-frontend
make build-frontend
```

## Docker Runtime

```bash
docker compose up --build
```

The docker compose stack runs `alembic upgrade head` at startup before launching the API.
For other deployments, run migrations separately.

## Render Deployment (Backend)

1. Create Render PostgreSQL and Redis instances.
2. Create a Render Web Service from this repo using the Dockerfile.
3. Configure environment variables:

```bash
DATABASE_URL=postgresql+asyncpg://<render-user>:<password>@<render-host>:5432/<db>
REDIS_URL=redis://:<password>@<render-redis-host>:6379/0
ENVIRONMENT=production
DEFAULT_API_KEY=replace-me
CORS_ALLOWED_ORIGINS=["https://your-frontend-domain"]
PORT=8000
```

4. Health check path: `/health/ready`.
5. Run migrations at deploy time (Render start command example):

```bash
alembic upgrade head && uvicorn inference_control_plane.main:app --app-dir src --host 0.0.0.0 --port 8000
```

## Common Checks

- API health: `GET /health/live`
- API readiness: `GET /health/ready`
- Metrics: `GET /metrics`
- Frontend: `http://localhost:3000`
- Prometheus: `http://localhost:9090`

## Database Migration Workflow

Create migration:

```bash
make migration m="add new field"
```

Apply migration:

```bash
make migrate
```

## Incident Quick Actions

- Restart app service: `docker compose restart app`
- Tail app logs: `docker compose logs -f app`
- Validate DB connectivity with readiness endpoint
- Check Redis health (`docker compose exec redis redis-cli ping`)
