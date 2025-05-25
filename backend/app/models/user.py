from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
import uuid
from enum import Enum

from .base import MongoBaseModel, TimeStampedModel

class UserRole(str, Enum):
    """Роли пользователей в системе."""
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"
    

class UserStatus(str, Enum):
    """Статусы пользователя в системе."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    BANNED = "banned"

class UserBase(BaseModel):
    """Базовая информация о пользователе."""
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Данные для создания нового пользователя."""
    password: str
    
    @field_validator('password')
    @classmethod
    def password_complexity(cls, v):
        """Проверяет сложность пароля."""
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        return v

class UserUpdate(BaseModel):
    """Данные для обновления существующего пользователя."""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(TimeStampedModel, UserBase):
    """Модель пользователя как она хранится в базе данных."""
    hashed_password: str
    roles: List[UserRole] = Field(default_factory=lambda: [UserRole.USER])
    status: UserStatus = UserStatus.ACTIVE
    is_active: bool = True
    is_verified: bool = False
    
class UserPublic(MongoBaseModel):
    """Модель для публичного представления пользователя."""
    id: uuid.UUID
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    roles: List[UserRole] = []
    status: UserStatus
    is_active: bool
    created_at: Optional[str] = None 

class UserLoginRequest(BaseModel):
    """Модель для данных входа пользователя (email и пароль)."""
    email: EmailStr
    password: str 