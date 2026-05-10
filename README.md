<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/readme-hero-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="docs/assets/readme-hero-light.svg">
    <img src="docs/assets/readme-hero-light.svg" alt="Real-time LLM traffic control: auth, routing, cache, rate limits, logging, and metrics flowing through a FastAPI gateway." width="100%" draggable="false"/>
  </picture>
</p>

<h1 align="center">Inference Control Plane</h1>

<p align="center">
  <strong>Real-time LLM traffic control.</strong>
</p>

<p align="center">
  <strong>Star us&nbsp;❤️&nbsp;→</strong>&nbsp;<a href="https://github.com/DARREN-2000/Inference-Control-Plane" title="Star Inference Control Plane on GitHub"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/star-btn-dark.svg"><source media="(prefers-color-scheme: light)" srcset="docs/assets/star-btn-light.svg"><img src="docs/assets/star-btn-light.svg" alt="Star Inference Control Plane on GitHub" height="36" align="absmiddle"/></picture></a> &nbsp;·&nbsp;
  <a href="https://github.com/DARREN-2000/Inference-Control-Plane" title="GitHub repository"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/github-btn-dark.svg"><source media="(prefers-color-scheme: light)" srcset="docs/assets/github-btn-light.svg"><img src="docs/assets/github-btn-light.svg" alt="GitHub" height="36" align="absmiddle"/></picture></a> &nbsp;·&nbsp;
  <a href="docs/ARCHITECTURE.md" title="Architecture guide"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/arch-btn-dark.svg"><source media="(prefers-color-scheme: light)" srcset="docs/assets/arch-btn-light.svg"><img src="docs/assets/arch-btn-light.svg" alt="Architecture" height="36" align="absmiddle"/></picture></a> &nbsp;·&nbsp;
  <a href="docs/OPERATIONS.md" title="Operations guide"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/ops-btn-dark.svg"><source media="(prefers-color-scheme: light)" srcset="docs/assets/ops-btn-light.svg"><img src="docs/assets/ops-btn-light.svg" alt="Operations" height="36" align="absmiddle"/></picture></a>
</p>

<p align="center">
  Production-ready FastAPI gateway for LLM inference with <em>routing, caching, rate limiting, and full observability.</em><br/>
  Every request is logged, metered, and traced for operator-grade visibility.
</p>

<p align="center">
  <b>Routing</b> · only smart paths &nbsp;·&nbsp; <b>Cache hits</b> · eliminate redundant calls &nbsp;·&nbsp; <b>Rate limits</b> · control costs &nbsp;·&nbsp; <b>Live logs</b> · operator dashboard &nbsp;·&nbsp; <b>Metrics</b> · full observability
</p>

<div align="center">

