import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, user_access_token: str) -> None:
    response = await client.get(
        url="/users", headers={"Authorization": f"Bearer {user_access_token}"}
    )

    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "user"


@pytest.mark.asyncio
async def test_update_me(client: AsyncClient, user_access_token: str) -> None:
    update_data = {
        "name": "updated",
        "username": "@user_name",
        "password": "userpass123",
    }
    response = await client.patch(
        url="/users",
        json=update_data,
        headers={"Authorization": f"Bearer {user_access_token}"},
    )

    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "updated"
    assert data["username"] == "@user_name"


@pytest.mark.asyncio
async def test_delete_me(client: AsyncClient, user_access_token: str) -> None:
    response = await client.delete(
        url="/users", headers={"Authorization": f"Bearer {user_access_token}"}
    )

    assert response.status_code == 200
