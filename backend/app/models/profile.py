from pydantic import BaseModel
from typing import Optional, Dict
import uuid
from datetime import date

from .base import MongoBaseModel, TimeStampedModel

class ProfileBase(BaseModel):
    """Базовые данные профиля пользователя."""
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    birth_date: Optional[date] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    social_media: Optional[Dict[str, str]] = None  # например, {"twitter": "username", "github": "username"}

class ProfileCreate(ProfileBase):
    """Данные для создания профиля пользователя."""
    user_id: uuid.UUID

class ProfileUpdate(ProfileBase):
    """Данные для обновления профиля пользователя."""
    pass

class ProfileInDB(TimeStampedModel, ProfileBase):
    """Модель профиля как она хранится в базе данных."""
    user_id: uuid.UUID

class ProfilePublic(MongoBaseModel, ProfileBase):
    """Модель для публичного представления профиля."""
    user_id: uuid.UUID 