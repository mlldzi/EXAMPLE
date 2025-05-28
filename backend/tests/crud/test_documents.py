import pytest
import asyncio
from uuid import uuid4
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.crud.document import CRUDDocument
from app.models.document import DocumentCreate, DocumentUpdate, Document, DocumentStatus
from pydantic import HttpUrl

# Предполагаем, что у вас есть фикстура mongo_db в conftest.py

@pytest.mark.asyncio
async def test_create_document(db: AsyncIOMotorDatabase):
    """Тест создания нормативного документа."""
    crud_document = CRUDDocument(db)
    user_id = uuid4() # Генерируем фиктивный user_id
    doc_in = DocumentCreate(
        title="Тестовый документ",
        document_number="ТД-001",
        approval_date=datetime.now(timezone.utc),
        description="Описание тестового документа",
        document_url=HttpUrl("http://example.com/test_doc")
    )
    
    document = await crud_document.create(doc_in=doc_in, user_id=user_id)
    
    assert document is not None
    assert isinstance(document, Document)
    assert document.title == "Тестовый документ"
    assert document.document_number == "ТД-001"
    assert document.owner_id == user_id
    assert document.status == DocumentStatus.DRAFT
    assert document.created_at is not None
    assert document.updated_at is not None
    assert str(document.document_url) == str(doc_in.document_url)
    
    # Проверяем, что документ действительно вставлен в БД
    found_document = await crud_document.get_by_id(doc_id=document.id)
    assert found_document is not None
    assert found_document.title == "Тестовый документ"

@pytest.mark.asyncio
async def test_get_document_by_id(db: AsyncIOMotorDatabase):
    """Тест получения документа по ID."""
    crud_document = CRUDDocument(db)
    user_id = uuid4()
    doc_in = DocumentCreate(
        title="Документ для поиска по ID",
        document_number="ДПИ-001",
        approval_date=datetime.now(timezone.utc)
    )
    created_document = await crud_document.create(doc_in=doc_in, user_id=user_id)
    
    found_document = await crud_document.get_by_id(doc_id=created_document.id)
    
    assert found_document is not None
    assert found_document.id == created_document.id
    assert found_document.title == "Документ для поиска по ID"

@pytest.mark.asyncio
async def test_get_document_by_document_number(db: AsyncIOMotorDatabase):
    """Тест получения документа по номеру."""
    crud_document = CRUDDocument(db)
    user_id = uuid4()
    doc_in = DocumentCreate(
        title="Документ с уникальным номером",
        document_number="УН-123",
        approval_date=datetime.now(timezone.utc)
    )
    await crud_document.create(doc_in=doc_in, user_id=user_id)
    
    found_document = await crud_document.get_by_document_number(document_number="УН-123")
    
    assert found_document is not None
    assert found_document.document_number == "УН-123"

@pytest.mark.asyncio
async def test_get_multiple_documents(db: AsyncIOMotorDatabase):
    """Тест получения нескольких документов."""
    crud_document = CRUDDocument(db)
    user_id = uuid4()
    
    # Создаем несколько документов
    await crud_document.create(doc_in=DocumentCreate(title="Док 1", document_number="Д-1", approval_date=datetime.now(timezone.utc)), user_id=user_id)
    await crud_document.create(doc_in=DocumentCreate(title="Док 2", document_number="Д-2", approval_date=datetime.now(timezone.utc)), user_id=user_id)
    await crud_document.create(doc_in=DocumentCreate(title="Док 3", document_number="Д-3", approval_date=datetime.now(timezone.utc)), user_id=user_id)
    
    documents = await crud_document.get_multiple(skip=0, limit=10)
    
    assert len(documents) >= 3 # Могут быть документы из других тестов
    # Проверяем наличие созданных документов по номерам
    doc_numbers = [d.document_number for d in documents]
    assert "Д-1" in doc_numbers
    assert "Д-2" in doc_numbers
    assert "Д-3" in doc_numbers

@pytest.mark.asyncio
async def test_update_document(db: AsyncIOMotorDatabase):
    """Тест обновления документа."""
    crud_document = CRUDDocument(db)
    user_id = uuid4()
    doc_in = DocumentCreate(
        title="Обновляемый документ",
        document_number="ОД-001",
        approval_date=datetime.now(timezone.utc),
        status=DocumentStatus.DRAFT
    )
    created_document = await crud_document.create(doc_in=doc_in, user_id=user_id)
    
    new_user_id = uuid4()
    doc_update_in = DocumentUpdate(
        title="Обновленный документ", 
        status=DocumentStatus.ACTIVE,
        description="Обновленное описание",
        tags=["updated", "test"]
    )
    
    updated_document = await crud_document.update(doc_id=created_document.id, doc_update=doc_update_in, user_id=new_user_id)
    
    assert updated_document is not None
    assert updated_document.id == created_document.id
    assert updated_document.title == "Обновленный документ"
    assert updated_document.status == DocumentStatus.ACTIVE
    assert updated_document.description == "Обновленное описание"
    assert updated_document.tags == ["updated", "test"]
    assert updated_document.approved_by == new_user_id # Проверяем, что approved_by обновился при смене статуса на ACTIVE
    assert updated_document.updated_at.replace(tzinfo=timezone.utc) > created_document.updated_at.replace(tzinfo=timezone.utc)

