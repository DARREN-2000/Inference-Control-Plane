# Configuration

Inference Control Plane is designed as a cloud-native, 12-factor application. All configuration is managed exclusively through environment variables.

This guide details all available configuration parameters.

## Core Settings

| Variable               | Type          | Default       | Description                                                                                   |
| ---------------------- | ------------- | ------------- | --------------------------------------------------------------------------------------------- |
| `ENVIRONMENT`          | string        | `development` | Set to `production` to enable JSON logging, disable debug endpoints, and enforce strict CORS. |
| `LOG_LEVEL`            | string        | `INFO`        | Standard Python logging levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).             |
| `DEFAULT_API_KEY`      | string        | `replace-me`  | The default admin API key. **Must be changed in production.**                                 |
| `CORS_ALLOWED_ORIGINS` | string (JSON) | `["*"]`       | JSON list of allowed origins. Example: `["https://dashboard.example.com"]`                    |
| `PORT`                 | int           | `8000`        | The port the FastAPI server listens on.                                                       |

## Database Connection

Inference Control Plane requires PostgreSQL via `asyncpg` driver and Redis for caching/rate-limiting.

| Variable                | Type   | Default                                                              | Description                                                                    |
| ----------------------- | ------ | -------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `DATABASE_URL`          | string | `postgresql+asyncpg://postgres:postgres@localhost:5432/inference_cp` | The async connection string to PostgreSQL.                                     |
| `DATABASE_POOL_SIZE`    | int    | `20`                                                                 | Base number of persistent database connections to keep open.                   |
| `DATABASE_MAX_OVERFLOW` | int    | `10`                                                                 | Maximum number of temporary connections to create beyond `DATABASE_POOL_SIZE`. |
| `REDIS_URL`             | string | `redis://localhost:6379/0`                                           | Connection string to Redis.                                                    |

## LLM Provider Keys

To route traffic to providers, Inference Control Plane needs their respective API keys. If a key is missing, Inference Control Plane will not route traffic to that provider.

| Variable                  | Type   | Description                                  |
| ------------------------- | ------ | -------------------------------------------- |
| `OPENAI_API_KEY`          | string | Your global OpenAI API key.                  |
| `ANTHROPIC_API_KEY`       | string | Your global Anthropic API key.               |
| `AZURE_OPENAI_API_KEY`    | string | Azure OpenAI API key.                        |
| `AZURE_OPENAI_BASE_URL`   | string | Azure OpenAI endpoint URL.                   |
| `AZURE_OPENAI_DEPLOYMENT` | string | The specific model deployment name in Azure. |

## Routing & Fallback Behavior

| Variable              | Type         | Default             | Description                                                                                         |
| --------------------- | ------------ | ------------------- | --------------------------------------------------------------------------------------------------- |
| `LLM_MODE`            | string       | `openai-compatible` | Dictates the default parsing mode.                                                                  |
| `LLM_PROVIDER_ORDER`  | string (CSV) | `openai,anthropic`  | The global fallback order if a dynamic routing policy isn't provided in the request.                |
| `LLM_TIMEOUT_SECONDS` | int          | `60`                | Global timeout for upstream LLM requests. If exceeded, Inference Control Plane triggers a fallback. |
| `LLM_MAX_RETRIES`     | int          | `2`                 | Number of times to retry a provider on 5xx errors before moving to the next provider.               |

## Caching

| Variable            | Type | Default | Description                                           |
| ------------------- | ---- | ------- | ----------------------------------------------------- |
| `CACHE_ENABLED`     | bool | `true`  | Globally enable or disable Redis exact-match caching. |
| `CACHE_TTL_SECONDS` | int  | `3600`  | How long to keep a cached response in Redis.          |

## Rate Limiting

| Variable                        | Type | Default | Description                                                             |
| ------------------------------- | ---- | ------- | ----------------------------------------------------------------------- |
| `RATE_LIMIT_ENABLED`            | bool | `true`  | Globally enable or disable Redis-based rate limiting.                   |
| `RATE_LIMIT_WINDOW_SECONDS`     | int  | `60`    | The sliding window duration for rate limits.                            |
| `DEFAULT_RATE_LIMIT_PER_MINUTE` | int  | `120`   | Default Requests-Per-Minute limit for tenants without a specific quota. |
| `USER_RATE_LIMIT_PER_MINUTE`    | int  | `60`    | Default Requests-Per-Minute limit for specific users (`user_id`).       |

## Observability

| Variable               | Type   | Default                   | Description                                                                                                                          |
| ---------------------- | ------ | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `PROMETHEUS_NAMESPACE` | string | `inference_control_plane` | Prefix for all exported Prometheus metrics.                                                                                          |
| `OTLP_ENDPOINT`        | string | `""`                      | OpenTelemetry Collector endpoint (e.g., `http://jaeger:4317`). Leave blank to disable OTLP tracing.                                  |
| `LOG_PAYLOADS`         | bool   | `false`                   | **SECURITY:** If `true`, full request prompts and response completions are saved to the database. Set to `false` for PII/compliance. |
