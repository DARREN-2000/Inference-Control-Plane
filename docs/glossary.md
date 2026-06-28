# Glossary

- **Gateway / Proxy:** A server that sits between a client application and backend services (like OpenAI), intercepting and managing traffic. Laminar is a gateway.
- **Tenant:** A logical grouping within Laminar, usually representing a single customer or internal organization. Quotas and billing are calculated per-tenant.
- **TTFT (Time To First Token):** A critical latency metric in streaming LLM applications. It measures the time from when the user sends a prompt to when the first word of the response appears on their screen.
- **Semantic Caching:** Caching responses based on the *meaning* (vector embedding) of a prompt rather than the exact text characters.
- **Fallback / Routing Policy:** A set of rules determining what Laminar should do if a primary model (e.g., `gpt-4o`) fails. (e.g., "If GPT-4 fails, try Claude 3.5. If Claude fails, return a 502 error").
- **Tokens:** The fundamental unit of data processed by LLMs. A token is roughly equivalent to 3/4 of a word. Providers bill based on the number of prompt tokens and completion tokens used.
- **Rate Limiting:** Restricting the number of requests a user or tenant can make in a given timeframe (e.g., 100 RPM - Requests Per Minute) to prevent abuse and control costs.
- **SSE (Server-Sent Events):** The HTTP standard used by LLMs and Laminar to stream partial responses back to the client as they are generated, rather than waiting for the entire response to finish.
