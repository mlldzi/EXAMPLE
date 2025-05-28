from typing import Any, List, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app import crud
from app.api.v1 import deps
from app.models.term_document import (
    TermDocumentRelation, 
    TermDocumentRelationCreate,
    TermDocumentRelationUpdate,
    ConflictDetail,
    TermConflictReportEntry
)
from app.models.user import UserPublic

router = APIRouter()

@router.get("/conflicts/{term_id}", response_model=List[ConflictDetail])
async def get_term_conflicts_report(
    term_id: UUID,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Получить отчет о конфликтах определений для заданного термина."""
    term_document_crud = crud.CRUDTermDocument(db)
    
    # Проверяем наличие термина
    term = await crud.CRUDTerm(db).get_by_id(term_id=term_id)
    if not term:
        raise HTTPException(status_code=404, detail="Термин не найден")
        
    conflicts = await term_document_crud.check_for_conflicts(term_id=term_id)
    
    return conflicts

@router.get("/conflicts", response_model=List[TermConflictReportEntry])
async def get_all_conflicts_report(
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Получить полный отчет обо всех конфликтах определений терминов."""
    term_document_crud = crud.CRUDTermDocument(db)
    
    # Получаем ID всех терминов, у которых есть конфликты
    term_ids_with_conflicts = await term_document_crud.get_terms_with_conflicts()
    
    all_conflicts_report = []
    
    # Для каждого термина с конфликтами получаем детальный отчет
    for term_id in term_ids_with_conflicts:
        conflicts_for_term = await term_document_crud.check_for_conflicts(term_id=term_id)
        if conflicts_for_term:
            # Добавляем отчет по этому термину
            all_conflicts_report.append({
                "term_id": str(term_id),
                "conflicts": conflicts_for_term
            })
            
    return all_conflicts_report

@router.post("/", response_model=TermDocumentRelation, status_code=201)
async def create_relation(
    relation_in: TermDocumentRelationCreate,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Создать новую связь термин-документ."""
    term_crud = crud.CRUDTerm(db)
    document_crud = crud.CRUDDocument(db)
    relation_crud = crud.CRUDTermDocument(db)

    # Проверка существования термина и документа перед созданием связи (опционально, но желательно)
    term = await term_crud.get_by_id(term_id=relation_in.term_id)
    if not term:
        raise HTTPException(status_code=404, detail="Термин не найден")
        
    document = await document_crud.get_by_id(doc_id=relation_in.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Документ не найден")
        
    # Проверка на дубликат связи (если связь уже существует между этим термином и документом)
    existing_relation = await relation_crud.get_by_term_and_document(
        term_id=relation_in.term_id, document_id=relation_in.document_id
    )
    if existing_relation:
        raise HTTPException(status_code=400, detail="Связь между этим термином и документом уже существует")

    relation = await relation_crud.create(relation_in=relation_in)
    
    # После создания связи, возможно, потребуется обновить статус конфликта для термина
    # await relation_crud.update_conflict_status(term_id=relation_in.term_id)
    
    return relation

@router.get("/{relation_id}", response_model=TermDocumentRelation)
async def read_relation_by_id(
    relation_id: UUID,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Получить связь термин-документ по ID."""
    relation_crud = crud.CRUDTermDocument(db)
    relation = await relation_crud.get_by_id(relation_id=relation_id)
    if not relation:
        raise HTTPException(status_code=404, detail="Связь не найдена")
    return relation

@router.get("/", response_model=List[TermDocumentRelation])
async def read_relations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Получить список связей термин-документ."""
    relation_crud = crud.CRUDTermDocument(db)
    relations = await relation_crud.get_multiple(skip=skip, limit=limit)
    return relations

@router.put("/{relation_id}", response_model=TermDocumentRelation)
async def update_relation(
    relation_id: UUID,
    relation_in: TermDocumentRelationUpdate,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Обновить связь термин-документ."""
    relation_crud = crud.CRUDTermDocument(db)
    relation = await relation_crud.get_by_id(relation_id=relation_id)
    if not relation:
        raise HTTPException(status_code=404, detail="Связь не найдена")
        
    # При обновлении, статус конфликта должен пересчитываться
    # await relation_crud.update_conflict_status(term_id=relation.term_id)

    updated_relation = await relation_crud.update(relation_id=relation_id, relation_update=relation_in, user_id=current_user.id)
    
    # После обновления, возможно, потребуется обновить статус конфликта для термина
    await relation_crud.update_conflict_status(term_id=updated_relation.term_id)

    return updated_relation

@router.delete("/{relation_id}", response_model=Dict[str, Any])
async def delete_relation(
    relation_id: UUID,
    db: AsyncIOMotorDatabase = Depends(deps.get_db),
    current_user: UserPublic = Depends(deps.get_current_user),
) -> Any:
    """Удалить связь термин-документ."""
    relation_crud = crud.CRUDTermDocument(db)
    relation = await relation_crud.get_by_id(relation_id=relation_id)
    if not relation:
        raise HTTPException(status_code=404, detail="Связь не найдена")
        
    delete_result = await relation_crud.delete(relation_id=relation_id)
    
    # После удаления связи, возможно, потребуется обновить статус конфликта для термина
    await relation_crud.update_conflict_status(term_id=relation.term_id)
    
    return {"success": delete_result, "id": relation_id} 