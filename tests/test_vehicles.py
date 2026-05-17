from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from jose import jwt

from app.core.config import settings


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def expired_admin_token() -> str:
    return jwt.encode(
        {
            "sub": "1",
            "role": "admin",
            "username": "admin",
            "exp": datetime.now(UTC) - timedelta(minutes=1),
        },
        settings.secret_key,
        algorithm=settings.algorithm,
    )


@pytest.mark.asyncio
async def test_viewer_can_list_vehicles(client: AsyncClient, viewer_token: str) -> None:
    response = await client.get("/api/v1/vehicles", headers=auth_headers(viewer_token))

    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"][0]["brand"] == "Toyota"
    assert body["data"][0]["arrival_location"] == "Bogota"
    assert body["data"][0]["applicant_name"] == "Laura Gomez"


@pytest.mark.asyncio
async def test_anonymous_user_cannot_list_vehicles(client: AsyncClient) -> None:
    response = await client.get("/api/v1/vehicles")

    body = response.json()

    assert response.status_code == 401
    assert body["success"] is False


@pytest.mark.asyncio
async def test_invalid_token_cannot_list_vehicles(client: AsyncClient) -> None:
    response = await client.get("/api/v1/vehicles", headers=auth_headers("invalid-token"))

    body = response.json()

    assert response.status_code == 401
    assert body["success"] is False


@pytest.mark.asyncio
async def test_expired_token_cannot_list_vehicles(client: AsyncClient) -> None:
    response = await client.get("/api/v1/vehicles", headers=auth_headers(expired_admin_token()))

    body = response.json()

    assert response.status_code == 401
    assert body["success"] is False


@pytest.mark.asyncio
async def test_viewer_cannot_create_vehicle(client: AsyncClient, viewer_token: str) -> None:
    response = await client.post(
        "/api/v1/vehicles",
        json={
            "brand": "Mazda",
            "arrival_location": "Medellin",
            "applicant_name": "Carlos Perez",
        },
        headers=auth_headers(viewer_token),
    )

    body = response.json()

    assert response.status_code == 403
    assert body["success"] is False


@pytest.mark.asyncio
async def test_viewer_cannot_update_vehicle(client: AsyncClient, viewer_token: str) -> None:
    response = await client.patch(
        "/api/v1/vehicles/1",
        json={"brand": "Mazda"},
        headers=auth_headers(viewer_token),
    )

    body = response.json()

    assert response.status_code == 403
    assert body["success"] is False


@pytest.mark.asyncio
async def test_viewer_cannot_delete_vehicle(client: AsyncClient, viewer_token: str) -> None:
    response = await client.delete("/api/v1/vehicles/1", headers=auth_headers(viewer_token))

    body = response.json()

    assert response.status_code == 403
    assert body["success"] is False


@pytest.mark.asyncio
async def test_authenticated_user_can_get_vehicle_detail(client: AsyncClient, viewer_token: str) -> None:
    response = await client.get("/api/v1/vehicles/1", headers=auth_headers(viewer_token))

    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["brand"] == "Toyota"


@pytest.mark.asyncio
async def test_get_vehicle_returns_404_when_missing(client: AsyncClient, viewer_token: str) -> None:
    response = await client.get("/api/v1/vehicles/999", headers=auth_headers(viewer_token))

    body = response.json()

    assert response.status_code == 404
    assert body["success"] is False


@pytest.mark.asyncio
async def test_create_vehicle_rejects_empty_fields(client: AsyncClient, admin_token: str) -> None:
    response = await client.post(
        "/api/v1/vehicles",
        json={
            "brand": "",
            "arrival_location": "",
            "applicant_name": "",
        },
        headers=auth_headers(admin_token),
    )

    body = response.json()

    assert response.status_code == 422
    assert body["success"] is False
    assert len(body["errors"]) == 3


@pytest.mark.asyncio
async def test_create_vehicle_rejects_too_long_fields(client: AsyncClient, admin_token: str) -> None:
    response = await client.post(
        "/api/v1/vehicles",
        json={
            "brand": "A" * 81,
            "arrival_location": "B" * 121,
            "applicant_name": "C" * 121,
        },
        headers=auth_headers(admin_token),
    )

    body = response.json()

    assert response.status_code == 422
    assert body["success"] is False
    assert len(body["errors"]) == 3


@pytest.mark.asyncio
async def test_update_vehicle_rejects_too_long_fields(client: AsyncClient, admin_token: str) -> None:
    response = await client.patch(
        "/api/v1/vehicles/1",
        json={"brand": "A" * 81},
        headers=auth_headers(admin_token),
    )

    body = response.json()

    assert response.status_code == 422
    assert body["success"] is False


@pytest.mark.asyncio
async def test_update_vehicle_returns_404_when_missing(client: AsyncClient, admin_token: str) -> None:
    response = await client.patch(
        "/api/v1/vehicles/999",
        json={"brand": "Mazda"},
        headers=auth_headers(admin_token),
    )

    body = response.json()

    assert response.status_code == 404
    assert body["success"] is False


@pytest.mark.asyncio
async def test_delete_vehicle_returns_404_when_missing(client: AsyncClient, admin_token: str) -> None:
    response = await client.delete("/api/v1/vehicles/999", headers=auth_headers(admin_token))

    body = response.json()

    assert response.status_code == 404
    assert body["success"] is False


@pytest.mark.asyncio
async def test_admin_can_create_update_and_delete_vehicle(client: AsyncClient, admin_token: str) -> None:
    headers = auth_headers(admin_token)

    create_response = await client.post(
        "/api/v1/vehicles",
        json={
            "brand": "Mazda",
            "arrival_location": "Medellin",
            "applicant_name": "Carlos Perez",
        },
        headers=headers,
    )
    created = create_response.json()["data"]

    assert create_response.status_code == 201
    assert created["brand"] == "Mazda"

    update_response = await client.patch(
        f"/api/v1/vehicles/{created['id']}",
        json={"arrival_location": "Cali"},
        headers=headers,
    )
    updated = update_response.json()["data"]

    assert update_response.status_code == 200
    assert updated["arrival_location"] == "Cali"

    delete_response = await client.delete(f"/api/v1/vehicles/{created['id']}", headers=headers)

    assert delete_response.status_code == 200
    assert delete_response.json()["success"] is True

    get_response = await client.get(f"/api/v1/vehicles/{created['id']}", headers=headers)

    assert get_response.status_code == 404
