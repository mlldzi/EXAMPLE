import pytest
from uuid import uuid4

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
    assert tokens["token_type"] == "bearer"

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
async def test_get_current_user(app_client, test_user, auth_headers):
    """Тест получения текущего пользователя."""
    # Делаем запрос на получение текущего пользователя
    response = await app_client.get(
        "/api/v1/users/me",
        headers=auth_headers
    )
    
    # Проверяем ответ
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["id"] == test_user["id"]
    assert user_data["email"] == test_user["email"] 