# API Reference

The Inference Control Plane API provides a unified interface for interacting with LLMs, as well as administrative endpoints for managing your control plane.

**Base URL:** `http://<your-inference_control_plane-host>:8000/v1`

## Authentication

All API requests must include your Inference Control Plane API key in the `Authorization` header.

```http
Authorization: Bearer sk-inference-control-plane-your-secret-key
```

## Inference Endpoints

### 1. Generate Completion

**`POST /generate`**

This is the primary endpoint for inference. It acts as a drop-in replacement for OpenAI's Chat Completions endpoint, with added support for Inference Control Plane-specific routing and caching policies.

#### Request Body (JSON)

| Field                                     | Type    | Required | Description                                                                                   |
| ----------------------------------------- | ------- | -------- | --------------------------------------------------------------------------------------------- |
| `model`                                   | string  | Yes      | The ID of the model to use (e.g., `gpt-4o`, `claude-3-5-sonnet`).                             |
| `messages`                                | array   | Yes      | A list of messages comprising the conversation.                                               |
| `temperature`                             | float   | No       | What sampling temperature to use, between 0 and 2. Default is 1.                              |
| `stream`                                  | boolean | No       | If true, partial message deltas will be sent via Server-Sent Events.                          |
| `user_id`                                 | string  | No       | A unique identifier representing your end-user, useful for rate limiting and billing.         |
| `inference_control_plane_fallback_models` | array   | No       | A list of model IDs to try if the primary `model` fails. (e.g. `["gpt-4", "gpt-3.5-turbo"]`). |
| `inference_control_plane_cache_bypass`    | boolean | No       | If true, forces the request to bypass the cache.                                              |

#### Example Request

```bash
curl -X POST "http://localhost:8000/v1/generate" \
  -H "Authorization: Bearer sk-inference-control-plane-your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Explain quantum computing in one sentence."}],
    "user_id": "user_98765",
    "inference_control_plane_fallback_models": ["claude-3-5-sonnet"]
  }'
```

#### Example Response (200 OK)

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gpt-4o",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Quantum computing is a type of computation that harnesses the collective properties of quantum states to perform calculations much faster than classical computers for certain problems."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 28,
    "total_tokens": 40
  },
  "inference_control_plane_metrics": {
    "cache_hit": false,
    "latency_ms": 842,
    "provider_used": "openai"
  }
}
```

#### Error Codes

- **401 Unauthorized:** Invalid or missing API key.
- **429 Too Many Requests:** The tenant or user has exceeded their rate limit or quota.
- **502 Bad Gateway:** The upstream provider failed and all fallbacks were exhausted.
- **504 Gateway Timeout:** The request to the provider timed out.

---

## Administrative Endpoints

### 2. Get Usage Summary

**`GET /usage/summary`**

Retrieves aggregated token usage and cost for a specific user or tenant over the current billing period.

#### Query Parameters

- `user_id` (string, required): The ID of the user to query.

#### Example Request

```bash
curl "http://localhost:8000/v1/usage/summary?user_id=user_98765" \
  -H "Authorization: Bearer sk-inference-control-plane-admin-key"
```

#### Example Response (200 OK)

```json
{
  "user_id": "user_98765",
  "total_requests": 142,
  "total_tokens": 45000,
  "estimated_cost_usd": 0.45
}
```

### 3. Get Usage Logs

**`GET /usage/logs`**

Retrieves raw request logs for auditing or debugging.

#### Query Parameters

- `user_id` (string, required): The user to query.
- `limit` (int, optional): Number of records to return (1-100, default 10).

#### Example Request

```bash
curl "http://localhost:8000/v1/usage/logs?user_id=user_98765&limit=2" \
  -H "Authorization: Bearer sk-inference-control-plane-admin-key"
```

---

## Health & Metrics

### 4. Liveness Probe

**`GET /health/live`**
Returns 200 OK. Used by Kubernetes/Docker to check if the pod is alive.

### 5. Readiness Probe

**`GET /health/ready`**
Checks connectivity to PostgreSQL and Redis. Returns 200 OK if both are connected, 503 otherwise.

### 6. Prometheus Metrics

**`GET /metrics`**
Exposes Prometheus-formatted metrics (no authentication required).
