with open("src/inference_control_plane/services/inference.py", "r") as f:
    content = f.read()

import re

# Fix exc definition missing in the HTTP Error part
content = content.replace('''        _queue_request_log(
            background_tasks,
            tenant_id=auth_context.tenant_id,
            user_id=payload.user_id,
            api_key_hash=auth_context.api_key_hash,
            prompt=safe_prompt,
            response="",
            model_used=routed_model,
            latency_ms=latency_ms,
            tokens=0,
            cost=0.0,
            cache_hit=False,
            status_value="error",
            error_message=f"HTTP Error during generation. Reason: {exc.detail}",
        )
        logger.exception(f"HTTP Error during generation. Reason: {exc.detail}", exc_info=exc)
        raise
    except Exception as exc:''', '''    except HTTPException as exc:
        latency_ms = (perf_counter() - started) * 1000.0
        record_request(
            model=routed_model,
            status="error",
            latency_ms=latency_ms,
            cache_hit=False,
        )

        _queue_request_log(
            background_tasks,
            tenant_id=auth_context.tenant_id,
            user_id=payload.user_id,
            api_key_hash=auth_context.api_key_hash,
            prompt=safe_prompt,
            response="",
            model_used=routed_model,
            latency_ms=latency_ms,
            tokens=0,
            cost=0.0,
            cache_hit=False,
            status_value="error",
            error_message=str(exc.detail),
        )
        raise
    except Exception as exc:''')

with open("src/inference_control_plane/services/inference.py", "w") as f:
    f.write(content)

with open("src/inference_control_plane/api/routes.py", "r") as f:
    content = f.read()

content = content.replace("RequestLog.cache_hit == True", "RequestLog.cache_hit")
content = content.replace('stmt = select(RequestLog).where(RequestLog.status != "success").order_by(RequestLog.created_at.desc()).limit(5)',
'''stmt = (
        select(RequestLog)
        .where(RequestLog.status != "success")
        .order_by(RequestLog.created_at.desc())
        .limit(5)
    )''')
content = content.replace('''stmt_hits = select(func.count(RequestLog.id)).where(RequestLog.created_at >= yesterday, RequestLog.cache_hit)''',
'''stmt_hits = select(func.count(RequestLog.id)).where(
        RequestLog.created_at >= yesterday, RequestLog.cache_hit
    )''')

with open("src/inference_control_plane/api/routes.py", "w") as f:
    f.write(content)
