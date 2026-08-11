# syntax=docker/dockerfile:1

# ---- build/runtime image -------------------------------------------------
# The core pipeline uses only the standard library. The production image installs
# the optional AWS extra (boto3) for the DynamoDB checkpoint store.
FROM python:3.12-slim AS runtime

# Do not buffer stdout/stderr (so logs show up promptly in ECS/CloudWatch),
# and never write .pyc files in the container layer.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install the package first (leverages layer caching on source-only changes).
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir '.[aws]'

# Fixtures used by the demo/default invocation.
COPY data ./data

# Run as a non-root user.
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

# Entry point is the installed console script (gateway-sli -> gateway_sli.cli:main).
ENTRYPOINT ["gateway-sli"]
# Default: emit to a local collector over OTLP/HTTP. Override in the task def.
CMD ["--source", "data/sample_traces.json", "--emit", "console"]
