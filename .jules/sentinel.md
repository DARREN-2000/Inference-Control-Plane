## 2025-02-24 - Unhandled Exception Logging
**Vulnerability:** Unhandled exceptions (`500 INTERNAL_ERROR`) were intentionally swallowed and returned as generic error messages to the client to prevent stack trace leakage, which is good practice. However, the original exception trace was not logged locally, creating an operational blind spot and potential for undetected repeated exploits/crashes.
**Learning:** Returning safe `500`s to clients doesn't mean we shouldn't log the full error backend-side. Security relies on auditability and visibility just as much as preventing information leakage.
**Prevention:** Always log `exc_info=exc` for caught unhandled exceptions before translating them into sanitized `500 INTERNAL_ERROR` API responses.

## 2024-05-30 - Sanitize Request Validation Errors
**Vulnerability:** FastAPI default RequestValidationError handler exposes the raw user input in the `input` field of validation errors.
**Learning:** Unsanitized user inputs in 422 error responses can lead to data leakage and Cross-Site Scripting (XSS) or log injection if error responses are logged or rendered indiscriminately.
**Prevention:** Always implement a custom `RequestValidationError` exception handler to strip the `input` field and only return safe keys like `loc`, `msg`, and `type`.

## 2025-02-24 - Prevent Exception Data Leakage in Usage Logs
**Vulnerability:** The application was logging raw, unsanitized exception strings (`str(exc)[:1000]`) to the `RequestLog` database table when unhandled exceptions occurred during inference. Because these logs are accessible to end-users via the `/usage/logs` endpoint, this could lead to data leakage (e.g. exposing internal file paths, API keys in the prompt, or network details from httpx).
**Learning:** Even if the API returns a safe 500 error to the client, storing raw exception text in any database table that is eventually exposed to users creates a severe data leakage vector. The database layer and logging layer must be treated differently.
**Prevention:** Never store raw exception strings (`str(exc)`) in database records that are exposed to end-users. Always sanitize them with generic messages and log the actual exception locally with `logger.exception`.
