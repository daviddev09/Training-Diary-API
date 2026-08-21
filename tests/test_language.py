import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_change_language(client: AsyncClient) -> None:
    response = await client.patch(url="/language/set", params={"lang_code": "ru"})
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "success"
    assert data["current_language"] == "ru"


@pytest.mark.asyncio
async def test_get_translations_for_frontend(client: AsyncClient) -> None:
    response = await client.get(url="/language/translations")

    assert response.status_code == 200
