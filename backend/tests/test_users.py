import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid
from uuid import uuid4

# Импорт моделей
from app.models.user import UserCreate, UserPublic, UserUpdate, UserRole

# Импорт CRUD операций
from app.crud.user import CRUDUser

# Отмечаем все тесты как асинхронные
pytestmark = pytest.mark.asyncio

@pytest.mark.asyncio
async def test_db_connection(db_client_fixture):
    """Проверяем, что подключение к MongoDB работает."""
    assert db_client_fixture is not None
    result = await db_client_fixture.admin.command('ping')
    assert result.get('ok') == 1.0

@pytest.mark.asyncio
async def test_get_users_list_simple(app_client, auth_headers):
    """Упрощенный тест получения списка пользователей."""
    response = await app_client.get(
        "/api/v1/users/",
        headers=auth_headers
    )
    
    # Проверяем успешный ответ
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # Должен быть хотя бы один пользователь (тот, от имени которого делаем запрос)
    assert len(data) > 0

@pytest.mark.asyncio
async def test_get_user_by_id(app_client, test_user, auth_headers):
    """Тест получения пользователя по ID."""
    user_id = test_user["id"]
    
    # Делаем запрос по ID пользователя
    response = await app_client.get(
        f"/api/v1/users/{user_id}",
        headers=auth_headers
    )
    
    # Проверяем ответ
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["id"] == user_id
    assert user_data["email"] == test_user["email"]
    assert user_data["username"] == test_user["username"]

@pytest.mark.asyncio
async def test_create_user_api(app_client):
    """Тест создания нового пользователя через API."""
    test_email = f"test_create_{uuid.uuid4()}@example.com"
    user_data = {
        "email": test_email,
        "password": "securepassword123",
        "username": f"testcreateuser_{uuid.uuid4()}",
        "full_name": "Test Create User"
    }
    response = await app_client.post("/api/v1/users/", json=user_data)
    
    assert response.status_code == 201
    created_user_data = response.json()
    assert created_user_data["email"] == user_data["email"]
    assert "is_active" in created_user_data and created_user_data["is_active"] is True

@pytest.mark.asyncio
async def test_create_existing_user(app_client):
    """Тест попытки создания пользователя с уже существующим email."""
    # Генерируем уникальный email
    existing_email = f"existing_{uuid.uuid4()}@example.com"
    
    # Данные для создания пользователя
    user_data = {
        "email": existing_email,
        "password": "securepassword",
        "username": f"existinguser_{uuid.uuid4()}",
        "full_name": "Existing User"
    }
    
    # Создаем пользователя первый раз через API
    create_response = await app_client.post("/api/v1/users/", json=user_data)
    assert create_response.status_code == 201
    
    # Пытаемся создать пользователя с тем же email еще раз
    response = await app_client.post("/api/v1/users/", json=user_data)
    
    # Должны получить ошибку
    assert response.status_code == 400
    response_data = response.json()
    assert "detail" in response_data
    assert "Пользователь с таким email уже существует." in response_data["detail"]

@pytest.mark.asyncio
async def test_get_nonexistent_user(app_client, auth_headers):
    """Тест получения несуществующего пользователя."""
    # Генерируем случайный UUID
    fake_user_id = str(uuid4())
    
    # Делаем запрос с несуществующим ID
    response = await app_client.get(
        f"/api/v1/users/{fake_user_id}",
        headers=auth_headers
    )
    
    # Должен быть статус 404
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_user_api(app_client, test_user, auth_headers):
    """Тест обновления данных пользователя."""
    user_id = test_user["id"]
    
    # Данные для обновления
    update_data = {
        "full_name": "Обновленное Имя",
        "username": f"updated_user_{uuid4()}"
    }
    
    # Отправляем запрос на обновление
    response = await app_client.put(
        f"/api/v1/users/{user_id}",
        json=update_data,
        headers=auth_headers
    )
    
    # Проверяем ответ
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["id"] == user_id
    assert updated_user["full_name"] == update_data["full_name"]
    assert updated_user["username"] == update_data["username"]
    
    # Проверяем, что данные действительно обновились
    get_response = await app_client.get(
        f"/api/v1/users/{user_id}",
        headers=auth_headers
    )
    assert get_response.status_code == 200
    fetched_user = get_response.json()
    assert fetched_user["full_name"] == update_data["full_name"]

@pytest.mark.asyncio
async def test_unauthorized_access(app_client):
    """Тест доступа без авторизации."""
    # Попытка получить список пользователей без токена
    response = await app_client.get("/api/v1/users/")
    
    # Должен быть статус 401
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_user_api(app_client, admin_user, admin_auth_headers, db):
    """Тест удаления пользователя."""
    # Создаем тестового пользователя для удаления
    test_email = f"delete_test_{uuid.uuid4()}@example.com"
    user_data = {
        "email": test_email,
        "password": "DeletePassword123!",
        "username": f"deleteuser_{uuid.uuid4()}",
        "full_name": "Delete Test User"
    }
    
    # Создаем пользователя
    create_response = await app_client.post("/api/v1/users/", json=user_data)
    assert create_response.status_code == 201
    
    created_user = create_response.json()
    user_id = created_user["id"]
    
    # Удаляем пользователя через API
    delete_response = await app_client.delete(
        f"/api/v1/users/{user_id}",
        headers=admin_auth_headers
    )
    
    # Проверяем успешное удаление
    assert delete_response.status_code == 200
    
    # Проверяем, что пользователя больше нет в базе
    user_in_db = await db["users"].find_one({"_id": uuid.UUID(user_id)})
    assert user_in_db is None

# TODO: Добавить тесты для обновления пароля, ролей, и других полей, если применимо.
# TODO: Рассмотреть возможность создания отдельной фикстуры для аутентифицированного клиента. 