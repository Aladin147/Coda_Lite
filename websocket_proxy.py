#!/usr/bin/env python3
"""
WebSocket proxy server for Coda.

This module provides a WebSocket proxy server that allows the dashboard to connect to Coda
without browser security restrictions.
"""

import asyncio
import logging
import websockets
import json
from websockets.server import WebSocketServerProtocol
from websockets.client import WebSocketClientProtocol

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("websocket_proxy")

class WebSocketProxy:
    """
    WebSocket proxy server for Coda.

    This server acts as a bridge between the dashboard and Coda's WebSocket server.
    """

    def __init__(self, coda_host="localhost", coda_port=8765, proxy_host="localhost", proxy_port=8766):
        """
        Initialize the WebSocket proxy.

        Args:
            coda_host: Coda WebSocket server host (default: localhost)
            coda_port: Coda WebSocket server port (default: 8765)
            proxy_host: Proxy server host (default: localhost)
            proxy_port: Proxy server port (default: 8766)
        """
        self.coda_url = f"ws://{coda_host}:{coda_port}"
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.clients = {}
        self.server = None

        logger.info(f"WebSocket proxy initialized: {self.coda_url} -> ws://{proxy_host}:{proxy_port}")

    async def start(self):
        """Start the WebSocket proxy server."""
        try:
            # Create a handler function that doesn't require a separate path parameter
            async def handler(websocket):
                await self.handle_client(websocket)

            self.server = await websockets.serve(
                handler,
                self.proxy_host,
                self.proxy_port,
                ping_interval=30,
                ping_timeout=10
            )

            logger.info(f"WebSocket proxy started at ws://{self.proxy_host}:{self.proxy_port}")

            # Keep the server running
            await asyncio.Future()
        except Exception as e:
            logger.error(f"Failed to start WebSocket proxy: {e}")
            raise

    async def handle_client(self, client_websocket: WebSocketServerProtocol):
        """
        Handle a client connection.

        Args:
            client_websocket: The client WebSocket connection
            path: The connection path
        """
        client_id = id(client_websocket)
        logger.info(f"Client {client_id} connected")

        # Connect to Coda's WebSocket server
        try:
            logger.info(f"Connecting to Coda WebSocket server at {self.coda_url}")
            coda_websocket = await websockets.connect(self.coda_url)
            logger.info(f"Connected to Coda WebSocket server")

            # Store the client and Coda WebSocket connections
            self.clients[client_id] = {
                "client": client_websocket,
                "coda": coda_websocket
            }

            # Create tasks for forwarding messages in both directions
            client_to_coda = asyncio.create_task(self.forward_messages(client_websocket, coda_websocket, "client", "coda"))
            coda_to_client = asyncio.create_task(self.forward_messages(coda_websocket, client_websocket, "coda", "client"))

            # Wait for either task to complete (connection closed)
            _, pending = await asyncio.wait(
                [client_to_coda, coda_to_client],
                return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel the remaining task
            for task in pending:
                task.cancel()

            # Clean up
            if client_id in self.clients:
                del self.clients[client_id]

            logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")

            # Send an error message to the client
            try:
                error_message = {
                    "type": "error",
                    "data": {
                        "message": f"Failed to connect to Coda WebSocket server: {str(e)}"
                    }
                }
                await client_websocket.send(json.dumps(error_message))
            except:
                pass

    async def forward_messages(self, source: WebSocketClientProtocol, destination: WebSocketServerProtocol,
                              source_name: str, dest_name: str):
        """
        Forward messages from source to destination.

        Args:
            source: The source WebSocket connection
            destination: The destination WebSocket connection
            source_name: The name of the source (for logging)
            dest_name: The name of the destination (for logging)
        """
        try:
            async for message in source:
                try:
                    # Log the message (truncated if too long)
                    if len(message) > 200:
                        logger.debug(f"Forwarding {source_name} -> {dest_name}: {message[:200]}...")
                    else:
                        logger.debug(f"Forwarding {source_name} -> {dest_name}: {message}")

                    # Forward the message
                    await destination.send(message)
                except Exception as e:
                    logger.error(f"Error forwarding message from {source_name} to {dest_name}: {e}")
                    break
        except websockets.exceptions.ConnectionClosed as e:
            logger.info(f"{source_name} connection closed: {e.code} {e.reason}")
        except Exception as e:
            logger.error(f"Error in forward_messages {source_name} -> {dest_name}: {e}")

async def main():
    """Main entry point."""
    logger.info("Starting WebSocket proxy server")

    # Create and start the proxy server
    proxy = WebSocketProxy()
    await proxy.start()

if __name__ == "__main__":
    asyncio.run(main())
