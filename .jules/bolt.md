## 2024-05-24 - Moved Cache Writing to Background Task
**Learning:** Writing to cache (like Redis) after generating a response is on the critical path of returning the data to the client if awaited directly. In FastAPI, `BackgroundTasks` provide a clean mechanism to offload I/O operations (like storing to a cache or logging to a database) without blocking the response latency.
**Action:** Always look for operations that don't need to be strictly completed *before* returning a response to the client (like updating caches, persisting usage logs, or sending non-critical events) and move them to asynchronous background tasks.
## 2024-06-18 - Concurrent Redis lookups
**Learning:** Sequential network IO requests (like Redis calls) on the critical request path create unnecessary cumulative latency, especially with un-batched operations.
**Action:** Use `asyncio.gather` to perform independent async operations (like checking API key and user rate limits) concurrently.
## 2025-02-12 - Reusing httpx.AsyncClient for external API calls
**Learning:** Creating a new `httpx.AsyncClient` inside a function body for every outbound API request destroys the ability to connection pool and requires a full TCP and TLS handshake every time. This creates enormous, redundant latency on the critical path of an application.
**Action:** Always maintain long-lived `httpx.AsyncClient` instances globally (or within class instances) initialized during application startup and reuse them for consecutive requests to the same endpoints to capitalize on connection pooling.
