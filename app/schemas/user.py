from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import UserRole


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.VIEWER


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    id: int
    username: str
    role: UserRole
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
