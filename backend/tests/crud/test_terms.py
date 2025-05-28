import pytest
from uuid import uuid4
from datetime import timezone

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.crud.term import CRUDTerm
from app.models.term import TermCreate, TermUpdate, Term

# Предполагаем, что у вас есть фикстура mongo_db в conftest.py
# @pytest.fixture(scope="module")
# def event_loop():
#     loop = asyncio.get_event_loop()
#     yield loop
#     loop.close()

@pytest.mark.asyncio
async def test_create_term(db: AsyncIOMotorDatabase):
    """Тест создания термина."""
    crud_term = CRUDTerm(db)
    user_id = uuid4() # Генерируем фиктивный user_id
    term_in = TermCreate(name="Тестовый термин", definition="Это тестовое определение")
    
    term = await crud_term.create(term_in=term_in, user_id=user_id)
    
    assert term is not None
    assert isinstance(term, Term)
    assert term.name == "Тестовый термин"
    assert term.current_definition == "Это тестовое определение"
    assert len(term.definitions_history) == 1
    assert term.definitions_history[0].definition == "Это тестовое определение"
    assert term.definitions_history[0].created_by == user_id
    assert term.is_approved is False
    assert term.created_at is not None
    assert term.updated_at is not None
    
    # Проверяем, что термин действительно вставлен в БД
    found_term = await crud_term.get_by_id(term_id=term.id)
    assert found_term is not None
    assert found_term.name == "Тестовый термин"

@pytest.mark.asyncio
async def test_get_term_by_id(db: AsyncIOMotorDatabase):
    """Тест получения термина по ID."""
    crud_term = CRUDTerm(db)
    user_id = uuid4()
    term_in = TermCreate(name="Термин для поиска по ID", definition="Определение")
    created_term = await crud_term.create(term_in=term_in, user_id=user_id)
    
    found_term = await crud_term.get_by_id(term_id=created_term.id)
    
    assert found_term is not None
    assert found_term.id == created_term.id
    assert found_term.name == "Термин для поиска по ID"

@pytest.mark.asyncio
async def test_get_term_by_name(db: AsyncIOMotorDatabase):
    """Тест получения термина по названию."""
    crud_term = CRUDTerm(db)
    user_id = uuid4()
    term_in = TermCreate(name="Уникальный термин", definition="Определение")
    await crud_term.create(term_in=term_in, user_id=user_id)
    
    found_term = await crud_term.get_by_name(name="Уникальный термин")
    
    assert found_term is not None
    assert found_term.name == "Уникальный термин"

@pytest.mark.asyncio
async def test_get_multiple_terms(db: AsyncIOMotorDatabase):
    """Тест получения нескольких терминов."""
    crud_term = CRUDTerm(db)
    user_id = uuid4()
    
    # Создаем несколько терминов
    await crud_term.create(term_in=TermCreate(name="Термин 1", definition="Опр 1"), user_id=user_id)
    await crud_term.create(term_in=TermCreate(name="Термин 2", definition="Опр 2"), user_id=user_id)
    await crud_term.create(term_in=TermCreate(name="Термин 3", definition="Опр 3"), user_id=user_id)
    
    terms = await crud_term.get_multiple(skip=0, limit=10)
    
    assert len(terms) >= 3 # Могут быть термины из других тестов, но должно быть минимум 3 новых
    # Проверяем наличие созданных терминов по именам
    term_names = [t.name for t in terms]
    assert "Термин 1" in term_names
    assert "Термин 2" in term_names
    assert "Термин 3" in term_names

@pytest.mark.asyncio
async def test_update_term(db: AsyncIOMotorDatabase):
    """Тест обновления термина."""
    crud_term = CRUDTerm(db)
    user_id = uuid4()
    term_in = TermCreate(name="Обновляемый термин", definition="Старое определение")
    created_term = await crud_term.create(term_in=term_in, user_id=user_id)
    
    new_user_id = uuid4()
    term_update_in = TermUpdate(
        name="Обновленный термин", 
        definition="Новое определение", 
        is_approved=True,
        tags=["test", "updated"]
    )
    
    updated_term = await crud_term.update(term_id=created_term.id, term_update=term_update_in, user_id=new_user_id)
    
    assert updated_term is not None
    assert updated_term.id == created_term.id
    assert updated_term.name == "Обновленный термин"
    assert updated_term.current_definition == "Новое определение"
    assert updated_term.is_approved is True
    assert updated_term.approved_by == new_user_id
    assert updated_term.approved_at is not None
    assert updated_term.tags == ["test", "updated"]
    assert updated_term.updated_at.replace(tzinfo=timezone.utc) > created_term.updated_at.replace(tzinfo=timezone.utc)
    
    # Проверяем историю определений
    assert len(updated_term.definitions_history) == 2 # Старое + новое
    definitions_text = [d.definition for d in updated_term.definitions_history]
    assert "Старое определение" in definitions_text
    assert "Новое определение" in definitions_text

@pytest.mark.asyncio
async def test_delete_term(db: AsyncIOMotorDatabase):
    """Тест удаления термина."""
    crud_term = CRUDTerm(db)
    user_id = uuid4()
    term_in = TermCreate(name="Удаляемый термин", definition="Определение для удаления")
    created_term = await crud_term.create(term_in=term_in, user_id=user_id)
    
    delete_result = await crud_term.delete(term_id=created_term.id)
    
    assert delete_result is True
    
    # Проверяем, что термин удален из БД
    found_term = await crud_term.get_by_id(term_id=created_term.id)
    assert found_term is None

@pytest.mark.asyncio
async def test_search_terms(db: AsyncIOMotorDatabase):
    """Тест поиска терминов."""
    crud_term = CRUDTerm(db)
    user_id = uuid4()
    
    # Создаем термины для поиска
    await crud_term.create(term_in=TermCreate(name="Поисковый термин А", definition="Определение A о поиске"), user_id=user_id)
    await crud_term.create(term_in=TermCreate(name="Другой термин Б", definition="Определение Б"), user_id=user_id)
    await crud_term.create(term_in=TermCreate(name="Термин В с поиском", definition="Опр В"), user_id=user_id)
    
    # Поиск по названию
    search_results_name = await crud_term.search(query="Поисковый")
    assert len(search_results_name) >= 1
    assert any(t.name == "Поисковый термин А" for t in search_results_name)
    
    # Поиск по определению
    search_results_definition = await crud_term.search(query="о поиске")
    assert len(search_results_definition) >= 1
    assert any(t.name == "Поисковый термин А" for t in search_results_definition)
    
    # Поиск, который не должен найти результатов
    search_results_none = await crud_term.search(query="несуществующий")
    assert len(search_results_none) == 0 