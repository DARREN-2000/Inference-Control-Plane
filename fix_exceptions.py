import re

with open("src/inference_control_plane/services/inference.py", "r") as f:
    content = f.read()

# Replace the first bad except block which does not re-raise or do anything useful
content = re.sub(r'    except HTTPException:\s+latency_ms = \(perf_counter\(\) - started\) \* 1000\.0\s+record_request\(\s+model=routed_model,\s+status="error",\s+latency_ms=latency_ms,\s+cache_hit=False,\s+\)\s+', '', content)

with open("src/inference_control_plane/services/inference.py", "w") as f:
    f.write(content)
