# Examples

This document provides practical, real-world examples of how to utilize Inference Control Plane's capabilities to solve common AI engineering challenges.

## 1. High Availability (Zero-Downtime Provider Failover)

**Scenario:** You are building a critical customer-facing chatbot. You prefer `gpt-4o`, but OpenAI sometimes experiences degraded performance. If that happens, you want to automatically failover to Anthropic's `claude-3-5-sonnet` so the user doesn't experience an error.

**Implementation (Python):**
By using `extra_body`, you instruct Inference Control Plane on how to handle failures.

```python
from openai import OpenAI

client = OpenAI(base_url="http://inference_control_plane-host:8000/v1", api_key="sk-inference-control-plane...")

try:
    response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": "Help me reset my password."}], extra_body={"inference_control_plane_fallback_models": ["claude-3-5-sonnet", "gpt-3.5-turbo"]})
    print(response.choices[0].message.content)
except Exception as e:
    print(f"All models failed: {e}")
```

_What happens in Inference Control Plane:_

1. Inference Control Plane calls OpenAI `gpt-4o`.
2. OpenAI returns a 500 error.
3. Inference Control Plane catches the error, looks at `inference_control_plane_fallback_models`, and instantly retries the exact same prompt against Anthropic's `claude-3-5-sonnet`.
4. The client receives a successful response seamlessly.

---

## 2. Cost Reduction via Exact Caching

**Scenario:** You have a CI/CD pipeline that summarizes Git commits using an LLM. Many commits are similar or developers re-run the same pipeline. You want to cache responses to save money.

**Implementation:**
Ensure `CACHE_ENABLED=true` is set in your Inference Control Plane `.env`.

```bash
# Request 1 (Takes 1.5s, Costs $0.001)
curl -X POST "http://localhost:8000/v1/generate" \
  -H "Authorization: Bearer sk-inference-control-plane..." \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Summarize this diff: + print(1)"}]
  }'

# Request 2 (Identical payload, sent 5 minutes later)
# Takes 0.005s, Costs $0.000. Served entirely from Redis.
curl -X POST "http://localhost:8000/v1/generate" \
  -H "Authorization: Bearer sk-inference-control-plane..." \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Summarize this diff: + print(1)"}]
  }'
```

To explicitly force the LLM to generate a new response and ignore the cache, append `"inference_control_plane_cache_bypass": true` to the request payload.

---

## 3. Protecting Budgets (Rate Limiting per User)

**Scenario:** You have a multi-tenant SaaS application. You want to ensure no single user can spam your LLM and rack up a massive bill.

**Implementation:**
In your Inference Control Plane environment, set `USER_RATE_LIMIT_PER_MINUTE=10`.

Then, in your application, ensure you pass the `user` field with the end-user's ID.

```typescript
import OpenAI from "openai";
const client = new OpenAI({
  baseURL: "http://localhost:8000/v1",
  apiKey: "sk-inference-control-plane...",
});

// Inside your web app endpoint:
app.post("/ask-ai", async (req, res) => {
  const currentUserId = req.session.userId; // e.g., 'usr_abc123'

  try {
    const completion = await client.chat.completions.create({
      model: "gpt-4",
      messages: [{ role: "user", content: req.body.prompt }],
      user: currentUserId, // Crucial for rate limiting
    });
    res.json({ answer: completion.choices[0].message.content });
  } catch (error) {
    if (error.status === 429) {
      res
        .status(429)
        .json({ error: "You are making too many requests. Please slow down." });
    }
  }
});
```

If `usr_abc123` makes 11 requests in a minute, Inference Control Plane will reject the 11th request locally at the Redis layer, returning a 429 without ever calling OpenAI.

---

## 4. Unified Logging for Billing

**Scenario:** You need to bill internal departments (e.g., "Marketing", "Engineering") based on their LLM token usage at the end of the month.

**Implementation:**
Create separate Inference Control Plane API keys for each department. Inference Control Plane treats each API key as a distinct `tenant_id`.

When departments make requests using their respective keys, Inference Control Plane tags all logs in PostgreSQL with that `tenant_id`.

You can then query the Inference Control Plane Admin API (or view the Dashboard) to get usage metrics:

```bash
# Query usage for the Marketing department
curl "http://localhost:8000/v1/usage/summary?tenant_id=marketing_dept" \
  -H "Authorization: Bearer sk-inference-control-plane-admin-key"
```
