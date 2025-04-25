"""
Thread-safe WebSocket server for Coda.

This module provides a thread-safe WebSocket server that allows clients to connect to Coda
and receive real-time events about its operation.
"""

import asyncio
import json
import logging
import uuid
import threading
import time
from typing import Dict, Set, Any, Optional, List, Callable, MutableMapping, Tuple
import websockets
from websockets.server import WebSocketServerProtocol
from concurrent.futures import ThreadPoolExecutor

# Import our new modules
from .event_loop_manager import get_event_loop, run_coroutine_threadsafe
from .message_deduplication import is_duplicate_message
from .authentication import validate_token, generate_token

logger = logging.getLogger("coda.websocket")

class ThreadSafeDict(MutableMapping):
    """A thread-safe dictionary implementation."""

    def __init__(self, *args, **kwargs):
        self._dict = dict(*args, **kwargs)
        self._lock = threading.RLock()

    def __getitem__(self, key):
        with self._lock:
            return self._dict[key]

    def __setitem__(self, key, value):
        with self._lock:
            self._dict[key] = value

    def __delitem__(self, key):
        with self._lock:
            del self._dict[key]

    def __iter__(self):
        # Create a copy of the keys to avoid "dictionary changed size during iteration"
        with self._lock:
            return iter(list(self._dict.keys()))

    def __len__(self):
        with self._lock:
            return len(self._dict)

    def items(self):
        """Return a copy of the dictionary items."""
        with self._lock:
            return list(self._dict.items())

    def keys(self):
        """Return a copy of the dictionary keys."""
        with self._lock:
            return list(self._dict.keys())

    def values(self):
        """Return a copy of the dictionary values."""
        with self._lock:
            return list(self._dict.values())

    def get(self, key, default=None):
        """Get a value with a default."""
        with self._lock:
            return self._dict.get(key, default)

    def pop(self, key, default=None):
        """Remove and return a value."""
        with self._lock:
            return self._dict.pop(key, default)

    def clear(self):
        """Clear the dictionary."""
        with self._lock:
            self._dict.clear()


