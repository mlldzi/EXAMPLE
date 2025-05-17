from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import ValidationError

from backend.shared.config.settings import settings
from backend.shared.models.auth_schemas import TokenPayload, TokenType

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class JWTAuthenticationError(Exception):
    """Кастомное исключение для ошибок аутентификации JWT."""
    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

def create_jwt_token(
    subject: str, # Обычно user_id или email
    token_type: TokenType,
    expires_delta: Optional[timedelta] = None,
    custom_claims: Optional[Dict[str, Any]] = None
) -> str:
    """Создает JWT токен (access или refresh)."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        if token_type == TokenType.ACCESS:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        elif token_type == TokenType.REFRESH:
            expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        else:
            raise ValueError("Invalid token type for default expiry") # unreachable

    payload = TokenPayload(
        sub=subject,
        type=token_type,
        exp=int(expire.timestamp()),
        # iat и jti будут сгенерированы моделью TokenPayload
    )

    if custom_claims:
        # Обновляем payload стандартными полями, если они есть в custom_claims,
        # и добавляем кастомные поля.
        # Это позволяет передать, например, roles из custom_claims в TokenPayload
        payload_dict = payload.model_dump()
        for key, value in custom_claims.items():
            if hasattr(payload, key) and key not in ["sub", "type", "exp", "iat", "jti"]: # Не перезаписываем ключевые поля
                 payload_dict[key] = value
            elif key not in payload_dict: # Добавляем только новые кастомные поля
                payload_dict[key] = value
        payload = TokenPayload(**payload_dict) # Валидируем снова с кастомными полями

    encoded_jwt = jwt.encode(
        payload.model_dump(exclude_none=True), 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def create_access_token(subject: str, custom_claims: Optional[Dict[str, Any]] = None) -> str:
    """Создает access токен."""
    return create_jwt_token(
        subject=subject, 
        token_type=TokenType.ACCESS, 
        custom_claims=custom_claims
    )

def create_refresh_token(subject: str) -> str:
    """Создает refresh токен."""
    return create_jwt_token(
        subject=subject, 
        token_type=TokenType.REFRESH
    )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет обычный пароль на соответствие хешированному."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Генерирует хеш для пароля."""
    return pwd_context.hash(password)

def decode_jwt_token(token: str) -> Optional[TokenPayload]:
    """
    Декодирует и валидирует JWT токен.
    Возвращает TokenPayload или вызывает JWTAuthenticationError.
    """
    try:
        payload_dict = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False} # Audience verification можно добавить, если нужно
        )
        # Валидация с помощью Pydantic модели
        token_payload = TokenPayload(**payload_dict)
        
        # Проверка времени истечения
        if datetime.fromtimestamp(token_payload.exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise JWTAuthenticationError("Token has expired", status_code=401)
            
        return token_payload
    except JWTError as e:
        raise JWTAuthenticationError(f"Invalid token: {str(e)}", status_code=401)
    except ValidationError as e:
        raise JWTAuthenticationError(f"Invalid token payload: {str(e)}", status_code=401)
    except Exception as e: # Ловим другие возможные ошибки
        raise JWTAuthenticationError(f"Token processing error: {str(e)}", status_code=400) 