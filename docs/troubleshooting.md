# Troubleshooting

This guide addresses common issues encountered when deploying or operating Inference Control Plane.

## 1. 401 Unauthorized Errors

**Symptom:** Client requests immediately fail with `{"detail": "Invalid API Key"}`.

**Possible Causes:**
1. The client is not sending the `Authorization: Bearer <key>` header.
2. The key has been revoked or expired.
3. **Common Dev Issue:** You generated a key using the CLI, but Redis is out of sync with Postgres.
   - *Fix:* Ensure Redis and Postgres are connected. Restart the API pod to flush any corrupted local state.

## 2. 503 Service Unavailable / 502 Bad Gateway

**Symptom:** Requests fail after a delay, or the `/health/ready` endpoint returns 503.

**Possible Causes:**
1. **Upstream Provider Failure:** All models in your fallback chain failed.
   - *Fix:* Check `LLM_PROVIDER_ORDER`. Ensure you have valid API keys for the providers in your fallback chain.
2. **Database Connectivity:** Inference Control Plane cannot connect to PostgreSQL.
   - *Fix:* Verify `DATABASE_URL`. If using Docker Compose, ensure the `postgres` container is healthy. Check for "Too many clients" errors indicating connection pool exhaustion.
3. **Redis Connectivity:** Inference Control Plane cannot connect to Redis.
   - *Fix:* Verify `REDIS_URL`.

## 3. Streaming Responses Are Buffered (Not Streaming)

**Symptom:** The client sets `stream: true`, but the response arrives all at once after a long delay instead of token-by-token.

**Possible Causes:**
1. **Ingress/Proxy Buffering:** Your NGINX, Cloudflare, or AWS ALB is buffering the HTTP response.
   - *Fix:* Configure your proxy to support Server-Sent Events (SSE). For NGINX, disable `proxy_buffering`.
2. **Upstream Not Streaming:** The provider (e.g., Azure OpenAI) might be ignoring the stream flag due to a misconfiguration in deployment settings.

## 4. No Usage Logs Appearing in Database

**Symptom:** Requests are succeeding, but `usage_logs` in PostgreSQL remains empty.

**Possible Causes:**
1. **Background Task Failure:** The API process crashed before the background task could execute.
2. **Database Write Errors:** The background task is attempting to write, but failing (e.g., due to schema mismatch or foreign key constraint on `tenant_id`).
   - *Fix:* Check the API stdout logs for `SQLAlchemyError` or `IntegrityError`. Ensure you ran `alembic upgrade head`.

## 5. Next.js Dashboard Fails to Load Data

**Symptom:** The dashboard UI loads, but charts are empty or show "Failed to fetch".

**Possible Causes:**
1. **CORS:** The API is rejecting the request from the Dashboard's origin.
   - *Fix:* Add the Dashboard's domain to `CORS_ALLOWED_ORIGINS` in the API `.env`. Example: `CORS_ALLOWED_ORIGINS=["http://localhost:3000"]`.
2. **Wrong API URL:** The frontend is pointing to the wrong backend URL.
   - *Fix:* Verify `NEXT_PUBLIC_API_BASE_URL` in the frontend `.env.local`.
