<div align="center">

  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/readme-hero-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="docs/assets/readme-hero-light.svg">
    <img alt="Inference Control Plane Hero Banner" src="docs/assets/readme-hero-light.svg" width="100%">
  </picture>

  <h1>Inference Control Plane</h1>
  <p><b>The Enterprise LLM Gateway for Production AI Infrastructure</b></p>

  <p>
    <a href="https://github.com/DARREN-2000/Inference-Control-Plane/actions/workflows/ci.yml">
      <img src="https://github.com/DARREN-2000/Inference-Control-Plane/actions/workflows/ci.yml/badge.svg" alt="CI/CD Status">
    </a>
    <a href="https://github.com/DARREN-2000/Inference-Control-Plane/releases">
      <img src="https://img.shields.io/github/v/release/DARREN-2000/Inference-Control-Plane" alt="Latest Release">
    </a>
    <a href="https://hub.docker.com/r/darren2000/inference-control-plane-api">
      <img src="https://img.shields.io/docker/pulls/darren2000/inference-control-plane-api" alt="Docker Pulls">
    </a>
    <a href="LICENSE">
      <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License">
    </a>
  </p>

  <p>
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-architecture">Architecture</a> •
    <a href="#-key-features">Features</a> •
    <a href="docs/api-reference.md">API Reference</a> •
    <a href="docs/">Documentation</a>
  </p>
</div>

---

## ⚡ What is Inference Control Plane?

Inference Control Plane is a high-performance, asynchronous LLM API gateway engineered in Python (FastAPI/asyncpg). It sits within your VPC, intercepting outbound requests to models like OpenAI, Anthropic, or Azure, and provides a unified layer for intelligent routing, semantic caching, rate limiting, and observability.

Designed for scale, it handles thousands of concurrent streaming connections with **sub-millisecond proxy overhead**, enabling engineering teams to decouple their applications from specific AI vendors and maintain granular control over their API usage and costs.

---

## ✨ Key Features

- **🚀 Unified API:** Drop-in replacement for OpenAI SDKs. Write code once, route to any provider.
- **🧠 Intelligent Routing:** Dynamically route traffic based on performance policies or automatically fallback if a primary model degrades.
- **💾 Semantic & Exact Caching:** Slash latency and costs by caching identical queries in Redis edge nodes.
- **🚦 Advanced Rate Limiting:** Enforce token and request quotas via Redis sliding windows per-tenant, per-user, or per-model.
- **🛡️ Enterprise Security:** Built-in secret management, strict RBAC, and payload redaction capabilities to keep data secure.
- **📊 Deep Observability:** Integrated Prometheus metrics, OpenTelemetry tracing, and detailed usage logs stored in PostgreSQL.
- **⚡ High Performance:** Engineered for asynchronous throughput handling 10k+ RPM per node.

---

## 🏗 Architecture Overview

Inference Control Plane is built around a non-blocking asynchronous pipeline designed to minimize TTFT (Time To First Token) during generation.

<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/readme-system-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="docs/assets/readme-system-light.svg">
    <img alt="System Architecture Diagram" src="docs/assets/readme-system-light.svg" width="90%">
  </picture>
</div>

### Component Responsibilities

1. **Proxy API (FastAPI):** Handles incoming client requests, manages Redis rate-limit checks, hashes prompts for cache lookups, and orchestrates asynchronous provider calls and SSE streaming.
2. **Transactional DB (PostgreSQL):** The source of truth for tenants, api keys, routing rules, and comprehensive usage logs (flushed asynchronously).
3. **In-Memory Store (Redis):** Provides ultra-fast key validation, sliding-window rate limiting, and exact-match prompt caching.
4. **Dashboard (Next.js):** An administrative UI serving dynamic metrics and error tracking directly from the Proxy API.

_For a detailed look at the internal data flows, see our [Architecture Deep Dive](docs/architecture.md)._

---

## 🚀 Quick Start

The fastest way to run Inference Control Plane locally is via Docker Compose.

