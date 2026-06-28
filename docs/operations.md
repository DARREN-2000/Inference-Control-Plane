# Operations Guide

This guide covers day-to-day operational tasks, maintenance, and alerting strategies for a Laminar cluster.

## Maintenance

### Database Migrations
When upgrading Laminar to a new version, the database schema may change.
- Always review the release notes.
- Migrations are handled by Alembic.
- **Downtime:** Migrations are designed to be backward compatible where possible, allowing rolling upgrades. However, taking a database backup before running `alembic upgrade head` in production is strongly recommended.

### Log Pruning
The `usage_logs` PostgreSQL table will grow rapidly. To maintain performance, configure a cron job to prune old logs.

Using the Laminar CLI:
```bash
# Delete logs older than 90 days
python -m inference_control_plane.cli db prune-logs --days 90
```
*Recommendation: Run this nightly during low-traffic periods.*

## Alerting Strategies

Based on the exposed Prometheus metrics, we recommend setting up the following alerts in Alertmanager, Datadog, or PagerDuty:

### 1. High Error Rate (5xx)
**Condition:** `rate(request_count_total{status_code=~"5.."}[5m]) / rate(request_count_total[5m]) > 0.05`
**Meaning:** More than 5% of requests are failing completely (after all routing fallbacks have been exhausted).
**Action:** Check provider status pages (OpenAI, Anthropic). Check Laminar application logs for network timeouts or authentication failures with the upstream provider.

### 2. High Upstream Latency
**Condition:** `histogram_quantile(0.95, rate(upstream_latency_seconds_bucket[5m])) > 10`
**Meaning:** The 95th percentile response time from the LLM providers is exceeding 10 seconds.
**Action:** This is usually an upstream provider issue. Consider adjusting your `LLM_PROVIDER_ORDER` to prioritize a faster or more stable provider temporarily.

### 3. Rate Limit Exhaustion (429 Spike)
**Condition:** `rate(rate_limit_exceeded_total[5m]) > 50`
**Meaning:** A tenant or the system is being heavily rate-limited.
**Action:** Check if a specific Tenant is under a DDoS attack or if their allocated quota is simply too low for their organic traffic.

### 4. Database Connection Pool Exhaustion
**Condition:** Application logs show `TimeoutError` when acquiring a connection from `asyncpg` pool.
**Meaning:** The API pods are blocked waiting for PostgreSQL connections.
**Action:** Increase `DATABASE_POOL_SIZE`, or scale out PgBouncer. Ensure background logging tasks are not failing and hanging open transactions.

## Disaster Recovery

1. **State:** The only critical state to back up is the PostgreSQL database (Configurations, API Keys, Usage Logs).
2. **Loss of Redis:** If the Redis cluster is lost, all API keys will fallback to being queried from PostgreSQL. Rate limiting windows will reset to 0, and the cache will be empty. The system will recover automatically once Redis is restored.
