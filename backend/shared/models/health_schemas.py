from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class DependencyHealth(BaseModel):
    """Статус работоспособности отдельной зависимости."""
    name: str
    status: str = Field(default="healthy")
    detail: Optional[str] = None

class HealthCheckResponse(BaseModel):
    """Модель для ответа эндпоинта проверки работоспособности."""
    service_name: str
    status: str = Field(default="healthy")
    version: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    dependencies: Optional[List[DependencyHealth]] = Field(default_factory=list) 