## 2024-05-24 - Moved Cache Writing to Background Task
**Learning:** Writing to cache (like Redis) after generating a response is on the critical path of returning the data to the client if awaited directly. In FastAPI, `BackgroundTasks` provide a clean mechanism to offload I/O operations (like storing to a cache or logging to a database) without blocking the response latency.
**Action:** Always look for operations that don't need to be strictly completed *before* returning a response to the client (like updating caches, persisting usage logs, or sending non-critical events) and move them to asynchronous background tasks.
## 2024-06-18 - Concurrent Redis lookups
**Learning:** Sequential network IO requests (like Redis calls) on the critical request path create unnecessary cumulative latency, especially with un-batched operations.
**Action:** Use `asyncio.gather` to perform independent async operations (like checking API key and user rate limits) concurrently.
## 2024-06-21 - Optimize HTTP client connection pooling
**Learning:** Creating a new `httpx.AsyncClient` inside every incoming request (e.g., `async with httpx.AsyncClient() as client:`) defeats HTTP/1.1 keep-alive connection pooling. This causes severe performance degradation due to repeated TCP connection setups and expensive TLS handshakes on every outbound request to LLM providers.
**Action:** Always instantiate a shared `httpx.AsyncClient` tied to the application lifecycle (e.g. FastAPI `lifespan`) and reuse it across requests. Ensure the client is properly closed during app shutdown to prevent resource leaks.
