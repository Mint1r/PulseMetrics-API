from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict

class EventCreateSchema(BaseModel):

    project_id : UUID = Field(
        ..., 
        description = 'Уникальный идентификатор сайта/проекта',
        examples=["9f8e7d6c-5b4a-3f2e-1d0c-9b8a7f6e5d4c"]
    )

    api_key: str = Field(
        ...,
        min_length=32,
        description="Секретный API-ключ проекта"
    )

    event_type: str = Field(
        ..., 
        min_length=3, 
        max_length=64,
        description="Тип события в формате snake_case",
        examples=["cart_item_added"]
    )

    user_id: Optional[str] = Field(
        default=None, 
        max_length=128,
        description="ID пользователя в системе клиента",
        examples=["usr_12345"]
    )

    session_id: str = Field(
        ..., 
        min_length=8, 
        max_length=128,
        description="ID сессии браузера/устройства",
        examples=["sess_abc123xyz"]
    )

    properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Произвольные дополнительные атрибуты события",
        examples=[{"item_id": 42, "price": 1200.50, "currency": "RUB"}]
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp возникновения события"
    )

    model_config = ConfigDict(
        extra="ignore"  # Игнорируем лишние неизвестные поля в JSON
    )

    
class EventResponseSchema(BaseModel):
    status: str = Field(default="queued", examples=["queued"])
    event_id: UUID = Field(
        default_factory=uuid4, 
        description="Сгенерированный ID события для отслеживания"
    )
