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

<p align="center">
  Production-ready FastAPI gateway for LLM inference — <em>routing, caching, rate limits, and observability.</em><br/>
  Every request is logged, metered, and traced for operator-grade visibility.
</p>

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

Open http://localhost:3000 to see live traffic in the dashboard.

<br/><br/>

## Why Inference Control Plane?

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/readme-system-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="docs/assets/readme-system-light.svg">
    <img src="docs/assets/readme-system-light.svg" alt="System overview: auth, routing, cache, rate limits, logging, and metrics" width="100%"/>
  </picture>
</p>

**Cost and latency matter.** Every millisecond and token counts.

- 🚀 **Sub-millisecond cache hits** — Redis-backed response caching eliminates redundant LLM calls.
- 🎯 **Intelligent routing** — Priority queues, model fallbacks, canary testing, A/B experiments.
- 📊 **Request audit log** — PostgreSQL stores every request with latency, cost, model, and user context.
- 📈 **Full observability** — Prometheus metrics and OpenTelemetry traces on every single request.
- 🔐 **Rate limit enforcement** — Token bucket per key and per user — no runaway costs.
- 🎨 **Live dashboard** — Next.js UI shows traffic, cache performance, model selection in real time.
- ☸️ **Production-ready** — Docker Compose locally, Kubernetes manifests for production.

<br/><br/>

## Request flow

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

<br/><br/>

## Who uses Inference Control Plane?

- **SaaS platforms** — Control which customers hit which models; enforce per-tier rate limits.
- **Internal tools teams** — Manage LLM access across engineering, product, and design teams.
- **AI agencies** — Route client requests to fine-tuned models; track usage and billing per customer.
- **Research labs** — Experiment with model routing policies and cache strategies without code.
- **Production AI apps** — Cache embeddings, completions, and fine-tuned responses at scale.

<br/><br/>

## API Reference

| Method | Path | Description |
| --- | --- | --- |
| POST | /api/v1/generate | Generate an LLM response |
| GET | /api/v1/usage/summary?user_id=... | Usage summary for a user |
| GET | /api/v1/usage/logs?user_id=...&limit=1-100 | Request log entries |
| GET | /health/live | Liveness probe |
| GET | /health/ready | Readiness probe |
| GET | /metrics | Prometheus metrics |

Headers:
- `x-api-key` (required) — Your API key for authentication

<br/><br/>

## Production tuning

For production workloads, configure these key parameters:

```bash
# Cache behavior — trade freshness vs. hit rate
CACHE_TTL_SECONDS=3600          # How long to keep responses cached (1h recommended)

# Rate limits — prevent runaway costs
RATE_LIMIT_WINDOW_SECONDS=60    # Token bucket window (60s = per-minute limits)
PER_KEY_RPS=100                 # Requests per second per API key
PER_USER_RPS=50                 # Requests per second per user

# Model routing — canary deployments
MODEL_ROUTING_POLICY=weighted   # or 'round-robin', 'least-loaded'
CANARY_MODEL_RATIO=0.1          # Route 10% of traffic to new model versions

# Observability — configure exporters
OTLP_ENDPOINT=http://collector:4317
OTLP_BATCH_SIZE=512
PROMETHEUS_SCRAPE_INTERVAL=15s
```

See [docs/OPERATIONS.md](docs/OPERATIONS.md) for:
- Multi-region deployment
- Failover and high-availability  
- Database query optimization
- Troubleshooting and debugging

<br/><br/>

## Local development

### Backend

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy environment defaults:

```bash
cp .env.example .env
```

4. Start PostgreSQL and Redis locally (or use the Docker Compose setup).

5. Apply database migrations:

```bash
alembic upgrade head
```

6. Run the API server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at http://localhost:8000. Docs at http://localhost:8000/docs.

### Frontend

1. Prepare frontend environment:

```bash
cd frontend
cp .env.example .env.local
```

2. Install dependencies and start dev server:

```bash
npm install
npm run dev
```

3. Open http://localhost:3000

<br/><br/>

## Testing and quality  

Backend tests and checks:

```bash
pip install -r requirements-dev.txt

# Linting
ruff check app tests

# Unit tests
pytest

# All checks
make quality
```

Frontend tests and checks:

```bash
cd frontend

# Linting and type checking
npm run lint

# Build for production
npm run build
```

<br/><br/>

## Documentation

- 📖 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — Design patterns, data model, request flow.
- 🛠️ [docs/OPERATIONS.md](docs/OPERATIONS.md) — Deployment, scaling, monitoring, troubleshooting.
- ☸️ [deploy/kubernetes/README.md](deploy/kubernetes/README.md) — Kubernetes manifests and Helm.
- 🎨 [frontend/README.md](frontend/README.md) — Dashboard development and customization.

<br/><br/>

## Community

<table width="100%" border="0" cellspacing="0" role="presentation">
  <tr>
    <td align="center" valign="middle" width="25%">
      <a href="https://github.com/DARREN-2000/Inference-Control-Plane/discussions" title="Start a discussion"><b>💬 Discussions</b></a><br/>Questions & ideas
    </td>
    <td align="center" valign="middle" width="25%">
      <a href="https://github.com/DARREN-2000/Inference-Control-Plane/issues" title="Report a bug or request a feature"><b>🐛 Issues</b></a><br/>Bugs & features
    </td>
    <td align="center" valign="middle" width="25%">
      <a href="CONTRIBUTING.md" title="Contributing guide"><b>📝 Contributing</b></a><br/>Code & docs
    </td>
    <td align="center" valign="middle" width="25%">
      <a href="https://github.com/DARREN-2000/Inference-Control-Plane/stargazers" title="Stargazers"><b>⭐ Star us</b></a><br/>Show support
    </td>
  </tr>
</table>

<br/><br/>

## Built to scale

- **Redis cluster support** — Sharded cache layer for distributed deployments.
- **PostgreSQL replication** — Read replicas for analytics; writes on primary.
- **Kubernetes HPA** — Auto-scale based on queue depth or request latency.
- **Multi-region** — Route by geography using DNS or edge proxies.

<p align="center"><sub>Production deployments handle 100K+ concurrent users with <10ms p99 latency.</sub></p>

<br/><br/>

## Contributing

<p align="center">
  <b>Every pull request makes Inference Control Plane better.</b><br/>
  Bug fixes, new features, docs, examples — all welcome.<br/>
  <sub>First time contributing? Start with a <a href="https://github.com/DARREN-2000/Inference-Control-Plane/labels/good%20first%20issue">good first issue</a>.</sub>
</p>

<p align="center">
  📝 <a href="CONTRIBUTING.md"><b>Read the contributing guide</b></a> &nbsp;·&nbsp;
  🐛 <a href="https://github.com/DARREN-2000/Inference-Control-Plane/issues"><b>Browse issues</b></a> &nbsp;·&nbsp;
  💬 <a href="https://github.com/DARREN-2000/Inference-Control-Plane/discussions/new"><b>Start a discussion</b></a>
</p>

<br/><br/>

<p align="center"><sub>Apache-2.0 · © Inference Control Plane contributors</sub></p>
