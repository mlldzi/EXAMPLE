from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from app.models.user import UserCreate, UserInDB, UserUpdate
from app.db.session import USERS_COLLECTION
from app.core.security import get_password_hash

class CRUDUser:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[USERS_COLLECTION]

    async def get_by_id(self, user_id: UUID) -> Optional[UserInDB]:
        """Получает пользователя по его UUID."""
        user_data = await self.collection.find_one({"id": user_id})
        if user_data:
            return UserInDB(**user_data)
        return None

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        """Получает пользователя по email."""
        user_data = await self.collection.find_one({"email": email})
        if user_data:
            return UserInDB(**user_data)
        return None

    async def create(self, user_in: UserCreate) -> UserInDB:
        """Создает нового пользователя."""
        hashed_password = get_password_hash(user_in.password)
        user_data = user_in.model_dump()
        user_data["hashed_password"] = hashed_password
        del user_data["password"] # Удаляем сырой пароль перед сохранением
        
        # Создаем объект UserInDB для получения дефолтных значений (id, created_at, etc.)
        user_in_db = UserInDB(**user_data)
        user_dict = user_in_db.model_dump(by_alias=True)
        
        await self.collection.insert_one(user_dict)
        return user_in_db

    async def update(self, user_id: UUID, user_update: UserUpdate) -> Optional[UserInDB]:
        """Обновляет данные пользователя."""
        update_data = user_update.model_dump(exclude_unset=True)
        
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data["password"])
            del update_data["password"]
            
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        result = await self.collection.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 1:
            updated_user = await self.get_by_id(user_id)
            return updated_user
        return None

    async def delete(self, user_id: UUID) -> bool:
        """Удаляет пользователя по его UUID."""
        result = await self.collection.delete_one({"id": user_id})
        return result.deleted_count == 1

    async def get_multiple(self, skip: int = 0, limit: int = 100) -> List[UserInDB]:
        """Получает список пользователей с пагинацией."""
        users = await self.collection.find({}).skip(skip).limit(limit).to_list(length=limit)
        return [UserInDB(**user) for user in users]
