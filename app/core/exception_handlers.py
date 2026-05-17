import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppException
from app.core.responses import error_response


logger = logging.getLogger("app.exceptions")


def translate_validation_message(message: str) -> str:
    translations = {
        "Field required": "Campo requerido",
        "Input should be a valid integer": "Debe ser un número entero válido",
        "Input should be a valid string": "Debe ser un texto válido",
        "Input should be a valid boolean": "Debe ser un valor booleano válido",
        "String should have at least 1 character": "El texto debe tener al menos 1 carácter",
    }
    return translations.get(message, message)


def translate_http_message(message: str) -> str:
    translations = {
        "Not Found": "Recurso no encontrado",
        "Method Not Allowed": "Método no permitido",
        "Unauthorized": "No autorizado",
        "Forbidden": "No tienes permisos para realizar esta acción",
    }
    return translations.get(message, message)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(message=exc.message),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        message = translate_http_message(str(exc.detail))
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(message=message),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        errors = [
            f"{'.'.join(str(location) for location in error['loc'])}: "
            f"{translate_validation_message(error['msg'])}"
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=error_response(message="Error de validación", errors=errors),
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(_: Request, __: SQLAlchemyError) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=error_response(message="Error de base de datos"),
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Error inesperado no controlado", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=error_response(message="Error inesperado del servidor"),
        )
