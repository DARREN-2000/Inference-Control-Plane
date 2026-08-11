# Performance Tuning

Inference Control Plane is built on an asynchronous architecture capable of high throughput, but out-of-the-box defaults may need tuning for massive scale.

## 1. Connection Pooling (HTTPX)

Inference Control Plane uses `httpx.AsyncClient` to make requests to LLM providers.

- **The Optimization:** The client is instantiated once during the FastAPI application lifecycle (`lifespan`) and shared across all requests. This prevents the TCP/TLS handshake overhead (which can take 50-100ms) on every single API call.
- **Tuning:** If you are hitting thousands of requests per second, you may need to increase the `httpx.Limits(max_connections=...)` internally in the codebase.

## 2. Uvicorn Workers

By default, running `uvicorn` starts a single worker process. Because Python has a Global Interpreter Lock (GIL), a single process can only utilize one CPU core.

For production, you must run multiple workers.
**Docker Configuration:**
The provided Dockerfile uses standard Uvicorn. To utilize multiple cores, pass the `--workers` flag based on the core count of your container/node.

```bash
uvicorn inference_control_plane.main:app --host 0.0.0.0 --port 8000 --workers 4
```

_Rule of Thumb: Set workers to `(Number of CPU Cores * 2) + 1`._

## 3. Database AsyncPG Limits

FastAPI uses `asyncpg` to communicate with Postgres asynchronously.
If your API starts returning `500` errors related to timeouts acquiring a connection, your worker threads are starved for database connections.

**Tuning Variables:**

- `DATABASE_POOL_SIZE`: Base number of connections per worker.
- `DATABASE_MAX_OVERFLOW`: Extra connections allowed during spikes.

_Warning: If you have 4 Uvicorn workers and `DATABASE_POOL_SIZE=20`, your pod will open 80 connections to Postgres. If you have 10 pods, that is 800 connections. Standard Postgres starts failing around 100-200. You **must** use PgBouncer in this scenario._

## 4. Redis Pipelining

Rate limiting in Inference Control Plane uses Redis Lua scripts to ensure atomicity and speed.
If you notice Redis latency spiking during high traffic:

- Ensure Redis is deployed in the same VPC/Region as your API pods to minimize network hops.
- Keep `CACHE_ENABLED=true` even if you have low hit rates, as the lookup cost (<<1ms) is vastly outweighed by the latency saved on a hit.

## 5. Avoiding Premature Optimization

Avoid altering the core routing logic to shave microseconds off the proxy execution time. The overwhelming majority of request latency (99%+) comes from the LLM provider generation time (often 1000ms - 5000ms), not the Inference Control Plane proxy overhead (< 3ms). Focus your optimization efforts on caching strategies and intelligent routing policies.
