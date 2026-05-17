from collections.abc import Callable

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import UserRole
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    auth_error = getattr(request.state, "auth_error", None)
    if auth_error:
        raise UnauthorizedException(auth_error)

    payload = getattr(request.state, "current_user", None)
    if not payload:
        raise UnauthorizedException("Autenticación requerida")

    user = await UserRepository(db).get_by_id(int(payload["sub"]))
    if not user or not user.is_active:
        raise UnauthorizedException("El usuario está inactivo o ya no existe")

    return user


def require_roles(*allowed_roles: UserRole) -> Callable[[User], User]:
    async def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenException()
        return current_user

    return role_dependency


require_admin = require_roles(UserRole.ADMIN)
require_authenticated = require_roles(UserRole.ADMIN, UserRole.VIEWER)
