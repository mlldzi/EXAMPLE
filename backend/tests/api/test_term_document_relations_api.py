import pytest
from httpx import AsyncClient
from uuid import uuid4, UUID
from datetime import datetime, timezone

# Предполагаем, что у вас есть фикстуры app_client и auth_headers в conftest.py

# Вспомогательные функции для создания термина и документа через API
async def create_test_term(client: AsyncClient, headers: dict):
    term_data = {"name": f"Термин для связи {uuid4()}", "definition": "Определение для связи"}
    response = await client.post("/api/v1/terms/", json=term_data, headers=headers)
    assert response.status_code == 201
    return response.json()

async def create_test_document(client: AsyncClient, headers: dict):
    doc_data = {
        "title": f"Документ для связи {uuid4()}",
        "document_number": f"ДС-{uuid4()}",
        "approval_date": datetime.now(timezone.utc).isoformat()
    }
    response = await client.post("/api/v1/documents/", json=doc_data, headers=headers)
    assert response.status_code == 201
    return response.json()

@pytest.mark.asyncio
async def test_create_relation_api(app_client: AsyncClient, auth_headers: dict):
    """Тест создания связи термин-документ через API."""
    # Создаем тестовые термин и документ
    term = await create_test_term(app_client, auth_headers)
    document = await create_test_document(app_client, auth_headers)
    
    relation_data = {
        "term_id": str(term["id"]),
        "document_id": str(document["id"]),
        "term_definition_in_document": "Определение из документа (API)",
        "context": "Контекст использования (API)",
        "locations": [{"page": 1, "section": "Введение (API)"}]
    }
    
    response = await app_client.post(
        "/api/v1/term_document_relations/",
        json=relation_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    created_relation = response.json()
    
    assert created_relation["term_id"] == relation_data["term_id"]
    assert created_relation["document_id"] == relation_data["document_id"]
    assert created_relation["term_definition_in_document"] == relation_data["term_definition_in_document"]
    assert created_relation["context"] == relation_data["context"]
    assert created_relation["locations"] == relation_data["locations"]
    assert "id" in created_relation
    assert "created_at" in created_relation
    assert "updated_at" in created_relation
    assert "conflict_status" in created_relation

@pytest.mark.asyncio
async def test_create_relation_api_unauthenticated(app_client: AsyncClient):
    """Тест создания связи без аутентификации."""
    relation_data = {
        "term_id": str(uuid4()),
        "document_id": str(uuid4()),
        "term_definition_in_document": "Определение"
    }
    
    response = await app_client.post(
        "/api/v1/term_document_relations/",
        json=relation_data
    )
    
    assert response.status_code == 401 # Unauthorized

@pytest.mark.asyncio
async def test_get_relation_by_id_api(app_client: AsyncClient, auth_headers: dict):
    """Тест получения связи по ID через API."""
    # Создаем тестовые термин и документ
    term = await create_test_term(app_client, auth_headers)
    document = await create_test_document(app_client, auth_headers)
    
    # Сначала создаем связь
    create_response = await app_client.post(
        "/api/v1/term_document_relations/",
        json={
            "term_id": str(term["id"]),
            "document_id": str(document["id"]),
            "term_definition_in_document": "Определение для получения по ID API"
        },
        headers=auth_headers
    )
    assert create_response.status_code == 201
    created_relation_id = create_response.json()["id"]
    
    # Теперь получаем ее по ID
    get_response = await app_client.get(
        f"/api/v1/term_document_relations/{created_relation_id}",
        headers=auth_headers
    )
    
    assert get_response.status_code == 200
    found_relation = get_response.json()
    
    assert found_relation["id"] == created_relation_id
    assert found_relation["term_id"] == str(term["id"])
    assert found_relation["document_id"] == str(document["id"])

@pytest.mark.asyncio
async def test_get_relation_by_id_api_not_found(app_client: AsyncClient, auth_headers: dict):
    """Тест получения несуществующей связи по ID через API."""
    fake_relation_id = uuid4()
    
    get_response = await app_client.get(
        f"/api/v1/term_document_relations/{fake_relation_id}",
        headers=auth_headers
    )
    
    assert get_response.status_code == 404 # Not Found

@pytest.mark.asyncio
async def test_get_relations_api(app_client: AsyncClient, auth_headers: dict):
    """Тест получения списка связей через API."""
    # Создаем тестовые термин и документ
    term1 = await create_test_term(app_client, auth_headers)
    doc1 = await create_test_document(app_client, auth_headers)
    term2 = await create_test_term(app_client, auth_headers)
    doc2 = await create_test_document(app_client, auth_headers)
    
    # Создаем несколько связей
    await app_client.post(
        "/api/v1/term_document_relations/", 
        json={
            "term_id": str(term1["id"]),
            "document_id": str(doc1["id"]),
            "term_definition_in_document": "Связь API 1"
        },
        headers=auth_headers
    )
    await app_client.post(
         "/api/v1/term_document_relations/", 
        json={
            "term_id": str(term2["id"]),
            "document_id": str(doc2["id"]),
            "term_definition_in_document": "Связь API 2"
        },
        headers=auth_headers
    )
    
    get_response = await app_client.get(
        "/api/v1/term_document_relations/",
        headers=auth_headers
    )
    
    assert get_response.status_code == 200
    relations = get_response.json()
    
    assert isinstance(relations, list)
    assert len(relations) >= 2 # Могут быть связи из других тестов
    
    # Проверяем наличие созданных связей по определениям
    definitions_in_results = [r["term_definition_in_document"] for r in relations]
    assert "Связь API 1" in definitions_in_results
    assert "Связь API 2" in definitions_in_results

@pytest.mark.asyncio
async def test_update_relation_api(app_client: AsyncClient, auth_headers: dict):
    """Тест обновления связи термин-документ через API."""
     # Создаем тестовые термин и документ
    term = await create_test_term(app_client, auth_headers)
    document = await create_test_document(app_client, auth_headers)
    
    # Сначала создаем связь
    create_response = await app_client.post(
        "/api/v1/term_document_relations/",
        json={
            "term_id": str(term["id"]),
            "document_id": str(document["id"]),
            "term_definition_in_document": "Старое определение связи API",
            "context": "Старый контекст API"
        },
        headers=auth_headers
    )
    assert create_response.status_code == 201
    created_relation = create_response.json()
    created_relation_id = created_relation["id"]
    original_updated_at = created_relation["updated_at"]
    
    # Данные для обновления
    update_data = {
        "term_definition_in_document": "Новое определение связи API",
        "context": "Новый контекст API"
        # Статус конфликта не обновляется напрямую через PUT
    }
    
    update_response = await app_client.put(
        f"/api/v1/term_document_relations/{created_relation_id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert update_response.status_code == 200
    updated_relation = update_response.json()
    
    assert updated_relation["id"] == created_relation_id
    assert updated_relation["term_definition_in_document"] == update_data["term_definition_in_document"]
    assert updated_relation["context"] == update_data["context"]
    assert updated_relation["updated_at"] > original_updated_at
    # Проверяем, что статус конфликта не изменился
    assert updated_relation["conflict_status"] == created_relation["conflict_status"]

@pytest.mark.asyncio
async def test_delete_relation_api(app_client: AsyncClient, auth_headers: dict):
    """Тест удаления связи термин-документ через API."""
    # Создаем тестовые термин и документ
    term = await create_test_term(app_client, auth_headers)
    document = await create_test_document(app_client, auth_headers)
    
    # Сначала создаем связь
    create_response = await app_client.post(
        "/api/v1/term_document_relations/",
        json={
            "term_id": str(term["id"]),
            "document_id": str(document["id"]),
            "term_definition_in_document": "Определение для удаления связи API"
        },
        headers=auth_headers
    )
    assert create_response.status_code == 201
    created_relation_id = create_response.json()["id"]
    
    # Теперь удаляем ее
    delete_response = await app_client.delete(
        f"/api/v1/term_document_relations/{created_relation_id}",
        headers=auth_headers
    )
    
    assert delete_response.status_code == 200
    delete_result = delete_response.json()
    
    assert delete_result["success"] is True
    assert delete_result["id"] == created_relation_id
    
    # Проверяем, что связь удалена
    get_response = await app_client.get(
        f"/api/v1/term_document_relations/{created_relation_id}",
        headers=auth_headers
    )
    
    assert get_response.status_code == 404 # Not Found

@pytest.mark.asyncio
async def test_get_term_conflicts_report_api(app_client: AsyncClient, auth_headers: dict):
    """Тест получения отчета о конфликтах для термина через API."""
    # Создаем тестовый термин
    term = await create_test_term(app_client, auth_headers)
    term_id = term["id"]

    # Создаем два документа с разными определениями для одного термина
    doc1 = await create_test_document(app_client, auth_headers)
    doc2 = await create_test_document(app_client, auth_headers)
    
    definition1 = "Определение термина в документе 1"
    definition2 = "Другое определение термина в документе 2"

    # Создаем первую связь
    relation_data1 = {
        "term_id": term_id,
        "document_id": doc1["id"],
        "term_definition_in_document": definition1
    }
    create_response1 = await app_client.post(
        "/api/v1/term_document_relations/",
        json=relation_data1,
        headers=auth_headers
    )
    assert create_response1.status_code == 201

    # Создаем вторую связь с другим определением
    relation_data2 = {
        "term_id": term_id,
        "document_id": doc2["id"],
        "term_definition_in_document": definition2
    }
    create_response2 = await app_client.post(
        "/api/v1/term_document_relations/",
        json=relation_data2,
        headers=auth_headers
    )
    assert create_response2.status_code == 201

    # Получаем отчет о конфликтах для термина
    conflicts_response = await app_client.get(
        f"/api/v1/term_document_relations/conflicts/{term_id}",
        headers=auth_headers
    )
    
    assert conflicts_response.status_code == 200
    conflicts = conflicts_response.json()
    
    # Проверяем, что отчет содержит ожидаемый конфликт
    assert isinstance(conflicts, list)
    assert len(conflicts) == 1 # Ожидаем один конфликт между двумя определениями
    
    conflict = conflicts[0]
    assert conflict["definition1"] in [definition1, definition2]
    assert conflict["definition2"] in [definition1, definition2]
    assert conflict["definition1"] != conflict["definition2"]
    
    # Проверяем, что в отчете указаны соответствующие документы
    docs1_ids = [UUID(d) for d in conflict["documents1"]]
    docs2_ids = [UUID(d) for d in conflict["documents2"]]
    
    assert UUID(doc1["id"]) in docs1_ids or UUID(doc1["id"]) in docs2_ids
    assert UUID(doc2["id"]) in docs1_ids or UUID(doc2["id"]) in docs2_ids
    
    # Проверяем отсутствие конфликтов, если определения одинаковые (опционально, можно добавить отдельный тест)
    relation_data3 = {
        "term_id": term_id,
        "document_id": doc1["id"],
        "term_definition_in_document": definition1 # То же определение
    }
    # Обновляем первую связь с тем же определением
    # update_response = await app_client.put(
    #     f"/api/v1/term_document_relations/{create_response1.json()['id']}",
    #     json=relation_data3,
    #     headers=auth_headers
    # )
    # assert update_response.status_code == 200
    
    # # Снова получаем отчет
    # conflicts_response_after_update = await app_client.get(
    #     f"/api/v1/term_document_relations/conflicts/{term_id}",
    #     headers=auth_headers
    # )
    # assert conflicts_response_after_update.status_code == 200
    # conflicts_after_update = conflicts_response_after_update.json()
    # assert len(conflicts_after_update) == 0 # Теперь конфликтов быть не должно 

@pytest.mark.asyncio
async def test_get_all_conflicts_report_api(app_client: AsyncClient, auth_headers: dict):
    """Тест получения полного отчета обо всех конфликтах через API."""
    # Создаем два тестовых термина
    term1 = await create_test_term(app_client, auth_headers)
    term1_id = term1["id"]

    term2 = await create_test_term(app_client, auth_headers)
    term2_id = term2["id"]

    # Создаем несколько документов
    doc1 = await create_test_document(app_client, auth_headers)
    doc2 = await create_test_document(app_client, auth_headers)
    doc3 = await create_test_document(app_client, auth_headers)
    doc4 = await create_test_document(app_client, auth_headers)

    # Создаем связи, чтобы у term1 были конфликты, а у term2 - нет
    # Связи для term1 (конфликт)
    await app_client.post(
        "/api/v1/term_document_relations/",
        json={
            "term_id": term1_id,
            "document_id": doc1["id"],
            "term_definition_in_document": "Определение 1 для term1"
        },
        headers=auth_headers
    )
    await app_client.post(
        "/api/v1/term_document_relations/",
        json={
            "term_id": term1_id,
            "document_id": doc2["id"],
            "term_definition_in_document": "Определение 2 для term1 (конфликт)"
        },
        headers=auth_headers
    )

    # Связи для term2 (без конфликта)
    await app_client.post(
        "/api/v1/term_document_relations/",
        json={
            "term_id": term2_id,
            "document_id": doc3["id"],
            "term_definition_in_document": "Определение для term2"
        },
        headers=auth_headers
    )
    await app_client.post(
        "/api/v1/term_document_relations/",
        json={
            "term_id": term2_id,
            "document_id": doc4["id"],
            "term_definition_in_document": "Определение для term2" # То же определение
        },
        headers=auth_headers
    )

    # Получаем полный отчет о конфликтах
    response = await app_client.get(
        "/api/v1/term_document_relations/conflicts",
        headers=auth_headers
    )

    # Печатаем тело ответа при ошибке 422 для диагностики
    if response.status_code == 422:
        print("Response body on 422 error:", response.json())

    assert response.status_code == 200
    report = response.json()

    assert isinstance(report, list)
    
    # Ожидаем, что в отчете будет информация только о term1
    assert len(report) == 1
    
    conflict_entry = report[0]
    assert conflict_entry["term_id"] == term1_id
    assert "conflicts" in conflict_entry
    
    conflicts_list = conflict_entry["conflicts"]
    assert isinstance(conflicts_list, list)
    assert len(conflicts_list) == 1 # Ожидаем один конфликт между двумя определениями для term1

    conflict = conflicts_list[0]
    definitions = [conflict["definition1"], conflict["definition2"]]
    assert "Определение 1 для term1" in definitions
    assert "Определение 2 для term1 (конфликт)" in definitions 