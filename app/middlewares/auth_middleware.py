from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import UnauthorizedException
from app.core.security import decode_access_token


PUBLIC_PATH_PREFIXES = (
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request.state.current_user = None
        request.state.auth_error = None

        if request.url.path.startswith(PUBLIC_PATH_PREFIXES):
            return await call_next(request)

        authorization = request.headers.get("Authorization")
        if authorization and authorization.lower().startswith("bearer "):
            token = authorization.split(" ", 1)[1]
            try:
                request.state.current_user = decode_access_token(token)
            except UnauthorizedException as exc:
                # La dependencia de seguridad genera la respuesta 401 con el formato estándar.
                request.state.auth_error = exc.message

        return await call_next(request)
