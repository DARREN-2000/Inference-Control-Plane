# CLI Reference

Inference Control Plane includes a built-in Python Command Line Interface (CLI) for managing the control plane, generating API keys, and interacting with the database.

The CLI is executed via the `api/cli.py` script.

## Accessing the CLI

If running via **Docker Compose**:
```bash
docker-compose exec inference-api python -m inference_control_plane.cli [COMMAND]
```

If running **locally**:
```bash
uv run python -m inference_control_plane.cli [COMMAND]
```

## Commands

### `keys`

Manage API keys for tenants.

#### Create a Key
Creates a new API key and associates it with a Tenant ID.

```bash
python -m inference_control_plane.cli keys create --tenant-id org_marketing_01
```

**Options:**
- `--tenant-id` (Required): The identifier for the tenant/organization.
- `--expires-in-days` (Optional): Number of days until the key expires.
- `--rate-limit` (Optional): Override the default RPM limit (e.g., `500`).

#### List Keys
Lists all active keys for a specific tenant.

```bash
python -m inference_control_plane.cli keys list --tenant-id org_marketing_01
```

#### Revoke a Key
Instantly revokes an API key, preventing it from being used for future requests.

```bash
python -m inference_control_plane.cli keys revoke --key-id key_abc123
```

---

### `cache`

Manage the Redis cache layer.

#### Clear Cache
Purges the entire exact-match cache from Redis. Useful during major prompt engineering updates.

```bash
python -m inference_control_plane.cli cache clear
```

#### Get Cache Stats
Displays hit/miss ratios and memory usage of the Redis cache.

```bash
python -m inference_control_plane.cli cache stats
```

---

### `db`

Database administration tasks. (Note: standard migrations should be run via Alembic).

#### Verify Connection
Tests the connection to PostgreSQL and Redis.

```bash
python -m inference_control_plane.cli db ping
```

#### Prune Logs
Deletes request logs older than a specified number of days to free up database storage.

```bash
python -m inference_control_plane.cli db prune-logs --days 30
```
