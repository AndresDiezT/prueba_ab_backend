from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserRegister
from app.core.enums import UserRole


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.user_repository = UserRepository(db)

    async def authenticate(self, username: str, password: str) -> str:
        user = await self.user_repository.get_by_username(username)
        if not user or not user.is_active or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Usuario o contraseña inválidos")

        return create_access_token(subject=str(user.id), claims={"role": user.role, "username": user.username})

    async def create_user(self, user_in: UserCreate) -> User:
        existing_user = await self.user_repository.get_by_username(user_in.username)
        if existing_user:
            raise ConflictException("El nombre de usuario ya existe")

        user = User(
            username=user_in.username,
            hashed_password=hash_password(user_in.password),
            role=user_in.role,
        )
        return await self.user_repository.create(user)

    async def register_viewer(self, user_in: UserRegister) -> User:
        existing_user = await self.user_repository.get_by_username(user_in.username)
        if existing_user:
            raise ConflictException("El nombre de usuario ya existe")

        user = User(
            username=user_in.username,
            hashed_password=hash_password(user_in.password),
            role=UserRole.VIEWER,
        )
        return await self.user_repository.create(user)
