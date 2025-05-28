from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from app.models.document import Document, DocumentCreate, DocumentUpdate, DocumentStatus
from bson import Binary

class CRUDDocument:
    """Класс для управления CRUD операциями с нормативными документами."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """Инициализирует класс с экземпляром базы данных."""
        self.db = db
        self.collection = db.documents
        
    async def create(self, *, doc_in: DocumentCreate, user_id: UUID) -> Document:
        """
        Создает новый нормативный документ в базе данных.
        
        Args:
            doc_in: Данные для создания документа
            user_id: ID пользователя, создающего документ
            
        Returns:
            Созданный документ
        """
        # Генерируем UUID для нового документа
        doc_id = uuid4()
        
        # Создаем объект документа
        doc_data = {
            "_id": Binary.from_uuid(doc_id),
            "id": doc_id,
            "title": doc_in.title,
            "document_number": doc_in.document_number,
            "approval_date": doc_in.approval_date,
            "status": DocumentStatus.DRAFT.value,
            "description": doc_in.description,
            "document_url": str(doc_in.document_url) if doc_in.document_url else None,
            "document_file_path": None,
            "owner_id": user_id,
            "approved_by": None,
            "term_ids": [],
            "department": doc_in.department,
            "tags": doc_in.tags,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Добавляем документ в базу данных
        await self.collection.insert_one(doc_data)
        
        # Получаем и возвращаем созданный документ
        return Document(**doc_data)
        
    async def get_by_id(self, *, doc_id: UUID) -> Optional[Document]:
        """
        Получает документ по его ID.
        
        Args:
            doc_id: ID документа
            
        Returns:
            Документ, если найден, иначе None
        """
        doc_data = await self.collection.find_one({"_id": Binary.from_uuid(doc_id)})
        if doc_data:
            return Document(**doc_data)
        return None
    
    async def get_by_document_number(self, *, document_number: str) -> Optional[Document]:
        """
        Получает документ по его номеру.
        
        Args:
            document_number: Номер документа
            
        Returns:
            Документ, если найден, иначе None
        """
        doc_data = await self.collection.find_one({"document_number": document_number})
        if doc_data:
            return Document(**doc_data)
        return None
    
    async def get_multiple(
        self, *, skip: int = 0, limit: int = 100, query: Dict[str, Any] = None
    ) -> List[Document]:
        """
        Получает список документов с возможностью фильтрации.
        
        Args:
            skip: Сколько записей пропустить
            limit: Максимальное количество документов для возврата
            query: Опциональный словарь для фильтрации
            
        Returns:
            Список документов
        """
        query = query or {}
        cursor = self.collection.find(query).skip(skip).limit(limit)
        documents = []
        async for doc_data in cursor:
            documents.append(Document(**doc_data))
        return documents
    
    async def update(self, *, doc_id: UUID, doc_update: DocumentUpdate, user_id: UUID) -> Optional[Document]:
        """
        Обновляет документ.
        
        Args:
            doc_id: ID документа для обновления
            doc_update: Данные для обновления
            user_id: ID пользователя, выполняющего обновление
            
        Returns:
            Обновленный документ, если найден, иначе None
        """
        # Получаем текущий документ
        document = await self.get_by_id(doc_id=doc_id)
        if not document:
            return None
            
        # Подготавливаем данные для обновления
        update_data = {"updated_at": datetime.now(timezone.utc)}
        
        # Обновляем поля
        if doc_update.title is not None:
            update_data["title"] = doc_update.title
            
        if doc_update.document_number is not None:
            update_data["document_number"] = doc_update.document_number
            
        if doc_update.approval_date is not None:
            update_data["approval_date"] = doc_update.approval_date
            
        if doc_update.status is not None:
            update_data["status"] = doc_update.status.value
            # Если документ стал активным и не был ранее утвержден
            if doc_update.status == DocumentStatus.ACTIVE and document.approved_by is None:
                update_data["approved_by"] = user_id
            
        if doc_update.description is not None:
            update_data["description"] = doc_update.description
            
        if doc_update.document_url is not None:
            update_data["document_url"] = str(doc_update.document_url)
            
        if doc_update.document_file_path is not None:
            update_data["document_file_path"] = doc_update.document_file_path
            
        if doc_update.department is not None:
            update_data["department"] = doc_update.department
            
        if doc_update.tags is not None:
            update_data["tags"] = doc_update.tags
            
        # Выполняем обновление в базе данных
        updated_doc = await self.collection.find_one_and_update(
            {"_id": Binary.from_uuid(doc_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        
        if updated_doc:
            return Document(**updated_doc)
        return None
    
    async def delete(self, *, doc_id: UUID) -> bool:
        """
        Удаляет документ из базы данных.
        
        Args:
            doc_id: ID документа для удаления
            
        Returns:
            True, если документ был успешно удален, иначе False
        """
        result = await self.collection.delete_one({"_id": Binary.from_uuid(doc_id)})
        return result.deleted_count > 0
    
    async def add_term(self, *, doc_id: UUID, term_id: UUID) -> bool:
        """
        Добавляет термин в список терминов документа.
        
        Args:
            doc_id: ID документа
            term_id: ID термина
            
        Returns:
            True, если термин успешно добавлен, иначе False
        """
        # Попытка добавить term_id в сет. Modified count будет 1 только если элемент был добавлен
        add_result = await self.collection.update_one(
            {"_id": Binary.from_uuid(doc_id)},
            {"$addToSet": {"term_ids": term_id}}
        )

        # Если элемент был фактически добавлен в сет, обновляем updated_at и возвращаем True
        if add_result.modified_count == 1:
            await self.collection.update_one(
                {"_id": Binary.from_uuid(doc_id)},
                {"$set": {"updated_at": datetime.now(timezone.utc)}}
            )
            return True

        # Если элемент не был добавлен (уже существовал или документ не найден), возвращаем False
        # Если документ не найден (matched_count == 0), modified_count тоже будет 0
        return False
    
    async def remove_term(self, *, doc_id: UUID, term_id: UUID) -> bool:
        """
        Удаляет термин из списка терминов документа.
        
        Args:
            doc_id: ID документа
            term_id: ID термина
            
        Returns:
            True, если термин успешно удален, иначе False
        """
        # Попытка удалить term_id из списка. Modified count будет > 0 только если элемент был удален
        remove_result = await self.collection.update_one(
            {"_id": Binary.from_uuid(doc_id)},
            {"$pull": {"term_ids": term_id}}
        )

        # Если элемент был фактически удален, обновляем updated_at и возвращаем True
        if remove_result.modified_count > 0:
            await self.collection.update_one(
                {"_id": Binary.from_uuid(doc_id)},
                {"$set": {"updated_at": datetime.now(timezone.utc)}}
            )
            return True

        # Если элемент не был удален (не существовал или документ не найден), возвращаем False
        # Если документ не найден (matched_count == 0), modified_count тоже будет 0
        return False
    
    async def search(self, *, query: str, limit: int = 20) -> List[Document]:
        """
        Поиск документов по названию, номеру или описанию.
        
        Args:
            query: Строка поиска
            limit: Максимальное количество результатов
            
        Returns:
            Список найденных документов
        """
        search_results = await self.collection.find(
            {
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"document_number": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}},
                    {"department": {"$regex": query, "$options": "i"}},
                    {"tags": {"$regex": query, "$options": "i"}}
                ]
            }
        ).limit(limit).to_list(length=limit)
        
        return [Document(**doc_data) for doc_data in search_results] 