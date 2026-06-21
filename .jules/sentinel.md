## 2025-02-24 - Unhandled Exception Logging
**Vulnerability:** Unhandled exceptions (`500 INTERNAL_ERROR`) were intentionally swallowed and returned as generic error messages to the client to prevent stack trace leakage, which is good practice. However, the original exception trace was not logged locally, creating an operational blind spot and potential for undetected repeated exploits/crashes.
**Learning:** Returning safe `500`s to clients doesn't mean we shouldn't log the full error backend-side. Security relies on auditability and visibility just as much as preventing information leakage.
**Prevention:** Always log `exc_info=exc` for caught unhandled exceptions before translating them into sanitized `500 INTERNAL_ERROR` API responses.

## 2024-05-30 - Sanitize Request Validation Errors
**Vulnerability:** FastAPI default RequestValidationError handler exposes the raw user input in the `input` field of validation errors.
**Learning:** Unsanitized user inputs in 422 error responses can lead to data leakage and Cross-Site Scripting (XSS) or log injection if error responses are logged or rendered indiscriminately.
**Prevention:** Always implement a custom `RequestValidationError` exception handler to strip the `input` field and only return safe keys like `loc`, `msg`, and `type`.
## 2025-06-21 - Fix Exception Data Leakage in Request Logging
**Vulnerability:** Raw exception strings (`str(exc)`) were stored directly in database records via `_queue_request_log` on unhandled exceptions in `handle_generate_request`. This creates an information leakage vector, potentially exposing stack traces or sensitive internal application data to users viewing their own usage logs.
**Learning:** Even internal database records intended for observability can leak information if they power user-facing endpoints (like usage/logs APIs). Raw exceptions should never be saved in persistent data stores accessible by non-administrative users.
**Prevention:** Replace raw exceptions in database payloads with generic error messages (e.g., "An internal error occurred during generation.") and explicitly log the raw exception object locally using `logger.exception(..., exc_info=exc)` for operations to investigate later.
