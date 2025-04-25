#!/usr/bin/env python3
"""
Test script for the enhanced WebSocket server.

This script tests the WebSocket server with event loop management, message deduplication,
and authentication.
"""

import asyncio
import json
import logging
import sys
import time
import threading
import unittest
import websockets
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from websocket.server_fixed import CodaWebSocketServer
from websocket.integration_fixed import CodaWebSocketIntegration
from websocket.events import EventType

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_websocket_server_fixed_v2")


class TestWebSocketServerFixedV2(unittest.TestCase):
    """Test cases for the enhanced WebSocket server."""

    async def asyncSetUp(self):
        """Set up the test environment."""
        # Initialize the server
        self.server = CodaWebSocketServer(host="localhost", port=8765)

        # Initialize the integration
        self.integration = CodaWebSocketIntegration(self.server)

        # Start the server
        await self.server.start()
        logger.info("WebSocket server started")

    async def asyncTearDown(self):
        """Clean up the test environment."""
        # Stop the server
        await self.server.stop()
        logger.info("WebSocket server stopped")

    async def test_server_start_stop(self):
        """Test starting and stopping the server."""
        # Check that the server is running
        self.assertTrue(self.server.running)

        # Stop the server
        await self.server.stop()

        # Check that the server is not running
        self.assertFalse(self.server.running)

        # Start the server again
        await self.server.start()

        # Check that the server is running
        self.assertTrue(self.server.running)

    async def test_client_connection(self):
        """Test client connection and authentication."""
        # Connect a client
        async with websockets.connect("ws://localhost:8765") as websocket:
            # Wait for the authentication challenge
            message = await websocket.recv()
            data = json.loads(message)

            # Check that it's an authentication challenge
            self.assertEqual(data["type"], "auth_challenge")
            self.assertIn("token", data["data"])

            # Send the authentication response
            token = data["data"]["token"]
            await websocket.send(json.dumps({
                "type": "auth_response",
                "data": {
                    "token": token
                }
            }))

            # Wait for the authentication result
            message = await websocket.recv()
            data = json.loads(message)

            # Check that it's an authentication result
            self.assertEqual(data["type"], "auth_result")
            self.assertTrue(data["data"]["success"])
            self.assertIn("client_id", data["data"])

    async def test_duplicate_message_detection(self):
        """Test duplicate message detection."""
        # Connect a client
        async with websockets.connect("ws://localhost:8765") as websocket:
            # Authenticate
            message = await websocket.recv()
            data = json.loads(message)
            token = data["data"]["token"]

            await websocket.send(json.dumps({
                "type": "auth_response",
                "data": {
                    "token": token
                }
            }))

            # Wait for the authentication result
            message = await websocket.recv()

            # Send a message
            test_message = {
                "type": "client_message",
                "data": {
                    "message_type": "test",
                    "message_data": {
                        "content": "Test message"
                    }
                }
            }

            await websocket.send(json.dumps(test_message))

            # Send the same message again
            await websocket.send(json.dumps(test_message))

            # Wait for the duplicate message notification
            message = await websocket.recv()
            data = json.loads(message)

            # Check that it's a duplicate message notification
            self.assertEqual(data["type"], "duplicate_message")
            self.assertEqual(data["data"]["original_type"], "client_message")
            self.assertEqual(data["data"]["count"], 2)

    async def test_event_broadcasting(self):
        """Test broadcasting events to clients."""
        # Connect a client
        async with websockets.connect("ws://localhost:8765") as websocket:
            # Authenticate
            message = await websocket.recv()
            data = json.loads(message)
            token = data["data"]["token"]

            await websocket.send(json.dumps({
                "type": "auth_response",
                "data": {
                    "token": token
                }
            }))

            # Wait for the authentication result
            message = await websocket.recv()

            # Broadcast an event
            await self.server.broadcast_event("test_event", {
                "message": "Test event"
            })

            # Wait for the event
            message = await websocket.recv()
            data = json.loads(message)

            # Check that it's the test event
            self.assertEqual(data["type"], "test_event")
            self.assertEqual(data["data"]["message"], "Test event")

    async def test_integration_events(self):
        """Test events through the integration."""
        # Connect a client
        async with websockets.connect("ws://localhost:8765") as websocket:
            # Authenticate
            message = await websocket.recv()
            data = json.loads(message)
            token = data["data"]["token"]

            await websocket.send(json.dumps({
                "type": "auth_response",
                "data": {
                    "token": token
                }
            }))

            # Wait for the authentication result
            message = await websocket.recv()

            # Start a session
            self.integration.start_session()

            # Wait for the session start event
            message = await websocket.recv()
            data = json.loads(message)

            # Check that it's a session start event
            self.assertEqual(data["type"], EventType.SESSION_START)

            # Add a conversation turn
            self.integration.add_conversation_turn("user", "Hello, world!")

            # Wait for the conversation turn event
            message = await websocket.recv()
            data = json.loads(message)

            # Check that it's a conversation turn event
            self.assertEqual(data["type"], EventType.CONVERSATION_TURN)
            self.assertEqual(data["data"]["role"], "user")
            self.assertEqual(data["data"]["content"], "Hello, world!")

            # End the session
            self.integration.end_session()

            # Wait for the session end event
            message = await websocket.recv()
            data = json.loads(message)

            # Check that it's a session end event
            self.assertEqual(data["type"], EventType.SESSION_END)

    async def test_concurrent_clients(self):
        """Test multiple concurrent clients."""
        # Connect multiple clients
        async with websockets.connect("ws://localhost:8765") as websocket1, \
                  websockets.connect("ws://localhost:8765") as websocket2, \
                  websockets.connect("ws://localhost:8765") as websocket3:

            # Authenticate client 1
            message = await websocket1.recv()
            data = json.loads(message)
            token1 = data["data"]["token"]

            await websocket1.send(json.dumps({
                "type": "auth_response",
                "data": {
                    "token": token1
                }
            }))

            # Authenticate client 2
            message = await websocket2.recv()
            data = json.loads(message)
            token2 = data["data"]["token"]

            await websocket2.send(json.dumps({
                "type": "auth_response",
                "data": {
                    "token": token2
                }
            }))

            # Authenticate client 3
            message = await websocket3.recv()
            data = json.loads(message)
            token3 = data["data"]["token"]

            await websocket3.send(json.dumps({
                "type": "auth_response",
                "data": {
                    "token": token3
                }
            }))

            # Wait for all authentication results
            await websocket1.recv()
            await websocket2.recv()
            await websocket3.recv()

            # Broadcast an event
            await self.server.broadcast_event("test_event", {
                "message": "Test event"
            })

            # Wait for the event on all clients
            message1 = await websocket1.recv()
            message2 = await websocket2.recv()
            message3 = await websocket3.recv()

            # Check that all clients received the event
            data1 = json.loads(message1)
            data2 = json.loads(message2)
            data3 = json.loads(message3)

            self.assertEqual(data1["type"], "test_event")
            self.assertEqual(data2["type"], "test_event")
            self.assertEqual(data3["type"], "test_event")

            self.assertEqual(data1["data"]["message"], "Test event")
            self.assertEqual(data2["data"]["message"], "Test event")
            self.assertEqual(data3["data"]["message"], "Test event")

    async def test_client_disconnect(self):
        """Test client disconnection."""
        # Connect a client
        websocket = await websockets.connect("ws://localhost:8765")

        # Authenticate
        message = await websocket.recv()
        data = json.loads(message)
        token = data["data"]["token"]

        await websocket.send(json.dumps({
            "type": "auth_response",
            "data": {
                "token": token
            }
        }))

        # Wait for the authentication result
        message = await websocket.recv()

        # Check the number of clients
        self.assertEqual(len(self.server.clients), 1)

        # Disconnect the client
        await websocket.close()

        # Wait for the server to process the disconnection
        await asyncio.sleep(0.1)

        # Check that the client was removed
        self.assertEqual(len(self.server.clients), 0)

    async def test_push_event_from_thread(self):
        """Test pushing events from a separate thread."""
        # Connect a client
        async with websockets.connect("ws://localhost:8765") as websocket:
            # Authenticate
            message = await websocket.recv()
            data = json.loads(message)
            token = data["data"]["token"]

            await websocket.send(json.dumps({
                "type": "auth_response",
                "data": {
                    "token": token
                }
            }))

            # Wait for the authentication result
            message = await websocket.recv()

            # Define a function to run in a thread
            def thread_func():
                # Push an event from this thread
                self.server.push_event("thread_event", {
                    "message": "Event from thread",
                    "thread_id": threading.get_ident()
                })

            # Create a thread
            thread = threading.Thread(target=thread_func)
            thread.start()

            # Wait for the thread to complete
            thread.join()

            # Wait for the event
            message = await websocket.recv()
            data = json.loads(message)

            # Check that it's the thread event
            self.assertEqual(data["type"], "thread_event")
            self.assertEqual(data["data"]["message"], "Event from thread")
            self.assertIn("thread_id", data["data"])


# Helper function to run async tests
async def run_async_test(test_class, test_method_name):
    """Run an async test method from a test class."""
    # Create an instance of the test class
    test_instance = test_class()

    try:
        # Call the asyncSetUp method
        await test_instance.asyncSetUp()

        # Get the test method
        test_method = getattr(test_instance, test_method_name)

        # Call the test method
        await test_method()
    finally:
        # Call the asyncTearDown method
        await test_instance.asyncTearDown()


# Define test functions that run the async tests
async def test_all():
    """Run all tests."""
    # Define the test methods to run
    test_methods = [
        "test_server_start_stop",
        "test_client_connection",
        "test_duplicate_message_detection",
        "test_event_broadcasting",
        "test_integration_events",
        "test_concurrent_clients",
        "test_client_disconnect",
        "test_push_event_from_thread"
    ]

    # Run each test method
    for method_name in test_methods:
        logger.info(f"Running test: {method_name}")
        await run_async_test(TestWebSocketServerFixedV2, method_name)
        logger.info(f"Test {method_name} passed")


# Main function to run all tests
def run_tests():
    """Run all tests."""
    asyncio.run(test_all())


if __name__ == "__main__":
    # Run all tests
    run_tests()

    print("All tests passed!")
