## 2025-02-24 - Unhandled Exception Logging
**Vulnerability:** Unhandled exceptions (`500 INTERNAL_ERROR`) were intentionally swallowed and returned as generic error messages to the client to prevent stack trace leakage, which is good practice. However, the original exception trace was not logged locally, creating an operational blind spot and potential for undetected repeated exploits/crashes.
**Learning:** Returning safe `500`s to clients doesn't mean we shouldn't log the full error backend-side. Security relies on auditability and visibility just as much as preventing information leakage.
**Prevention:** Always log `exc_info=exc` for caught unhandled exceptions before translating them into sanitized `500 INTERNAL_ERROR` API responses.

## 2024-05-30 - Sanitize Request Validation Errors
**Vulnerability:** FastAPI default RequestValidationError handler exposes the raw user input in the `input` field of validation errors.
**Learning:** Unsanitized user inputs in 422 error responses can lead to data leakage and Cross-Site Scripting (XSS) or log injection if error responses are logged or rendered indiscriminately.
**Prevention:** Always implement a custom `RequestValidationError` exception handler to strip the `input` field and only return safe keys like `loc`, `msg`, and `type`.

## 2025-02-28 - Sanitize raw exception strings in database logs
**Vulnerability:** Raw exception strings (`str(exc)`) were stored in database usage logs (which might be user-exposed) when an upstream model generation failed.
**Learning:** Storing raw exceptions in database logs can leak sensitive internal state, network configurations, API keys (if part of an error message), or software stack details to users who might view these logs.
**Prevention:** Never store raw exception strings (`str(exc)`) in database records that are exposed to end-users (e.g., usage logs). Always sanitize them with generic messages and log the actual exception locally with `logger.exception`.
