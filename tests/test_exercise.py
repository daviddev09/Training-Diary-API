from typing import Any

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_exercise(client: AsyncClient, user_access_token: str) -> None:
    response = await client.post(
        url="/exercises",
        json={"name": "Handstand"},
        headers={"Authorization": f"Bearer {user_access_token}"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["is_system"] == False


@pytest.mark.asyncio
async def test_get_exercise(client: AsyncClient, test_exercise: Any) -> None:
    response = await client.get(url=f"/exercises/{test_exercise.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == test_exercise.name


@pytest.mark.asyncio
async def test_get_exercises_paginated(
    client: AsyncClient, test_exercise: None
) -> None:
    response = await client.get(url="/exercises/page/1")
    data = response.json()

    assert response.status_code == 200
    assert type(data) == list


@pytest.mark.asyncio
async def test_get_exercise_by_ilike_name(
    client: AsyncClient, test_exercise: Any
) -> None:
    response = await client.get(
        url="/exercises", params={"exercise_name": test_exercise.name.upper()}
    )
    data = response.json()

    assert response.status_code == 200
    assert type(data) == list
    assert data is not None


@pytest.mark.asyncio
async def test_user_update_exercise(
    client: AsyncClient, user_access_token: str
) -> None:
    header = {"Authorization": f"Bearer {user_access_token}"}
    exercise_resonse = await client.post(
        url="/exercises", json={"name": "Handstand"}, headers=header
    )
    exercise_data = exercise_resonse.json()
    exercise_id = exercise_data["id"]

    response = await client.patch(
        url=f"/exercises/{exercise_id}",
        json={"name": "L-sit to handstand"},
        headers=header,
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "L-sit to handstand"


@pytest.mark.asyncio
async def test_admin_update_exercise(
    client: AsyncClient, test_exercise: Any, admin_access_token: str
) -> None:
    response = await client.patch(
        url=f"/exercises/admin/{test_exercise.id}",
        json={"name": "L-sit to handstand"},
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] != test_exercise.name


@pytest.mark.asyncio
async def test_delete_exercise(
    client: AsyncClient, test_exercise: Any, admin_access_token: str
) -> None:
    response = await client.delete(
        url=f"/exercises/admin/{test_exercise.id}",
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data is None
