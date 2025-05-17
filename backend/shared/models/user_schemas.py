from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, SecretStr
from enum import Enum

from .base_schemas import BaseDBModel

class UserRole(str, Enum):
    """Роли пользователей."""
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"

class UserBase(BaseModel):
    """Базовая модель пользователя с общими полями."""
    email: EmailStr = Field(..., example="user@example.com")
    first_name: Optional[str] = Field(None, example="Иван")
    last_name: Optional[str] = Field(None, example="Иванов")

class UserCreate(UserBase):
    """Модель для создания нового пользователя, включает пароль."""
    password: SecretStr # Используем SecretStr для безопасности

class UserUpdate(BaseModel):
    """Модель для обновления данных пользователя (частичное обновление)."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    # Не позволяем обновлять пароль через этот DTO, для этого нужен отдельный эндпоинт/DTO
    # password: Optional[SecretStr] = None

class UserRead(UserBase, BaseDBModel):
    """Модель для чтения данных пользователя из БД."""
    is_active: bool = Field(default=True)
    role: UserRole = Field(default=UserRole.USER)

class UserInDB(UserRead): # Может использоваться для представления пользователя в базе данных
    hashed_password: str

class UserWithToken(UserRead):
    """Модель пользователя с токеном доступа (для ответа при логине/регистрации)."""
    access_token: str
    token_type: str = "bearer" 