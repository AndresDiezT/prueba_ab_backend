from fastapi import status


class AppException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Error inesperado de la aplicación"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.message


class UnauthorizedException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Credenciales inválidas o ausentes"


class ForbiddenException(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    message = "No tienes permisos para realizar esta acción"


class NotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Recurso no encontrado"


class ConflictException(AppException):
    status_code = status.HTTP_409_CONFLICT
    message = "El recurso ya existe"
