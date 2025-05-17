from typing import Optional
from pydantic import BaseModel, Field
import uuid

from .base_schemas import BaseDBModel # Относительный импорт

class ItemBase(BaseModel):
    """Базовая модель для Предмета."""
    name: str = Field(..., min_length=1, max_length=100, example="Мой Предмет")
    description: Optional[str] = Field(None, max_length=500, example="Детальное описание предмета")
    price: Optional[float] = Field(None, gt=0, example=19.99)

class ItemCreate(ItemBase):
    """Модель для создания нового Предмета."""
    # Можно добавить поля, специфичные для создания, если есть
    # owner_id: Optional[uuid.UUID] = None # Пример, если предмет связан с пользователем
    pass

class ItemUpdate(BaseModel):
    """Модель для обновления Предмета (частичное обновление)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    # owner_id: Optional[uuid.UUID] = None

class ItemRead(ItemBase, BaseDBModel):
    """Модель для чтения Предмета из БД."""
    # Дополнительные поля, которые есть в БД, но не в ItemBase
    # owner_id: Optional[uuid.UUID] = None # Пример
    pass 