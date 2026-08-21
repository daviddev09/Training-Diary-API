from typing import Any

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_users_paginate(
    client: AsyncClient, test_user: None, admin_access_token: str
) -> None:
    response = await client.get(
        url="/admin/users/page/1",
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )
    data = response.json()

    assert response.status_code == 200
    assert type(data) == list


@pytest.mark.asyncio
async def test_grant_admin_rights(
    client: AsyncClient, test_user: Any, owner_access_token: str
) -> None:
    response = await client.patch(
        url="/admin/grant",
        params={"user_uuid": test_user.uuid},
        headers={"Authorization": f"Bearer {owner_access_token}"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == test_user.name
    assert data["role"] == "admin"


@pytest.mark.asyncio
async def test_revoke_admin_rights(
    client: AsyncClient, admin_user: Any, owner_access_token: str
) -> None:
    response = await client.patch(
        url="/admin/revoke",
        params={"user_uuid": admin_user.uuid},
        headers={"Authorization": f"Bearer {owner_access_token}"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == admin_user.name
    assert data["role"] == "user"


@pytest.mark.asyncio
async def test_delete_user(
    client: AsyncClient, test_user: Any, admin_access_token: str
) -> None:
    response = await client.delete(
        url="/admin/user",
        params={"user_uuid": test_user.uuid},
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )

    assert response.status_code == 200
