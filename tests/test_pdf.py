from typing import Any
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest_asyncio.fixture
async def add_training_day(
    client: AsyncClient, test_diary: Any, user_access_token: str
) -> int:
    tr_day_data: dict[str, Any] = {
        "date": "2026-08-21T00:00:00",
        "difficulty": "hard",
        "total_time_seconds": 3000,
    }
    header = {"Authorization": f"Bearer {user_access_token}"}
    await client.post(
        url=f"/diaries/{test_diary.id}/training-day", json=tr_day_data, headers=header
    )
    return test_diary.id


@pytest.mark.asyncio
async def test_generate_diary_pdf(
    client: AsyncClient,
    mock_celery: MagicMock,
    add_training_day: int,
    user_access_token: str,
) -> None:
    diary_id = add_training_day
    header = {"Authorization": f"Bearer {user_access_token}"}
    response = await client.post(url=f"/pdf/diary/{diary_id}", headers=header)

    assert response.status_code == 200
    mock_celery.assert_called_once()

    called_task_name = mock_celery.call_args[0][0]
    assert called_task_name == "app.workers.pdf_worker.create_pdf_diary"
