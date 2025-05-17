import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

class BaseDBModel(BaseModel):
    """
    Базовая модель для сущностей БД, включает ID и временные метки.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None) # Обновляется логикой приложения или БД

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda dt: dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        }
    ) 