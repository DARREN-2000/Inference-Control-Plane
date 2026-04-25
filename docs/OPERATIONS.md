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

The app service runs `alembic upgrade head` at startup before launching the API.

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
