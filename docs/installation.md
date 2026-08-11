# Installation Guide

This guide covers the various ways to install and run Inference Control Plane depending on your use case, from local development to production deployment.

## Method 1: Docker Compose (Recommended for Quick Start)

The Docker Compose method is the fastest way to get a fully featured Inference Control Plane environment, including the required PostgreSQL and Redis dependencies.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/DARREN-2000/Inference-Control-Plane.git
   cd Inference-Control-Plane
   ```

2. Create your environment configuration:

   ```bash
   cp .env.example .env
   # Edit .env to add your LLM provider API keys (e.g., OPENAI_API_KEY)
   ```

3. Start the stack:

   ```bash
   docker-compose up -d
   ```

4. Verify installation:
   ```bash
   curl http://localhost:8000/health/live
   # Expected output: {"status": "ok"}
   ```

## Method 2: Local Python Development

If you want to contribute to the Inference Control Plane backend or run it natively for debugging, you can install it using `uv`, the fast Python package installer.

### Prerequisites

- Python 3.12+
- PostgreSQL server (running locally or remote)
- Redis server (running locally or remote)
- `uv` (Install via `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/DARREN-2000/Inference-Control-Plane.git
   cd Inference-Control-Plane
   ```

2. Sync dependencies:

   ```bash
   uv sync --extra dev
   ```

3. Configure the environment:

   ```bash
   cp .env.example .env
   ```

   Open `.env` and ensure `DATABASE_URL` and `REDIS_URL` point to your running Postgres and Redis instances.

4. Run Database Migrations:
   Inference Control Plane uses Alembic to manage database schema. Initialize the tables:

   ```bash
   alembic upgrade head
   ```

5. Start the API server:
   ```bash
   uvicorn inference_control_plane.main:app --app-dir src --reload --host 0.0.0.0 --port 8000
   ```

## Method 3: Kubernetes (Helm / Kustomize)

For production deployments, Inference Control Plane provides Kubernetes manifests.

### Prerequisites

- A running Kubernetes cluster
- `kubectl` configured

### Steps

We provide base Kustomize manifests in `deploy/kubernetes/base`.

1. Review the base configuration:

   ```bash
   cat deploy/kubernetes/base/deployment.yaml
   ```

2. Apply the configuration:
   ```bash
   kubectl apply -k deploy/kubernetes/base/
   ```

_For advanced Kubernetes configurations including High Availability, Ingress, and Autoscaling, see the [Deployment Guide](deployment.md)._

## Method 4: Frontend Development

If you only want to work on the Inference Control Plane Next.js Dashboard:

### Prerequisites

- Node.js 20+
- `pnpm`

### Steps

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   pnpm install
   ```

3. Start the development server:
   ```bash
   pnpm run dev
   ```
   The dashboard will be available at `http://localhost:3000`. Ensure the backend API is running concurrently for data to load properly.
