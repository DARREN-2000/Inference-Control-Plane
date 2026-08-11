## 2024-06-26 - Reuse HTTPX Client for Connection Pooling

**Learning:** Found that `httpx.AsyncClient()` was being instantiated on every outbound API call in `services/llm_client.py`. In an application handling inference traffic, establishing a new TCP/TLS connection for every LLM request creates significant overhead.
**Action:** Implemented a shared, long-lived `httpx.AsyncClient` initialized during the FastAPI app lifecycle (lifespan) to maintain connection pools and prevent TLS handshake latency on every request.

## 2024-06-26 - Reuse HTTPX Client for Connection Pooling

**Learning:** Found that `httpx.AsyncClient()` was being instantiated on every outbound API call in `services/llm_client.py`. In an application handling inference traffic, establishing a new TCP/TLS connection for every LLM request creates significant overhead.
**Action:** Implemented a shared, long-lived `httpx.AsyncClient` initialized during the FastAPI app lifecycle (lifespan) to maintain connection pools and prevent TLS handshake latency on every request.
