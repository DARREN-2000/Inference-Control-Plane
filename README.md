<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/banner-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="docs/assets/banner-light.svg">
    <img src="docs/assets/banner-light.svg" alt="Inference Control Plane - Enterprise LLM Gateway" width="100%"/>
  </picture>
  <br/>
  <h1>Inference Control Plane</h1>
  <p><b>The Enterprise-Grade Inference Control Plane for AI Traffic</b></p>

  <p>
    <a href="https://github.com/DARREN-2000/Inference-Control-Plane/actions"><img src="https://img.shields.io/github/actions/workflow/status/DARREN-2000/Inference-Control-Plane/ci.yml?style=for-the-badge&logo=github" alt="Build Status"/></a>
    <a href="https://hub.docker.com/r/darren-2000/inference-control-plane"><img src="https://img.shields.io/docker/pulls/darren-2000/inference-control-plane?style=for-the-badge&logo=docker" alt="Docker Pulls"/></a>
    <a href="https://github.com/DARREN-2000/Inference-Control-Plane/blob/main/LICENSE"><img src="https://img.shields.io/github/license/DARREN-2000/Inference-Control-Plane?style=for-the-badge" alt="License: Apache 2.0"/></a>
    <a href="https://github.com/DARREN-2000/Inference-Control-Plane/releases"><img src="https://img.shields.io/github/v/release/DARREN-2000/Inference-Control-Plane?style=for-the-badge" alt="Release"/></a>
  </p>
</div>

<br/>

## 📖 Project Overview

**Inference Control Plane** is a high-performance, enterprise-ready LLM API gateway and inference control plane. It acts as a unified proxy between your applications and various foundational models (OpenAI, Anthropic, Azure, local deployments), providing essential capabilities like intelligent routing, semantic caching, fallback mechanisms, rate limiting, and comprehensive observability.

Designed for massive scale, Inference Control Plane processes thousands of tokens per second with sub-millisecond overhead, empowering engineering teams to build robust, AI-driven products without worrying about provider outages, quota limits, or uncontrolled spend.

## 🔭 Product Vision

Our vision is to commoditize the AI infrastructure layer. As AI models become ubiquitous, the differentiation will lie in how reliably, securely, and efficiently they are served. Inference Control Plane aims to be the standard open-source control plane for all AI inference traffic—just as Nginx or Envoy became standard for HTTP traffic. We provide the tools for platform engineering teams to maintain total control over their AI consumption.

## ✨ Key Features

- 🚀 **Unified API:** Drop-in replacement for OpenAI SDKs. Write code once, route to any provider.
- 🧠 **Intelligent Routing & Fallbacks:** Automatically reroute traffic if a primary model degrades or rate-limits.
- 💾 **Semantic & Exact Caching:** Slash latency and cost by caching identical or semantically similar queries at the edge.
- 🚦 **Advanced Rate Limiting:** Enforce token and request quotas per-tenant, per-user, or per-model.
- 🛡️ **Enterprise Security:** Built-in secret management, PII redaction, and granular access control (RBAC).
- 📊 **Deep Observability:** Prometheus metrics, OpenTelemetry tracing, and rich usage logs (cost & token tracking).
- ⚡ **High Performance:** Asynchronous Python (FastAPI/asyncpg) back-end capable of 10k+ RPM per node.

## 🏛️ Architecture Overview

Inference Control Plane sits securely within your VPC, intercepting outbound LLM requests.

1. **Client Request:** Your app calls Inference Control Plane using standard OpenAI SDKs.
2. **Auth & Quota:** Inference Control Plane validates the API key and checks distributed Redis rate limits.
3. **Cache Lookup:** In-memory or Redis caches are queried for a matching response.
4. **Provider Routing:** If a cache miss occurs, the request is dynamically routed to the best provider based on cost, latency, or availability policies.
5. **Response Streaming & Logging:** The response is streamed back to the client while usage metrics (tokens, cost, latency) are asynchronously flushed to PostgreSQL.

