#!/usr/bin/env python3
"""
Test script for WebSocket client-server communication with authentication.

This script tests the communication between a WebSocket client and server
with authentication, message deduplication, and event loop management.
"""

import asyncio
import json
import logging
import sys
import time
import threading
from pathlib import Path

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
logger = logging.getLogger("test_websocket_client_server_auth")


async def connect_test_client(uri="ws://localhost:8765"):
    """
    Connect a test client to the WebSocket server.
    
    Args:
        uri: The WebSocket URI to connect to
        
    Returns:
        A tuple of (websocket, client_id)
    """
    import websockets
    
    # Connect to the server
    websocket = await websockets.connect(uri)
    logger.info(f"Connected to {uri}")
    
    # Wait for the authentication challenge
    message = await websocket.recv()
    data = json.loads(message)
    
    if data["type"] != "auth_challenge":
        logger.error(f"Expected auth_challenge, got {data['type']}")
        await websocket.close()
        return None, None
    
    # Get the token
    token = data["data"]["token"]
    logger.info(f"Received authentication token: {token}")
    
    # Send the authentication response
    await websocket.send(json.dumps({
        "type": "auth_response",
        "data": {
            "token": token
        }
    }))
    logger.info("Sent authentication response")
    
    # Wait for the authentication result
    message = await websocket.recv()
    data = json.loads(message)
    
    if data["type"] != "auth_result":
        logger.error(f"Expected auth_result, got {data['type']}")
        await websocket.close()
        return None, None
    
    # Check if authentication was successful
    if not data["data"]["success"]:
        logger.error(f"Authentication failed: {data['data'].get('message', 'Unknown error')}")
        await websocket.close()
        return None, None
    
    # Get the client ID
    client_id = data["data"]["client_id"]
    logger.info(f"Authentication successful, client ID: {client_id}")
    
    return websocket, client_id


async def send_client_message(websocket, message_type, message_data=None):
    """
    Send a client message to the server.
    
    Args:
        websocket: The WebSocket connection
        message_type: The message type
        message_data: The message data (default: None)
        
    Returns:
        True if the message was sent successfully, False otherwise
    """
    if message_data is None:
        message_data = {}
    
    # Create the message
    message = {
        "type": "client_message",
        "data": {
            "message_type": message_type,
            "message_data": message_data
        }
    }
    
    # Send the message
    try:
        await websocket.send(json.dumps(message))
        logger.info(f"Sent client message: {message_type}")
        return True
    except Exception as e:
        logger.error(f"Error sending client message: {e}")
        return False


async def receive_event(websocket, timeout=5.0):
    """
    Receive an event from the server.
    
    Args:
        websocket: The WebSocket connection
        timeout: The timeout in seconds (default: 5.0)
        
    Returns:
        The event data, or None if no event was received
    """
    try:
        # Set a timeout
        message = await asyncio.wait_for(websocket.recv(), timeout=timeout)
        
        # Parse the message
        data = json.loads(message)
        logger.info(f"Received event: {data['type']}")
        
        return data
    except asyncio.TimeoutError:
        logger.warning(f"Timeout waiting for event")
        return None
    except Exception as e:
        logger.error(f"Error receiving event: {e}")
        return None


async def test_push_to_talk():
    """Test the push-to-talk functionality."""
    logger.info("Testing push-to-talk functionality...")
    
    # Connect a test client
    websocket, client_id = await connect_test_client()
    
    if websocket is None:
        logger.error("Failed to connect test client")
        return False
    
    try:
        # Send a push-to-talk request
        success = await send_client_message(websocket, "push_to_talk", {
            "duration": 3,
            "continuous": False
        })
        
        if not success:
            logger.error("Failed to send push-to-talk request")
            return False
        
        # Wait for events
        events = []
        
        # We should receive at least an STT start event
        while True:
            event = await receive_event(websocket)
            
            if event is None:
                break
            
            events.append(event)
            
            # If we receive an STT end event, we're done
            if event["type"] == EventType.STT_END:
                break
        
        # Check that we received the expected events
        event_types = [event["type"] for event in events]
        logger.info(f"Received events: {event_types}")
        
        # We should have received at least an STT start event
        if EventType.STT_START not in event_types:
            logger.error(f"Missing STT_START event")
            return False
        
        return True
    finally:
        # Close the WebSocket connection
        await websocket.close()
        logger.info("Closed WebSocket connection")


