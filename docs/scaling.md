# Scaling Model

Inference Control Plane is designed to handle petabyte-scale API traffic. This document explains how to scale the control plane components.

## 1. Scaling the Proxy API (Compute)

The Inference Control Plane Proxy is inherently stateless. All state is offloaded to Redis and PostgreSQL. Therefore, scaling the API is as simple as adding more pods.

### Horizontal Pod Autoscaling (HPA)

We strongly recommend configuring an HPA based on **CPU utilization**. Because Inference Control Plane is asynchronous (FastAPI/asyncio), it is highly CPU-bound rather than memory-bound during heavy streaming workloads.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: inference_control_plane-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: inference_control_plane-api
  minReplicas: 3
  maxReplicas: 50
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

_Note: Ensure your `Deployment` has appropriate CPU `requests` and `limits` defined for the HPA to function correctly._

## 2. Scaling the Database (PostgreSQL)

While Inference Control Plane's reads from Postgres are minimal (mostly loading configuration at startup), its writes are extremely heavy. **Every single LLM request results in a database insert** for usage logging.

### Connection Pooling (PgBouncer)

As you scale API pods horizontally, the number of open connections to Postgres will spike.

1. Use `asyncpg` built-in pooling (`DATABASE_POOL_SIZE=20`).
2. If you have > 20 pods, you **must** use an external connection pooler like PgBouncer in front of your PostgreSQL instance in `transaction` pooling mode.

### Database Partitioning

Over time, the `usage_logs` table will grow massive. For enterprise deployments, we recommend:

1. Setting up table partitioning by date (e.g., monthly partitions) on the `usage_logs` table.
2. Running a cron job (via the CLI tool) to prune logs older than 90 days.

## 3. Scaling Redis

Redis is heavily utilized for:

- API Key validation (Read-heavy)
- Rate limiting (Write-heavy, Lua scripts)
- Semantic/Exact caching (Read/Write)

### Redis Clustering

For deployments exceeding 5,000 Requests Per Minute (RPM), a single Redis node may become a bottleneck due to the single-threaded nature of Lua script execution used in rate limiting.

- Deploy a Redis Cluster.
- Configure Inference Control Plane to use `redis-py-cluster` (supported via standard connection strings).

## 4. Multi-Region Scaling

To reduce latency for a global user base, Inference Control Plane supports Multi-Region deployments.

- Deploy API pods and a local Redis cluster in Region A (e.g., US-East) and Region B (e.g., EU-West).
- Use a Global Server Load Balancer (GSLB) to route user traffic to the nearest region.
- Point both regions to a central PostgreSQL database. Since writes are performed asynchronously, the cross-region database latency will not impact the user's TTFT (Time To First Token).