*For a detailed deep dive, see our [Architecture Guide](docs/architecture.md).*

## 🤔 Why This Exists

As organizations scale their AI initiatives, they encounter several pain points:
1. **Vendor Lock-in:** Hardcoding integrations to specific providers (e.g., OpenAI, Anthropic).
2. **Reliability Issues:** Provider outages breaking critical application flows.
3. **Unpredictable Costs:** Lack of granular visibility and control over token usage per team.
4. **Latency:** Unnecessary roundtrips for repeated queries.

Inference Control Plane solves these by providing a resilient, transparent middleware layer that abstracts away provider complexities.

## ⚖️ Comparison With Alternatives

| Feature | Inference Control Plane | LiteLLM | Portkey | Kong AI Gateway |
|---------|:---:|:---:|:---:|:---:|
| **Open Source** | ✅ | ✅ | ❌ | ✅ |
| **Enterprise RBAC** | ✅ | ❌ | ✅ | ✅ |
| **Semantic Caching** | ✅ | ❌ | ✅ | ❌ |
| **Native Dashboard**| ✅ | ✅ | ✅ | ❌ |
| **Python Native** | ✅ | ✅ | ❌ | ❌ |
| **Streaming Support**| ✅ | ✅ | ✅ | ✅ |

## 📸 Screenshots & GIF Demonstrations

*(Note: Add path to actual screenshots/GIFs here once assets are generated or populated in `docs/assets/`)*

<div align="center">
  <img src="docs/assets/dashboard-preview.png" alt="Dashboard Preview" width="80%"/>
  <p><i>The Inference Control Plane Analytics Dashboard</i></p>
</div>

## 🛠️ Technology Stack

- **Backend:** Python 3.12+, FastAPI, SQLAlchemy, asyncpg, Alembic
- **Databases:** PostgreSQL (Relational Data & Logs), Redis (Caching & Rate Limiting)
- **Frontend:** Next.js 15, React 19, Tailwind CSS v4, Framer Motion
- **Observability:** Prometheus, OpenTelemetry
- **Infrastructure:** Docker, Kubernetes (Helm), GitHub Actions

## 📂 Project Structure

```
.
├── src/inference_control_plane/ # Core backend application
├── frontend/                     # Next.js administrative dashboard
├── website/                      # Static marketing and product website
├── docs/                         # Comprehensive documentation
├── deploy/                       # Docker Compose and Kubernetes manifests
├── alembic/                      # Database migrations
└── tests/                        # Pytest test suite
```

## 🚀 Installation & Quick Start

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.12+ (for local development)
- Node.js 20+ & pnpm (for frontend development)
- `uv` package manager

### 2. Docker Quick Start

The fastest way to get Inference Control Plane running is via Docker Compose:

```bash
# Clone the repository
git clone https://github.com/DARREN-2000/Inference-Control-Plane.git
cd Inference-Control-Plane

# Start the stack (API, Dashboard, Postgres, Redis, Prometheus)
docker-compose up -d

# Check the status
docker-compose ps
```

Inference Control Plane API is now available at `http://localhost:8000` and the Dashboard at `http://localhost:3000`.

## ⚙️ Configuration & Environment Variables

Inference Control Plane is heavily configurable via environment variables. See `.env.example` for all options.

**Core Configuration:**
```bash
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
REDIS_URL=redis://:pass@host:6379/0
DEFAULT_API_KEY=sk-inference-control-plane-your-secret-key
```

**Provider Configuration:**
```bash
LLM_PROVIDER_ORDER=openai,anthropic,azure
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
```

## 🐳 Docker Support

Official Docker images are available on GHCR:
- `ghcr.io/darren-2000/inference-control-plane-api:latest`
- `ghcr.io/darren-2000/inference-control-plane-dashboard:latest`

Use the provided `Dockerfile` to build custom images or inject proprietary certificates.

## 💻 Running Locally (Development)

