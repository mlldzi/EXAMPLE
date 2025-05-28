import pytest
import uuid
from motor.motor_asyncio import AsyncIOMotorDatabase

pytestmark = pytest.mark.asyncio

@pytest.mark.asyncio
async def test_db_connection(db_client_fixture):
    """Проверка подключения к MongoDB."""
    if db_client_fixture is None:
        pytest.skip("MongoDB недоступна для тестирования")
    
    # Проверяем, что можем выполнить команду ping
    result = await db_client_fixture.admin.command('ping')
    assert result.get('ok') == 1.0

@pytest.mark.asyncio
async def test_db_crud_operations(db):
    """Проверка базовых CRUD операций с MongoDB."""
    if db is None:
        pytest.skip("MongoDB недоступна для тестирования")
    
    # Готовим тестовые данные
    test_collection = db["test_collection"]
    test_id = str(uuid.uuid4())
    test_data = {"_id": test_id, "name": "Test Item", "value": 42}
    
    # Create
    await test_collection.insert_one(test_data)
    
    # Read
    retrieved_data = await test_collection.find_one({"_id": test_id})
    assert retrieved_data is not None
    assert retrieved_data["name"] == "Test Item"
    assert retrieved_data["value"] == 42
    
    # Update
    await test_collection.update_one(
        {"_id": test_id},
        {"$set": {"value": 100}}
    )
    
    # Проверяем обновление
    updated_data = await test_collection.find_one({"_id": test_id})
    assert updated_data["value"] == 100
    
    # Delete
    delete_result = await test_collection.delete_one({"_id": test_id})
    assert delete_result.deleted_count == 1
    
    # Проверяем удаление
    deleted_check = await test_collection.find_one({"_id": test_id})
    assert deleted_check is None

@pytest.mark.asyncio
async def test_indices(db):
    """Проверка создания индексов."""
    if db is None:
        pytest.skip("MongoDB недоступна для тестирования")
    
    # Проверяем наличие индексов в коллекции users
    # В нашем случае должен быть уникальный индекс по email
    indices = await db.users.index_information()
    
    # Проверяем, есть ли индекс для email
    email_index_exists = False
    for index_name, index_info in indices.items():
        if any("email" in key for key, _ in index_info.get("key", [])):
            email_index_exists = True
            # Проверяем, что индекс уникальный
            if "unique" in index_info and index_info["unique"]:
                assert True
                return
    
    # Если мы дошли до этой точки, значит не нашли уникальный индекс для email
    if not email_index_exists:
        pytest.fail("Не найден индекс для поля email в коллекции users")
    else:
        pytest.fail("Индекс для поля email в коллекции users не является уникальным") 