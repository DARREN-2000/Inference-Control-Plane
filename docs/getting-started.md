# Getting Started

Welcome to Inference Control Plane! This guide will help you get your first Inference Control Plane proxy up and running in under 5 minutes.

Inference Control Plane acts as a single endpoint for all your LLM traffic, giving you observability, caching, and failovers without changing how you write code.

## Prerequisites

Before starting, ensure you have:
1. **Docker and Docker Compose** installed.
2. At least one **LLM Provider API Key** (e.g., an OpenAI API key).

## 1. Start the Control Plane

The easiest way to start Inference Control Plane is using the provided Docker Compose stack, which includes the API, a Postgres database for logs, Redis for caching/rate-limiting, and Prometheus for metrics.

```bash
# Clone the repo
git clone https://github.com/DARREN-2000/Inference-Control-Plane.git
cd Inference-Control-Plane

# Start the services in detached mode
docker-compose up -d
```

Verify that all containers are running:
```bash
docker-compose ps
```

You should see `inference-api`, `postgres`, `redis`, and `prometheus` running successfully.

## 2. Configure Your Environment

By default, Inference Control Plane loads configuration from `.env`. While `docker-compose.yml` provides sensible defaults, you need to provide your actual LLM API keys.

Copy the example environment file:
```bash
cp .env.example .env
```

Open `.env` and add your provider keys. For example, to enable OpenAI:
```env
OPENAI_API_KEY=sk-your-openai-api-key
```

*Note: If you update `.env` while Docker is running, you must restart the API container:*
```bash
docker-compose restart inference-api
```

## 3. Make Your First Request

Inference Control Plane exposes a unified API that matches the standard OpenAI `/v1/chat/completions` format.

Instead of sending requests directly to OpenAI, you send them to Inference Control Plane (`http://localhost:8000/v1`). Inference Control Plane requires its own API key for authentication, which defaults to `replace-me` for local development.

```bash
curl -X POST http://localhost:8000/v1/generate \
  -H "Authorization: Bearer replace-me" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "What is the capital of France?"
      }
    ]
  }'
```

You should receive a standard ChatCompletion response. Behind the scenes, Inference Control Plane authenticated your request, checked rate limits, routed the request to OpenAI, and logged the usage metrics.

## 4. Test Semantic Caching

Run the exact same `curl` command again.

You should notice the response is almost instantaneous. Because the exact same prompt was sent, Inference Control Plane served the response directly from its Redis cache, saving you both latency and token costs.

## 5. View Your Usage Dashboard

Inference Control Plane includes a built-in admin dashboard (served by Next.js) to visualize traffic, manage keys, and view logs.

By default, the dashboard is available at:
**http://localhost:3000**

*(If the dashboard container isn't running in your compose file, you can start it manually from the `frontend/` directory using `npm run dev`).*

## Next Steps

Now that you have Inference Control Plane running, explore how to productionize and scale it:

- 📚 **[Core Concepts](concepts.md)**: Learn about Tenants, Policies, and Routing.
- ⚙️ **[Configuration](configuration.md)**: Explore all available environment variables.
- 🚀 **[Deployment](deployment.md)**: Deploy Inference Control Plane to Kubernetes or Render.
- 👨‍💻 **[SDK Guide](sdk-guide.md)**: Integrate Inference Control Plane with Python and TypeScript SDKs.
