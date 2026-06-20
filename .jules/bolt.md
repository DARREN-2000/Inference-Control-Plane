## 2024-05-24 - Moved Cache Writing to Background Task
**Learning:** Writing to cache (like Redis) after generating a response is on the critical path of returning the data to the client if awaited directly. In FastAPI, `BackgroundTasks` provide a clean mechanism to offload I/O operations (like storing to a cache or logging to a database) without blocking the response latency.
**Action:** Always look for operations that don't need to be strictly completed *before* returning a response to the client (like updating caches, persisting usage logs, or sending non-critical events) and move them to asynchronous background tasks.
## 2024-06-18 - Concurrent Redis lookups
**Learning:** Sequential network IO requests (like Redis calls) on the critical request path create unnecessary cumulative latency, especially with un-batched operations.
**Action:** Use `asyncio.gather` to perform independent async operations (like checking API key and user rate limits) concurrently.
## 2024-06-20 - Connection pooling for outgoing API calls
**Learning:** Initializing a new HTTP client (`httpx.AsyncClient`) for every outbound request inside an endpoint or a service function prevents connection pooling and introduces TCP/TLS handshake overhead on every call, heavily impacting the latency.
**Action:** Always utilize a shared, long-lived HTTP client initialized during the FastAPI application lifecycle (lifespan) to maintain connection pools across requests.
