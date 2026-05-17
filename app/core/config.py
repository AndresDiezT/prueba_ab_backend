from functools import lru_cache
import json
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str
    environment: Literal["local", "staging", "production"] = "local"
    debug: bool

    api_v1_prefix: str
    database_url: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    cors_origins: str
    log_file_path: str = "logs/app.log"
    log_max_bytes: int = 1_000_000
    log_backup_count: int = 5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        # Permite usar CORS_ORIGINS como lista JSON o como valores separados por coma.
        if not self.cors_origins:
            return []
        if self.cors_origins.startswith("["):
            return [str(origin) for origin in json.loads(self.cors_origins)]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value: bool | str) -> bool | str:
        if isinstance(value, str) and value.lower() in {"release", "production", "prod"}:
            return False
        return value

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        # Render entrega URLs postgres:// o postgresql://; SQLAlchemy async requiere asyncpg.
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+asyncpg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
