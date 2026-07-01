# Security

Inference Control Plane is designed to be deployed in highly regulated enterprise environments (e.g., SOC2, HIPAA compliant). This document outlines the security architecture and recommendations.

## Threat Model & Attack Vectors

### 1. Provider Key Exfiltration
**Risk:** An attacker gains access to your raw OpenAI/Anthropic API keys.
**Mitigation:** Inference Control Plane never exposes provider keys to the client. Keys are stored in the server's environment variables. They should be injected at runtime using a secure vault (e.g., AWS KMS) and never hardcoded in `.env` files in source control.

### 2. Data Leakage (PII)
**Risk:** Sensitive user prompts containing PII (Personally Identifiable Information) or PHI are logged in plain text.
**Mitigation:** By default, Inference Control Plane does **not** log request payloads (prompts) or responses to the database. It only logs metadata (tokens, latency). To ensure compliance, keep `LOG_PAYLOADS=false` in production.
If you must log payloads for audit purposes, consider implementing a middleware step to sanitize PII using an external service before the payload is stored.

### 3. Unhandled Exceptions Leaking Stack Traces
**Risk:** A crash in the API layer returns a raw Python stack trace to the end-user, exposing internal system paths or database queries.
**Mitigation:** Inference Control Plane implements global exception handlers in FastAPI. Any unhandled exception is caught, logged locally via `logger.exception()` (to alert your operations team), and a sanitized, generic `500 Internal Server Error` is returned to the client.

### 4. Payload Injection (Malicious Input)
**Risk:** A client sends a massive or malformed JSON payload designed to crash the JSON parser or consume all memory.
**Mitigation:** Inference Control Plane uses Pydantic for strict request validation. The custom `RequestValidationError` handler sanitizes 422 responses, preventing the echo of potentially malicious raw input payloads back to the client.

## Network Security (Defense in Depth)

1. **VPC Isolation:** The Inference Control Plane API pods, PostgreSQL instance, and Redis cluster should all reside in private subnets within a Virtual Private Cloud (VPC). Only the API pods should be exposed to the internet via an Ingress Controller/Load Balancer.
2. **TLS/SSL:** Terminate TLS at the Load Balancer. Communication between the client and Inference Control Plane must be encrypted (HTTPS).
3. **CORS:** Restrict `CORS_ALLOWED_ORIGINS` to exactly the domains that require access to the API (e.g., your frontend application). Do not use `["*"]` in production.

## Audit Logging

Every configuration change, key generation, and administrative action should be traceable.
- All requests are logged with a unique `request_id`.
- Access to administrative endpoints requires the `DEFAULT_API_KEY`. Keep access to this key restricted to a small number of DevOps personnel.

## Vulnerability Reporting

If you discover a security vulnerability in Inference Control Plane, please do not open a public GitHub issue.

Please follow the instructions in our [SECURITY.md](../SECURITY.md) file to report the issue responsibly.
