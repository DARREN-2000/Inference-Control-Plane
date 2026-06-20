## 2025-02-24 - Unhandled Exception Logging
**Vulnerability:** Unhandled exceptions (`500 INTERNAL_ERROR`) were intentionally swallowed and returned as generic error messages to the client to prevent stack trace leakage, which is good practice. However, the original exception trace was not logged locally, creating an operational blind spot and potential for undetected repeated exploits/crashes.
**Learning:** Returning safe `500`s to clients doesn't mean we shouldn't log the full error backend-side. Security relies on auditability and visibility just as much as preventing information leakage.
**Prevention:** Always log `exc_info=exc` for caught unhandled exceptions before translating them into sanitized `500 INTERNAL_ERROR` API responses.

## 2024-05-30 - Sanitize Request Validation Errors
**Vulnerability:** FastAPI default RequestValidationError handler exposes the raw user input in the `input` field of validation errors.
**Learning:** Unsanitized user inputs in 422 error responses can lead to data leakage and Cross-Site Scripting (XSS) or log injection if error responses are logged or rendered indiscriminately.
**Prevention:** Always implement a custom `RequestValidationError` exception handler to strip the `input` field and only return safe keys like `loc`, `msg`, and `type`.

## 2024-05-20 - Prevent Internal Exception Leakage in User Logs
**Vulnerability:** Raw exception strings (e.g., `str(exc)[:1000]`) were stored directly in `RequestLog.error_message`, which is exposed to end users via the `/usage/logs` endpoint, leading to internal infrastructure details and stack traces leaking to unauthorized users.
**Learning:** General `Exception` catch blocks that store error context in databases accessed by users are a common source of data leakage. Furthermore, raising `HTTPException` natively swallows the exception context from backend logs, causing an operational blind spot.
**Prevention:** Always log exceptions locally via `logger.exception("...", exc_info=exc)` *before* wrapping them in an `HTTPException`, and always sanitize error messages saved to user-accessible databases using a generic message (e.g., "An internal error occurred").
