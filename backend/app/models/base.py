from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, Any, Dict
import uuid

class MongoBaseModel(BaseModel):
    """Базовая модель с ID как UUID для всех моделей MongoDB."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "arbitrary_types_allowed": True # Добавлено для UUID
    }

class TimeStampedModel(MongoBaseModel):
    """Модель с автоматическими полями даты создания и обновления."""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

class ResponseStatus:
    """Статусы для унифицированного API ответа."""
    SUCCESS = "success"
    ERROR = "error"

class StandardResponse(BaseModel):
    """Стандартный формат ответа API для унификации всех ответов."""
    status: str
    data: Optional[Any] = None
    message: Optional[str] = None
    errors: Optional[Dict[str, Any]] = None

    @classmethod
    def success(cls, data: Any = None, message: Optional[str] = None) -> 'StandardResponse':
        """Создает ответ об успешном выполнении запроса."""
        return cls(status=ResponseStatus.SUCCESS, data=data, message=message)
    
    @classmethod
    def error(cls, message: str, errors: Optional[Dict[str, Any]] = None) -> 'StandardResponse':
        """Создает ответ об ошибке с подробностями."""
        return cls(status=ResponseStatus.ERROR, message=message, errors=errors)

class HTTPError(BaseModel):
    """Стандартная модель для HTTP ошибок с полем detail."""
    detail: str 