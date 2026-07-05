# Project Internals & Execution Flow

This document provides a deep dive into the internal mechanics of the Inference Control Plane gateway. Understanding these internals is essential for debugging, performance tuning, and contributing to the core repository.

## Execution Pipeline

The core application is an asynchronous FastAPI web service. Every inference request follows a highly optimized execution pipeline designed to minimize blocking operations.

### Request Flow Diagram

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI as API Router (FastAPI)
    participant Auth as Security (Depends)
    participant Redis as Redis (Rate Limiter / Cache)
    participant Engine as Inference Service
    participant ClientHTTP as httpx.AsyncClient
    participant Provider as LLM Provider
    participant Background as Background Tasks (Postgres)

    Client->>FastAPI: POST /v1/generate

    rect rgb(240, 240, 240)
        Note over FastAPI,Auth: 1. Dependency Injection Phase
        FastAPI->>Auth: get_auth_context()
        Auth->>Redis: Check API Key validity
        Redis-->>Auth: Valid (Tenant ID, Role)
        Auth-->>FastAPI: AuthContext injected
    end

    rect rgb(230, 245, 255)
        Note over FastAPI,Redis: 2. Pre-flight Checks Phase
        FastAPI->>Engine: handle_generate_request()
        Engine->>Redis: Atomic Increment (Sliding Window)
        Redis-->>Engine: Rate Limit OK
        Engine->>Redis: Cache Lookup (Prompt Hash)
    end

    alt Cache Hit
        Redis-->>Engine: Cached Tokens
        Engine-->>FastAPI: Return Cached Response
        FastAPI-->>Client: 200 OK (Fast Path)
    else Cache Miss
        Redis-->>Engine: Not Found

        rect rgb(255, 240, 230)
            Note over Engine,Provider: 3. Upstream Routing Phase
            Engine->>ClientHTTP: Provider routing (Primary Model)
            ClientHTTP->>Provider: Outbound API Call

            alt Primary Fails & Fallback Present
                Provider-->>ClientHTTP: 500 / 429 Error
                ClientHTTP-->>Engine: RequestException
                Engine->>ClientHTTP: Route to Fallback Model
                ClientHTTP->>Provider: Outbound API Call
            end

            Provider-->>ClientHTTP: Stream Response Tokens
            ClientHTTP-->>Engine: Async Iterator
            Engine-->>FastAPI: Yield tokens
            FastAPI-->>Client: SSE Stream
        end

        rect rgb(245, 255, 245)
            Note over Engine,Background: 4. Post-flight Phase
            Engine->>Background: Enqueue log_usage()
            Engine->>Background: Enqueue cache_response()
            Note over Background: Executes after Client disconnects
            Background->>Redis: SETEX prompt_hash
            Background->>Postgres: INSERT INTO request_logs
        end
    end
```

## Architectural Design Decisions

### 1. Asynchronous I/O (`asyncio`)
Given that calls to external LLM providers can take anywhere from a few milliseconds to several minutes, a traditional synchronous WSGI worker model (like standard Gunicorn/Flask) would quickly experience thread starvation. By leveraging ASGI (Uvicorn) and fully asynchronous I/O (`httpx`, `asyncpg`, `redis.asyncio`), a single API node can maintain thousands of concurrent upstream connections while using minimal memory.

### 2. Lifespan Connection Pooling
Opening and closing TCP connections and completing TLS handshakes for every request adds significant overhead. The FastAPI `lifespan` context manager is used to initialize shared, global connection pools on startup:
- `httpx.AsyncClient`: Used for all outbound provider requests.
- `asyncpg.create_pool()`: Manages PostgreSQL database connections efficiently.
- `redis.asyncio.Redis`: Shared Redis connection pool.

### 3. Background Tasks for Non-Critical Path Work
Writing usage logs to PostgreSQL and persisting items into the Redis cache are inherently blocking (at the network level) and do not need to delay the time it takes for a user to see their response.
These actions are dispatched to FastAPI's `BackgroundTasks`, executing immediately *after* the HTTP response has been returned and the connection closed.

### 4. Custom Error Handlers
To prevent data leakage and operational blind spots:
- `RequestValidationError`: Overridden to strip potentially malicious raw input from 422 responses while logging it locally.
- Global `Exception`: Caught unhandled exceptions are logged with full stack traces (`exc_info=True`) locally, but a sanitized generic `500 Internal Server Error` is returned to the client.
