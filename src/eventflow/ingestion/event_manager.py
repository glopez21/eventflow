"""Event ingestion and management."""

import json
import logging
import uuid
from datetime import datetime
from typing import List, Optional

import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from eventflow.core.config import settings
from eventflow.models import EventStatus, EventType

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class EventManager:
    """Manages event creation, processing, and storage."""

    def __init__(self):
        self.redis_client = None
        self._connect_redis()

    def _connect_redis(self):
        """Connect to Redis for real-time processing."""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
        except Exception as e:
            logger.warning(f"Redis not available: {e}")

    async def create_event(
        self,
        event_type: EventType,
        payload: dict,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> dict:
        """Create a new event."""
        event_id = str(uuid.uuid4())
        now = datetime.utcnow()

        event_data = {
            "id": event_id,
            "event_type": event_type.value,
            "payload": json.dumps(payload),
            "status": EventStatus.PENDING.value,
            "user_id": user_id,
            "session_id": session_id,
            "metadata": json.dumps(metadata) if metadata else None,
            "created_at": now.isoformat(),
        }

        async with AsyncSessionLocal() as db:
            await db.execute(
                text("""
                    INSERT INTO events (id, event_type, payload, status, user_id, session_id, metadata, created_at)
                    VALUES (:id, :event_type, :payload, :status, :user_id, :session_id, :metadata, :created_at)
                """),
                event_data
            )
            await db.commit()

        if self.redis_client:
            await self.redis_client.publish(
                "events:new",
                json.dumps({"event_id": event_id, "type": event_type.value})
            )

        return {
            "id": event_id,
            "event_type": event_type,
            "payload": payload,
            "status": EventStatus.PENDING,
            "user_id": user_id,
            "session_id": session_id,
            "created_at": now,
        }

    async def get_event(self, event_id: str) -> Optional[dict]:
        """Get an event by ID."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                text("SELECT * FROM events WHERE id = :id"),
                {"id": event_id}
            )
            row = result.fetchone()
            if row:
                return dict(row._mapping)
        return None

    async def list_events(self, limit: int = 50, status: Optional[str] = None) -> List[dict]:
        """List events with optional filtering."""
        async with AsyncSessionLocal() as db:
            query = "SELECT * FROM events ORDER BY created_at DESC LIMIT :limit"
            if status:
                query = "SELECT * FROM events WHERE status = :status ORDER BY created_at DESC LIMIT :limit"
                result = await db.execute(text(query), {"status": status, "limit": limit})
            else:
                result = await db.execute(text(query), {"limit": limit})

            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

    async def get_stats(self) -> dict:
        """Get event statistics."""
        async with AsyncSessionLocal() as db:
            total = await db.execute(text("SELECT COUNT(*) FROM events"))
            pending = await db.execute(text("SELECT COUNT(*) FROM events WHERE status = 'pending'"))
            processing = await db.execute(text("SELECT COUNT(*) FROM events WHERE status = 'processing'"))
            completed = await db.execute(text("SELECT COUNT(*) FROM events WHERE status = 'completed'"))
            failed = await db.execute(text("SELECT COUNT(*) FROM events WHERE status = 'failed'"))

            return {
                "total_events": total.scalar() or 0,
                "pending": pending.scalar() or 0,
                "processing": processing.scalar() or 0,
                "completed": completed.scalar() or 0,
                "failed": failed.scalar() or 0,
            }


event_manager = EventManager()