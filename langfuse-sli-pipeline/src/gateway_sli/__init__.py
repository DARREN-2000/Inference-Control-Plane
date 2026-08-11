"""gateway_sli: derive privacy-safe operational SLIs from Langfuse traces.

Langfuse/ClickHouse remain the source of truth for request-level traces. This
package reads traces, derives aggregate operational signals, and emits
bounded-cardinality metrics (OpenTelemetry-shaped) suitable for dashboards and
alerting. Raw prompts/responses and high-cardinality identifiers never leave the
privacy projection boundary.
"""

__version__ = "1.0.14"
