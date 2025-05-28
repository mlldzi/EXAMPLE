import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime, timezone

from app.models.document import DocumentStatus

# Предполагаем, что у вас есть фикстуры app_client и auth_headers в conftest.py

@pytest.mark.asyncio
async def test_create_document_api(app_client: AsyncClient, auth_headers: dict):
    """Тест создания документа через API."""
    doc_data = {
        "title": "API Тестовый документ",
        "document_number": "ТД-API-001",
        "approval_date": datetime.now(timezone.utc).isoformat(),
        "description": "Описание тестового документа через API",
        "document_url": "http://example.com/api_test_doc"
    }
    
    response = await app_client.post(
        "/api/v1/documents/",
        json=doc_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    created_document = response.json()
    
    assert created_document["title"] == doc_data["title"]
    assert created_document["document_number"] == doc_data["document_number"]
    assert created_document["status"] == DocumentStatus.DRAFT.value
    assert "id" in created_document
    assert "created_at" in created_document
    assert "updated_at" in created_document
    assert created_document["document_url"] == doc_data["document_url"]

@pytest.mark.asyncio
async def test_create_document_api_unauthenticated(app_client: AsyncClient):
    """Тест создания документа без аутентификации."""
    doc_data = {
        "title": "Неаутентифицированный документ",
        "document_number": "УНА-001",
        "approval_date": datetime.now(timezone.utc).isoformat()
    }
    
    response = await app_client.post(
        "/api/v1/documents/",
        json=doc_data
    )
    
    assert response.status_code == 401 # Unauthorized

@pytest.mark.asyncio
async def test_get_document_by_id_api(app_client: AsyncClient, auth_headers: dict):
    """Тест получения документа по ID через API."""
    # Сначала создаем документ
    create_response = await app_client.post(
        "/api/v1/documents/",
        json={
            "title": "Документ для получения по ID API",
            "document_number": "ДПИ-API-001",
            "approval_date": datetime.now(timezone.utc).isoformat()
        },
        headers=auth_headers
    )
    assert create_response.status_code == 201
    created_document_id = create_response.json()["id"]
    
    # Теперь получаем его по ID
    get_response = await app_client.get(
        f"/api/v1/documents/{created_document_id}",
        headers=auth_headers
    )
    
    assert get_response.status_code == 200
    found_document = get_response.json()
    
    assert found_document["id"] == created_document_id
    assert found_document["title"] == "Документ для получения по ID API"

@pytest.mark.asyncio
async def test_get_document_by_id_api_not_found(app_client: AsyncClient, auth_headers: dict):
    """Тест получения несуществующего документа по ID через API."""
    fake_doc_id = uuid4()
    
    get_response = await app_client.get(
        f"/api/v1/documents/{fake_doc_id}",
        headers=auth_headers
    )
    
    assert get_response.status_code == 404 # Not Found

@pytest.mark.asyncio
async def test_get_documents_api(app_client: AsyncClient, auth_headers: dict):
    """Тест получения списка документов через API."""
    # Создаем несколько документов
    await app_client.post("/api/v1/documents/", json={"title": "Список документ 1", "document_number": "СД-API-001", "approval_date": datetime.now(timezone.utc).isoformat()}, headers=auth_headers)
    await app_client.post("/api/v1/documents/", json={"title": "Список документ 2", "document_number": "СД-API-002", "approval_date": datetime.now(timezone.utc).isoformat()}, headers=auth_headers)
    
    get_response = await app_client.get(
        "/api/v1/documents/",
        headers=auth_headers
    )
    
    assert get_response.status_code == 200
    documents = get_response.json()
    
    assert isinstance(documents, list)
    assert len(documents) >= 2 # Могут быть документы из других тестов
    
    # Проверяем наличие созданных документов по номерам
    doc_numbers = [d["document_number"] for d in documents]
    assert "СД-API-001" in doc_numbers
    assert "СД-API-002" in doc_numbers

@pytest.mark.asyncio
async def test_update_document_api(app_client: AsyncClient, auth_headers: dict):
    """Тест обновления документа через API."""
    # Сначала создаем документ
    create_response = await app_client.post(
        "/api/v1/documents/",
        json={
            "title": "Документ для обновления API",
            "document_number": "ОД-API-001",
            "approval_date": datetime.now(timezone.utc).isoformat()
        },
        headers=auth_headers
    )
    assert create_response.status_code == 201
    created_document = create_response.json()
    created_document_id = created_document["id"]
    original_updated_at = created_document["updated_at"]
    
    # Данные для обновления
    update_data = {
        "title": "Обновленный документ API", 
        "status": DocumentStatus.ACTIVE.value,
        "description": "Обновленное описание API",
        "tags": ["updated", "api"]
    }
    
    update_response = await app_client.put(
        f"/api/v1/documents/{created_document_id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert update_response.status_code == 200
    updated_document = update_response.json()
    
    assert updated_document["id"] == created_document_id
    assert updated_document["title"] == update_data["title"]
    assert updated_document["status"] == update_data["status"]
    assert updated_document["description"] == update_data["description"]
    assert updated_document["tags"] == update_data["tags"]
    assert updated_document["updated_at"] > original_updated_at

@pytest.mark.asyncio
async def test_delete_document_api(app_client: AsyncClient, auth_headers: dict):
    """Тест удаления документа через API."""
    # Сначала создаем документ
    create_response = await app_client.post(
        "/api/v1/documents/",
        json={
            "title": "Документ для удаления API",
            "document_number": "УД-API-001",
            "approval_date": datetime.now(timezone.utc).isoformat()
        },
        headers=auth_headers
    )
    assert create_response.status_code == 201
    created_document_id = create_response.json()["id"]
    
    # Теперь удаляем его
    delete_response = await app_client.delete(
        f"/api/v1/documents/{created_document_id}",
        headers=auth_headers
    )
    
    assert delete_response.status_code == 200
    delete_result = delete_response.json()
    
    assert delete_result["success"] is True
    assert delete_result["id"] == created_document_id
    
    # Проверяем, что документ удален
    get_response = await app_client.get(
        f"/api/v1/documents/{created_document_id}",
        headers=auth_headers
    )
    
    assert get_response.status_code == 404 # Not Found 

# Вспомогательные функции для тестов связанных сущностей (можно перенести в conftest.py)
async def create_test_term(client: AsyncClient, headers: dict):
    term_data = {"name": f"Тестовый термин для связей {uuid4()}", "definition": "Определение для связи"}
    response = await client.post("/api/v1/terms/", json=term_data, headers=headers)
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
async def test_get_terms_for_document_api(app_client: AsyncClient, auth_headers: dict):
    """Тест получения списка терминов для документа через API."""
    # Создаем тестовый документ
    document = await app_client.post(
        "/api/v1/documents/",
        json={
            "title": "Документ со связанными терминами",
            "document_number": f"ДСТ-{uuid4()}",
            "approval_date": datetime.now(timezone.utc).isoformat()
        },
        headers=auth_headers
    )
    assert document.status_code == 201
    doc_id = document.json()["id"]

    # Создаем несколько тестовых терминов
    term1 = await create_test_term(app_client, auth_headers)
    term2 = await create_test_term(app_client, auth_headers)
    term3 = await create_test_term(app_client, auth_headers) # Не будем связывать

    # Создаем связи термин-документ
    await create_test_relation(app_client, auth_headers, term1["id"], doc_id)
    await create_test_relation(app_client, auth_headers, term2["id"], doc_id)

    # Получаем список терминов для документа
    response = await app_client.get(
        f"/api/v1/documents/{doc_id}/terms",
        headers=auth_headers
    )

    assert response.status_code == 200
    terms = response.json()

    assert isinstance(terms, list)
    assert len(terms) == 2 # Ожидаем 2 связанных термина

    # Проверяем, что возвращены правильные термины
    returned_term_ids = [t["id"] for t in terms]
    assert term1["id"] in returned_term_ids
    assert term2["id"] in returned_term_ids
    assert term3["id"] not in returned_term_ids

@pytest.mark.asyncio
async def test_delete_document_deletes_relations_api(app_client: AsyncClient, auth_headers: dict):
    """Тест: при удалении документа удаляются связанные с ним связи термин-документ."""
    # Создаем тестовый документ
    document = await app_client.post(
        "/api/v1/documents/",
        json={
            "title": "Документ для удаления со связями",
            "document_number": f"ДДУ-{uuid4()}",
            "approval_date": datetime.now(timezone.utc).isoformat()
        },
        headers=auth_headers
    )
    assert document.status_code == 201
    doc_id = document.json()["id"]

    # Создаем тестовый термин
    term = await create_test_term(app_client, auth_headers)
    term_id = term["id"]

    # Создаем связь термин-документ
    relation = await create_test_relation(app_client, auth_headers, term_id, doc_id)
    relation_id = relation["id"]

    # Проверяем, что связь существует
    get_relation_response = await app_client.get(
        f"/api/v1/term_document_relations/{relation_id}",
        headers=auth_headers
    )
    assert get_relation_response.status_code == 200

    # Удаляем документ
    delete_document_response = await app_client.delete(
        f"/api/v1/documents/{doc_id}",
        headers=auth_headers
    )
    assert delete_document_response.status_code == 200

    # Проверяем, что связь была удалена
    get_relation_after_delete_response = await app_client.get(
        f"/api/v1/term_document_relations/{relation_id}",
        headers=auth_headers
    )
    assert get_relation_after_delete_response.status_code == 404 # Связь не найдена 