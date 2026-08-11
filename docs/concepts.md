# Core Concepts

Understanding the core concepts of Inference Control Plane is crucial for designing a robust, scalable AI integration architecture.

## 1. Tenants & Users

Inference Control Plane uses a multi-tenant data model to strictly isolate traffic, quotas, and logs.

- **Tenant:** A logical grouping of resources. In a B2B SaaS context, a Tenant represents one of your customers. In an internal enterprise context, a Tenant might represent a specific engineering team (e.g., `data-science-team`, `frontend-team`).
- **User:** An individual actor within a Tenant. When making requests, you can optionally pass a `user_id` to track consumption down to the individual level.

API Keys are issued per-Tenant.

## 2. The Proxy Gateway

Inference Control Plane is fundamentally a reverse proxy. Applications do not talk to OpenAI, Anthropic, or Azure directly. Instead, they send requests to Inference Control Plane's `/v1/chat/completions` (or similar) endpoint.

Inference Control Plane intercepts the request, strips the internal Inference Control Plane API key, applies logic (caching, rate limiting), injects the actual provider API key, forwards the request, and streams the response back.

## 3. Intelligent Routing (Fallbacks)

Large Language Models fail. APIs go down, rate limits are hit, and timeouts occur.

Inference Control Plane supports **Routing Policies**. If you request `gpt-4o` and OpenAI returns a `529 Server Overloaded` error, Inference Control Plane can automatically retry the request against `claude-3-5-sonnet` (Anthropic) or `gpt-4` (Azure OpenAI) without the client application ever knowing an error occurred.

Routing configurations are defined globally via environment variables (e.g., `LLM_PROVIDER_ORDER=openai,anthropic`) or passed dynamically per-request.

## 4. Semantic Caching

Standard HTTP caching uses exact string matching. This is ineffective for LLMs where prompts differ slightly but mean the same thing.

Inference Control Plane implements **Semantic Caching**.

1. When a request arrives, Inference Control Plane hashes the prompt.
2. If exact caching is enabled, it checks Redis for that exact hash.
3. If semantic caching is enabled, Inference Control Plane generates an embedding vector for the prompt and searches a vector database (like Qdrant) for a highly similar previous prompt (e.g., > 0.95 cosine similarity).
4. If a match is found, the cached completion is returned instantly, bypassing the LLM provider entirely.

## 5. Rate Limiting and Quotas

Inference Control Plane protects your budget by enforcing limits at the proxy layer before a request reaches the expensive LLM provider.

- **Rate Limits:** Prevent spikes in traffic. Enforced via Redis sliding windows (e.g., `100 requests per minute`).
- **Token Quotas:** Hard limits on consumption over a period (e.g., `1,000,000 tokens per month`).

Limits can be applied globally, per-Tenant, or per-User.

## 6. Asynchronous Observability

Logging massive amounts of AI traffic (including full prompts and completions) to a database synchronously would add unacceptable latency to the proxy request.

Inference Control Plane utilizes **Background Tasks** and **Message Queues**. When a response finishes streaming to the client, Inference Control Plane immediately closes the HTTP connection, and asynchronously writes the usage metrics (tokens, latency, cost) and payloads to PostgreSQL.