### 1. Start the Stack

```bash
git clone https://github.com/DARREN-2000/Inference-Control-Plane.git
cd Inference-Control-Plane
docker-compose up -d
```

This spins up the FastAPI Gateway, Next.js Dashboard, PostgreSQL, Redis, and Prometheus.

### 2. Make an Inference Request

Inference Control Plane is fully compatible with OpenAI SDKs. You only need to change the `base_url`.

**cURL**

```bash
curl -X POST http://localhost:8000/v1/generate \
  -H "Authorization: Bearer sk-inference-control-plane-your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Explain quantum mechanics briefly."}],
    "inference_control_plane_fallback_models": ["claude-3-5-sonnet"]
  }'
```

**Python**

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(base_url="http://localhost:8000/v1", api_key="sk-inference-control-plane-your-secret-key")

response = await client.chat.completions.create(
    model="claude-3-5-sonnet",  # Inference Control Plane handles routing to Anthropic
    messages=[{"role": "user", "content": "Hello world!"}],
)
print(response.choices[0].message.content)
```

---

## 🛠 Technology Stack

- **Core Proxy Engine:** Python 3.12+, FastAPI, Uvicorn, httpx (Connection Pooling)
- **Data Persistence:** PostgreSQL, asyncpg, SQLAlchemy, Alembic
- **Caching & Rate Limits:** Redis, Lua Scripts
- **Administrative UI:** Next.js 15, React 19, Tailwind CSS v4, shadcn/ui
- **Observability:** Prometheus, OpenTelemetry
- **Orchestration:** Docker, Kubernetes (Kustomize/Helm), Argo Rollouts

---

## 📂 Project Structure

```text
.
├── src/inference_control_plane/  # Core async Python backend application
├── frontend/                     # Next.js administrative dashboard (React/Tailwind)
├── website/                      # Static marketing/documentation site
├── docs/                         # Comprehensive project documentation
├── deploy/                       # K8s manifests, Helm charts, Docker compose
├── alembic/                      # Database migrations
└── tests/                        # Comprehensive Pytest suite
```

---

## ☁️ Production Deployment

Inference Control Plane is fully containerized and intended to be deployed horizontally in Kubernetes environments.

### Using Kubernetes (Kustomize)

```bash
kubectl apply -k deploy/kubernetes/base/
```

### Using Helm

```bash
helm install inference-control-plane ./deploy/helm/inference-control-plane
```

_For highly-available multi-region setups and connection pooler (PgBouncer) configurations, consult the [Deployment Guide](docs/deployment.md)._

---

## ⚡ Performance Characteristics

Inference Control Plane is explicitly designed to not be the bottleneck in your AI workloads.

- **P99 Gateway Overhead:** `< 2.5ms`
- **Cache Hit Latency:** `< 5ms`
- **Throughput:** Capable of ~10,000 RPM per instance (2vCPU, 4GB RAM)

_Note: Benchmarks conducted via `wrk` on AWS c6g.large instances simulating concurrent SSE stream handling._

---

## 📖 Comprehensive Documentation

Our documentation aims to provide everything you need to run this system at scale:

- [API Reference](docs/api-reference.md)
- [Architecture Deep Dive](docs/architecture.md)
- [Configuration Guide](docs/configuration.md)
- [Deployment & Operations](docs/deployment.md)
- [Performance Tuning](docs/performance-tuning.md)

---

## 🤝 Contributing & Community

We believe in open source. Whether it's adding new features, improving documentation, or identifying bugs, we welcome community contributions.

- Review the [Contributing Guidelines](CONTRIBUTING.md) to get your local environment running (`uv sync`, `pnpm dev`, etc).
- Check the [Roadmap](ROADMAP.md) to see where we're heading.
- Need help? Start a [GitHub Discussion](https://github.com/DARREN-2000/Inference-Control-Plane/discussions).

---

## 📜 License

Inference Control Plane is released under the [Apache 2.0 License](LICENSE).
