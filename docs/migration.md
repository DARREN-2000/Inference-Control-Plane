# Migration Guide

## Upgrading from v0.x to v1.0

Inference Control Plane v1.0 introduces breaking changes to the database schema to support advanced multi-tenant features and RBAC.

### 1. Database Schema Changes
The `api_keys` table has been restructured. The `owner` column has been replaced with `tenant_id`.

**Migration Steps:**
1. Take a full snapshot of your PostgreSQL database.
2. Shut down all Inference Control Plane API pods to prevent new data from being written.
3. Run the Alembic upgrade:
   ```bash
   alembic upgrade head
   ```
4. *Note: Alembic will automatically migrate existing `owner` data to `tenant_id`.*

### 2. Environment Variable Updates
- `ADMIN_API_KEY` has been renamed to `DEFAULT_API_KEY`. Update your deployment manifests.
- `ENABLE_CACHE` has been renamed to `CACHE_ENABLED`.

### 3. Client Application Updates
No changes are required to client applications using OpenAI SDKs. The `/v1/chat/completions` endpoint remains fully backward compatible.

## Migrating from LiteLLM / Portkey

If you are migrating to Inference Control Plane from another open-source AI gateway:

1. **Proxy URL:** Update your application's `base_url` to point to Inference Control Plane.
2. **Headers:** Inference Control Plane handles routing logic via the JSON body (`inference_control_plane_fallback_models`) rather than custom HTTP headers (like Portkey's `x-portkey-retry`). Update your SDK initialization to pass these configurations in `extra_body` instead.
3. **Data Migration:** Inference Control Plane does not currently support importing historical usage logs from LiteLLM databases due to schema differences. You will start with a fresh metrics dashboard.
