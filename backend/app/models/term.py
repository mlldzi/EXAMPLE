from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime
from pydantic import Field

from app.models.base import MongoBaseModel, TimeStampedModel

class TermDefinition(MongoBaseModel):
    """Модель определения термина."""
    definition: str = Field(..., description="Текст определения термина")
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: UUID = Field(..., description="ID пользователя, создавшего определение")
    source_document_id: Optional[UUID] = Field(None, description="ID документа-источника определения")
    
class Term(TimeStampedModel):
    """Модель термина в глоссарии."""
    name: str = Field(..., description="Название термина")
    current_definition: str = Field(..., description="Текущее определение термина")
    definitions_history: List[TermDefinition] = Field(default_factory=list, description="История определений")
    is_approved: bool = Field(default=False, description="Флаг утверждения термина")
    approved_by: Optional[UUID] = Field(None, description="ID пользователя, утвердившего термин")
    approved_at: Optional[datetime] = Field(None, description="Дата утверждения термина")
    tags: List[str] = Field(default_factory=list, description="Теги для категоризации термина")
    
class TermCreate(MongoBaseModel):
    """Модель для создания нового термина."""
    name: str
    definition: str
    source_document_id: Optional[UUID] = None
    tags: List[str] = []

class TermUpdate(MongoBaseModel):
    """Модель для обновления термина."""
    name: Optional[str] = None
    definition: Optional[str] = None
    is_approved: Optional[bool] = None
    tags: Optional[List[str]] = None

class TermPublic(MongoBaseModel):
    """Публичная модель термина."""
    id: UUID
    name: str
    current_definition: str
    is_approved: bool
    created_at: str
    updated_at: Optional[str] = None
    tags: List[str] = [] 