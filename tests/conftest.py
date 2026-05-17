import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-32-characters"
os.environ["CORS_ORIGINS"] = "http://testserver"

# Las variables deben definirse antes de importar la app, porque Settings se instancia al cargar módulos.
from app.db import session as db_session  # noqa: E402
from app.db.session import Base  # noqa: E402
from app.main import app  # noqa: E402
from app.core.enums import UserRole  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.vehicle import Vehicle  # noqa: E402


test_engine = create_async_engine(
    "sqlite+aiosqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False, autoflush=False)
db_session.SessionLocal = TestSessionLocal


@pytest.fixture(autouse=True)
async def reset_database() -> AsyncGenerator[None, None]:
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as db:
        db.add(
            User(
                username="admin",
                hashed_password=hash_password("Admin12345"),
                role=UserRole.ADMIN,
            )
        )
        db.add(
            User(
                username="viewer",
                hashed_password=hash_password("Viewer12345"),
                role=UserRole.VIEWER,
            )
        )
        db.add(
            Vehicle(
                brand="Toyota",
                arrival_location="Bogota",
                applicant_name="Laura Gomez",
            )
        )
        await db.commit()

    yield


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client


async def login(client: AsyncClient, username: str, password: str) -> str:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


@pytest.fixture
async def admin_token(client: AsyncClient) -> str:
    return await login(client, "admin", "Admin12345")


@pytest.fixture
async def viewer_token(client: AsyncClient) -> str:
    return await login(client, "viewer", "Viewer12345")
