from typing import Any

import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest_asyncio.fixture
async def guest_diary(client: AsyncClient) -> str:
    response = await client.post(
        url="/guest/diary", json={"diary_name": "Calisthenics"}
    )
    guest_token = response.cookies["guest"]
    return guest_token


@pytest_asyncio.fixture
async def training_day(
    client: AsyncClient, guest_diary: str
) -> tuple[dict[str, Any], str]:
    guest_token = guest_diary
    client.cookies.set(name="guest", value=guest_token)
    response = await client.post(
        url="/guest/diary/training-day", json={"date": "2026-08-20T20:04:00"}
    )
    data = response.json()
    return data["training_days"][0], guest_token


@pytest_asyncio.fixture
async def circuit(
    client: AsyncClient, training_day: tuple[dict[str, Any], str]
) -> tuple[dict[str, Any], int, str]:
    tr_day_data, guest_token = training_day
    tr_day_id: int = tr_day_data["id"]
    client.cookies.set(name="guest", value=guest_token)

    response = await client.post(url=f"/guest/diary/training-day/{tr_day_id}/circuit")
    data = response.json()
    circuit_data = data["training_days"][0]["circuits"][0]
    return circuit_data, tr_day_id, guest_token


@pytest_asyncio.fixture
async def exercise(
    client: AsyncClient, test_exercise: Any, circuit: tuple[dict[str, Any], int, str]
) -> tuple[int, int, int, str]:
    circuit_data, tr_day_id, guest_token = circuit
    circuit_id: int = circuit_data["id"]
    exercise_id: int = test_exercise.id

    exercise_data = {"exercise_id": exercise_id}
    client.cookies.set(name="guest", value=guest_token)
    await client.post(
        url=f"/guest/diary/training-day/{tr_day_id}/circuit/{circuit_id}/exercise",
        json=exercise_data,
    )

    return tr_day_id, circuit_id, exercise_id, guest_token


# ----------------------------------------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_guest_diary(client: AsyncClient) -> None:
    response = await client.post(
        url="/guest/diary", json={"diary_name": "Calisthenics"}
    )
    data = response.json()

    assert response.status_code == 200
    assert "guest" in response.cookies.keys()
    assert "diary_name" in data


@pytest.mark.asyncio
async def test_add_tr_day(client: AsyncClient, guest_diary: str) -> None:
    guest_token = guest_diary
    client.cookies.set(name="guest", value=guest_token)
    tr_day_data = {"date": "2026-08-20T20:00:00"}

    response = await client.post(url="/guest/diary/training-day", json=tr_day_data)
    data = response.json()

    assert response.status_code == 200
    assert data["diary_name"] == "Calisthenics"
    assert data["training_days"] is not None


@pytest.mark.asyncio
async def test_add_circuit(
    client: AsyncClient, training_day: tuple[dict[str, Any], str]
) -> None:
    tr_day_data, guest_token = training_day
    client.cookies.set(name="guest", value=guest_token)

    response = await client.post(
        url=f"/guest/diary/training-day/{tr_day_data['id']}/circuit"
    )
    data = response.json()

    assert response.status_code == 200
    assert data["training_days"][0]["circuits"][0]["numberation"] == 1


@pytest.mark.asyncio
async def test_add_completed_exercise(
    client: AsyncClient, test_exercise: Any, circuit: tuple[dict[str, Any], int, str]
) -> None:
    circuit_data, tr_day_id, guest_token = circuit
    client.cookies.set(name="guest", value=guest_token)

    exercise_data = {"exercise_id": test_exercise.id}
    response = await client.post(
        url=f"/guest/diary/training-day/{tr_day_id}/circuit/{circuit_data['id']}/exercise",
        json=exercise_data,
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_guest_diary(client: AsyncClient, guest_diary: str) -> None:
    guest_token = guest_diary
    client.cookies.set(name="guest", value=guest_token)

    response = await client.get("/guest/diary")
    data = response.json()

    assert response.status_code == 200
    assert data["diary_name"] == "Calisthenics"


@pytest.mark.asyncio
async def test_delete_guest_diary(client: AsyncClient, guest_diary: str) -> None:
    guest_token = guest_diary
    client.cookies.set(name="guest", value=guest_token)

    response = await client.delete(url="/guest/diary")

    assert response.status_code == 200
    assert "guest" not in response.cookies.keys()


@pytest.mark.asyncio
async def test_delete_training_day(
    client: AsyncClient, training_day: tuple[dict[str, Any], str]
) -> None:
    tr_day_data, guest_token = training_day
    client.cookies.set(name="guest", value=guest_token)

    response = await client.delete(url=f"/guest/diary/training-day/{tr_day_data['id']}")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_circuit(
    client: AsyncClient, circuit: tuple[dict[str, Any], int, str]
) -> None:
    circuit_data, tr_day_id, guest_token = circuit
    client.cookies.set(name="guest", value=guest_token)

    response = await client.delete(
        url=f"/guest/diary/training-day/{tr_day_id}/circuit/{circuit_data['id']}"
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_exercise(
    client: AsyncClient, exercise: tuple[int, int, int, str]
) -> None:
    tr_day_id, circuit_id, exercise_id, guest_token = exercise

    client.cookies.set(name="guest", value=guest_token)
    response = await client.delete(
        url=f"/guest/diary/training-day/{tr_day_id}/circuit/{circuit_id}/exercise/{exercise_id}"
    )

    assert response.status_code == 200
