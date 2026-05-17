import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_returns_access_token(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "Admin12345"},
    )

    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["access_token"]
    assert body["data"]["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_rejects_invalid_credentials(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "wrong-password"},
    )

    body = response.json()

    assert response.status_code == 401
    assert body["success"] is False
    assert body["data"] is None


@pytest.mark.asyncio
async def test_public_register_creates_viewer_user(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"username": "new.viewer@example.com", "password": "Viewer12345!"},
    )

    body = response.json()

    assert response.status_code == 201
    assert body["success"] is True
    assert body["data"]["username"] == "new.viewer@example.com"
    assert body["data"]["role"] == "viewer"

    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "new.viewer@example.com", "password": "Viewer12345!"},
    )

    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_public_register_rejects_duplicate_username(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"username": "viewer", "password": "Viewer12345!"},
    )

    body = response.json()

    assert response.status_code == 409
    assert body["success"] is False
