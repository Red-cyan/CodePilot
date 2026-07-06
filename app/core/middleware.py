import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request, Response

logger = logging.getLogger("codepilot.access")


def install_request_tracing(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_tracing(request: Request, call_next) -> Response:  # noqa: ANN001
        request_id = request.headers.get("X-Request-Id") or str(uuid4())
        started_at = perf_counter()
        response = await call_next(request)
        duration_ms = int((perf_counter() - started_at) * 1000)
        response.headers["X-Request-Id"] = request_id
        response.headers["X-Process-Time-Ms"] = str(duration_ms)
        logger.info(
            "request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response
