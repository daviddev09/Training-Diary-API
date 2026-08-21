from typing import Any

import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest_asyncio.fixture
async def training_day(
    client: AsyncClient, test_diary: Any, user_access_token: str
) -> dict[str, Any]:
    training_day_data: dict[str, Any] = {
        "date": "2026-08-21T00:00:00",
        "difficulty": "easy",
        "total_time_seconds": 3000,
    }
    header = {"Authorization": f"Bearer {user_access_token}"}
    response = await client.post(
        url=f"/diaries/{test_diary.id}/training-day",
        json=training_day_data,
        headers=header,
    )
    return response.json()


@pytest_asyncio.fixture
async def circuit(
    client: AsyncClient, training_day: dict[str, Any], user_access_token: str
) -> dict[str, Any]:
    diary_id, tr_day_id = training_day["diary_id"], training_day["id"]
    header = {"Authorization": f"Bearer {user_access_token}"}

    response = await client.post(
        url=f"/diaries/{diary_id}/days/{tr_day_id}", headers=header
    )
    return response.json()


@pytest_asyncio.fixture
async def completed_exercise(
    client: AsyncClient,
    test_exercise: Any,
    circuit: dict[str, Any],
    user_access_token: str,
) -> tuple[int, int, int]:
    tr_day_id, circuit_id = circuit["training_day_id"], circuit["id"]
    header = {"Authorization": f"Bearer {user_access_token}"}
    compl_exercise_data: dict[str, Any] = {
        "exercise_id": test_exercise.id,
        "duration_seconds": 100,
        "rest_seconds": 300,
    }
    response = await client.post(
        url=f"/diaries/days/{tr_day_id}/circuits/{circuit_id}/exercise",
        json=[compl_exercise_data],
        headers=header,
    )
    return tr_day_id, circuit_id, response.json()[0]["id"]


