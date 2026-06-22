## 2025-02-24 - Unhandled Exception Logging
**Vulnerability:** Unhandled exceptions (`500 INTERNAL_ERROR`) were intentionally swallowed and returned as generic error messages to the client to prevent stack trace leakage, which is good practice. However, the original exception trace was not logged locally, creating an operational blind spot and potential for undetected repeated exploits/crashes.
**Learning:** Returning safe `500`s to clients doesn't mean we shouldn't log the full error backend-side. Security relies on auditability and visibility just as much as preventing information leakage.
**Prevention:** Always log `exc_info=exc` for caught unhandled exceptions before translating them into sanitized `500 INTERNAL_ERROR` API responses.

## 2024-05-30 - Sanitize Request Validation Errors
**Vulnerability:** FastAPI default RequestValidationError handler exposes the raw user input in the `input` field of validation errors.
**Learning:** Unsanitized user inputs in 422 error responses can lead to data leakage and Cross-Site Scripting (XSS) or log injection if error responses are logged or rendered indiscriminately.
**Prevention:** Always implement a custom `RequestValidationError` exception handler to strip the `input` field and only return safe keys like `loc`, `msg`, and `type`.

## 2025-02-24 - Exception Logging Leakage to Database
**Vulnerability:** Unhandled exceptions (`str(exc)`) were stored raw in the `error_message` database field. Since this field is intended to be visible via usage logs endpoints, raw traces or inner connection strings can be exposed to end users.
**Learning:** We need to explicitly separate data meant for audit logs versus internal systems and be careful about what text we commit to DB rows.
**Prevention:** Always log `exc_info=exc` for caught unhandled exceptions locally to server logs, and only write sanitized generic error messages like `"Internal server error"` into persistent storage intended for usage API endpoints.
