from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient

from app.core.languages import LANGUAGES

language = LANGUAGES["ru"]


@pytest.mark.asyncio
async def test_register_and_verify(client: AsyncClient, mock_celery: MagicMock) -> None:
    register_data: dict[str, str | int] = {
        "name": "user",
        "username": "@user",
        "email": "user@gmail.com",
        "password": "userpass123",
        "age": 18,
        "current_weight": 100,
    }
    response_reg = await client.post(url="/auth/register", json=register_data)
    reg_data = response_reg.json()
    task_name = mock_celery.call_args[0][0]

    assert response_reg.status_code == 200
    mock_celery.assert_called_once()
    assert task_name == "app.workers.smtp_worker.send_confirmation_code"
    assert reg_data["message"] == language.register_verification_code_sended

    verify_data = {"email": "user@gmail.com", "code": "1234"}
    response_verify = await client.post(url="/auth/register/verify", params=verify_data)

    assert response_verify.status_code == 200
    ver_data = response_verify.json()
    assert ver_data["name"] == "user"


@pytest.mark.asyncio
async def test_login(client: AsyncClient, test_user: None) -> None:
    login_data = {"username": "@user", "password": "userpass123"}
    response = await client.post(url="/auth/login", data=login_data)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_logout(
    client: AsyncClient, user_access_token: str, user_refresh_token: str
) -> None:
    response = await client.post(
        url="/auth/logout",
        headers={"Authorization": f"Bearer {user_access_token}"},
        cookies=({"refresh_token": user_refresh_token}),
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_refresh(client: AsyncClient, test_user: None) -> None:
    login_response = await client.post(
        url="/auth/login", data={"username": "@user", "password": "userpass123"}
    )
    refresh_token = login_response.cookies["refresh_token"]
    access_token = login_response.json()["access_token"]

    client.cookies.set(name="refresh_token", value=refresh_token)
    response = await client.post(
        url="/auth/refresh", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
