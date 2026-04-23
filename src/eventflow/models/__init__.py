"""Event models for EventFlow."""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class EventStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class EventType(str, Enum):
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    ANALYTICS = "analytics"
    NOTIFICATION = "notification"


class EventCreate(BaseModel):
    """Schema for creating an event."""

    event_type: EventType
    payload: dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class EventResponse(BaseModel):
    """Schema for event response."""

    id: str
    event_type: EventType
    payload: dict[str, Any]
    status: EventStatus
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None


class EventStats(BaseModel):
    """Schema for event statistics."""

    total_events: int
    pending: int
    processing: int
    completed: int
    failed: int


class StreamMessage(BaseModel):
    """WebSocket message schema."""

    type: str
    data: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)