#!/usr/bin/env python3
"""
Test script for the WebSocket server thread safety.

This script tests the thread safety of the WebSocket server implementation,
focusing on the issues with dictionary iteration and event loop mismatches.
"""

import asyncio
import logging
import sys
import time
import threading
import unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from websocket import CodaWebSocketServer, EventType
from websocket.integration import CodaWebSocketIntegration

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("websocket_thread_safety_test")


class TestWebSocketServerThreadSafety(unittest.TestCase):
    """Test cases for WebSocket server thread safety."""

    async def asyncSetUp(self):
        """Set up the test environment."""
        # Create a WebSocket server
        self.server = CodaWebSocketServer(host="localhost", port=8766)  # Use a different port for testing
        
        # Start the server
        await self.server.start()
        
        # Create a WebSocket integration
        self.integration = CodaWebSocketIntegration(self.server)
        
        logger.info("Test setup complete")

    async def asyncTearDown(self):
        """Clean up the test environment."""
        # Stop the server
        await self.server.stop()
        
        logger.info("Test teardown complete")

    def setUp(self):
        """Set up the test environment (synchronous wrapper)."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.asyncSetUp())

    def tearDown(self):
        """Clean up the test environment (synchronous wrapper)."""
        self.loop.run_until_complete(self.asyncTearDown())
        self.loop.close()

    async def _connect_test_client(self):
        """Connect a test client to the WebSocket server."""
        import websockets
        
        uri = f"ws://localhost:8766"
        websocket = await websockets.connect(uri)
        
        # Return the WebSocket connection
        return websocket

    async def test_client_connection(self):
        """Test that clients can connect to the server."""
        # Connect a test client
        websocket = await self._connect_test_client()
        
        # Check that the client is connected
        self.assertEqual(len(self.server.clients), 1)
        
        # Close the connection
        await websocket.close()
        
        # Wait for the server to process the disconnection
        await asyncio.sleep(0.1)
        
        # Check that the client is disconnected
        self.assertEqual(len(self.server.clients), 0)

    async def test_broadcast_event(self):
        """Test broadcasting events to clients."""
        # Connect a test client
        websocket = await self._connect_test_client()
        
        # Broadcast an event
        await self.server.broadcast_event(
            "test_event",
            {"message": "Hello, world!"},
            False
        )
        
        # Receive the event
        response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
        
        # Parse the response
        import json
        event = json.loads(response)
        
        # Check the event
        self.assertEqual(event["type"], "test_event")
        self.assertEqual(event["data"]["message"], "Hello, world!")
        
        # Close the connection
        await websocket.close()

    async def test_concurrent_client_connections(self):
        """Test concurrent client connections."""
        # Connect multiple test clients
        clients = []
        for i in range(5):
            websocket = await self._connect_test_client()
            clients.append(websocket)
        
        # Check that all clients are connected
        self.assertEqual(len(self.server.clients), 5)
        
        # Broadcast an event
        await self.server.broadcast_event(
            "test_event",
            {"message": "Hello, world!"},
            False
        )
        
        # Receive the event on all clients
        for websocket in clients:
            response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
            
            # Parse the response
            import json
            event = json.loads(response)
            
            # Check the event
            self.assertEqual(event["type"], "test_event")
            self.assertEqual(event["data"]["message"], "Hello, world!")
        
        # Close all connections
        for websocket in clients:
            await websocket.close()
        
        # Wait for the server to process the disconnections
        await asyncio.sleep(0.1)
        
        # Check that all clients are disconnected
        self.assertEqual(len(self.server.clients), 0)

    def test_concurrent_broadcasts(self):
        """Test concurrent broadcasts from multiple threads."""
        # Define a function to broadcast events
        async def broadcast_events(event_type, count):
            for i in range(count):
                await self.server.broadcast_event(
                    event_type,
                    {"message": f"Message {i}"},
                    False
                )
                await asyncio.sleep(0.01)  # Small delay to increase chance of concurrency issues
        
        # Connect a test client
        client = self.loop.run_until_complete(self._connect_test_client())
        
        # Create tasks to broadcast events concurrently
        tasks = []
        for i in range(5):
            task = asyncio.run_coroutine_threadsafe(
                broadcast_events(f"test_event_{i}", 10),
                self.loop
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        for task in tasks:
            task.result()
        
        # Close the client
        self.loop.run_until_complete(client.close())
        
        # Wait for the server to process the disconnection
        self.loop.run_until_complete(asyncio.sleep(0.1))

    def test_integration_event_queue(self):
        """Test the event queue in the integration class."""
        # Define a function to send events through the integration
        def send_events(event_type, count):
            for i in range(count):
                self.integration.event_queue.put((
                    event_type,
                    {"message": f"Message {i}"},
                    False
                ))
                time.sleep(0.01)  # Small delay to increase chance of concurrency issues
        
        # Connect a test client
        client = self.loop.run_until_complete(self._connect_test_client())
        
        # Create threads to send events concurrently
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=send_events,
                args=(f"test_event_{i}", 10)
            )
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Wait for the event queue to be processed
        self.integration.event_queue.join()
        
        # Close the client
        self.loop.run_until_complete(client.close())
        
        # Wait for the server to process the disconnection
        self.loop.run_until_complete(asyncio.sleep(0.1))

    def test_client_disconnect_during_broadcast(self):
        """Test client disconnection during broadcast."""
        # Define a function to disconnect a client
        async def disconnect_client(websocket, delay):
            await asyncio.sleep(delay)
            await websocket.close()
        
        # Connect multiple test clients
        clients = self.loop.run_until_complete(asyncio.gather(
            *[self._connect_test_client() for _ in range(5)]
        ))
        
        # Schedule disconnections at different times
        for i, client in enumerate(clients):
            asyncio.run_coroutine_threadsafe(
                disconnect_client(client, i * 0.05),
                self.loop
            )
        
        # Broadcast events continuously
        async def broadcast_continuously():
            for i in range(20):
                await self.server.broadcast_event(
                    "test_event",
                    {"message": f"Message {i}"},
                    False
                )
                await asyncio.sleep(0.05)
        
        # Run the broadcast
        self.loop.run_until_complete(broadcast_continuously())
        
        # Wait for all clients to disconnect
        self.loop.run_until_complete(asyncio.sleep(0.5))
        
        # Check that all clients are disconnected
        self.assertEqual(len(self.server.clients), 0)


def run_tests():
    """Run the tests."""
    unittest.main()


if __name__ == "__main__":
    run_tests()
