import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger("app.request")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        started_at = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        # AuthMiddleware deja estos datos en request.state cuando la petición trae JWT válido.
        user_payload = getattr(request.state, "current_user", None) or {}
        user_id = user_payload.get("sub", "anonymous")
        username = user_payload.get("username", "anonymous")
        role = user_payload.get("role", "public")

        logger.info(
            "%s %s finalizo con estado %s en %sms | user_id=%s username=%s role=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            user_id,
            username,
            role,
        )
        response.headers["X-Process-Time-ms"] = str(duration_ms)
        return response
