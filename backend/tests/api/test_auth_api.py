import pytest
from uuid import uuid4

pytestmark = pytest.mark.asyncio

@pytest.mark.asyncio
async def test_register_user(app_client):
    """Тест регистрации пользователя."""
    # Готовим тестовые данные
    test_data = {
        "email": f"test_{uuid4()}@example.com",
        "username": f"testuser_{uuid4()}",
        "full_name": "Тестовый Пользователь",
        "password": "StrongPass123!"
    }
    
    # Отправляем запрос на регистрацию
    response = await app_client.post(
        "/api/v1/auth/register",
        json=test_data
    )
    
    # Проверяем ответ
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_data["email"]
    assert data["username"] == test_data["username"]
    assert data["full_name"] == test_data["full_name"]
    assert "id" in data
    assert "hashed_password" not in data

@pytest.mark.asyncio
async def test_login(app_client):
    """Тест входа в систему."""
    # Готовим тестовые данные
    test_email = f"test_{uuid4()}@example.com"
    test_password = "StrongPass456!"
    test_data = {
        "email": test_email,
        "username": f"testuser_{uuid4()}",
        "full_name": "Тестовый Пользователь",
        "password": test_password
    }
    
    # Сначала регистрируем пользователя
    reg_response = await app_client.post(
        "/api/v1/auth/register",
        json=test_data
    )
    assert reg_response.status_code == 201
    
    # Затем пробуем войти
    login_response = await app_client.post(
        "/api/v1/auth/login",
        json={
            "email": test_email,
            "password": test_password
        }
    )
    
    # Проверяем ответ
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    # Может иметь 'bearer' или 'Bearer' в зависимости от реализации
    assert tokens.get("token_type", "").lower() == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(app_client):
    """Тест входа с неверными учетными данными."""
    # Готовим тестовые данные
    test_email = f"test_{uuid4()}@example.com"
    
    # Пытаемся войти с несуществующими данными
    login_response = await app_client.post(
        "/api/v1/auth/login",
        json={
            "email": test_email,
            "password": "WrongPassword123!"
        }
    )
    
    # Проверяем, что вход не выполнен
    assert login_response.status_code == 401

@pytest.mark.asyncio
async def test_refresh_token(app_client, test_user):
    """Тест обновления токена доступа по refresh токену."""
    # Используем refresh токен из фикстуры test_user
    refresh_data = {
        "refresh_token": test_user["refresh_token"]
    }
    
    # Отправляем запрос на обновление токена
    refresh_response = await app_client.post(
        "/api/v1/auth/refresh",
        json=refresh_data
    )
    
    # Проверяем ответ
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()
    assert "access_token" in new_tokens
    assert new_tokens["access_token"] != test_user["access_token"]

@pytest.mark.asyncio
async def test_protected_endpoint(app_client, auth_headers):
    """Тест доступа к защищенным эндпоинтам."""
    # Проверяем доступ к защищенному эндпоинту /api/v1/users/me
    response = await app_client.get(
        "/api/v1/users/me",
        headers=auth_headers
    )
    
    # Проверяем успешный ответ
    assert response.status_code == 200
    user_data = response.json()
    assert "id" in user_data
    assert "email" in user_data 