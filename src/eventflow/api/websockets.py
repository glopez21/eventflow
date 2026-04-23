"""WebSocket manager for real-time communication."""

import json
import logging
from typing import Dict, Set

import redis.asyncio as redis
from fastapi import WebSocket

from eventflow.core.config import settings

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and Redis pub/sub."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.redis_client: redis.Redis = None
        self.pubsub: redis.client.PubSub = None

    async def connect_redis(self):
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            await self.redis_client.ping()
            self.redis_connected = True
            logger.info("Connected to Redis")

            self.pubsub = self.redis_client.pubsub()
            asyncio.create_task(self._listen_to_channels())
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
            self.redis_connected = False

    async def disconnect_redis(self):
        """Disconnect from Redis."""
        if self.pubsub:
            await self.pubsub.close()
        if self.redis_client:
            await self.redis_client.close()

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and store a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")

        if self.redis_connected:
            await self.redis_client.subscribe(f"events:{client_id}")

    def disconnect(self, client_id: str):
        """Remove a WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")

    async def send_message(self, client_id: str, message: dict):
        """Send message to a specific client."""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        for client_id in self.active_connections:
            await self.send_message(client_id, message)

    async def handle_message(self, client_id: str, data: str):
        """Handle incoming message from client."""
        try:
            message = json.loads(data)
            event_type = message.get("type", "ping")

            if event_type == "ping":
                await self.send_message(client_id, {"type": "pong"})
            elif event_type == "subscribe":
                channel = message.get("channel")
                if self.redis_connected and channel:
                    await self.redis_client.subscribe(f"events:{channel}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from client {client_id}")

    async def _listen_to_channels(self):
        """Listen to Redis channels in background."""
        if not self.pubsub:
            return

        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    channel = message["channel"]
                    data = json.loads(message["data"])
                    client_id = channel.split(":")[-1]

                    if client_id in self.active_connections:
                        await self.send_message(client_id, data)
                    elif client_id == "broadcast":
                        await self.broadcast(data)
        except Exception as e:
            logger.error(f"Error in Redis listener: {e}")


import asyncio
websocket_manager = WebSocketManager()