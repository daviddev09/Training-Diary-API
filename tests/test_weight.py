from typing import Any

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_add_weight(client: AsyncClient, user_access_token: str) -> None:
    data: dict[str, Any] = {"weight": 100, "added_at": "2026-08-20T21:00:00"}
    response = await client.post(
        url="/weights",
        json=data,
        headers={"Authorization": f"Bearer {user_access_token}"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["weight"] == 100


@pytest.mark.asyncio
async def test_get_weight(
    client: AsyncClient, test_weight: Any, user_access_token: str
) -> None:
    response = await client.get(
        url=f"/weights/{test_weight.id}",
        headers={"Authorization": f"Bearer {user_access_token}"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["weight"] == 100


@pytest.mark.asyncio
async def test_get_weights(
    client: AsyncClient, test_weight: Any, user_access_token: str
) -> None:
    response = await client.get(
        url="/weights", headers={"Authorization": f"Bearer {user_access_token}"}
    )
    data = response.json()

    assert response.status_code == 200
    assert type(data) == list
    assert data is not None


@pytest.mark.asyncio
async def test_update_weight(
    client: AsyncClient, test_weight: Any, user_access_token: str
) -> None:
    new_weight_data: dict[str, Any] = {
        "weight": 100.100,
        "added_at": "2026-08-20T00:00:00",
    }
    response = await client.patch(
        url=f"/weights/{test_weight.id}",
        json=new_weight_data,
        headers={"Authorization": f"Bearer {user_access_token}"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["weight"] != test_weight.weight
    assert data["added_at"] != test_weight.added_at


@pytest.mark.asyncio
async def test_delete_weight(
    client: AsyncClient, test_weight: Any, user_access_token: str
) -> None:
    response = await client.delete(
        url=f"/weights/{test_weight.id}",
        headers={"Authorization": f"Bearer {user_access_token}"},
    )

    assert response.status_code == 200
