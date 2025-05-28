from typing import Any, List, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app import crud
from app.api.v1 import deps
from app.models.term import Term, TermCreate, TermUpdate, TermPublic
from app.models.user import UserPublic
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
    existing_term = await term_crud.get_by_name(name=term_in.name)
    if existing_term:
        raise HTTPException(status_code=400, detail="Термин с таким именем уже существует")
        
    term = await term_crud.create(term_in=term_in, user_id=current_user.id)
    return term

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
    documents_public = []
    for doc_id in document_ids:
        document = await document_crud.get_by_id(doc_id=doc_id)
        if document:
            # Преобразуем поля в строки для соответствия DocumentPublic
            document_dict = document.model_dump()
            document_dict['approval_date'] = str(document.approval_date) if document.approval_date else None
            document_dict['document_url'] = str(document.document_url) if document.document_url else None
            document_dict['created_at'] = str(document.created_at) if document.created_at else None
            document_dict['updated_at'] = str(document.updated_at) if document.updated_at else None
            # Убедимся, что ID в строковом формате, если он UUID
            if isinstance(document_dict.get('id'), UUID):
                 document_dict['id'] = str(document_dict['id'])
            
            documents_public.append(DocumentPublic(**document_dict))
            
    return documents_public