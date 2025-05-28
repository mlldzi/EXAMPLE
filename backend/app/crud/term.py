from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from app.models.term import Term, TermCreate, TermUpdate, TermDefinition
from bson import Binary

class CRUDTerm:
    """Класс для управления CRUD операциями с терминами."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """Инициализирует класс с экземпляром базы данных."""
        self.db = db
        self.collection = db.terms
        
    async def create(self, *, term_in: TermCreate, user_id: UUID) -> Term:
        """
        Создает новый термин в базе данных.
        
        Args:
            term_in: Данные для создания термина
            user_id: ID пользователя, создающего термин
            
        Returns:
            Созданный термин
        """
        # Создаем определение термина
        term_definition = TermDefinition(
            definition=term_in.definition,
            created_by=user_id,
            source_document_id=term_in.source_document_id
        )
        
        # Генерируем UUID для нового термина
        term_id = uuid4()
        
        # Создаем объект термина
        term_data = {
            "_id": Binary.from_uuid(term_id),
            "id": term_id,
            "name": term_in.name,
            "current_definition": term_in.definition,
            "definitions_history": [term_definition.model_dump()],
            "is_approved": False,
            "tags": term_in.tags,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Добавляем термин в базу данных
        await self.collection.insert_one(term_data)
        
        # Получаем и возвращаем созданный термин
        return Term(**term_data)
        
    async def get_by_id(self, *, term_id: UUID) -> Optional[Term]:
        """
        Получает термин по его ID.
        
        Args:
            term_id: ID термина
            
        Returns:
            Термин, если найден, иначе None
        """
        term_data = await self.collection.find_one({"_id": Binary.from_uuid(term_id)})
        if term_data:
            return Term(**term_data)
        return None
    
    async def get_by_name(self, *, name: str) -> Optional[Term]:
        """
        Получает термин по его названию.
        
        Args:
            name: Название термина
            
        Returns:
            Термин, если найден, иначе None
        """
        term_data = await self.collection.find_one({"name": name})
        if term_data:
            return Term(**term_data)
        return None
    
    async def get_multiple(
        self, *, skip: int = 0, limit: int = 100, query: str = None
    ) -> List[Term]:
        """
        Получает список терминов с возможностью фильтрации по названию или определению.
        
        Args:
            skip: Сколько записей пропустить
            limit: Максимальное количество терминов для возврата
            query: Опциональная строка для поиска по названию или определению
            
        Returns:
            Список терминов
        """
        filter_query = {}
        if query:
            # Используем $or для поиска совпадений в полях name или current_definition
            # $regex используется для нечеткого поиска (можно добавить опции i для регистронезависимости)
            filter_query['$or'] = [
                {'name': {'$regex': query, '$options': 'i'}},
                {'current_definition': {'$regex': query, '$options': 'i'}},
                {'tags': {'$regex': query, '$options': 'i'}}
            ]

        cursor = self.collection.find(filter_query).skip(skip).limit(limit)
        terms = []
        async for term_data in cursor:
            terms.append(Term(**term_data))
        return terms
    
    async def update(self, *, term_id: UUID, term_update: TermUpdate, user_id: UUID) -> Optional[Term]:
        """
        Обновляет термин.
        
        Args:
            term_id: ID термина для обновления
            term_update: Данные для обновления
            user_id: ID пользователя, выполняющего обновление
            
        Returns:
            Обновленный термин, если найден, иначе None
        """
        # Получаем текущий термин
        term = await self.get_by_id(term_id=term_id)
        if not term:
            return None
            
        # Подготавливаем данные для обновления
        set_data = {"updated_at": datetime.now(timezone.utc)}
        push_data = {}
        update_document = {}

        # Если определение изменилось, создаем новое определение в истории и обновляем текущее
        if term_update.definition is not None and term_update.definition != term.current_definition:
            new_definition = TermDefinition(
                definition=term_update.definition,
                created_by=user_id
                # source_document_id не обновляем через API update
            )

            set_data["current_definition"] = term_update.definition
            # Добавляем новое определение в историю
            push_data["definitions_history"] = new_definition.model_dump()

        # Обновляем другие поля
        if term_update.name is not None:
            set_data["name"] = term_update.name

        if term_update.is_approved is not None:
            set_data["is_approved"] = term_update.is_approved
            if term_update.is_approved:
                set_data["approved_by"] = user_id
                set_data["approved_at"] = datetime.now(timezone.utc)
            else: # Если снимаем утверждение, очищаем поля утверждения
                 set_data["approved_by"] = None
                 set_data["approved_at"] = None


        if term_update.tags is not None:
            set_data["tags"] = term_update.tags

        # Формируем итоговый документ обновления
        if set_data:
            update_document["$set"] = set_data
        if push_data:
             update_document["$push"] = push_data

        # Если нет данных для обновления, возвращаем текущий объект без изменений
        if not update_document:
             return term

        # Выполняем обновление в базе данных
        updated_term_data = await self.collection.find_one_and_update(
            {"_id": Binary.from_uuid(term_id)},
            update_document, # Передаем сформированный документ обновления
            return_document=ReturnDocument.AFTER
        )

        if updated_term_data:
            return Term(**updated_term_data)
        return None
    
    async def delete(self, *, term_id: UUID) -> bool:
        """
        Удаляет термин из базы данных.
        
        Args:
            term_id: ID термина для удаления
            
        Returns:
            True, если термин был успешно удален, иначе False
        """
        result = await self.collection.delete_one({"_id": Binary.from_uuid(term_id)})
        return result.deleted_count > 0
    
    async def search(self, *, query: str, limit: int = 20) -> List[Term]:
        """
        Поиск терминов по названию или определению.
        
        Args:
            query: Строка поиска
            limit: Максимальное количество результатов
            
        Returns:
            Список найденных терминов
        """
        search_results = await self.collection.find(
            {
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"current_definition": {"$regex": query, "$options": "i"}},
                    {"tags": {"$regex": query, "$options": "i"}}
                ]
            }
        ).limit(limit).to_list(length=limit)
        
        return [Term(**term_data) for term_data in search_results] 