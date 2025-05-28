# Тесты для логики выявления конфликтов 

import pytest
from uuid import uuid4, UUID
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.crud.term_document import CRUDTermDocument
from app.models.term_document import TermDocumentRelationCreate, ConflictStatus

@pytest.mark.asyncio
async def test_check_for_conflicts_no_conflicts(db: AsyncIOMotorDatabase):
    """Тест проверки отсутствия конфликтов."""
    crud_relation = CRUDTermDocument(db)
    term_id = uuid4()
    
    # Создаем несколько связей с одинаковым определением для одного термина
    await crud_relation.create(relation_in=TermDocumentRelationCreate(term_id=term_id, document_id=uuid4(), term_definition_in_document="Единое определение"))
    await crud_relation.create(relation_in=TermDocumentRelationCreate(term_id=term_id, document_id=uuid4(), term_definition_in_document="Единое определение"))
    
    conflicts = await crud_relation.check_for_conflicts(term_id=term_id)
    
    assert len(conflicts) == 0

@pytest.mark.asyncio
async def test_check_for_conflicts_with_conflicts(db: AsyncIOMotorDatabase):
    """Тест проверки наличия конфликтов."""
    crud_relation = CRUDTermDocument(db)
    term_id = uuid4()
    doc_id_1 = uuid4()
    doc_id_2 = uuid4()
    doc_id_3 = uuid4()
    
    # Создаем связи с разными определениями для одного термина
    await crud_relation.create(relation_in=TermDocumentRelationCreate(term_id=term_id, document_id=doc_id_1, term_definition_in_document="Определение А"))
    await crud_relation.create(relation_in=TermDocumentRelationCreate(term_id=term_id, document_id=doc_id_2, term_definition_in_document="Определение Б"))
    await crud_relation.create(relation_in=TermDocumentRelationCreate(term_id=term_id, document_id=doc_id_3, term_definition_in_document="Определение А")) # Дублируем определение А
    
    conflicts = await crud_relation.check_for_conflicts(term_id=term_id)
    
    assert len(conflicts) > 0
    
    # Проверяем структуру конфликтов (должны быть пары разных определений)
    definitions_in_conflicts = set()
    for conflict in conflicts:
        assert "definition1" in conflict and "documents1" in conflict
        assert "definition2" in conflict and "documents2" in conflict
        definitions_in_conflicts.add(conflict["definition1"])
        definitions_in_conflicts.add(conflict["definition2"])
        
    assert "Определение А" in definitions_in_conflicts
    assert "Определение Б" in definitions_in_conflicts
    
    # Проверяем, что документы с одинаковыми определениями сгруппированы
    for conflict in conflicts:
        if conflict["definition1"] == "Определение А":
            # Проверяем наличие строковых представлений UUID документов
            assert str(doc_id_1) in conflict["documents1"] or str(doc_id_3) in conflict["documents1"]
            if "Определение Б" in conflict["definition2"]:
                assert str(doc_id_2) in conflict["documents2"]
        elif conflict["definition1"] == "Определение Б":
             assert str(doc_id_2) in conflict["documents1"]
             if "Определение А" in conflict["definition2"]:
                 assert str(doc_id_1) in conflict["documents2"] or str(doc_id_3) in conflict["documents2"]

@pytest.mark.asyncio
async def test_update_conflict_status_no_conflicts(db: AsyncIOMotorDatabase):
    """Тест обновления статуса конфликта (нет конфликтов)."""
    crud_relation = CRUDTermDocument(db)
    term_id = uuid4()
    
    # Создаем связи без конфликтов
    relation_in_1 = TermDocumentRelationCreate(term_id=term_id, document_id=uuid4(), term_definition_in_document="Одинаковое определение")
    relation_in_2 = TermDocumentRelationCreate(term_id=term_id, document_id=uuid4(), term_definition_in_document="Одинаковое определение")
    relation1 = await crud_relation.create(relation_in=relation_in_1)
    relation2 = await crud_relation.create(relation_in=relation_in_2)
    
    # Убеждаемся, что изначально статус NO_CONFLICT
    assert relation1.conflict_status == ConflictStatus.NO_CONFLICT
    assert relation2.conflict_status == ConflictStatus.NO_CONFLICT
    
    # Обновляем статус конфликта
    update_result = await crud_relation.update_conflict_status(term_id=term_id)
    assert update_result is True
    
    # Проверяем, что статус остался NO_CONFLICT
    updated_relation1 = await crud_relation.get_by_id(relation_id=relation1.id)
    updated_relation2 = await crud_relation.get_by_id(relation_id=relation2.id)
    
    assert updated_relation1.conflict_status == ConflictStatus.NO_CONFLICT
    assert updated_relation1.conflict_description is None
    assert updated_relation2.conflict_status == ConflictStatus.NO_CONFLICT
    assert updated_relation2.conflict_description is None

@pytest.mark.asyncio
async def test_update_conflict_status_with_conflicts(db: AsyncIOMotorDatabase):
    """Тест обновления статуса конфликта (есть конфликты)."""
    crud_relation = CRUDTermDocument(db)
    term_id = uuid4()
    
    # Создаем связи с конфликтами
    relation_in_1 = TermDocumentRelationCreate(term_id=term_id, document_id=uuid4(), term_definition_in_document="Определение X")
    relation_in_2 = TermDocumentRelationCreate(term_id=term_id, document_id=uuid4(), term_definition_in_document="Определение Y")
    relation1 = await crud_relation.create(relation_in=relation_in_1)
    relation2 = await crud_relation.create(relation_in=relation_in_2)
    
    # Обновляем статус конфликта
    update_result = await crud_relation.update_conflict_status(term_id=term_id)
    assert update_result is True
    
    # Проверяем, что статус обновился на MAJOR_CONFLICT и добавилось описание
    updated_relation1 = await crud_relation.get_by_id(relation_id=relation1.id)
    updated_relation2 = await crud_relation.get_by_id(relation_id=relation2.id)
    
    assert updated_relation1.conflict_status == ConflictStatus.MAJOR_CONFLICT
    assert updated_relation1.conflict_description is not None
    assert "Обнаружено 1 конфликтов" in updated_relation1.conflict_description # Ожидаем 1 конфликт между X и Y
    
    assert updated_relation2.conflict_status == ConflictStatus.MAJOR_CONFLICT
    assert updated_relation2.conflict_description is not None
    assert "Обнаружено 1 конфликтов" in updated_relation2.conflict_description 