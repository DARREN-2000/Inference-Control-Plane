# Deployment Guide

This guide covers deploying Inference Control Plane for production workloads using Kubernetes, which is the recommended orchestration platform for high availability and scale.

## Prerequisites

- A Kubernetes cluster (EKS, GKE, AKS, or bare metal).
- Helm installed locally.
- Access to a production-grade PostgreSQL database (e.g., AWS RDS, Google Cloud SQL).
- Access to a production-grade Redis cluster (e.g., AWS ElastiCache, Redis Enterprise).

## 1. Database Setup

Before deploying the Inference Control Plane pods, you must provision your stateful infrastructure.
**Do not run PostgreSQL and Redis inside Kubernetes for production unless you have a dedicated DBRE team.**

1. Provision PostgreSQL (version 15+).
2. Provision Redis (version 7+).
3. Secure the credentials.

## 2. Using the Kubernetes Manifests

We provide base manifests in `deploy/kubernetes/base`. We recommend using Kustomize to patch these base resources for your specific environment.

### Secrets Management

Never commit API keys or database passwords to version control. Create a Kubernetes Secret manually or via a tool like External Secrets Operator.

```bash
kubectl create secret generic inference_control_plane-secrets \
  --from-literal=DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db" \
  --from-literal=REDIS_URL="redis://:pass@host:6379/0" \
  --from-literal=OPENAI_API_KEY="sk-..." \
  --from-literal=DEFAULT_API_KEY="sk-inference-control-plane-admin-key"
```

### Applying the Base Manifests

```bash
kubectl apply -k deploy/kubernetes/base/
```

This will create:
- A `Deployment` for the Inference Control Plane API.
- A `Service` to expose the API.
- A `ConfigMap` for non-sensitive environment variables.

### Database Migrations in Kubernetes

Alembic migrations must be run before the API pods start. The standard way to handle this is via an Init Container on the API Deployment, or a pre-install Helm hook/Kubernetes Job.

```yaml
# Example Init Container snippet
initContainers:
  - name: run-migrations
    image: ghcr.io/darren-2000/inference-control-plane-api:latest
    command: ["alembic", "upgrade", "head"]
    envFrom:
      - secretRef:
          name: inference_control_plane-secrets
```

## 3. Ingress and SSL

Inference Control Plane must be placed behind a Reverse Proxy (e.g., NGINX Ingress Controller, AWS ALB) that terminates SSL.

Ensure your Ingress controller is configured to support **Server-Sent Events (SSE)**.
- For NGINX Ingress, you may need to add annotations to disable buffering:
  ```yaml
  nginx.ingress.kubernetes.io/proxy-buffering: "off"
  ```

## 4. Deploying the Dashboard

The Next.js dashboard is built as a static export or standalone Node.js server.

If running the Docker container `ghcr.io/darren-2000/inference-control-plane-dashboard`:
1. Ensure the `NEXT_PUBLIC_API_BASE_URL` environment variable points to the public URL of your Inference Control Plane API.
2. Deploy the dashboard container using a standard Deployment and Service.
