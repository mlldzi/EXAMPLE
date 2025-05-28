from typing import Any, List, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app import crud
from app.api.v1 import deps
from app.models.document import Document, DocumentCreate, DocumentUpdate, DocumentPublic
from app.models.user import UserPublic

router = APIRouter()

@router.post("/", response_model=Document, status_code=201)
async def create_document(
    document_in: DocumentCreate,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Создать новый документ."""
    document_crud = crud.CRUDDocument(db)
    # Опционально: проверить наличие документа с таким же номером перед созданием
    existing_doc = await document_crud.get_by_document_number(document_number=document_in.document_number)
    if existing_doc:
        raise HTTPException(status_code=400, detail="Документ с таким номером уже существует")
        
    document = await document_crud.create(doc_in=document_in, user_id=current_user.id)
    return document

@router.get("/{doc_id}", response_model=DocumentPublic)
async def read_document(
    doc_id: UUID,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Получить документ по ID."""
    document_crud = crud.CRUDDocument(db)
    document = await document_crud.get_by_id(doc_id=doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Документ не найден")
        
    # Явно преобразуем поля в строки для соответствия DocumentPublic
    document_dict = document.model_dump()
    document_dict['approval_date'] = str(document.approval_date) if document.approval_date else None
    document_dict['document_url'] = str(document.document_url) if document.document_url else None
    document_dict['created_at'] = str(document.created_at) if document.created_at else None
    document_dict['updated_at'] = str(document.updated_at) if document.updated_at else None
    # Убедимся, что ID в строковом формате, если он UUID
    if isinstance(document_dict.get('id'), UUID):
         document_dict['id'] = str(document_dict['id'])

    return DocumentPublic(**document_dict)

@router.get("/", response_model=List[Document])
async def read_documents(
    skip: int = 0,
    limit: int = 100,
    query: str | None = None, # Добавляем параметр для поиска по названию/номеру
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Получить список документов с возможностью поиска."""
    document_crud = crud.CRUDDocument(db)
    documents = await document_crud.get_multiple(skip=skip, limit=limit, query=query)
    return documents

@router.put("/{doc_id}", response_model=Document)
async def update_document(
    doc_id: UUID,
    document_in: DocumentUpdate,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Обновить документ."""
    document_crud = crud.CRUDDocument(db)
    document = await document_crud.get_by_id(doc_id=doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Документ не найден")
        
    # Опционально: проверить, не создает ли обновление дубликат номера
    if document_in.document_number and document_in.document_number != document.document_number:
        existing_document = await document_crud.get_by_document_number(document_number=document_in.document_number)
        if existing_document:
             raise HTTPException(status_code=400, detail="Документ с таким номером уже существует")
             
    updated_document = await document_crud.update(doc_id=doc_id, doc_update=document_in, user_id=current_user.id)
    
    # После обновления документа, возможно, потребуется пересчитать статусы конфликтов для связанных связей
    # Это может быть сложная операция, возможно, ее стоит вынести в отдельную фоновую задачу
    # Получаем ID терминов, связанных с этим документом
    term_document_crud = crud.CRUDTermDocument(db)
    relations = await term_document_crud.get_by_document_id(document_id=doc_id)
    term_ids = list(set([str(relation.term_id) for relation in relations])) # Используем set для уникальных ID и конвертируем в str для безопасности сравнения

    # Обновляем статус конфликта для каждого связанного термина
    for term_id_str in term_ids:
        term_id = UUID(term_id_str)
        await term_document_crud.update_conflict_status(term_id=term_id)

    return updated_document

@router.delete("/{doc_id}", response_model=Dict[str, Any])
async def delete_document(
    doc_id: UUID,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Удалить документ."""
    document_crud = crud.CRUDDocument(db)
    document = await document_crud.get_by_id(doc_id=doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Документ не найден")
        
    # При удалении документа, также нужно удалить все связанные с ним связи термин-документ
    term_document_crud = crud.CRUDTermDocument(db)
    # Получаем ID терминов, связанных с этим документом, ДО удаления связей
    relations = await term_document_crud.get_by_document_id(document_id=doc_id)
    term_ids = list(set([str(relation.term_id) for relation in relations])) # Используем set для уникальных ID

    # Удаляем связанные связи термин-документ
    await term_document_crud.delete_by_document_id(document_id=doc_id)

    # Удаляем сам документ
    delete_result = await document_crud.delete(doc_id=doc_id)
    
    # После удаления документа и связей, возможно, потребуется пересчитать статусы конфликтов
    # для терминов, которые были связаны с этим документом
    for term_id_str in term_ids:
         await term_document_crud.update_conflict_status(term_id=UUID(term_id_str))

    
    return {"success": delete_result, "id": doc_id}

@router.get("/{doc_id}/terms", response_model=List[crud.term.Term])
async def read_terms_for_document(
    doc_id: UUID,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Получить список терминов, связанных с документом."""
    term_document_crud = crud.CRUDTermDocument(db)
    term_crud = crud.CRUDTerm(db)
    
    # Получаем все связи для данного документа
    relations = await term_document_crud.get_by_document_id(document_id=doc_id)
    
    # Извлекаем ID терминов из связей
    term_ids = [relation.term_id for relation in relations]
    
    # Получаем полную информацию о терминах по их ID
    terms = []
    for term_id in term_ids:
        term = await term_crud.get_by_id(term_id=term_id)
        if term:
            # print(f'DEBUG: Fetched term in read_terms_for_document: {term}') # Временное логирование
            terms.append(term)
            
    return terms