async def test_text_input():
    """Test the text input functionality."""
    logger.info("Testing text input functionality...")
    
    # Connect a test client
    websocket, client_id = await connect_test_client()
    
    if websocket is None:
        logger.error("Failed to connect test client")
        return False
    
    try:
        # Send a text input
        success = await send_client_message(websocket, "text_input", {
            "text": "Hello, world!"
        })
        
        if not success:
            logger.error("Failed to send text input")
            return False
        
        # Wait for events
        events = []
        
        # We should receive at least a conversation turn event
        while True:
            event = await receive_event(websocket)
            
            if event is None:
                break
            
            events.append(event)
            
            # If we receive an LLM end event, we're done
            if event["type"] == EventType.LLM_END:
                break
        
        # Check that we received the expected events
        event_types = [event["type"] for event in events]
        logger.info(f"Received events: {event_types}")
        
        # We should have received at least a conversation turn event
        if EventType.CONVERSATION_TURN not in event_types:
            logger.error(f"Missing CONVERSATION_TURN event")
            return False
        
        return True
    finally:
        # Close the WebSocket connection
        await websocket.close()
        logger.info("Closed WebSocket connection")


async def test_duplicate_message_detection():
    """Test duplicate message detection."""
    logger.info("Testing duplicate message detection...")
    
    # Connect a test client
    websocket, client_id = await connect_test_client()
    
    if websocket is None:
        logger.error("Failed to connect test client")
        return False
    
    try:
        # Send the same message twice
        message = {
            "type": "client_message",
            "data": {
                "message_type": "test",
                "message_data": {
                    "content": "Test message"
                }
            }
        }
        
        # Send the first message
        await websocket.send(json.dumps(message))
        logger.info("Sent first test message")
        
        # Send the second message (duplicate)
        await websocket.send(json.dumps(message))
        logger.info("Sent second test message (duplicate)")
        
        # Wait for the duplicate message notification
        event = await receive_event(websocket)
        
        if event is None:
            logger.error("No response received")
            return False
        
        # Check that it's a duplicate message notification
        if event["type"] != "duplicate_message":
            logger.error(f"Expected duplicate_message event, got {event['type']}")
            return False
        
        # Check the duplicate message details
        if event["data"]["original_type"] != "client_message":
            logger.error(f"Expected original_type=client_message, got {event['data']['original_type']}")
            return False
        
        if event["data"]["count"] != 2:
            logger.error(f"Expected count=2, got {event['data']['count']}")
            return False
        
        logger.info("Duplicate message detection working correctly")
        return True
    finally:
        # Close the WebSocket connection
        await websocket.close()
        logger.info("Closed WebSocket connection")


async def test_invalid_authentication():
    """Test invalid authentication."""
    logger.info("Testing invalid authentication...")
    
    import websockets
    
    # Connect to the server
    websocket = await websockets.connect("ws://localhost:8765")
    logger.info("Connected to server")
    
    try:
        # Wait for the authentication challenge
        message = await websocket.recv()
        data = json.loads(message)
        
        if data["type"] != "auth_challenge":
            logger.error(f"Expected auth_challenge, got {data['type']}")
            return False
        
        # Send an invalid authentication response
        await websocket.send(json.dumps({
            "type": "auth_response",
            "data": {
                "token": "invalid_token"
            }
        }))
        logger.info("Sent invalid authentication response")
        
        # Wait for the authentication result
        message = await websocket.recv()
        data = json.loads(message)
        
        if data["type"] != "auth_result":
            logger.error(f"Expected auth_result, got {data['type']}")
            return False
        
        # Check that authentication failed
        if data["data"]["success"]:
            logger.error("Authentication succeeded with invalid token")
            return False
        
        logger.info("Invalid authentication correctly rejected")
        return True
    finally:
        # Close the WebSocket connection
        await websocket.close()
        logger.info("Closed WebSocket connection")


async def main():
    """Main function."""
    # Initialize the server
    logger.info("Initializing WebSocket server...")
    server = CodaWebSocketServer(host="localhost", port=8765)
    
    # Initialize the integration
    logger.info("Initializing WebSocket integration...")
    integration = CodaWebSocketIntegration(server)
    
    # Start the server
    await server.start()
    logger.info("WebSocket server started")
    
    try:
        # Run the tests
        logger.info("Running tests...")
        
        # Test invalid authentication
        success = await test_invalid_authentication()
        logger.info(f"Invalid authentication test {'passed' if success else 'failed'}")
        
        # Test duplicate message detection
        success = await test_duplicate_message_detection()
        logger.info(f"Duplicate message detection test {'passed' if success else 'failed'}")
        
        # Test push-to-talk
        success = await test_push_to_talk()
        logger.info(f"Push-to-talk test {'passed' if success else 'failed'}")
        
        # Test text input
        success = await test_text_input()
        logger.info(f"Text input test {'passed' if success else 'failed'}")
        
        logger.info("All tests completed")
    except Exception as e:
        logger.error(f"Error running tests: {e}")
    finally:
        # Stop the server
        await server.stop()
        logger.info("WebSocket server stopped")


if __name__ == "__main__":
    asyncio.run(main())
