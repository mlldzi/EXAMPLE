from uuid import UUID
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from pydantic import Field

from app.models.base import MongoBaseModel, TimeStampedModel

class ConflictStatus(str, Enum):
    """Статус конфликта определений термина."""
    NO_CONFLICT = "no_conflict"         # Нет конфликта
    MINOR_CONFLICT = "minor_conflict"   # Незначительные расхождения
    MAJOR_CONFLICT = "major_conflict"   # Значительные расхождения
    CRITICAL_CONFLICT = "critical_conflict"  # Критические противоречия

class TermDocumentRelation(TimeStampedModel):
    """Модель связи между термином и документом."""
    term_id: UUID = Field(..., description="ID термина")
    document_id: UUID = Field(..., description="ID документа")
    term_definition_in_document: str = Field(..., description="Определение термина в данном документе")
    context: Optional[str] = Field(None, description="Контекст использования термина в документе")
    locations: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="Местоположения термина в документе (например, номера страниц, разделов)"
    )
    conflict_status: ConflictStatus = Field(
        default=ConflictStatus.NO_CONFLICT,
        description="Статус конфликта с другими определениями этого термина"
    )
    conflict_description: Optional[str] = Field(
        None, 
        description="Описание конфликта с другими определениями"
    )
    verified_by: Optional[UUID] = Field(None, description="ID пользователя, верифицировавшего связь")
    verified_at: Optional[datetime] = Field(None, description="Дата верификации связи")

class TermDocumentRelationCreate(MongoBaseModel):
    """Модель для создания связи термин-документ."""
    term_id: UUID
    document_id: UUID
    term_definition_in_document: str
    context: Optional[str] = None
    locations: Optional[List[Dict[str, Any]]] = None

class TermDocumentRelationUpdate(MongoBaseModel):
    """Модель для обновления связи термин-документ."""
    term_definition_in_document: Optional[str] = None
    context: Optional[str] = None
    locations: Optional[List[Dict[str, Any]]] = None
    conflict_status: Optional[ConflictStatus] = None
    conflict_description: Optional[str] = None

class TermDocumentRelationPublic(MongoBaseModel):
    """Публичная модель связи термин-документ."""
    id: UUID
    term_id: UUID
    document_id: UUID
    term_definition_in_document: str
    context: Optional[str] = None
    locations: List[Dict[str, Any]] = []
    conflict_status: ConflictStatus
    conflict_description: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

class ConflictReport(MongoBaseModel):
    """Модель отчета о конфликтах определений термина."""
    term_id: UUID
    term_name: str
    conflicts: List[Dict[str, Any]]
    conflict_count: int
    generated_at: datetime = Field(default_factory=datetime.now)

# Модель для статистики использования терминов
class TermUsageStatistic(MongoBaseModel):
    term_id: str = Field(..., description="ID термина (строка)")
    document_count: int = Field(..., description="Количество документов, в которых встречается термин")

# Модель для детализации одного конфликта в отчете
class ConflictDetail(MongoBaseModel):
    definition1: str = Field(..., description="Первое конфликтующее определение")
    documents1: List[str] = Field(..., description="Список ID документов (строки), содержащих определение 1")
    definition2: str = Field(..., description="Второе конфликтующее определение")
    documents2: List[str] = Field(..., description="Список ID документов (строки), содержащих определение 2")

# Модель для элемента полного отчета о конфликтах (для одного термина)
class TermConflictReportEntry(MongoBaseModel):
    term_id: str = Field(..., description="ID термина с конфликтами (строка)")
    conflicts: List[ConflictDetail] = Field(..., description="Список деталей конфликтов для данного термина") 