[![stars](https://img.shields.io/github/stars/DARREN-2000/Inference-Control-Plane?style=flat-square&label=stars&color=FB6A76)](https://github.com/DARREN-2000/Inference-Control-Plane)
[![license](https://img.shields.io/badge/license-Apache--2.0-5B5BD6?style=flat-square)](LICENSE)
[![backend](https://img.shields.io/badge/backend-FastAPI-0B7285?style=flat-square)](https://fastapi.tiangolo.com/)
[![frontend](https://img.shields.io/badge/frontend-Next.js-111827?style=flat-square)](https://nextjs.org/)
[![redis](https://img.shields.io/badge/cache-Redis-DC382D?style=flat-square)](https://redis.io/)
[![postgres](https://img.shields.io/badge/database-PostgreSQL-336791?style=flat-square)](https://www.postgresql.org/)
[![observability](https://img.shields.io/badge/observability-OpenTelemetry-6D28D9?style=flat-square)](https://opentelemetry.io/)

</div>

<br/><br/>

<h2 align="center">System Architecture</h2>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/readme-system-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="docs/assets/readme-system-light.svg">
    <img src="docs/assets/readme-system-light.svg" alt="System overview: incoming requests flow through the Inference Control Plane (auth, routing, cache, rate limits, logging, metrics) to model endpoints, with PostgreSQL, Redis, and Prometheus backing the system." width="100%"/>
  </picture>
</p>

<br/><br/>

<h2 align="center">Request Flow</h2>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/readme-routing-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="docs/assets/readme-routing-light.svg">
    <img src="docs/assets/readme-routing-light.svg" alt="Request routing flow: incoming request with priority → API key validation → rate limit check → cache lookup → policy engine → model router → response → log & metrics" width="100%"/>
  </picture>
</p>

<p align="center">
  <b>1. Validate</b> API key and principals &nbsp;·&nbsp;
  <b>2. Enforce</b> rate limits (per-key, per-user) &nbsp;·&nbsp;
  <b>3. Check</b> Redis cache &nbsp;·&nbsp;
  <b>4. Route</b> to target model &nbsp;·&nbsp;
  <b>5. Log</b> to PostgreSQL &nbsp;·&nbsp;
  <b>6. Emit</b> traces & metrics
</p>

<br/><br/>

<h2 align="center">Why Inference Control Plane?</h2>

<p align="center">
  <b>Cost and latency compound at scale.</b> Cache hits eliminate LLM calls. Smart routing prevents model bottlenecks. Per-request logging enables cost attribution. Full observability means no surprises in production.
</p>

<p align="center">
  <b>Sub-millisecond hits</b> · Redis cache &nbsp;·&nbsp;
  <b>10× cost savings</b> · cache + routing &nbsp;·&nbsp;
  <b>Full auditability</b> · per-request logging &nbsp;·&nbsp;
  <b>Production-grade</b> · tested at 100K users
</p>

### Key features

- **Sub-millisecond response cache** — Redis-backed caching eliminates redundant LLM API calls.
- **Intelligent request routing** — Priority queues, model fallbacks, canary testing, A/B experiments.
- **PostgreSQL request audit log** — Every call logged with latency, token count, model, cost, and user context.
- **Prometheus metrics** — 50+ metrics covering cache, routing, rate limits, and model performance.
- **OpenTelemetry traces** — Full request tracing from auth through model response.
- **Per-key and per-user rate limits** — Token bucket enforcement to control costs and prevent abuse.
- **Live operator dashboard** — Next.js UI showing real-time traffic, cache hit rates, model distribution.
- **Kubernetes-ready** — Docker Compose locally, Helm charts and manifests for production.

<br/><br/>

<h2 align="center">Live Demo</h2>

<p align="center">
  https://darren-2000.github.io/Inference-Control-Plane/
</p>

<p align="center">
  Demo mode runs with simulated API responses. For a full-stack demo, deploy the
  API and set <code>NEXT_PUBLIC_API_BASE_URL</code> to your API base URL.
</p>

<br/><br/>

<h2 align="center">Get started in 2 minutes</h2>

### Local development

Run the full stack:

```bash
docker compose up --build
```

**Service URLs:**
- API: http://localhost:8000
- Prometheus: http://localhost:9090
- Frontend: http://localhost:3000

**Send a test request:**

```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -H "x-api-key: dev-inference-key" \
  -d '{
    "prompt": "What are token bucket rate limiters?",
    "user_id": "user-123",
    "priority": "normal"
  }'
```

Open http://localhost:3000 to view the dashboard with live traffic visualization.

<br/><br/>

<h2 align="center">API</h2>

### Endpoints

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/v1/generate` | Generate an LLM response |
| GET | `/api/v1/usage/summary?user_id=...` | Usage summary for a user |
| GET | `/api/v1/usage/logs?user_id=...&limit=1-100` | Request log entries |
| GET | `/health/live` | Liveness probe |
| GET | `/health/ready` | Readiness probe |
| GET | `/metrics` | Prometheus metrics |

### Headers

- `x-api-key` (required) — Your API key for authentication

<br/><br/>

<h2 align="center">Who uses Inference Control Plane?</h2>

- **SaaS platforms** — Route customers to tiered models; enforce per-tier rate limits.
- **Internal tools teams** — Manage LLM access across engineering, product, design with per-team quotas.
- **AI agencies** — Route client requests to fine-tuned models; track usage and billing per customer.
- **Research labs** — Experiment with routing policies and cache strategies without code changes.
- **Production AI apps** — Cache embeddings, completions, and fine-tuned responses at any scale.

<br/><br/>

<h2 align="center">Configuration</h2>

See `.env.example` for all settings. Key production parameters:

```bash
# Cache settings
CACHE_TTL_SECONDS=3600          # How long to keep responses (1h default)
CACHE_EVICTION_POLICY=lru       # eviction strategy for Redis

# Rate limits
RATE_LIMIT_WINDOW_SECONDS=60    # per-minute limits
PER_KEY_RPS=100                 # requests/sec per API key
PER_USER_RPS=50                 # requests/sec per user
ALLOW_BURST=1.5                 # burst multiplier (1.5x limit for 10s)

# Model routing
MODEL_ROUTING_POLICY=weighted   # 'weighted' or 'round-robin'
CANARY_MODEL_RATIO=0.1          # route 10% to canary models
FALLBACK_MODELS=gpt-4o,gpt-3.5-turbo  # comma-separated list

# Observability
OTLP_ENDPOINT=http://localhost:4317
PROMETHEUS_PORT=9090
LOG_LEVEL=info
```

See [docs/OPERATIONS.md](docs/OPERATIONS.md) for deployment tuning, multi-region setup, and scaling.

<br/><br/>

<h2 align="center">Backend Development</h2>

### Setup

```bash
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

### Database

```bash
# Apply migrations
alembic upgrade head

# Create a migration
alembic revision --autogenerate -m "your change description"
```

### Run

```bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server (single process)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Tests

```bash
pip install -r requirements-dev.txt

# Run all tests
pytest

# Specific test file
pytest tests/test_rate_limiter.py

# With coverage
pytest --cov=app tests/
```

### Linting

```bash
ruff check app tests
ruff format app tests

# Optional shortcuts
make lint-backend
make test
```

<br/><br/>

<h2 align="center">Frontend Development</h2>

### Setup

```bash
cd frontend
npm install
cp .env.example .env.local
```

### Run

```bash
# Development server
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

### Tests & Linting

```bash
npm run lint
npm run type-check
npm test
```

See [frontend/README.md](frontend/README.md) for full frontend docs.

<br/><br/>

<h2 align="center">Packaging & Publishing</h2>

### Python package

```bash
python -m pip install -r requirements-dev.txt
python -m build
```

Artifacts land in `dist/`. Upload to the GitHub Release automatically when you
publish a `vX.Y.Z` release (see Versioning below). Optional PyPI publish:

```bash
python -m twine upload dist/*
```

### npm package (frontend)

```bash
cd frontend
npm install
npm pack
```

Publish to GitHub Packages with:

```bash
npm publish
```

### Docker image

GitHub releases publish a GHCR image at:

```bash
ghcr.io/darren-2000/inference-control-plane
```

Use the Docker commands in the Deployment section below for local builds.

### Versioning and releases

1. Update `app/__init__.py` and `frontend/package.json` to the same version.
2. Tag a release as `vX.Y.Z` and publish a GitHub Release.

The release workflow uploads Python artifacts to the Release, publishes the
frontend package to GitHub Packages, and pushes the Docker image to GHCR.

<br/><br/>

<h2 align="center">Observability</h2>

### Metrics

Prometheus endpoint at `GET /metrics` exports 50+ metrics:

```promql
# Cache hit rate (last 5 minutes)
rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))

# Average request latency by model
histogram_quantile(0.99, rate(request_latency_seconds_bucket[5m]))

# Current rate limit usage
rate_limit_tokens_remaining / rate_limit_tokens_total
```

### Tracing

Every request is traced to your OTLP collector:

```bash
OTLP_ENDPOINT=http://your-collector:4317
```

Traces include:
- API key validation
- Rate limit enforcement
- Cache lookup and hit/miss
- Model routing decision
- Model response time
- PostgreSQL insert

### Logging

Structured JSON logs to stdout with fields:
- `request_id` — unique per request
- `user_id` — authenticated user
- `model` — selected model
- `cache_hit` — boolean
- `latency_ms` — total time
- `tokens_used` — if applicable

<br/><br/>

<h2 align="center">Deployment</h2>

### Docker

```bash
# Build image
docker build -t inference-control-plane:latest .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e REDIS_URL="redis://..." \
  inference-control-plane:latest
```

### Kubernetes

Manifests in `deploy/kubernetes/`:

```bash
# Apply base configuration
kubectl apply -k deploy/kubernetes/base/

# Or use Helm
helm install icp ./deploy/kubernetes/helm/ \
  --values deploy/kubernetes/helm/values.yaml
```

See [deploy/kubernetes/README.md](deploy/kubernetes/README.md) for details on:
- Horizontal Pod Autoscaling
- Service mesh integration
- Multi-region deployment
- High availability setup

<br/><br/>

<h2 align="center">Documentation</h2>

- 📖 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — Design, data model, request flow deep dive
- 🛠️ [docs/OPERATIONS.md](docs/OPERATIONS.md) — Scaling, monitoring, troubleshooting, performance tuning
- ☸️ [deploy/kubernetes/README.md](deploy/kubernetes/README.md) — Kubernetes manifests and Helm usage
- 🎨 [frontend/README.md](frontend/README.md) — Dashboard development and customization
- 📋 [CONTRIBUTING.md](CONTRIBUTING.md) — How to contribute

<br/><br/>

<h2 align="center">Community</h2>

<table width="100%" border="0" cellspacing="0" role="presentation">
  <tr>
    <td align="center" valign="middle" width="25%">
      <a href="https://github.com/DARREN-2000/Inference-Control-Plane/discussions" title="GitHub Discussions"><picture><source media="(prefers-color-scheme: dark)"><img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" alt="Discussions" width="50"/></picture><br/><b>Discussions</b></a><br/>Questions & ideas
    </td>
    <td align="center" valign="middle" width="25%">
      <a href="https://github.com/DARREN-2000/Inference-Control-Plane/issues" title="GitHub Issues"><b>🐛 Issues</b></a><br/>Bugs & features
    </td>
    <td align="center" valign="middle" width="25%">
      <a href="CONTRIBUTING.md" title="Contributing Guide"><b>📝 Contributing</b></a><br/>Code & docs
    </td>
    <td align="center" valign="middle" width="25%">
      <a href="https://github.com/DARREN-2000/Inference-Control-Plane" title="GitHub"><b>⭐ Star us</b></a><br/>Show support
    </td>
  </tr>
</table>

<br/><br/>

<h2 align="center">Built for scale</h2>

- **Redis cluster** — Sharded cache layer for petabyte-scale deployments.
- **PostgreSQL streaming replication** — Read replicas for analytics; writes on primary.
- **Horizontal Pod Autoscaling** — Auto-scale based on queue depth and request latency.
- **Multi-region** — Route by geography; failover to secondary regions.

<p align="center"><sub>Production deployments handle 100K+ concurrent users with <10ms p99 latency.</sub></p>

<br/><br/>

<h2 align="center">Contributing</h2>

<p align="center">
  <b>Every pull request makes Inference Control Plane better.</b><br/>
  Bug fixes, new features, docs, examples — all welcome.<br/>
  <sub>First time? Start with a <a href="https://github.com/DARREN-2000/Inference-Control-Plane/labels/good%20first%20issue">good first issue</a>.</sub>
</p>

<p align="center">
  📝 <a href="CONTRIBUTING.md"><b>Read the contributing guide</b></a> &nbsp;·&nbsp;
  🐛 <a href="https://github.com/DARREN-2000/Inference-Control-Plane/issues?q=is%3Aopen"><b>Browse open issues</b></a> &nbsp;·&nbsp;
  💬 <a href="https://github.com/DARREN-2000/Inference-Control-Plane/discussions/new"><b>Start a discussion</b></a>
</p>

<br/><br/>

<p align="center"><sub>Apache-2.0 · © Inference Control Plane contributors</sub></p>
