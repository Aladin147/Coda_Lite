"""
WebSocket server for Coda.

This module provides a WebSocket server that allows clients to connect to Coda
and receive real-time events about its operation.
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Set, Any, Optional, List, Callable
import websockets
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger("coda.websocket")

class CodaWebSocketServer:
    """
    WebSocket server for Coda.

    This server allows clients to connect and receive real-time events about
    Coda's operation, including STT, LLM, TTS, and memory events.
    """

    def __init__(self, host: str = "localhost", port: int = 8765):
        """
        Initialize the WebSocket server.

        Args:
            host: Host to bind to (default: localhost)
            port: Port to bind to (default: 8765)
        """
        self.host = host
        self.port = port
        self.clients: Dict[str, WebSocketServerProtocol] = {}
        self.server = None
        self.sequence_number = 0
        self.replay_buffer: List[Dict[str, Any]] = []
        self.max_replay_events = 50
        self.running = False

        # Event handlers
        self.on_connect_handlers: List[Callable[[str], None]] = []
        self.on_disconnect_handlers: List[Callable[[str], None]] = []

        logger.info(f"WebSocket server initialized at ws://{host}:{port}")

    async def start(self):
        """Start the WebSocket server."""
        if self.running:
            logger.warning("WebSocket server already running")
            return

        self.running = True

        try:
            async def handler(websocket):
                await self._handle_client(websocket, "/")

            self.server = await websockets.serve(
                handler,
                self.host,
                self.port
            )

            logger.info(f"WebSocket server started at ws://{self.host}:{self.port}")
        except Exception as e:
            self.running = False
            logger.error(f"Failed to start WebSocket server: {e}")
            raise

    async def stop(self):
        """Stop the WebSocket server."""
        if not self.running:
            logger.warning("WebSocket server not running")
            return

        self.running = False

        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None

        # Close all client connections
        close_tasks = []
        for client_id, websocket in self.clients.items():
            try:
                close_tasks.append(websocket.close())
            except Exception as e:
                logger.error(f"Error closing client {client_id}: {e}")

        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)

        self.clients.clear()
        logger.info("WebSocket server stopped")

    async def _handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """
        Handle a client connection.

        Args:
            websocket: The WebSocket connection
            path: The connection path
        """
        client_id = str(uuid.uuid4())
        self.clients[client_id] = websocket

        # Notify connection handlers
        for handler in self.on_connect_handlers:
            try:
                handler(client_id)
            except Exception as e:
                logger.error(f"Error in connect handler: {e}")

        logger.info(f"Client {client_id} connected")

        # Send replay buffer if available
        if self.replay_buffer:
            try:
                await websocket.send(json.dumps({
                    "type": "replay",
                    "events": self.replay_buffer
                }))
                logger.debug(f"Sent replay buffer to client {client_id}")
            except Exception as e:
                logger.error(f"Error sending replay buffer to client {client_id}: {e}")

        try:
            # Keep the connection open and handle messages
            async for message in websocket:
                try:
                    # Parse the message
                    data = json.loads(message)

                    # Handle client messages (authentication, etc.)
                    await self._handle_message(client_id, data)
                except json.JSONDecodeError:
                    logger.warning(f"Received invalid JSON from client {client_id}")
                except Exception as e:
                    logger.error(f"Error handling message from client {client_id}: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Error with client {client_id}: {e}")
        finally:
            # Clean up
            self.clients.pop(client_id, None)

            # Notify disconnect handlers
            for handler in self.on_disconnect_handlers:
                try:
                    handler(client_id)
                except Exception as e:
                    logger.error(f"Error in disconnect handler: {e}")

    async def _handle_message(self, client_id: str, message: Dict[str, Any]):
        """
        Handle a message from a client.

        Args:
            client_id: The client ID
            message: The message data
        """
        logger.debug(f"Received message from client {client_id}: {message}")

        # Check if the message has a type
        if "type" not in message:
            logger.warning(f"Message from client {client_id} missing 'type' field")
            return

        # Handle different message types
        message_type = message.get("type")
        message_data = message.get("data", {})

        # Emit a client message event for other components to handle
        self.push_event("client_message", {
            "client_id": client_id,
            "message_type": message_type,
            "message_data": message_data
        })

    async def broadcast_event(self, event_type: str, data: Dict[str, Any],
                             high_priority: bool = False):
        """
        Broadcast an event to all connected clients.

        Args:
            event_type: The type of event
            data: The event data
            high_priority: Whether this is a high-priority event (for replay buffer)
        """
        if not self.running:
            logger.debug(f"Event {event_type} dropped (server not running)")
            return

        if not self.clients:
            logger.debug(f"Event {event_type} dropped (no clients connected)")
            return

        # Create the event
        self.sequence_number += 1
        event = {
            "version": "1.0",
            "seq": self.sequence_number,
            "timestamp": asyncio.get_event_loop().time(),
            "type": event_type,
            "data": data
        }

        # Add to replay buffer if high priority
        if high_priority:
            self.replay_buffer.append(event)
            # Trim buffer if needed
            if len(self.replay_buffer) > self.max_replay_events:
                self.replay_buffer = self.replay_buffer[-self.max_replay_events:]

        # Serialize the event
        event_json = json.dumps(event)

        # Broadcast to all clients
        disconnected_clients = []
        for client_id, websocket in self.clients.items():
            try:
                await websocket.send(event_json)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(client_id)
            except Exception as e:
                logger.error(f"Error sending event to client {client_id}: {e}")
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.clients.pop(client_id, None)
            logger.info(f"Removed disconnected client {client_id}")

            # Notify disconnect handlers
            for handler in self.on_disconnect_handlers:
                try:
                    handler(client_id)
                except Exception as e:
                    logger.error(f"Error in disconnect handler: {e}")

        logger.debug(f"Broadcast event {event_type} to {len(self.clients)} clients")

    async def push_event_async(self, event_type: str, data: Dict[str, Any],
                           high_priority: bool = False):
        """
        Push an event to all connected clients (async version).

        This is the async version of push_event that can be awaited.

        Args:
            event_type: The type of event
            data: The event data
            high_priority: Whether this is a high-priority event (for replay buffer)
        """
        if not self.running:
            logger.debug(f"Event {event_type} dropped (server not running)")
            return

        if not self.clients:
            logger.debug(f"Event {event_type} dropped (no clients connected)")
            return

        # Broadcast the event
        await self.broadcast_event(event_type, data, high_priority)

    def push_event(self, event_type: str, data: Dict[str, Any],
                  high_priority: bool = False):
        """
        Push an event to all connected clients (non-async version).

        This is a convenience method for pushing events from non-async code.
        It schedules the broadcast on the event loop.

        Args:
            event_type: The type of event
            data: The event data
            high_priority: Whether this is a high-priority event (for replay buffer)
        """
        if not self.running:
            logger.debug(f"Event {event_type} dropped (server not running)")
            return

        if not self.clients:
            logger.debug(f"Event {event_type} dropped (no clients connected)")
            return

        # Get the event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Schedule the broadcast
                asyncio.create_task(self.broadcast_event(event_type, data, high_priority))
            else:
                logger.warning(f"Event loop not running, event {event_type} dropped")
        except RuntimeError:
            logger.warning(f"No event loop in current thread, event {event_type} dropped")

    def register_connect_handler(self, handler: Callable[[str], None]):
        """
        Register a handler for client connections.

        Args:
            handler: Function to call when a client connects (takes client_id)
        """
        self.on_connect_handlers.append(handler)

    def register_disconnect_handler(self, handler: Callable[[str], None]):
        """
        Register a handler for client disconnections.

        Args:
            handler: Function to call when a client disconnects (takes client_id)
        """
        self.on_disconnect_handlers.append(handler)

    def get_client_count(self) -> int:
        """
        Get the number of connected clients.

        Returns:
            Number of connected clients
        """
        return len(self.clients)
