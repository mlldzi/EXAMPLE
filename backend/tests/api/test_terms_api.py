import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime, timezone

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

# Вспомогательные функции для тестов связанных сущностей (можно перенести в conftest.py)
async def create_test_document(client: AsyncClient, headers: dict):
    doc_data = {
        "title": f"Тестовый документ для связей {uuid4()}",
        "document_number": f"ТД-{uuid4()}",
        "approval_date": datetime.now(timezone.utc).isoformat()
    }
    response = await client.post("/api/v1/documents/", json=doc_data, headers=headers)
    assert response.status_code == 201
    return response.json()

async def create_test_relation(
    client: AsyncClient, 
    headers: dict, 
    term_id: str, 
    document_id: str,
    definition: str = "Тестовое определение в документе"
):
    relation_data = {
        "term_id": term_id,
        "document_id": document_id,
        "term_definition_in_document": definition
    }
    response = await client.post(
        "/api/v1/term_document_relations/",
        json=relation_data,
        headers=headers
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_get_documents_for_term_api(app_client: AsyncClient, auth_headers: dict):
    """Тест получения списка документов для термина через API."""
    # Создаем тестовый термин
    term = await app_client.post(
        "/api/v1/terms/",
        json={
            "name": "Термин со связанными документами",
            "definition": "Определение"
        },
        headers=auth_headers
    )
    assert term.status_code == 201
    term_id = term.json()["id"]

    # Создаем несколько тестовых документов
    doc1 = await create_test_document(app_client, auth_headers)
    doc2 = await create_test_document(app_client, auth_headers)
    doc3 = await create_test_document(app_client, auth_headers) # Не будем связывать

    # Создаем связи термин-документ
    await create_test_relation(app_client, auth_headers, term_id, doc1["id"])
    await create_test_relation(app_client, auth_headers, term_id, doc2["id"])

    # Получаем список документов для термина
    response = await app_client.get(
        f"/api/v1/terms/{term_id}/documents",
        headers=auth_headers
    )

    assert response.status_code == 200
    documents = response.json()

    assert isinstance(documents, list)
    assert len(documents) == 2 # Ожидаем 2 связанных документа

    # Проверяем, что возвращены правильные документы
    returned_doc_ids = [d["id"] for d in documents]
    assert doc1["id"] in returned_doc_ids
    assert doc2["id"] in returned_doc_ids
    assert doc3["id"] not in returned_doc_ids

@pytest.mark.asyncio
async def test_delete_term_deletes_relations_api(app_client: AsyncClient, auth_headers: dict):
    """Тест: при удалении термина удаляются связанные с ним связи термин-документ."""
    # Создаем тестовый термин
    term = await app_client.post(
        "/api/v1/terms/",
        json={
            "name": "Термин для удаления со связями",
            "definition": "Определение для удаления связей"
        },
        headers=auth_headers
    )
    assert term.status_code == 201
    term_id = term.json()["id"]

    # Создаем тестовый документ
    document = await create_test_document(app_client, auth_headers)
    doc_id = document["id"]

    # Создаем связь термин-документ
    relation = await create_test_relation(app_client, auth_headers, term_id, doc_id)
    relation_id = relation["id"]

    # Проверяем, что связь существует
    get_relation_response = await app_client.get(
        f"/api/v1/term_document_relations/{relation_id}",
        headers=auth_headers
    )
    assert get_relation_response.status_code == 200

    # Удаляем термин
    delete_term_response = await app_client.delete(
        f"/api/v1/terms/{term_id}",
        headers=auth_headers
    )
    assert delete_term_response.status_code == 200

    # Проверяем, что связь была удалена
    get_relation_after_delete_response = await app_client.get(
        f"/api/v1/term_document_relations/{relation_id}",
        headers=auth_headers
    )
    assert get_relation_after_delete_response.status_code == 404 # Связь не найдена 

@pytest.mark.asyncio
async def test_get_terms_statistics_api(app_client: AsyncClient, auth_headers: dict):
    """Тест получения статистики использования терминов через API."""
    # Создаем тестовый термин
    term_data = {
        "name": "Термин для статистики",
        "definition": "Определение для статистики"
    }
    create_term_response = await app_client.post(
        "/api/v1/terms/",
        json=term_data,
        headers=auth_headers
    )
    assert create_term_response.status_code == 201
    term_id = create_term_response.json()["id"]

    # Создаем тестовый документ
    doc = await create_test_document(app_client, auth_headers)

    # Создаем связь между термином и документом
    await create_test_relation(app_client, auth_headers, term_id, doc["id"])

    # Получаем статистику
    response = await app_client.get(
        "/api/v1/terms/statistics",
        headers=auth_headers
    )

    assert response.status_code == 200
    statistics = response.json()

    # Ожидаем, что статистика будет содержать наш термин с count = 1
    assert isinstance(statistics, list)
    # Находим нашу статистику по term_id
    term_stat = next((item for item in statistics if item["term_id"] == term_id), None)

    assert term_stat is not None
    assert term_stat["document_count"] == 1

@pytest.mark.asyncio
async def test_get_terms_statistics_excludes_unrelated(app_client: AsyncClient, auth_headers: dict):
    """Тест, что статистика использования терминов включает термины без связей с count 0."""
    # Создаем тестовый термин, который будет иметь связь
    term_with_relation_data = {
        "name": "Термин со связью для статистики",
        "definition": "Определение"
    }
    create_term_with_relation_response = await app_client.post(
        "/api/v1/terms/",
        json=term_with_relation_data,
        headers=auth_headers
    )
    assert create_term_with_relation_response.status_code == 201
    term_with_relation_id = create_term_with_relation_response.json()["id"]

    # Создаем тестовый документ и связь
    doc = await create_test_document(app_client, auth_headers)
    await create_test_relation(app_client, auth_headers, term_with_relation_id, doc["id"])

    # Создаем тестовый термин, который не будет иметь связей
    term_without_relation_data = {
        "name": "Термин без связи для статистики",
        "definition": "Определение"
    }
    create_term_without_relation_response = await app_client.post(
        "/api/v1/terms/",
        json=term_without_relation_data,
        headers=auth_headers
    )
    assert create_term_without_relation_response.status_code == 201
    term_without_relation_id = create_term_without_relation_response.json()["id"]

    # Получаем статистику
    response = await app_client.get(
        "/api/v1/terms/statistics",
        headers=auth_headers
    )

    assert response.status_code == 200
    statistics = response.json()

    # Проверяем, что статистика включает оба термина
    term_with_relation_stat = next((item for item in statistics if item["term_id"] == term_with_relation_id), None)
    term_without_relation_stat = next((item for item in statistics if item["term_id"] == term_without_relation_id), None)

    assert term_with_relation_stat is not None
    assert term_without_relation_stat is not None

    # Проверяем количество документов
    assert term_with_relation_stat["document_count"] > 0  # У этого термина есть связь
    assert term_without_relation_stat["document_count"] == 0 # У этого термина нет связей 