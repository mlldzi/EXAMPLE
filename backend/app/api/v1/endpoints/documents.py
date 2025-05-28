from typing import Any, List, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app import crud
from app.api.v1 import deps
from app.models.document import Document, DocumentCreate, DocumentUpdate
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

@router.get("/{doc_id}", response_model=Document)
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
    return document

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
    # await crud.term_document.update_conflict_status_for_document_relations(db, doc_id=doc_id)

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
    # await crud.term_document.delete_by_document_id(db, doc_id=doc_id)

    delete_result = await document_crud.delete(doc_id=doc_id)
    
    return {"success": delete_result, "id": doc_id}