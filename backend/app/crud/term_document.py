from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from app.models.term_document import (
    TermDocumentRelation, 
    TermDocumentRelationCreate,
    TermDocumentRelationUpdate, 
    ConflictStatus
)
from bson import Binary

class CRUDTermDocument:
    """Класс для управления CRUD операциями со связями термин-документ."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """Инициализирует класс с экземпляром базы данных."""
        self.db = db
        self.collection = db.term_document_relations
        self.terms_collection = db.terms # Добавляем доступ к коллекции терминов
        
    async def create(self, *, relation_in: TermDocumentRelationCreate) -> TermDocumentRelation:
        """
        Создает новую связь термин-документ в базе данных.
        
        Args:
            relation_in: Данные для создания связи
            
        Returns:
            Созданная связь
        """
        # Генерируем UUID для новой связи
        relation_id = uuid4()
        
        # Подготавливаем начальные данные для связи
        locations = relation_in.locations or []
        
        # Создаем объект связи
        relation_data = {
            "_id": Binary.from_uuid(relation_id),
            "id": relation_id,
            "term_id": relation_in.term_id,
            "document_id": relation_in.document_id,
            "term_definition_in_document": relation_in.term_definition_in_document,
            "context": relation_in.context,
            "locations": locations,
            "conflict_status": ConflictStatus.NO_CONFLICT.value,  # По умолчанию, конфликта нет
            "conflict_description": None,
            "verified_by": None,
            "verified_at": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Добавляем связь в базу данных
        await self.collection.insert_one(relation_data)
        
        # Получаем и возвращаем созданную связь
        return TermDocumentRelation(**relation_data)
        
    async def get_by_id(self, *, relation_id: UUID) -> Optional[TermDocumentRelation]:
        """
        Получает связь по ее ID.
        
        Args:
            relation_id: ID связи
            
        Returns:
            Связь, если найдена, иначе None
        """
        relation_data = await self.collection.find_one({"_id": Binary.from_uuid(relation_id)})
        if relation_data:
            return TermDocumentRelation(**relation_data)
        return None
    
    async def get_by_term_and_document(self, *, term_id: UUID, document_id: UUID) -> Optional[TermDocumentRelation]:
        """
        Получает связь по ID термина и ID документа.
        
        Args:
            term_id: ID термина
            document_id: ID документа
            
        Returns:
            Связь, если найдена, иначе None
        """
        relation_data = await self.collection.find_one({
            "term_id": term_id,
            "document_id": document_id
        })
        if relation_data:
            return TermDocumentRelation(**relation_data)
        return None
    
    async def get_by_term_id(self, *, term_id: UUID) -> List[TermDocumentRelation]:
        """
        Получает все связи для заданного термина.
        
        Args:
            term_id: ID термина
            
        Returns:
            Список связей
        """
        cursor = self.collection.find({"term_id": term_id})
        relations = []
        async for relation_data in cursor:
            relations.append(TermDocumentRelation(**relation_data))
        return relations
    
    async def get_by_document_id(self, *, document_id: UUID) -> List[TermDocumentRelation]:
        """
        Получает все связи для заданного документа.
        
        Args:
            document_id: ID документа
            
        Returns:
            Список связей
        """
        cursor = self.collection.find({"document_id": document_id})
        relations = []
        async for relation_data in cursor:
            relations.append(TermDocumentRelation(**relation_data))
        return relations
    
    async def get_multiple(
        self, *, skip: int = 0, limit: int = 100, query: Dict[str, Any] = None
    ) -> List[TermDocumentRelation]:
        """
        Получает список связей с возможностью фильтрации.
        
        Args:
            skip: Сколько записей пропустить
            limit: Максимальное количество связей для возврата
            query: Опциональный словарь для фильтрации
            
        Returns:
            Список связей
        """
        query = query or {}
        cursor = self.collection.find(query).skip(skip).limit(limit)
        relations = []
        async for relation_data in cursor:
            relations.append(TermDocumentRelation(**relation_data))
        return relations
    
    async def get_term_usage_statistics(self) -> List[Dict[str, Any]]:
        """
        Получает статистику использования терминов (количество документов, в которых встречается каждый термин).
        Включает все термины, даже если у них 0 связанных документов.

        Returns:
            Список словарей с term_id, term_name и document_count.
        """
        pipeline = [
            {  # Шаг 1: Получить все термины и их связи (Left Join)
                '$lookup': {
                    'from': 'term_document_relations',  # Коллекция связей
                    'localField': 'id',  # Поле в коллекции 'terms'
                    'foreignField': 'term_id',  # Поле в коллекции 'term_document_relations'
                    'as': 'relations'  # Название нового поля для связей
                }
            },
            {  # Шаг 2: Развернуть массив связей (включая термины без связей)
                '$unwind': {
                    'path': '$relations',
                    'preserveNullAndEmptyArrays': True
                }
            },
            {  # Шаг 3: Сгруппировать по ID и имени термина и собрать уникальные document_id
                 '$group': {
                     '_id': '$_id', # Группируем по ID термина (из коллекции terms)
                     'term_name': { '$first': '$name' }, # Берем имя термина
                     'document_ids': { '$addToSet': '$relations.document_id' } # Собираем уникальные document_id
                 }
             },
            {  # Шаг 4: Сформировать финальный результат
                '$project': {
                    '_id': 0,
                    'term_id': '$_id',
                    'term_name': '$term_name', 
                    'document_count': { '$size': '$document_ids' } # Подсчитываем количество уникальных document_id
                }
            }
        ]

        # Выполняем агрегацию на коллекции терминов
        cursor = self.terms_collection.aggregate(pipeline)
        results = []
        async for doc in cursor:
            # MongoDB возвращает UUID как Binary, преобразуем в str для консистентности с моделями
            doc["term_id"] = str(doc["term_id"])
            results.append(doc)
        return results
    
    async def update(
        self, *, relation_id: UUID, relation_update: TermDocumentRelationUpdate, user_id: Optional[UUID] = None
    ) -> Optional[TermDocumentRelation]:
        """
        Обновляет связь термин-документ.
        
        Args:
            relation_id: ID связи для обновления
            relation_update: Данные для обновления
            user_id: ID пользователя, выполняющего обновление
            
        Returns:
            Обновленная связь, если найдена, иначе None
        """
        # Получаем текущую связь
        relation = await self.get_by_id(relation_id=relation_id)
        if not relation:
            return None
            
        # Подготавливаем данные для обновления
        update_data = {"updated_at": datetime.now(timezone.utc)}
        
        # Обновляем поля
        if relation_update.term_definition_in_document is not None:
            update_data["term_definition_in_document"] = relation_update.term_definition_in_document
            
        if relation_update.context is not None:
            update_data["context"] = relation_update.context
            
        if relation_update.locations is not None:
            update_data["locations"] = relation_update.locations
            
        if relation_update.conflict_status is not None:
            update_data["conflict_status"] = relation_update.conflict_status.value
            
        if relation_update.conflict_description is not None:
            update_data["conflict_description"] = relation_update.conflict_description
            
        if user_id:
            update_data["verified_by"] = user_id
            update_data["verified_at"] = datetime.now(timezone.utc)
            
        # Выполняем обновление в базе данных
        updated_relation = await self.collection.find_one_and_update(
            {"_id": Binary.from_uuid(relation_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        
        if updated_relation:
            return TermDocumentRelation(**updated_relation)
        return None
    
    async def delete(self, *, relation_id: UUID) -> bool:
        """
        Удаляет связь из базы данных.
        
        Args:
            relation_id: ID связи для удаления
            
        Returns:
            True, если связь была успешно удалена, иначе False
        """
        result = await self.collection.delete_one({"_id": Binary.from_uuid(relation_id)})
        return result.deleted_count > 0
    
    async def delete_by_term_and_document(self, *, term_id: UUID, document_id: UUID) -> bool:
        """
        Удаляет связь по ID термина и ID документа.
        
        Args:
            term_id: ID термина
            document_id: ID документа
            
        Returns:
            True, если связь была успешно удалена, иначе False
        """
        result = await self.collection.delete_one({
            "term_id": term_id,
            "document_id": document_id
        })
        return result.deleted_count > 0
    
    async def delete_by_term_id(self, *, term_id: UUID) -> int:
        """
        Удаляет все связи для заданного термина.

        Args:
            term_id: ID термина

        Returns:
            Количество удаленных связей.
        """
        result = await self.collection.delete_many({"term_id": term_id})
        return result.deleted_count

    async def delete_by_document_id(self, *, document_id: UUID) -> int:
        """
        Удаляет все связи для заданного документа.

        Args:
            document_id: ID документа

        Returns:
            Количество удаленных связей.
        """
        result = await self.collection.delete_many({"document_id": document_id})
        return result.deleted_count
    
    async def check_for_conflicts(self, *, term_id: UUID) -> List[Dict[str, Any]]:
        """
        Проверяет наличие конфликтов в определениях термина в разных документах.
        
        Args:
            term_id: ID термина
            
        Returns:
            Список обнаруженных конфликтов
        """
        # Получаем все связи для данного термина
        relations = await self.get_by_term_id(term_id=term_id)
        
        # Если связей меньше 2, конфликты невозможны
        if len(relations) < 2:
            return []
        
        conflicts = []
        # Словарь определений для быстрого сравнения
        definitions = {}
        
        # Собираем все определения из разных документов
        for relation in relations:
            definition = relation.term_definition_in_document
            if definition in definitions:
                # Это определение уже встречалось, добавляем документ к списку
                definitions[definition].append(relation.document_id)
            else:
                # Новое определение
                definitions[definition] = [relation.document_id]
        
        # Если есть только одно уникальное определение, конфликтов нет
        if len(definitions) <= 1:
            return []
        
        # Иначе формируем отчет о конфликтах
        for i, (def1, docs1) in enumerate(definitions.items()):
            for def2, docs2 in list(definitions.items())[i+1:]:
                # Для каждой пары разных определений создаем запись о конфликте
                conflicts.append({
                    "definition1": def1,
                    "documents1": docs1,
                    "definition2": def2,
                    "documents2": docs2
                })
        
        # Преобразуем UUID документов в строки для соответствия Pydantic моделям
        for conflict in conflicts:
            conflict["documents1"] = [str(doc_id) for doc_id in conflict["documents1"]]
            conflict["documents2"] = [str(doc_id) for doc_id in conflict["documents2"]]
            
        return conflicts
    
    async def update_conflict_status(self, *, term_id: UUID) -> bool:
        """
        Обновляет статус конфликта для всех связей термина.
        
        Args:
            term_id: ID термина
            
        Returns:
            True, если обновление выполнено успешно
        """
        # Проверяем наличие конфликтов
        conflicts = await self.check_for_conflicts(term_id=term_id)
        
        # Если конфликтов нет, устанавливаем всем связям статус NO_CONFLICT
        if not conflicts:
            await self.collection.update_many(
                {"term_id": term_id},
                {
                    "$set": {
                        "conflict_status": ConflictStatus.NO_CONFLICT.value,
                        "conflict_description": None
                    }
                }
            )
            return True
        
        # Если есть конфликты, обновляем статусы для всех связей
        # Простой алгоритм: устанавливаем всем связям статус MAJOR_CONFLICT
        # В реальном приложении здесь был бы более сложный алгоритм анализа различий
        
        conflict_description = f"Обнаружено {len(conflicts)} конфликтов в определениях термина"
        await self.collection.update_many(
            {"term_id": term_id},
            {
                "$set": {
                    "conflict_status": ConflictStatus.MAJOR_CONFLICT.value,
                    "conflict_description": conflict_description
                }
            }
        )
        return True

    async def get_terms_with_conflicts(self) -> List[UUID]:
        """
        Находит все term_id, у которых есть конфликты определений в разных документах.

        Returns:
            Список UUID терминов с конфликтами.
        """
        pipeline = [
            {
                "$group": {
                    "_id": "$term_id",
                    "distinct_definitions": {"$addToSet": "$term_definition_in_document"}
                }
            },
            {
                "$match": {
                    "$expr": { "$gt": [{ "$size": "$distinct_definitions" }, 1] }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "term_id": "$_id"
                }
            }
        ]
        
        cursor = self.collection.aggregate(pipeline)
        term_ids_with_conflicts = [doc["term_id"] for doc in await cursor.to_list(None)]
        return term_ids_with_conflicts 