from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, SecretStr
import uuid
from datetime import datetime, timezone
from enum import Enum

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

class LoginRequest(BaseModel):
    """Модель запроса для входа пользователя."""
    email: EmailStr = Field(..., example="user@example.com")
    password: SecretStr

class Token(BaseModel):
    """Модель ответа для токенов аутентификации."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = Field(default="bearer")
    # expires_in: Optional[int] = None # Время жизни access_token в секундах (информационное)
    # refresh_expires_in: Optional[int] = None # Время жизни refresh_token (информационное)

class TokenPayload(BaseModel):
    """
    Содержимое JWT.
    """
    sub: str  # Subject (например, user_id)
    type: TokenType # Тип токена (access или refresh)
    exp: int  # Время истечения (Unix timestamp)
    iat: int = Field(default_factory=lambda: int(datetime.now(timezone.utc).timestamp())) # Issued At
    jti: str = Field(default_factory=lambda: str(uuid.uuid4())) # JWT ID

    # Дополнительные поля, специфичные для access токена
    # roles: Optional[List[str]] = None
    # permissions: Optional[List[str]] = None
    
    # Поле для связи refresh и access токенов (если используется)
    # refresh_jti: Optional[str] = None # jti оригинального refresh токена

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str # Обычно это одноразовый токен, не JWT
    new_password: SecretStr

class RefreshTokenRequest(BaseModel):
    """Модель запроса для обновления access токена с помощью refresh токена."""
    refresh_token: str 