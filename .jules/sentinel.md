## 2025-02-24 - Unhandled Exception Logging
**Vulnerability:** Unhandled exceptions (`500 INTERNAL_ERROR`) were intentionally swallowed and returned as generic error messages to the client to prevent stack trace leakage, which is good practice. However, the original exception trace was not logged locally, creating an operational blind spot and potential for undetected repeated exploits/crashes.
**Learning:** Returning safe `500`s to clients doesn't mean we shouldn't log the full error backend-side. Security relies on auditability and visibility just as much as preventing information leakage.
**Prevention:** Always log `exc_info=exc` for caught unhandled exceptions before translating them into sanitized `500 INTERNAL_ERROR` API responses.

## 2024-05-30 - Sanitize Request Validation Errors
**Vulnerability:** FastAPI default RequestValidationError handler exposes the raw user input in the `input` field of validation errors.
**Learning:** Unsanitized user inputs in 422 error responses can lead to data leakage and Cross-Site Scripting (XSS) or log injection if error responses are logged or rendered indiscriminately.
**Prevention:** Always implement a custom `RequestValidationError` exception handler to strip the `input` field and only return safe keys like `loc`, `msg`, and `type`.

## 2024-05-24 - Exception details exposed in DB logs
**Vulnerability:** Raw exception messages from failed generations were being saved to DB logs using `str(exc)`. This could leak sensitive internal environment details, such as DB URLs, API keys, or stack traces, via the `error_message` DB column. This DB log might be queryable by users later.
**Learning:** We need to sanitize error messages written to DB logs, replacing raw exceptions with generic messages, while making sure the full exception and its traceback are logged locally with `logger.exception("message", exc_info=exc)`.
**Prevention:** Never use `str(exc)` in code that persists errors to DBs or sends them to external clients, unless the exception class is explicitly defined to contain user-safe data. Always log raw exceptions locally.
