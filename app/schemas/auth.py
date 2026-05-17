from pydantic import BaseModel

from app.core.enums import UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    role: UserRole


class CurrentUser(BaseModel):
    id: int
    username: str
    role: UserRole
