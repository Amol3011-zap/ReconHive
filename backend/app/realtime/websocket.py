from fastapi import WebSocket, WebSocketDisconnect
from typing import Set, Dict
from app.events.bus import event_bus, Event
from app.utils.logger import logger
import json


class ConnectionManager:
    """Manage WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.user_subscriptions: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = set()
        self.user_subscriptions[user_id].add(websocket)
        logger.info("websocket_connected", user_id=user_id, connections=len(self.active_connections))

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        if user_id in self.user_subscriptions:
            self.user_subscriptions[user_id].discard(websocket)
        logger.info("websocket_disconnected", user_id=user_id, connections=len(self.active_connections))

    async def broadcast(self, message: dict):
        """Broadcast message to all connections."""
        for connection in self.active_connections.copy():
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error("websocket_broadcast_failed", error=str(e))
                self.active_connections.discard(connection)

    async def broadcast_to_user(self, user_id: str, message: dict):
        """Broadcast message to user's connections."""
        if user_id in self.user_subscriptions:
            for connection in self.user_subscriptions[user_id].copy():
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error("websocket_user_broadcast_failed", user_id=user_id, error=str(e))

    async def listen_to_events(self, manager_instance):
        """Listen to event bus and broadcast updates."""
        def event_handler(event: Event):
            message = {
                "event_type": event.event_type.value,
                "event_id": event.event_id,
                "timestamp": event.timestamp.isoformat(),
                "data": event.data,
            }
            import asyncio
            # This would need to be run in async context properly
            logger.info("event_broadcast", event_type=event.event_type.value)

        # Subscribe to all event types
        from app.events.bus import EventType
        for event_type in EventType:
            event_bus.subscribe(event_type, event_handler)


# Global connection manager
manager = ConnectionManager()