@pytest.mark.asyncio
async def test_delete_document(db: AsyncIOMotorDatabase):
    """Тест удаления документа."""
    crud_document = CRUDDocument(db)
    user_id = uuid4()
    doc_in = DocumentCreate(
        title="Удаляемый документ",
        document_number="УД-001",
        approval_date=datetime.now(timezone.utc)
    )
    created_document = await crud_document.create(doc_in=doc_in, user_id=user_id)
    
    delete_result = await crud_document.delete(doc_id=created_document.id)
    
    assert delete_result is True
    
    # Проверяем, что документ удален из БД
    found_document = await crud_document.get_by_id(doc_id=created_document.id)
    assert found_document is None

@pytest.mark.asyncio
async def test_search_documents(db: AsyncIOMotorDatabase):
    """Тест поиска документов."""
    crud_document = CRUDDocument(db)
    user_id = uuid4()
    
    # Создаем документы для поиска
    await crud_document.create(doc_in=DocumentCreate(title="Поисковый документ А", document_number="ПА-001", approval_date=datetime.now(timezone.utc), description="Документ А для поиска"), user_id=user_id)
    await crud_document.create(doc_in=DocumentCreate(title="Другой документ Б", document_number="ДБ-001", approval_date=datetime.now(timezone.utc)), user_id=user_id)
    await crud_document.create(doc_in=DocumentCreate(title="Документ В с поиском", document_number="ПВ-001", approval_date=datetime.now(timezone.utc)), user_id=user_id)
    
    # Поиск по названию
    search_results_title = await crud_document.search(query="Поисковый")
    assert len(search_results_title) >= 1
    assert any(d.title == "Поисковый документ А" for d in search_results_title)
    
    # Поиск по номеру
    search_results_number = await crud_document.search(query="ПА-001")
    assert len(search_results_number) >= 1
    assert any(d.document_number == "ПА-001" for d in search_results_number)
    
    # Поиск по описанию
    search_results_description = await crud_document.search(query="для поиска")
    assert len(search_results_description) >= 1
    assert any(d.title == "Поисковый документ А" for d in search_results_description)
    
    # Поиск, который не должен найти результатов
    search_results_none = await crud_document.search(query="несуществующий номер")
    assert len(search_results_none) == 0

@pytest.mark.asyncio
async def test_add_and_remove_term_from_document(db: AsyncIOMotorDatabase):
    """Тест добавления и удаления термина из списка терминов документа."""
    crud_document = CRUDDocument(db)
    user_id = uuid4()
    doc_in = DocumentCreate(
        title="Документ для связей",
        document_number="ДС-001",
        approval_date=datetime.now(timezone.utc)
    )
    document = await crud_document.create(doc_in=doc_in, user_id=user_id)
    
    term_id_1 = uuid4()
    term_id_2 = uuid4()
    
    # Добавляем термины
    add_result_1 = await crud_document.add_term(doc_id=document.id, term_id=term_id_1)
    assert add_result_1 is True
    updated_doc_1 = await crud_document.get_by_id(doc_id=document.id)
    assert term_id_1 in updated_doc_1.term_ids
    
    add_result_2 = await crud_document.add_term(doc_id=document.id, term_id=term_id_2)
    assert add_result_2 is True
    updated_doc_2 = await crud_document.get_by_id(doc_id=document.id)
    assert term_id_1 in updated_doc_2.term_ids
    assert term_id_2 in updated_doc_2.term_ids
    
    # Пытаемся добавить тот же термин еще раз (не должен дублироваться)
    add_result_3 = await crud_document.add_term(doc_id=document.id, term_id=term_id_1)
    assert add_result_3 is False # Modified count должен быть 0 если элемент уже есть
    updated_doc_3 = await crud_document.get_by_id(doc_id=document.id)
    assert updated_doc_3.term_ids.count(term_id_1) == 1
    assert len(updated_doc_3.term_ids) == 2
    
    # Удаляем термины
    remove_result_1 = await crud_document.remove_term(doc_id=document.id, term_id=term_id_1)
    assert remove_result_1 is True
    updated_doc_4 = await crud_document.get_by_id(doc_id=document.id)
    assert term_id_1 not in updated_doc_4.term_ids
    assert term_id_2 in updated_doc_4.term_ids
    
    remove_result_2 = await crud_document.remove_term(doc_id=document.id, term_id=term_id_2)
    assert remove_result_2 is True
    updated_doc_5 = await crud_document.get_by_id(doc_id=document.id)
    assert term_id_1 not in updated_doc_5.term_ids
    assert term_id_2 not in updated_doc_5.term_ids
    assert len(updated_doc_5.term_ids) == 0
    
    # Пытаемся удалить несуществующий термин
    remove_result_3 = await crud_document.remove_term(doc_id=document.id, term_id=uuid4())
    assert remove_result_3 is False 