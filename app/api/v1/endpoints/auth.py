from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_admin
from app.db.session import get_db
from app.models.user import User
from app.core.responses import success_response
from app.schemas.auth import Token
from app.schemas.response import ApiResponse
from app.schemas.user import UserCreate, UserRead, UserRegister
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=ApiResponse[Token])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> dict:
    access_token = await AuthService(db).authenticate(form_data.username, form_data.password)
    return success_response(
        message="Inicio de sesión exitoso",
        data=Token(access_token=access_token),
    )


@router.post("/register", response_model=ApiResponse[UserRead], status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserRegister,
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await AuthService(db).register_viewer(user_in)
    return success_response(message="Usuario registrado correctamente", data=user)


@router.post("/users", response_model=ApiResponse[UserRead], status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await AuthService(db).create_user(user_in)
    return success_response(message="Usuario creado correctamente", data=user)
