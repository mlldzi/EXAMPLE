from typing import Any, List, Dict
from uuid import UUID
import re

from fastapi import APIRouter, Depends, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorDatabase

from app import crud
from app.api.v1 import deps
# Обновляем импорт, чтобы включить новые модели
from app.models.term import Term, TermCreate, TermUpdate, TermPublic, TermConflictCheck, ConflictDetails, AnalyzedTermData
from app.models.user import UserPublic, UserRole
from app.models.term_document import TermUsageStatistic
from app.models.document import DocumentPublic

router = APIRouter()

@router.post("/", response_model=Term, status_code=201)
async def create_term(
    term_in: TermCreate,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Создать новый термин."""
    term_crud = crud.CRUDTerm(db)
    # Опционально: проверить наличие термина с таким же именем перед созданием
    # existing_term = await term_crud.get_by_name(name=term_in.name)
    # if existing_term:
    #     raise HTTPException(status_code=400, detail="Термин с таким именем уже существует")
        
    term = await term_crud.create(term_in=term_in, user_id=current_user.id)
    return term

@router.post("/bulk-save", response_model=Dict[str, Any])
async def bulk_save_terms(
    terms_in: List[AnalyzedTermData],
    save_history: bool = True,
    replace_definitions: bool = True,
    update_existing: bool = False,  # Новый параметр для обновления существующих терминов
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Dict[str, Any]:
    """Сохранить список терминов, полученных после анализа документа."""
    term_crud = crud.CRUDTerm(db)
    saved_count = 0
    updated_count = 0  # Счетчик обновленных терминов
    errors = []
    saved_terms = []  # Список созданных терминов с полными данными
    updated_terms = []  # Список обновленных терминов

    for term_data in terms_in:
        try:
            # Проверяем, существует ли термин с таким именем (регистронезависимо)
            existing_term = await term_crud.get_by_name_case_insensitive(name=term_data.name)
            
            if existing_term:
                if update_existing:
                    # Обновляем существующий термин, если разрешено
                    term_update_data = TermUpdate(
                        definition=term_data.definition,
                        # Сохраняем историю только если указан параметр
                        save_definition_history=save_history
                    )
                    
                    updated_term = await term_crud.update(
                        term_id=existing_term.id, 
                        term_update=term_update_data,
                        user_id=current_user.id
                    )
                    
                    updated_count += 1
                    updated_terms.append(updated_term)
                else:
                    # Если обновление не разрешено, добавляем в ошибки
                    errors.append({"name": term_data.name, "detail": "Термин с таким именем уже существует"})
                continue
            
            # Создаем объект TermCreate для использования с CRUD
            term_create_data = TermCreate(
                name=term_data.name,
                definition=term_data.definition,
                # source_document_id пока не передаем при bulk-save
                tags=[] # Теги пока не передаем при bulk-save
            )
            
            # Создаем термин
            new_term = await term_crud.create(term_in=term_create_data, user_id=current_user.id)
            saved_count += 1
            saved_terms.append(new_term)
            
        except Exception as e:
            errors.append({"name": term_data.name, "detail": str(e)})

    return {
        "saved_count": saved_count, 
        "updated_count": updated_count,
        "errors": errors,
        "saved_terms": saved_terms,
        "updated_terms": updated_terms
    }

@router.post("/check-conflict", response_model=List[ConflictDetails])
async def check_term_conflict(
    term_check_in: TermConflictCheck,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Проверить наличие конфликтов для данного термина (по имени или схожему определению)."""
    term_crud = crud.CRUDTerm(db)
    conflicts: Dict[UUID, ConflictDetails] = {}

    # 1. Проверка на совпадение по имени (регистронезависимая)
    existing_term_by_name = await term_crud.get_by_name_case_insensitive(name=term_check_in.name)
    if existing_term_by_name:
        # Получаем ID документа-источника для текущего определения, если оно есть
        source_document_id = None
        source_document_title = None
        if existing_term_by_name.definitions_history:
            latest_definition = existing_term_by_name.definitions_history[0] # Предполагаем, что первое определение - самое актуальное или основное
            source_document_id = latest_definition.source_document_id
            
            # Если ID источника есть, пытаемся получить название документа
            if source_document_id:
                 document_crud = crud.CRUDDocument(db) # Создаем экземпляр CRUD для документов
                 source_document = await document_crud.get_by_id(doc_id=source_document_id)
                 if source_document:
                     source_document_title = source_document.title

        conflicts[existing_term_by_name.id] = ConflictDetails(
            conflicting_term_id=existing_term_by_name.id,
            conflicting_term_name=existing_term_by_name.name,
            conflicting_definition=existing_term_by_name.current_definition,
            source_document_id=source_document_id, # Добавляем ID источника
            source_document_title=source_document_title # Добавляем название источника
        )

    # 2. Проверка на совпадение по определению (нечеткое совпадение с использованием regex)
    # Ищем термины, где определение содержит подстроку из проверяемого определения
    # или проверяемое определение содержит подстроку из определения термина
    # (Базовый нечеткий поиск, можно улучшить)
    definition_query = term_check_in.definition
    if definition_query:
        # Экранируем специальные символы regex в запросе пользователя
        # Используем re.escape для корректного экранирования
        escaped_query = re.escape(definition_query)
        
        # Ищем термины, чье определение содержит искомую строку (регистронезависимо)
        terms_matching_definition = await term_crud.search_by_definition(query=escaped_query)
        
        for term in terms_matching_definition:
            # Избегаем добавления уже найденного конфликта по имени, если это тот же термин
            if term.id not in conflicts:
                 conflicts[term.id] = ConflictDetails(
                    conflicting_term_id=term.id,
                    conflicting_term_name=term.name,
                    conflicting_definition=term.current_definition
                )

    # TODO: Добавить логику проверки конфликтов с учетом года, если это необходимо
    # Например, термины с одинаковым названием, но разным годом могут считаться конфликтом.

    # Возвращаем список уникальных конфликтов
    return list(conflicts.values())

# В CRUD потребуется метод search_by_definition
# Добавляю заглушку здесь, чтобы не забыть
# async def search_by_definition(self, query: str, limit: int = 20) -> List[Term]:
#     # Implement search by definition
#     pass

@router.get("/", response_model=List[TermPublic])
async def read_terms(
    skip: int = 0,
    limit: int = 100,
    query: str | None = None, # Добавляем параметр для поиска по имени/определению
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Получить список терминов с возможностью поиска."""
    term_crud = crud.CRUDTerm(db)
    terms = await term_crud.get_multiple(skip=skip, limit=limit, query=query)
    
    terms_public = []
    for term in terms:
        term_dict = term.model_dump() # Получаем словарь из модели Pydantic
        term_dict['created_at'] = str(term.created_at) if term.created_at else None
        term_dict['updated_at'] = str(term.updated_at) if term.updated_at else None
        # Преобразуем id в строку, если он не строка (модель TermPublic ожидает строку)
        if isinstance(term_dict.get('id'), UUID):
            term_dict['id'] = str(term_dict['id'])
            
        terms_public.append(TermPublic(**term_dict))

    return terms_public

@router.get("/statistics", response_model=List[TermUsageStatistic])
async def get_terms_statistics(
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Получить статистику использования терминов (количество документов, в которых встречается каждый термин)."""
    term_document_crud = crud.CRUDTermDocument(db)
    statistics = await term_document_crud.get_term_usage_statistics()
    return statistics

@router.get("/{term_id}", response_model=Term)
async def read_term(
    term_id: UUID,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Получить термин по ID."""
    term_crud = crud.CRUDTerm(db)
    term = await term_crud.get_by_id(term_id=term_id)
    if not term:
        raise HTTPException(status_code=404, detail="Термин не найден")
    return term

@router.put("/{term_id}", response_model=Term)
async def update_term(
    term_id: UUID,
    term_in: TermUpdate,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Обновить термин."""
    # Проверяем права доступа - только администраторы и модераторы могут утверждать термины
    if term_in.is_approved is not None and not any(role in current_user.roles for role in [UserRole.ADMIN, UserRole.MODERATOR]):
        raise HTTPException(
            status_code=403,
            detail=f"У вас нет прав для утверждения термина. Требуется роль {UserRole.ADMIN} или {UserRole.MODERATOR}."
        )
        
    term_crud = crud.CRUDTerm(db)
    term = await term_crud.get_by_id(term_id=term_id)
    if not term:
        raise HTTPException(status_code=404, detail="Термин не найден")
        
    # Опционально: проверить, не создает ли обновление дубликат имени
    if term_in.name and term_in.name != term.name:
        existing_term = await term_crud.get_by_name(name=term_in.name)
        if existing_term:
             raise HTTPException(status_code=400, detail="Термин с таким именем уже существует")
             
    updated_term = await term_crud.update(term_id=term_id, term_update=term_in, user_id=current_user.id)
    
    # После обновления термина, возможно, потребуется пересчитать статусы конфликтов для связанных связей
    # Это может быть сложная операция, возможно, ее стоит вынести в отдельную фоновую задачу
    term_document_crud = crud.CRUDTermDocument(db)
    await term_document_crud.update_conflict_status(term_id=term_id)

    return updated_term

@router.delete("/{term_id}", response_model=Dict[str, Any])
async def delete_term(
    term_id: UUID,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Удалить термин."""
    term_crud = crud.CRUDTerm(db)
    term = await term_crud.get_by_id(term_id=term_id)
    if not term:
        raise HTTPException(status_code=404, detail="Термин не найден")
        
    # При удалении термина, также нужно удалить все связанные с ним связи термин-документ
    term_document_crud = crud.CRUDTermDocument(db)
    await term_document_crud.delete_by_term_id(term_id=term_id)

    delete_result = await term_crud.delete(term_id=term_id)
    
    return {"success": delete_result, "id": term_id}

@router.get("/{term_id}/documents", response_model=List[DocumentPublic])
async def read_documents_for_term(
    term_id: UUID,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Получить список документов, связанных с термином."""
    term_document_crud = crud.CRUDTermDocument(db)
    document_crud = crud.CRUDDocument(db)
    
    # Получаем все связи для данного термина
    relations = await term_document_crud.get_by_term_id(term_id=term_id)
    
    # Извлекаем ID документов из связей
    document_ids = [relation.document_id for relation in relations]
    
    # Получаем полную информацию о документах по их ID
    documents = []
    for doc_id in document_ids:
        document = await document_crud.get_by_id(doc_id=doc_id)
        if document:
            # Преобразуем в словарь и форматируем даты в строки
            document_dict = document.model_dump()
            document_dict['approval_date'] = str(document.approval_date) if document.approval_date else None
            document_dict['created_at'] = str(document.created_at) if document.created_at else None
            document_dict['updated_at'] = str(document.updated_at) if document.updated_at else None
            # Убедимся, что ID в строковом формате
            if isinstance(document_dict.get('id'), UUID):
                document_dict['id'] = str(document_dict['id'])
                
            documents.append(DocumentPublic(**document_dict))
            
    return documents

@router.post("/get-by-names", response_model=List[Term])
async def get_terms_by_names(
    request: Dict[str, List[str]],
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Получить список терминов по их именам."""
    if 'names' not in request or not isinstance(request['names'], list):
        raise HTTPException(status_code=400, detail="Должен быть предоставлен список имен в поле 'names'")
    
    term_crud = crud.CRUDTerm(db)
    terms = []
    
    for name in request['names']:
        term = await term_crud.get_by_name_case_insensitive(name=name)
        if term:
            terms.append(term)
    
    return terms