import pytest
import asyncio
from uuid import uuid4, UUID
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.crud.term_document import CRUDTermDocument
from app.models.term_document import TermDocumentRelationCreate, TermDocumentRelationUpdate, TermDocumentRelation, ConflictStatus
from app.crud.term import CRUDTerm
from app.models.term import TermCreate
from app.crud.document import CRUDDocument
from app.models.document import DocumentCreate

# Предполагаем, что у вас есть фикстура mongo_db в conftest.py

@pytest.mark.asyncio
async def test_create_relation(db: AsyncIOMotorDatabase):
    """Тест создания связи термин-документ."""
    crud_relation = CRUDTermDocument(db)
    
    # Создаем фиктивные term_id и document_id
    term_id = uuid4()
    document_id = uuid4()
    
    relation_in = TermDocumentRelationCreate(
        term_id=term_id,
        document_id=document_id,
        term_definition_in_document="Определение из документа",
        context="Контекст использования",
        locations=[{"page": 1, "section": "Введение"}]
    )
    
    relation = await crud_relation.create(relation_in=relation_in)
    
    assert relation is not None
    assert isinstance(relation, TermDocumentRelation)
    assert relation.term_id == term_id
    assert relation.document_id == document_id
    assert relation.term_definition_in_document == "Определение из документа"
    assert relation.context == "Контекст использования"
    assert relation.locations == [{"page": 1, "section": "Введение"}]
    assert relation.conflict_status == ConflictStatus.NO_CONFLICT
    assert relation.created_at is not None
    assert relation.updated_at is not None
    
    # Проверяем, что связь действительно вставлена в БД
    found_relation = await crud_relation.get_by_id(relation_id=relation.id)
    assert found_relation is not None
    assert found_relation.term_id == term_id
    assert found_relation.document_id == document_id

@pytest.mark.asyncio
async def test_get_relation_by_id(db: AsyncIOMotorDatabase):
    """Тест получения связи по ID."""
    crud_relation = CRUDTermDocument(db)
    term_id = uuid4()
    document_id = uuid4()
    relation_in = TermDocumentRelationCreate(
        term_id=term_id,
        document_id=document_id,
        term_definition_in_document="Определение"
    )
    created_relation = await crud_relation.create(relation_in=relation_in)
    
    found_relation = await crud_relation.get_by_id(relation_id=created_relation.id)
    
    assert found_relation is not None
    assert found_relation.id == created_relation.id
    assert found_relation.term_id == term_id

@pytest.mark.asyncio
async def test_get_relation_by_term_and_document(db: AsyncIOMotorDatabase):
    """Тест получения связи по ID термина и ID документа."""
    crud_relation = CRUDTermDocument(db)
    term_id = uuid4()
    document_id = uuid4()
    relation_in = TermDocumentRelationCreate(
        term_id=term_id,
        document_id=document_id,
        term_definition_in_document="Определение"
    )
    await crud_relation.create(relation_in=relation_in)
    
    found_relation = await crud_relation.get_by_term_and_document(term_id=term_id, document_id=document_id)
    
    assert found_relation is not None
    assert found_relation.term_id == term_id
    assert found_relation.document_id == document_id

@pytest.mark.asyncio
async def test_get_relations_by_term_id(db: AsyncIOMotorDatabase):
    """Тест получения всех связей для заданного термина."""
    crud_relation = CRUDTermDocument(db)
    term_id = uuid4()
    doc_id_1 = uuid4()
    doc_id_2 = uuid4()
    
    await crud_relation.create(relation_in=TermDocumentRelationCreate(term_id=term_id, document_id=doc_id_1, term_definition_in_document="Опр 1"))
    await crud_relation.create(relation_in=TermDocumentRelationCreate(term_id=term_id, document_id=doc_id_2, term_definition_in_document="Опр 2"))
    await crud_relation.create(relation_in=TermDocumentRelationCreate(term_id=uuid4(), document_id=uuid4(), term_definition_in_document="Другое")) # Другой термин
    
    relations = await crud_relation.get_by_term_id(term_id=term_id)
    
    assert len(relations) >= 2 # Могут быть связи из других тестов, но должно быть минимум 2 созданных
    term_ids_in_results = [r.term_id for r in relations]
    document_ids_in_results = [r.document_id for r in relations]
    
    assert all(tid == term_id for tid in term_ids_in_results)
    assert doc_id_1 in document_ids_in_results
    assert doc_id_2 in document_ids_in_results

