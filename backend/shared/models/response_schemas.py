from typing import Optional, List, TypeVar, Generic, Any
from pydantic import BaseModel, Field, ConfigDict

DataType = TypeVar('DataType')

class MessageResponse(BaseModel):
    """Общая модель для простых текстовых ответов API."""
    message: str

class StatusResponse(BaseModel):
    """Общая модель для ответов о статусе операции."""
    success: bool = True
    detail: Optional[str] = None

class Paginated(Generic[DataType], BaseModel):
    """Общая модель для пагинированных ответов API."""
    total_items: int
    items: List[DataType]
    page: int
    size: int
    total_pages: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class ErrorDetail(BaseModel):
    """Детализация ошибки для одного поля или аспекта."""
    loc: Optional[List[str]] = None # ["body", "field_name"]
    msg: str
    type: str # Тип ошибки, например "value_error.missing"

class ErrorResponse(BaseModel):
    """Стандартная модель для ответов об ошибках."""
    detail: str # Общее сообщение об ошибке
    errors: Optional[List[ErrorDetail]] = None # Список конкретных ошибок валидации 