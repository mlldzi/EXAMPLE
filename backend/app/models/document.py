from uuid import UUID
from typing import List, Optional
from datetime import datetime
from enum import Enum
from pydantic import Field, HttpUrl

from app.models.base import MongoBaseModel, TimeStampedModel

class DocumentStatus(str, Enum):
    """Статусы нормативного документа."""
    DRAFT = "draft"         # Черновик
    ACTIVE = "active"       # Активный
    OUTDATED = "outdated"   # Устаревший
    ARCHIVED = "archived"   # Архивный
    
class Document(TimeStampedModel):
    """Модель нормативного документа."""
    title: str = Field(..., description="Название документа")
    document_number: str = Field(..., description="Номер документа")
    approval_date: datetime = Field(..., description="Дата утверждения документа")
    status: DocumentStatus = Field(default=DocumentStatus.ACTIVE, description="Статус документа")
    description: Optional[str] = Field(None, description="Краткое описание документа")
    document_url: Optional[HttpUrl] = Field(None, description="Ссылка на документ")
    document_file_path: Optional[str] = Field(None, description="Путь к файлу документа в системе")
    owner_id: UUID = Field(..., description="ID владельца/автора документа")
    approved_by: Optional[UUID] = Field(None, description="ID пользователя, утвердившего документ")
    term_ids: List[UUID] = Field(default_factory=list, description="Список ID терминов, используемых в документе")
    department: Optional[str] = Field(None, description="Отдел/департамент, ответственный за документ")
    tags: List[str] = Field(default_factory=list, description="Теги для категоризации документа")

class DocumentCreate(MongoBaseModel):
    """Модель для создания нового документа."""
    title: str
    document_number: str
    approval_date: datetime
    description: Optional[str] = None
    document_url: Optional[HttpUrl] = None
    department: Optional[str] = None
    tags: List[str] = []

class DocumentUpdate(MongoBaseModel):
    """Модель для обновления документа."""
    title: Optional[str] = None
    document_number: Optional[str] = None
    approval_date: Optional[datetime] = None
    status: Optional[DocumentStatus] = None
    description: Optional[str] = None
    document_url: Optional[HttpUrl] = None
    document_file_path: Optional[str] = None
    department: Optional[str] = None
    tags: Optional[List[str]] = None

class DocumentPublic(MongoBaseModel):
    """Публичная модель документа."""
    id: UUID
    title: str
    document_number: str
    approval_date: str
    status: DocumentStatus
    description: Optional[str] = None
    document_url: Optional[str] = None
    department: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None
    tags: List[str] = [] 