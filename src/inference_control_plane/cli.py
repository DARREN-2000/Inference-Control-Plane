from __future__ import annotations

import uvicorn

from inference_control_plane.core.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "inference_control_plane.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