### Backend
```bash
uv sync --extra dev
cp .env.example .env
# Edit .env with your local Postgres/Redis details
alembic upgrade head
uvicorn inference_control_plane.main:app --app-dir src --reload
```

### Frontend
```bash
cd frontend
pnpm install
cp .env.example .env.local
pnpm run dev
```

## ☁️ Production Deployment

Inference Control Plane is designed to be deployed on Kubernetes. Manifests are provided in `deploy/kubernetes`.

```bash
kubectl apply -k deploy/kubernetes/base/
```
Please consult the [Deployment Guide](docs/deployment.md) for High Availability (HA) setups, multi-region routing, and database connection pooling (PgBouncer).

## 💡 Usage Examples

### API Examples

Inference Control Plane exposes an API compatible with OpenAI's format. Point your existing applications to Inference Control Plane by overriding the `base_url`.

**cURL:**
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer sk-inference-control-plane-your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Explain quantum computing."}]
  }'
```

**Python (OpenAI SDK):**
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="http://localhost:8000/v1",
    api_key="sk-inference-control-plane-your-secret-key"
)

response = await client.chat.completions.create(
    model="claude-3-5-sonnet", # Will route to Anthropic automatically
    messages=[{"role": "user", "content": "Hello, world!"}]
)
```

### CLI Examples

*(Inference Control Plane CLI documentation available in [CLI Reference](docs/cli-reference.md))*
```bash
# Generate a new API key for a tenant
inference_control_plane keys create --tenant-id org_123 --limit 1000/min

# View real-time traffic logs
inference_control_plane logs tail --model gpt-4
```

## ⚡ Performance & Benchmarks

Inference Control Plane is built for speed. By utilizing connection pooling (`httpx.AsyncClient`, `asyncpg`) and Redis pipelining, the proxy overhead is negligible.

- **P99 Proxy Overhead:** `< 2.5ms`
- **Cache Hit Latency:** `< 5ms`
- **Throughput:** `~10,000 RPM` per worker instance (2vCPU, 4GB RAM)

*Benchmarks conducted on AWS c6g.large instances using `wrk`. See [Performance Tuning](docs/performance-tuning.md).*

## 🔒 Security

Security is critical when handling sensitive AI data.
- **Data Privacy:** Payloads are not logged by default. Enable `LOG_PAYLOADS=true` only for debugging.
- **RBAC:** Strict access controls for admin vs. tenant-level API keys.
- **Vulnerability Reporting:** Please report issues to `security@inference_control_plane.ai`. Read our [Security Policy](SECURITY.md).

## ⚠️ Limitations

- Multi-modal caching (images, audio) is currently highly experimental.
- Semantic cache requires an active embedding provider (e.g., text-embedding-3-small).

## 🛣️ Roadmap

- [ ] **Q3 2024:** Advanced Semantic Caching via Qdrant integration.
- [ ] **Q4 2024:** Custom Model Load Balancing (Round Robin, Least Connections).
- [ ] **Q1 2025:** Native support for Google Gemini & Vertex AI.

## 🤝 Contributing

We welcome contributions from the community! Whether it's a bug fix, new feature, or documentation update, your help is appreciated.

Please read our [Contributing Guide](CONTRIBUTING.md) to get started.

## 📄 License

Inference Control Plane is open-source software licensed under the [Apache 2.0 License](LICENSE).

## 🙏 Acknowledgements

- The [FastAPI](https://fastapi.tiangolo.com/) community for an incredible web framework.
- [Next.js](https://nextjs.org/) for powering our frontend dashboard.

## 💬 Support & FAQ

- **Need Help?** Open a [GitHub Discussion](https://github.com/DARREN-2000/Inference-Control-Plane/discussions).
- **Found a Bug?** Open a [GitHub Issue](https://github.com/DARREN-2000/Inference-Control-Plane/issues).
- **FAQ:** See our [FAQ Documentation](docs/faq.md).
