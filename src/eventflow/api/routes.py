"""API routes for EventFlow."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import text

from eventflow.core.config import settings
from eventflow.models import (
    EventCreate, EventResponse, EventStats, StreamMessage, EventType
)
from eventflow.api.websockets import websocket_manager

router = APIRouter()


@router.get("/")
async def root():
    """Root endpoint."""
    return {"service": "EventFlow", "version": "0.1.0"}


@router.post("/events", response_model=EventResponse)
async def create_event(event: EventCreate):
    """Create a new event."""
    from eventflow.ingestion.event_manager import event_manager

    result = await event_manager.create_event(
        event_type=event.event_type,
        payload=event.payload,
        user_id=event.user_id,
        session_id=event.session_id,
        metadata=event.metadata,
    )
    return result


@router.get("/events", response_model=List[EventResponse])
async def list_events(limit: int = 50, status: str = None):
    """List events with optional filtering."""
    from eventflow.ingestion.event_manager import event_manager

    events = await event_manager.list_events(limit=limit, status=status)
    return events


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(event_id: str):
    """Get a specific event."""
    from eventflow.ingestion.event_manager import event_manager

    event = await event_manager.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/stats", response_model=EventStats)
async def get_stats():
    """Get event statistics."""
    from eventflow.ingestion.event_manager import event_manager

    return await event_manager.get_stats()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time events."""
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.handle_message(client_id, data)
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)


router.add_api_websocket_route("/ws", websocket_endpoint)