@pytest.mark.asyncio
async def test_get_relations_by_document_id(db: AsyncIOMotorDatabase):
    """Тест получения всех связей для заданного документа."""
    crud_relation = CRUDTermDocument(db)
    document_id = uuid4()
    term_id_1 = uuid4()
    term_id_2 = uuid4()
    
    await crud_relation.create(relation_in=TermDocumentRelationCreate(term_id=term_id_1, document_id=document_id, term_definition_in_document="Опр 1"))
    await crud_relation.create(relation_in=TermDocumentRelationCreate(term_id=term_id_2, document_id=document_id, term_definition_in_document="Опр 2"))
    await crud_relation.create(relation_in=TermDocumentRelationCreate(term_id=uuid4(), document_id=uuid4(), term_definition_in_document="Другое")) # Другой документ
    
    relations = await crud_relation.get_by_document_id(document_id=document_id)
    
    assert len(relations) >= 2 # Могут быть связи из других тестов, но должно быть минимум 2 созданных
    document_ids_in_results = [r.document_id for r in relations]
    term_ids_in_results = [r.term_id for r in relations]
    
    assert all(did == document_id for did in document_ids_in_results)
    assert term_id_1 in term_ids_in_results
    assert term_id_2 in term_ids_in_results

@pytest.mark.asyncio
async def test_get_multiple_relations(db: AsyncIOMotorDatabase):
    """Тест получения нескольких связей."""
    crud_relation = CRUDTermDocument(db)
    
    # Создаем несколько связей
    await crud_relation.create(relation_in=TermDocumentRelationCreate(term_id=uuid4(), document_id=uuid4(), term_definition_in_document="Связь 1"))
    await crud_relation.create(relation_in=TermDocumentRelationCreate(term_id=uuid4(), document_id=uuid4(), term_definition_in_document="Связь 2"))
    await crud_relation.create(relation_in=TermDocumentRelationCreate(term_id=uuid4(), document_id=uuid4(), term_definition_in_document="Связь 3"))
    
    relations = await crud_relation.get_multiple(skip=0, limit=10)
    
    assert len(relations) >= 3 # Могут быть связи из других тестов
    # Проверяем наличие созданных связей по определениям
    definitions_in_results = [r.term_definition_in_document for r in relations]
    assert "Связь 1" in definitions_in_results
    assert "Связь 2" in definitions_in_results
    assert "Связь 3" in definitions_in_results

@pytest.mark.asyncio
async def test_update_relation(db: AsyncIOMotorDatabase):
    """Тест обновления связи термин-документ."""
    crud_relation = CRUDTermDocument(db)
    term_id = uuid4()
    document_id = uuid4()
    relation_in = TermDocumentRelationCreate(
        term_id=term_id,
        document_id=document_id,
        term_definition_in_document="Старое определение связи",
        context="Старый контекст"
    )
    created_relation = await crud_relation.create(relation_in=relation_in)
    
    relation_update_in = TermDocumentRelationUpdate(
        term_definition_in_document="Новое определение связи",
        context="Новый контекст",
        conflict_status=ConflictStatus.MINOR_CONFLICT,
        conflict_description="Незначительные расхождения"
    )
    user_id = uuid4()
    
    updated_relation = await crud_relation.update(relation_id=created_relation.id, relation_update=relation_update_in, user_id=user_id)
    
    assert updated_relation is not None
    assert updated_relation.id == created_relation.id
    assert updated_relation.term_definition_in_document == "Новое определение связи"
    assert updated_relation.context == "Новый контекст"
    assert updated_relation.conflict_status == ConflictStatus.MINOR_CONFLICT
    assert updated_relation.conflict_description == "Незначительные расхождения"
    assert updated_relation.verified_by == user_id
    assert updated_relation.verified_at is not None
    assert updated_relation.updated_at.replace(tzinfo=timezone.utc) > created_relation.updated_at.replace(tzinfo=timezone.utc)

@pytest.mark.asyncio
async def test_delete_relation(db: AsyncIOMotorDatabase):
    """Тест удаления связи термин-документ по ID."""
    crud_relation = CRUDTermDocument(db)
    term_id = uuid4()
    document_id = uuid4()
    relation_in = TermDocumentRelationCreate(
        term_id=term_id,
        document_id=document_id,
        term_definition_in_document="Определение для удаления"
    )
    created_relation = await crud_relation.create(relation_in=relation_in)
    
    delete_result = await crud_relation.delete(relation_id=created_relation.id)
    
    assert delete_result is True
    
    # Проверяем, что связь удалена из БД
    found_relation = await crud_relation.get_by_id(relation_id=created_relation.id)
    assert found_relation is None

@pytest.mark.asyncio
async def test_delete_relation_by_term_and_document(db: AsyncIOMotorDatabase):
    """Тест удаления связи по ID термина и ID документа."""
    crud_relation = CRUDTermDocument(db)
    term_id = uuid4()
    document_id = uuid4()
    relation_in = TermDocumentRelationCreate(
        term_id=term_id,
        document_id=document_id,
        term_definition_in_document="Определение для удаления 2"
    )
    await crud_relation.create(relation_in=relation_in)
    
    delete_result = await crud_relation.delete_by_term_and_document(term_id=term_id, document_id=document_id)
    
    assert delete_result is True
    
    # Проверяем, что связь удалена из БД
    found_relation = await crud_relation.get_by_term_and_document(term_id=term_id, document_id=document_id)
    assert found_relation is None
