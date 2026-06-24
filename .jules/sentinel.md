## 2025-02-24 - Unhandled Exception Logging
**Vulnerability:** Unhandled exceptions (`500 INTERNAL_ERROR`) were intentionally swallowed and returned as generic error messages to the client to prevent stack trace leakage, which is good practice. However, the original exception trace was not logged locally, creating an operational blind spot and potential for undetected repeated exploits/crashes.
**Learning:** Returning safe `500`s to clients doesn't mean we shouldn't log the full error backend-side. Security relies on auditability and visibility just as much as preventing information leakage.
**Prevention:** Always log `exc_info=exc` for caught unhandled exceptions before translating them into sanitized `500 INTERNAL_ERROR` API responses.

## 2024-05-30 - Sanitize Request Validation Errors
**Vulnerability:** FastAPI default RequestValidationError handler exposes the raw user input in the `input` field of validation errors.
**Learning:** Unsanitized user inputs in 422 error responses can lead to data leakage and Cross-Site Scripting (XSS) or log injection if error responses are logged or rendered indiscriminately.
**Prevention:** Always implement a custom `RequestValidationError` exception handler to strip the `input` field and only return safe keys like `loc`, `msg`, and `type`.

## 2024-06-24 - Avoid Information Leakage in Audit Logs
**Vulnerability:** Raw exception strings (`str(exc)`) were stored in database records (request logs) which are exposed to end-users via the `/usage/logs` API endpoint.
**Learning:** Exception string representations can contain sensitive system state, such as file paths, IP addresses, tokens, or network configuration. Logging them to user-accessible tables violates the principle of least privilege and leads to information leakage.
**Prevention:** Always sanitize user-facing audit logs with generic messages (e.g., "An internal error occurred"). Log the actual unhandled exception locally using standard server loggers (e.g., `logger.exception("...", exc_info=exc)`) for safe operational debugging without compromising data privacy.
