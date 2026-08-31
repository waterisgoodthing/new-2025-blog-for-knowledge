import logging
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Request, Response
from fastapi.responses import JSONResponse


logger = logging.getLogger("app.observability")


async def request_observability(request: Request, call_next) -> Response:
    request_id = str(uuid4())
    request.state.request_id = request_id
    try:
        response = await call_next(request)
    except Exception as error:
        route = request.scope.get("route")
        safe_route = getattr(route, "path", request.url.path)
        logger.error(
            "unhandled_request_error",
            extra={
                "safe_route": safe_route,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": request_id,
                "actor": getattr(request.state, "actor", "anonymous"),
                "error_class": type(error).__name__,
                "safe_summary": "Unhandled application error",
            },
        )
        response = JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "request_id": request_id,
            },
        )
    response.headers["X-Request-ID"] = request_id
    return response
