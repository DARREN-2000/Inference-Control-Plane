# Authentication & Authorization

Securing the control plane and correctly isolating tenants is a primary responsibility of Inference Control Plane.

## The Two Layers of Authentication

Inference Control Plane deals with two distinct API layers, and therefore two types of authentication.

### 1. Client-to-Inference Control Plane (Ingress Auth)
When a client application (e.g., your Next.js app, your internal microservice) makes a request to Inference Control Plane, it must authenticate using a Inference Control Plane-issued API key.

```http
Authorization: Bearer sk-inference-control-plane-abc123def456
```
This key tells Inference Control Plane *who* is making the request (Tenant) and dictates what rate limits and policies apply.

### 2. Inference Control Plane-to-Provider (Egress Auth)
When Inference Control Plane routes a request to OpenAI or Anthropic, it strips the Inference Control Plane API key and injects the actual provider API key (e.g., `sk-proj-...`). The client application never sees or possesses the provider keys.

## API Key Architecture

Inference Control Plane API Keys follow the format: `sk-inference-control-plane-[random_bytes]`.

### Key Validation Flow
1. Request arrives.
2. The `Depends(get_auth_context)` middleware extracts the Bearer token.
3. Inference Control Plane hashes the token (SHA-256) and looks it up in Redis.
4. If found in Redis, the request proceeds (Sub-millisecond).
5. If not found in Redis, Inference Control Plane queries PostgreSQL. If valid, it hydrates the Redis cache and proceeds. If invalid, returns `401 Unauthorized`.

## Tenants and Role-Based Access Control (RBAC)

Keys are tied to **Tenants**.

### Admin vs. Tenant Keys
- **Admin Key:** Set via the `DEFAULT_API_KEY` environment variable. This key has permissions to hit administrative endpoints (e.g., `/usage/summary`, generating new keys).
- **Tenant Keys:** Generated via the CLI or Admin Dashboard. These keys can only hit inference endpoints (`/generate`) and are strictly isolated to their own usage quotas.

## Security Best Practices

1. **Rotate the Default Key:** The `DEFAULT_API_KEY` in `.env.example` is `replace-me`. If deployed to production with this key, your control plane is entirely open to abuse. You must generate a strong cryptographically secure string and inject it as an environment variable.
2. **Never commit Provider Keys:** Ensure `OPENAI_API_KEY` and others are injected via secure Secret Managers (AWS Secrets Manager, HashiCorp Vault).
3. **Use Short-Lived Keys:** When issuing keys to tenants or internal teams, configure an expiration date using the CLI to limit the blast radius of a leaked key.
