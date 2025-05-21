import pytest
import pytest_asyncio
import os
import sys
import asyncio
import httpx
from typing import AsyncGenerator
import uuid
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

# Добавляем родительские директории в путь для импорта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

# Импортируем необходимые модули
from app.models.user import UserCreate, UserRole
from app.core.config import settings
from app.db.session import db_client, connect_to_mongo, close_mongo_connection

# Устанавливаем переменные окружения для тестов
os.environ["JWT_SECRET_KEY"] = "test_secret_key_for_tests"
os.environ["TESTING"] = "True"

# Используем тестовую MongoDB для юнит-тестов
TEST_MONGO_URI = "mongodb://localhost:27017/"
TEST_DB_NAME = "testdb"

@pytest_asyncio.fixture
async def db_client_fixture() -> AsyncGenerator:
    """
    Создает клиент базы данных для тестов, используя локальный MongoDB.
    При необходимости используйте Docker или testcontainers в реальных проектах.
    """
    # Сохраняем оригинальные настройки
    original_mongo_uri = settings.MONGO_URI
    original_db_name = settings.MONGO_DB_NAME
    
    # Устанавливаем тестовые настройки
    settings.MONGO_URI = TEST_MONGO_URI
    settings.MONGO_DB_NAME = TEST_DB_NAME
    
    # Инициализируем глобальную переменную db_client для всего приложения
    await connect_to_mongo()
    
    # Создаем клиент для тестов
    client = AsyncIOMotorClient(
        settings.MONGO_URI,
        uuidRepresentation='standard',
        serverSelectionTimeoutMS=5000  # Увеличиваем тайм-аут выбора сервера
    )
    
    try:
        # Проверяем соединение
        await client.admin.command('ping')
        
        # Очищаем тестовую базу данных перед каждым тестом
        try:
            await client.drop_database(TEST_DB_NAME)
            
            # Пересоздаем БД и пересоздаем индексы (после очистки)
            await connect_to_mongo()
        except Exception as e:
            print(f"Ошибка при очистке базы данных: {e}")
        
        yield client
    except Exception as e:
        print(f"Ошибка подключения к MongoDB: {e}")
        # Для юнит-тестов можно использовать моки вместо реальной БД
        # если соединение не установлено
        yield None
    finally:
        # Закрываем соединения
        client.close()
        await close_mongo_connection()
        
        # Восстанавливаем настройки
        settings.MONGO_URI = original_mongo_uri
        settings.MONGO_DB_NAME = original_db_name

@pytest_asyncio.fixture
async def db(db_client_fixture) -> AsyncGenerator:
    """Предоставляет тестовую базу данных и создает необходимые индексы."""
    if db_client_fixture is None:
        # Для случаев когда MongoDB недоступна
        yield None
        return
    
    # Используем базу данных из глобального клиента для совместимости с app.db.session
    # Это важно, чтобы избежать ошибки "Database not initialized"
    test_db = db_client.db
    
    yield test_db
    
    # НЕ очищаем базу данных после теста, чтобы избежать конфликтов с созданием индексов
    # Очистка будет происходить в начале следующего теста в db_client

@pytest_asyncio.fixture
async def app_client(db) -> AsyncGenerator:
    """Создает тестовый клиент FastAPI."""
    # Импортируем здесь, чтобы использовать правильные настройки БД
    from app.main import app
    
    # Создаем асинхронный клиент с явным указанием транспорта
    # Это избавит от предупреждений о deprecation
    async with AsyncClient(
        base_url="http://test",
        transport=httpx.ASGITransport(app=app)
    ) as client:
        yield client

@pytest_asyncio.fixture
async def test_user(app_client) -> dict:
    """Создает тестового пользователя и возвращает его данные."""
    # Генерируем уникальные данные для каждого теста
    test_email = f"test_{uuid.uuid4()}@example.com"
    test_password = "Test_password123!"
    username = f"test_user_{uuid.uuid4()}"
    
    # Создаем пользователя
    user_data = UserCreate(
        email=test_email,
        username=username,
        full_name="Test User",
        password=test_password
    )
    
    # Регистрируем пользователя через API
    register_response = await app_client.post(
        "/api/v1/auth/register",
        json=user_data.model_dump(exclude={"roles"})
    )
    
    assert register_response.status_code == 201, f"Ошибка при регистрации: {register_response.text}"
    
    user_response = register_response.json()
    
    # Получаем токены
    login_response = await app_client.post(
        "/api/v1/auth/login",
        json={"email": test_email, "password": test_password}
    )
    
    assert login_response.status_code == 200, f"Ошибка при логине: {login_response.text}"
    tokens = login_response.json()
    
    # Возвращаем данные для использования в тестах
    return {
        "id": user_response["id"],
        "email": test_email,
        "username": username,
        "password": test_password,
        "access_token": tokens["access_token"],
        "refresh_token": tokens.get("refresh_token"),
    }

@pytest_asyncio.fixture
async def admin_user(app_client, db) -> dict:
    """Создает тестового администратора и возвращает его данные."""
    test_email = f"admin_{uuid.uuid4()}@example.com"
    test_password = "Admin_password123!"
    username = f"admin_user_{uuid.uuid4()}"

    user_data = UserCreate(
        email=test_email,
        username=username,
        full_name="Admin User",
        password=test_password
    )

    register_response = await app_client.post(
        "/api/v1/auth/register",
        json=user_data.model_dump()
    )
    assert register_response.status_code == 201, f"Ошибка при регистрации админа: {register_response.text}"
    user_response_data = register_response.json()
    user_id_str = user_response_data["id"]

    # Обновляем роль пользователя на ADMIN в базе данных
    # Это нужно делать до логина, чтобы токен содержал правильные роли
    if db is not None:
        user_collection = db["users"]
        await user_collection.update_one(
            {"id": uuid.UUID(user_id_str)}, # Исправлено: используем "id" вместо "_id"
            {"$set": {"roles": [UserRole.ADMIN.value]}}
        )
        # Проверка, что пользователь действительно обновлен (опционально)
        # updated_user_doc = await user_collection.find_one({"id": uuid.UUID(user_id_str)})
        # print(f"Updated admin user in DB: {updated_user_doc}")
    else:
        raise Exception("DB fixture is not available for admin_user setup")

    # Логинимся как админ, чтобы получить токен с ролью ADMIN
    login_response = await app_client.post(
        "/api/v1/auth/login",
        json={"email": test_email, "password": test_password}
    )
    assert login_response.status_code == 200, f"Ошибка при логине админа: {login_response.text}"
    tokens = login_response.json()

    return {
        "id": user_id_str,
        "email": test_email,
        "username": username,
        "password": test_password,
        "access_token": tokens["access_token"],
        "refresh_token": tokens.get("refresh_token"),
        "roles": [UserRole.ADMIN.value] # Добавляем роли для удобства
    }

@pytest_asyncio.fixture
async def admin_auth_headers(admin_user) -> dict:
    """Возвращает заголовки авторизации для тестового администратора."""
    return {"Authorization": f"Bearer {admin_user['access_token']}"}

@pytest_asyncio.fixture
async def auth_headers(test_user) -> dict:
    """Возвращает заголовки авторизации для тестового пользователя."""
    return {"Authorization": f"Bearer {test_user['access_token']}"} 