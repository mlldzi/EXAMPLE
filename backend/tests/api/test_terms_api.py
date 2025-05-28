import pytest
from httpx import AsyncClient
from uuid import uuid4

from app.models.term import TermCreate, TermUpdate

# Предполагаем, что у вас есть фикстуры app_client и auth_headers в conftest.py

@pytest.mark.asyncio
async def test_create_term_api(app_client: AsyncClient, auth_headers: dict):
    """Тест создания термина через API."""
    term_data = {
        "name": "API Тестовый термин",
        "definition": "Определение тестового термина через API"
    }
    
    response = await app_client.post(
        "/api/v1/terms/",
        json=term_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    created_term = response.json()
    
    assert created_term["name"] == term_data["name"]
    assert created_term["current_definition"] == term_data["definition"]
    assert created_term["is_approved"] is False
    assert "id" in created_term
    assert "created_at" in created_term
    assert "updated_at" in created_term
    assert len(created_term["definitions_history"]) == 1
    assert created_term["definitions_history"][0]["definition"] == term_data["definition"]

@pytest.mark.asyncio
async def test_create_term_api_unauthenticated(app_client: AsyncClient):
    """Тест создания термина без аутентификации."""
    term_data = {
        "name": "Неаутентифицированный термин",
        "definition": "Определение"
    }
    
    response = await app_client.post(
        "/api/v1/terms/",
        json=term_data
    )
    
    assert response.status_code == 401 # Unauthorized

@pytest.mark.asyncio
async def test_get_term_by_id_api(app_client: AsyncClient, auth_headers: dict):
    """Тест получения термина по ID через API."""
    # Сначала создаем термин
    create_response = await app_client.post(
        "/api/v1/terms/",
        json={
            "name": "Термин для получения по ID API",
            "definition": "Определение"
        },
        headers=auth_headers
    )
    assert create_response.status_code == 201
    created_term_id = create_response.json()["id"]
    
    # Теперь получаем его по ID
    get_response = await app_client.get(
        f"/api/v1/terms/{created_term_id}",
        headers=auth_headers
    )
    
    assert get_response.status_code == 200
    found_term = get_response.json()
    
    assert found_term["id"] == created_term_id
    assert found_term["name"] == "Термин для получения по ID API"

@pytest.mark.asyncio
async def test_get_term_by_id_api_not_found(app_client: AsyncClient, auth_headers: dict):
    """Тест получения несуществующего термина по ID через API."""
    fake_term_id = uuid4()
    
    get_response = await app_client.get(
        f"/api/v1/terms/{fake_term_id}",
        headers=auth_headers
    )
    
    assert get_response.status_code == 404 # Not Found

@pytest.mark.asyncio
async def test_get_terms_api(app_client: AsyncClient, auth_headers: dict):
    """Тест получения списка терминов через API."""
    # Создаем несколько терминов
    await app_client.post("/api/v1/terms/", json={"name": "Список термин 1", "definition": "Опр 1"}, headers=auth_headers)
    await app_client.post("/api/v1/terms/", json={"name": "Список термин 2", "definition": "Опр 2"}, headers=auth_headers)
    
    get_response = await app_client.get(
        "/api/v1/terms/",
        headers=auth_headers
    )
    
    assert get_response.status_code == 200
    terms = get_response.json()
    
    assert isinstance(terms, list)
    assert len(terms) >= 2 # Могут быть термины из других тестов
    
    # Проверяем наличие созданных терминов по именам
    term_names = [t["name"] for t in terms]
    assert "Список термин 1" in term_names
    assert "Список термин 2" in term_names

@pytest.mark.asyncio
async def test_update_term_api(app_client: AsyncClient, auth_headers: dict):
    """Тест обновления термина через API."""
    # Сначала создаем термин
    create_response = await app_client.post(
        "/api/v1/terms/",
        json={
            "name": "Термин для обновления API",
            "definition": "Старое определение API"
        },
        headers=auth_headers
    )
    assert create_response.status_code == 201
    created_term = create_response.json()
    created_term_id = created_term["id"]
    original_updated_at = created_term["updated_at"]
    
    # Данные для обновления
    update_data = {
        "name": "Обновленный термин API", 
        "definition": "Новое определение API",
        "is_approved": True
    }
    
    update_response = await app_client.put(
        f"/api/v1/terms/{created_term_id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert update_response.status_code == 200
    updated_term = update_response.json()
    
    assert updated_term["id"] == created_term_id
    assert updated_term["name"] == update_data["name"]
    assert updated_term["current_definition"] == update_data["definition"]
    assert updated_term["is_approved"] is True
    assert updated_term["updated_at"] > original_updated_at
    assert len(updated_term["definitions_history"]) == 2 # Старое + новое

@pytest.mark.asyncio
async def test_delete_term_api(app_client: AsyncClient, auth_headers: dict):
    """Тест удаления термина через API."""
    # Сначала создаем термин
    create_response = await app_client.post(
        "/api/v1/terms/",
        json={
            "name": "Термин для удаления API",
            "definition": "Определение для удаления"
        },
        headers=auth_headers
    )
    assert create_response.status_code == 201
    created_term_id = create_response.json()["id"]
    
    # Теперь удаляем его
    delete_response = await app_client.delete(
        f"/api/v1/terms/{created_term_id}",
        headers=auth_headers
    )
    
    assert delete_response.status_code == 200
    delete_result = delete_response.json()
    
    assert delete_result["success"] is True
    assert delete_result["id"] == created_term_id
    
    # Проверяем, что термин удален
    get_response = await app_client.get(
        f"/api/v1/terms/{created_term_id}",
        headers=auth_headers
    )
    
    assert get_response.status_code == 404 # Not Found 