class CodaWebSocketServer:
    """
    Thread-safe WebSocket server for Coda.

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
        self.clients = ThreadSafeDict()  # Thread-safe dictionary for clients
        self.server = None
        self.sequence_number = 0
        self.sequence_lock = threading.Lock()  # Lock for sequence number
        self.replay_buffer: List[Dict[str, Any]] = []
        self.replay_lock = threading.Lock()  # Lock for replay buffer
        self.max_replay_events = 50
        self.running = False
        self.event_loop = None
        self.server_loop = None

        # Event handlers
        self.on_connect_handlers: List[Callable[[str], None]] = []
        self.on_disconnect_handlers: List[Callable[[str], None]] = []

        # Thread pool for handling client messages
        self.thread_pool = ThreadPoolExecutor(max_workers=10)

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

            # Get the event loop using our event loop manager
            self.event_loop = get_event_loop()

            # Set this as the main loop in our event loop manager
            from .event_loop_manager import get_event_loop_manager
            get_event_loop_manager().set_main_loop(self.event_loop)

            # For Windows, use SelectorEventLoop instead of ProactorEventLoop
            # This helps avoid the _ProactorBaseWritePipeTransport._loop_writing assertion errors
            if self.event_loop.__class__.__name__ == 'ProactorEventLoop':
                logger.warning("Detected ProactorEventLoop on Windows, which may cause issues with WebSockets")
                logger.info("Consider using 'asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())' at startup")

            self.server = await websockets.serve(
                handler,
                self.host,
                self.port,
                compression=None,  # Disable WebSocket compression to avoid permessage_deflate issues
                max_size=10 * 1024 * 1024,  # 10MB max message size
                max_queue=32  # Limit message queue to prevent memory issues
            )

            # Store a reference to the server's event loop
            self.server_loop = self.event_loop

            logger.info(f"WebSocket server started at ws://{self.host}:{self.port}")
        except Exception as e:
            self.running = False
            logger.error(f"Failed to start WebSocket server: {e}", exc_info=True)
            raise

    async def stop(self):
        """Stop the WebSocket server."""
        if not self.running:
            logger.warning("WebSocket server not running")
            return

        self.running = False

        try:
            # Close all client connections
            close_tasks = []
            for client_id, websocket in self.clients.items():
                try:
                    close_tasks.append(websocket.close())
                except Exception as e:
                    logger.error(f"Error closing client {client_id}: {e}")

            # Wait for all clients to close
            if close_tasks:
                await asyncio.gather(*close_tasks, return_exceptions=True)

            # Clear the clients dictionary
            self.clients.clear()

            # Close the server
            if self.server:
                self.server.close()
                await self.server.wait_closed()
                self.server = None

            logger.info("WebSocket server stopped")
        except Exception as e:
            logger.error(f"Error stopping WebSocket server: {e}")
            raise

    async def _handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """
        Handle a client connection.

        Args:
            websocket: The WebSocket connection
            path: The connection path
        """
        # Generate a temporary client ID for the connection
        temp_client_id = str(uuid.uuid4())

        # Authentication flag
        authenticated = False
        client_id = temp_client_id

        # Generate an authentication token for this client
        auth_token = generate_token(temp_client_id)

        # Send authentication challenge
        try:
            await websocket.send(json.dumps({
                "type": "auth_challenge",
                "data": {
                    "token": auth_token,
                    "message": "Please authenticate with this token"
                }
            }))
            logger.debug(f"Sent authentication challenge to client {temp_client_id}")
        except Exception as e:
            logger.error(f"Error sending authentication challenge: {e}")
            return

        # Wait for authentication response (with timeout)
        try:
            # Set a timeout for authentication
            auth_timeout = 30  # seconds
            auth_deadline = time.time() + auth_timeout

            while time.time() < auth_deadline and not authenticated:
                try:
                    # Wait for a message with a short timeout to allow checking the deadline
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)

                    # Parse the message
                    try:
                        data = json.loads(message)
                    except json.JSONDecodeError:
                        logger.warning(f"Received invalid JSON during authentication")
                        continue

                    # Check if this is an authentication response
                    if data.get("type") == "auth_response":
                        token = data.get("data", {}).get("token")

                        if token:
                            # Validate the token
                            is_valid, validated_client_id = validate_token(token)

                            if is_valid and validated_client_id:
                                authenticated = True
                                client_id = validated_client_id
                                logger.info(f"Client {client_id} authenticated successfully")

                                # Send authentication success
                                await websocket.send(json.dumps({
                                    "type": "auth_result",
                                    "data": {
                                        "success": True,
                                        "client_id": client_id
                                    }
                                }))

                                break
                            else:
                                logger.warning(f"Invalid authentication token from client")

                                # Send authentication failure
                                await websocket.send(json.dumps({
                                    "type": "auth_result",
                                    "data": {
                                        "success": False,
                                        "message": "Invalid authentication token"
                                    }
                                }))
                    else:
                        # Not an authentication response, ignore
                        logger.warning(f"Received non-authentication message during authentication phase")
                except asyncio.TimeoutError:
                    # Timeout waiting for a message, check the deadline
                    continue

            # Check if authentication succeeded
            if not authenticated:
                logger.warning(f"Authentication timeout for client {temp_client_id}")

                # Send authentication failure
                await websocket.send(json.dumps({
                    "type": "auth_result",
                    "data": {
                        "success": False,
                        "message": "Authentication timeout"
                    }
                }))

                return
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected during authentication")
            return
        except Exception as e:
            logger.error(f"Error during authentication: {e}")
            return

        # Client is now authenticated, add to clients dictionary
        self.clients[client_id] = websocket

        # Notify connection handlers
        for handler in self.on_connect_handlers:
            try:
                handler(client_id)
            except Exception as e:
                logger.error(f"Error in connect handler: {e}")

        logger.info(f"Client {client_id} connected and authenticated")

        # Send replay buffer if available
        with self.replay_lock:
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

                    # Check for duplicate messages
                    message_type = data.get("type", "unknown")
                    message_data = data.get("data", {})

                    is_duplicate, count = is_duplicate_message(message_type, message_data)

                    if is_duplicate:
                        logger.warning(f"Duplicate message detected from client {client_id}: {message_type} (count: {count})")

                        # Send duplicate message notification
                        await websocket.send(json.dumps({
                            "type": "duplicate_message",
                            "data": {
                                "original_type": message_type,
                                "count": count
                            }
                        }))

                        continue

                    # Handle client messages
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

        # Check for duplicate events
        is_duplicate, count = is_duplicate_message(event_type, data)
        if is_duplicate:
            logger.warning(f"Duplicate event detected: {event_type} (count: {count})")
            # Still proceed with broadcasting, but log the duplicate

        # Create the event
        with self.sequence_lock:
            self.sequence_number += 1
            seq = self.sequence_number

        # Get the current event loop safely
        try:
            loop = get_event_loop()
            current_time = loop.time()
        except Exception:
            # Fallback if we can't get the event loop time
            current_time = time.time()

        event = {
            "version": "1.0",
            "seq": seq,
            "timestamp": current_time,
            "type": event_type,
            "data": data
        }

        # Add to replay buffer if high priority
        if high_priority:
            with self.replay_lock:
                self.replay_buffer.append(event)
                # Trim buffer if needed
                if len(self.replay_buffer) > self.max_replay_events:
                    self.replay_buffer = self.replay_buffer[-self.max_replay_events:]

        # Serialize the event
        event_json = json.dumps(event)

        # Get a snapshot of the clients to avoid iteration issues
        client_items = list(self.clients.items())

        # Broadcast to all clients
        disconnected_clients = []
        for client_id, websocket in client_items:
            try:
                # Use a semaphore to limit concurrent sends
                # This helps prevent the "assert f is self._write_fut" error
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

        logger.debug(f"Broadcast event {event_type} to {len(client_items)} clients")

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

        # Check for duplicate events
        is_duplicate, count = is_duplicate_message(event_type, data)
        if is_duplicate:
            logger.warning(f"Duplicate event detected in push_event: {event_type} (count: {count})")
            # Still proceed with broadcasting, but log the duplicate

        # Get the event loop in a thread-safe way
        try:
            # Use the server's event loop for all operations
            if self.server_loop is None:
                logger.error("Server event loop not initialized")
                return

            # Use our thread-safe event loop manager to run the coroutine
            future = run_coroutine_threadsafe(
                self.broadcast_event(event_type, data, high_priority),
                self.server_loop
            )

            # We don't need to wait for the result, but we can log any exceptions
            def log_exception(fut):
                try:
                    fut.result()
                except Exception as e:
                    logger.error(f"Error in broadcast_event: {e}", exc_info=True)

            future.add_done_callback(log_exception)
        except Exception as e:
            logger.warning(f"Error dispatching event {event_type}: {e}", exc_info=True)

    def register_connect_handler(self, handler: Callable[[str], None]):
        """
        Register a handler for client connections.

        Args:
            handler: The handler function
        """
        self.on_connect_handlers.append(handler)

    def register_disconnect_handler(self, handler: Callable[[str], None]):
        """
        Register a handler for client disconnections.

        Args:
            handler: The handler function
        """
        self.on_disconnect_handlers.append(handler)

    def get_client_count(self):
        """Get the number of connected clients."""
        return len(self.clients)