# ---------------------------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_diary(client: AsyncClient, user_access_token: str) -> None:
    diary_data = {"diary_name": "Calisthenics"}
    response = await client.post(
        url="/diaries",
        json=diary_data,
        headers={"Authorization": f"Bearer {user_access_token}"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["id"]


@pytest.mark.asyncio
async def test_add_training_day(
    client: AsyncClient, test_diary: Any, user_access_token: str
) -> None:
    training_day_data: dict[str, Any] = {
        "date": "2026-08-21T00:00:00",
        "difficulty": "easy",
        "total_time_seconds": 3000,
    }
    header = {"Authorization": f"Bearer {user_access_token}"}
    response = await client.post(
        url=f"/diaries/{test_diary.id}/training-day",
        json=training_day_data,
        headers=header,
    )
    data = response.json()

    assert response.status_code == 200
    assert data["diary_id"] == test_diary.id


@pytest.mark.asyncio
async def test_add_circuit(
    client: AsyncClient, training_day: dict[str, Any], user_access_token: str
) -> None:
    diary_id, tr_day_id = training_day["diary_id"], training_day["id"]
    header = {"Authorization": f"Bearer {user_access_token}"}

    response = await client.post(
        url=f"/diaries/{diary_id}/days/{tr_day_id}", headers=header
    )
    data = response.json()

    assert response.status_code == 200
    assert data["numberation"] == 1
    assert data["training_day_id"] == tr_day_id


@pytest.mark.asyncio
async def test_add_completed_exercise(
    client: AsyncClient,
    test_exercise: Any,
    circuit: dict[str, Any],
    user_access_token: str,
) -> None:
    tr_day_id, circuit_id = circuit["training_day_id"], circuit["id"]
    header = {"Authorization": f"Bearer {user_access_token}"}
    compl_exercise_data: dict[str, Any] = {
        "exercise_id": test_exercise.id,
        "duration_seconds": 100,
        "rest_seconds": 300,
    }
    response = await client.post(
        url=f"/diaries/days/{tr_day_id}/circuits/{circuit_id}/exercise",
        json=[compl_exercise_data],
        headers=header,
    )
    data = response.json()

    assert response.status_code == 200
    assert type(data) == list
    assert data[0]["id"]
    assert data[0]["exercise_id"] == test_exercise.id


@pytest.mark.asyncio
async def test_get_diary(
    client: AsyncClient, test_diary: Any, user_access_token: str
) -> None:
    header = {"Authorization": f"Bearer {user_access_token}"}

    response = await client.get(url=f"/diaries/{test_diary.id}", headers=header)
    data = response.json()

    assert response.status_code == 200
    assert data["diary_name"] == "Calisthenics"


@pytest.mark.asyncio
async def test_get_diaries(
    client: AsyncClient, test_diary: Any, user_access_token: str
) -> None:
    header = {"Authorization": f"Bearer {user_access_token}"}

    response = await client.get(url="/diaries", headers=header)
    data = response.json()

    assert response.status_code == 200
    assert type(data) == list
    assert data[0]["diary_name"] == "Calisthenics"


@pytest.mark.asyncio
async def test_update_diary(
    client: AsyncClient, test_diary: Any, user_access_token: str
) -> None:
    header = {"Authorization": f"Bearer {user_access_token}"}
    update_data = {"diary_name": "Boxing"}

    response = await client.patch(
        url=f"/diaries/{test_diary.id}", json=update_data, headers=header
    )
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == test_diary.id
    assert data["diary_name"] != test_diary.diary_name


@pytest.mark.asyncio
async def test_update_training_day(
    client: AsyncClient, training_day: dict[str, Any], user_access_token: str
) -> None:
    diary_id, tr_day_id = training_day["diary_id"], training_day["id"]
    header = {"Authorization": f"Bearer {user_access_token}"}
    update_data: dict[str, Any] = {
        "date": "2026-08-21T01:00:00",
        "difficulty": "medium",
        "total_time_seconds": 3000,
    }

    response = await client.patch(
        url=f"/diaries/{diary_id}/days/{tr_day_id}", json=update_data, headers=header
    )
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == tr_day_id
    assert data["date"] != training_day["date"]
    assert data["difficulty"] != training_day["difficulty"]
    assert data["total_time_seconds"] == training_day["total_time_seconds"]


@pytest.mark.asyncio
async def test_update_completed_exercise(
    client: AsyncClient,
    completed_exercise: tuple[int, int, int],
    user_access_token: str,
) -> None:
    tr_day_id, circuit_id, compl_exercise_id = (
        completed_exercise[0],
        completed_exercise[1],
        completed_exercise[2],
    )
    header = {"Authorization": f"Bearer {user_access_token}"}
    update_data = {"duration_seconds": 200, "rest_seconds": 600}

    response = await client.patch(
        url=f"/diaries/days/{tr_day_id}/circuits/{circuit_id}/exercises/{compl_exercise_id}",
        json=update_data,
        headers=header,
    )
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == compl_exercise_id


@pytest.mark.asyncio
async def test_delete_diary(
    client: AsyncClient, test_diary: Any, user_access_token: str
) -> None:
    header = {"Authorization": f"Bearer {user_access_token}"}
    response = await client.delete(url=f"/diaries/{test_diary.id}", headers=header)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_training_day(
    client: AsyncClient, training_day: dict[str, Any], user_access_token: str
) -> None:
    diary_id, tr_day_id = training_day["diary_id"], training_day["id"]
    header = {"Authorization": f"Bearer {user_access_token}"}

    response = await client.delete(
        url=f"/diaries/{diary_id}/days/{tr_day_id}", headers=header
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_circuit(
    client: AsyncClient, circuit: dict[str, Any], user_access_token: str
) -> None:
    tr_day_id, circuit_id = circuit["training_day_id"], circuit["id"]
    header = {"Authorization": f"Bearer {user_access_token}"}

    response = await client.delete(
        url=f"/diaries/days/{tr_day_id}/circuits/{circuit_id}", headers=header
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_completed_exercise(
    client: AsyncClient,
    completed_exercise: tuple[int, int, int],
    user_access_token: str,
) -> None:
    tr_day_id, circuit_id, compl_exercise_id = (
        completed_exercise[0],
        completed_exercise[1],
        completed_exercise[2],
    )
    header = {"Authorization": f"Bearer {user_access_token}"}

    response = await client.delete(
        url=f"/diaries/days/{tr_day_id}/circuits/{circuit_id}/exercises/{compl_exercise_id}",
        headers=header,
    )

    assert response.status_code == 200
