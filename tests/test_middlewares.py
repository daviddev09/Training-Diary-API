import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_global_ip_rate_limiter_middleware(client: AsyncClient) -> None:
    limit_counter = 0
    while True:
        response = await client.get(url="/")
        if response.status_code == 429:
            break
        limit_counter += 1
    data = response.json()
    assert response.status_code == 429
    assert data["detail"] == "IP rate limit exceeded"
    assert limit_counter == 60


@pytest.mark.asyncio
async def test_global_jwt_rate_limiter_middleware(
    client: AsyncClient, user_access_token: str
) -> None:
    header = {"Authorization": f"Bearer {user_access_token}"}
    limit_counter = 0
    while True:
        response = await client.get(url="/", headers=header)
        if response.status_code == 429:
            break
        limit_counter += 1
    data = response.json()
    assert response.status_code == 429
    assert data["detail"] == "User account rate limit exceeded"
    assert limit_counter == 100


@pytest.mark.asyncio
async def test_register_endpoint_rate_limiter_middleware(client: AsyncClient) -> None:
    limit_counter = 0
    while True:
        response = await client.post(url="/auth/register")
        if response.status_code == 429:
            break
        limit_counter += 1
    data = response.json()
    assert response.status_code == 429
    assert data["detail"] == "Registering limit exceeded"
    assert limit_counter == 5


@pytest.mark.asyncio
async def test_login_endpoint_rate_limiter_middleware(client: AsyncClient) -> None:
    limit_counter = 0
    while True:
        response = await client.post(url="/auth/login")
        if response.status_code == 429:
            break
        limit_counter += 1
    data = response.json()
    assert response.status_code == 429
    assert data["detail"] == "Login limit exceeded"
    assert limit_counter == 5


@pytest.mark.asyncio
async def test_guest_diary_create_endpoint_rate_limiter_middleware(
    client: AsyncClient,
) -> None:
    limit_counter = 0
    while True:
        response = await client.post(url="/guest/diary")
        if response.status_code == 429:
            break
        limit_counter += 1
    data = response.json()
    assert response.status_code == 429
    assert data["detail"] == "Guest diary limit exceeded"
    assert limit_counter == 1


@pytest.mark.asyncio
async def test_generate_diary_pdf_endpoint_rate_limiter_middleware(
    client: AsyncClient, user_access_token: str
) -> None:
    header = {"Authorization": f"Bearer {user_access_token}"}
    limit_counter = 0
    while True:
        response = await client.post("/pdf/diary/1", headers=header)
        if response.status_code == 429:
            break
        limit_counter += 1
    data = response.json()
    assert response.status_code == 429
    assert data["detail"] == "Generate pdf limit exceeded"
    assert limit_counter == 1
