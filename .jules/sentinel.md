## 2023-10-27 - [Information Leakage] Sanitizing Validation Errors
**Vulnerability:** Information Leakage via FastAPI RequestValidationError
**Learning:** By default, FastAPI's RequestValidationError exposes raw user input in its 422 responses. For malicious or malformed payloads, this can inadvertently echo malicious input back into the response body or leak internal parsing logic/schema details.
**Prevention:** Implement a custom exception handler for `fastapi.exceptions.RequestValidationError` that sanitizes the errors by popping the `input` field before wrapping the error in the application's standard secure error response format.
