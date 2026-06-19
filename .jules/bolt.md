## 2024-05-24 - Moved Cache Writing to Background Task
**Learning:** Writing to cache (like Redis) after generating a response is on the critical path of returning the data to the client if awaited directly. In FastAPI, `BackgroundTasks` provide a clean mechanism to offload I/O operations (like storing to a cache or logging to a database) without blocking the response latency.
**Action:** Always look for operations that don't need to be strictly completed *before* returning a response to the client (like updating caches, persisting usage logs, or sending non-critical events) and move them to asynchronous background tasks.

## 2024-05-25 - Share HTTP Client to Reduce Connection Overhead
**Learning:** Re-instantiating `httpx.AsyncClient` for every request incurs a high connection setup cost (TCP handshake, SSL negotiation). This significantly impacts latency when making frequent calls to the same host (e.g. LLM providers).
**Action:** Use a long-lived, shared HTTP client for outbound requests. Initialize the client at application startup and close it on application shutdown to maximize connection reuse.
