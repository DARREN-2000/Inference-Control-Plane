# Frequently Asked Questions (FAQ)

### What is the performance overhead of using Inference Control Plane?

Inference Control Plane is engineered for ultra-low latency. The proxy overhead (validating keys, checking rate limits, and routing) is typically under 3 milliseconds. If a response is served from the exact-match cache, the total latency is often under 10ms, which is significantly faster than hitting an upstream LLM provider.

### Does Inference Control Plane store my users' prompts and data?

**No, not by default.** Data privacy is paramount. Inference Control Plane only logs metadata (tokens used, latency, model selected, user IDs) to the database. The actual content of the `messages` array (prompts and completions) is processed in memory and discarded. You can optionally enable payload logging by setting `LOG_PAYLOADS=true` if your compliance team requires audit trails.

### Can I run Inference Control Plane without Redis?

No. Redis is a hard requirement. It is critical for maintaining sub-millisecond latency on rate limiting (via sliding window Lua scripts) and API key validation. PostgreSQL is too slow for these high-velocity operations on every request.

### Can I use local models like Ollama or vLLM?

Yes! Inference Control Plane's router is agnostic. As long as your local model server exposes an OpenAI-compatible API, you can add it to Inference Control Plane. You can route to it by configuring a custom provider endpoint in the environment variables (e.g., overriding the OpenAI base URL for a specific model name).

### How does Semantic Caching differ from Exact Caching?

- **Exact Caching (Redis):** Checks if the exact string `"What is the capital of France?"` has been asked before. Very fast, but easily defeated by a single extra space or typo.
- **Semantic Caching (Qdrant):** Converts the prompt into a mathematical vector (embedding). If someone asks `"Tell me the capital of France"`, the vector is mathematically similar to the previous prompt, and the cache hits. (Note: Semantic caching is currently on the roadmap).

### Is Inference Control Plane a replacement for LangChain/LlamaIndex?

No. Inference Control Plane sits at the infrastructure level (networking), while LangChain/LlamaIndex sit at the application level (orchestration). Your application code uses LangChain to construct prompts and RAG pipelines, and then LangChain sends the final request to Inference Control Plane instead of OpenAI directly.

### What happens if the database goes down?

If PostgreSQL goes down, the API will continue to serve inference traffic using cached keys from Redis. However, new usage logs will be lost (or buffered in memory until failure), and administrative endpoints will fail. If Redis goes down, API requests will fail open/closed depending on your HA configuration until Redis is restored.
