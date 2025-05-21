from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime

from .base import MongoBaseModel, TimeStampedModel

class Token(BaseModel):
    """Базовая модель ответа с токеном."""
    access_token: str
    token_type: str = "bearer"
    
class TokenData(BaseModel):
    """Данные, извлекаемые из токена."""
    user_id: uuid.UUID
    roles: Optional[List[str]] = None
    exp: Optional[int] = None

class TokenResponse(BaseModel):
    """Расширенная модель ответа с токенами."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    """Модель запроса для обновления токена."""
    refresh_token: str

class RefreshTokenInDB(TimeStampedModel):
    """Модель refresh токена в базе данных."""
    user_id: uuid.UUID
    refresh_token: str
    expires_at: datetime
    is_revoked: bool = False

class TokenBlacklist(MongoBaseModel):
    """Модель для хранения отозванных токенов."""
    token: str
    expires_at: datetime 