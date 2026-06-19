## 2025-06-19 - Fast API Default RequestValidationError payload leak

**Vulnerability:** FastAPIs default `RequestValidationError` exception handler echoes the raw incoming payload under the `input` field of validation errors.
**Learning:** If clients misconfigure payloads and send raw credentials or sensitive fields under unexpected fields, those details might get echoed verbatim in the 422 JSON response. This creates an operational blindspot where logs/interceptors that depend on application logic to sanitize fields miss these because validation rejects the request earlier.
**Prevention:** Always register a custom exception handler for `RequestValidationError` that sanitizes outputs before calling `JSONResponse` (i.e. removing `url`, `ctx` and `input` from `exc.errors()`).

## 2024-05-19 - FastAPI Default RequestValidationError payload leak

**Vulnerability:** FastAPIs default `RequestValidationError` exception handler echoes the raw incoming payload under the `input` field of validation errors.
**Learning:** If clients misconfigure payloads and send raw credentials or sensitive fields under unexpected fields, those details might get echoed verbatim in the 422 JSON response. This creates an operational blindspot where logs/interceptors that depend on application logic to sanitize fields miss these because validation rejects the request earlier.
**Prevention:** Always register a custom exception handler for `RequestValidationError` that sanitizes outputs before calling `JSONResponse` (i.e. removing `url`, `ctx` and `input` from `exc.errors()`).
