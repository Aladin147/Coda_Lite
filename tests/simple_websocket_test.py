#!/usr/bin/env python3
"""
Simple test script for the WebSocket implementation.

This script tests the basic functionality of the WebSocket server,
message deduplication, and authentication.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from websocket.server_fixed import CodaWebSocketServer
from websocket.integration_fixed import CodaWebSocketIntegration
from websocket.events import EventType
from websocket.message_deduplication import is_duplicate_message
from websocket.authentication import generate_token, validate_token

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("simple_websocket_test")


async def test_message_deduplication():
    """Test message deduplication."""
    logger.info("Testing message deduplication...")
    
    # Check a new message
    is_duplicate, count = is_duplicate_message("test_type", {"data": "test"})
    logger.info(f"First message: is_duplicate={is_duplicate}, count={count}")
    
    # Check the same message again
    is_duplicate, count = is_duplicate_message("test_type", {"data": "test"})
    logger.info(f"Second message: is_duplicate={is_duplicate}, count={count}")
    
    # Check a different message
    is_duplicate, count = is_duplicate_message("test_type", {"data": "different"})
    logger.info(f"Different message: is_duplicate={is_duplicate}, count={count}")
    
    logger.info("Message deduplication test completed")


async def test_authentication():
    """Test authentication."""
    logger.info("Testing authentication...")
    
    # Generate a token
    token = generate_token("test_client")
    logger.info(f"Generated token: {token}")
    
    # Validate the token
    is_valid, client_id = validate_token(token)
    logger.info(f"Token validation: is_valid={is_valid}, client_id={client_id}")
    
    # Validate an invalid token
    is_valid, client_id = validate_token("invalid_token")
    logger.info(f"Invalid token validation: is_valid={is_valid}, client_id={client_id}")
    
    logger.info("Authentication test completed")


async def test_websocket_server():
    """Test the WebSocket server."""
    logger.info("Testing WebSocket server...")
    
    # Initialize the server
    server = CodaWebSocketServer(host="localhost", port=8765)
    
    # Initialize the integration
    integration = CodaWebSocketIntegration(server)
    
    # Start the server
    await server.start()
    logger.info("WebSocket server started")
    
    try:
        # Start a session
        integration.start_session()
        logger.info("Session started")
        
        # Add a conversation turn
        integration.add_conversation_turn("user", "Hello, world!")
        logger.info("Added conversation turn")
        
        # Wait for a bit
        await asyncio.sleep(1)
        
        # End the session
        integration.end_session()
        logger.info("Session ended")
    finally:
        # Stop the server
        await server.stop()
        logger.info("WebSocket server stopped")
    
    logger.info("WebSocket server test completed")


async def main():
    """Main function."""
    logger.info("Starting simple WebSocket tests...")
    
    # Test message deduplication
    await test_message_deduplication()
    
    # Test authentication
    await test_authentication()
    
    # Test WebSocket server
    await test_websocket_server()
    
    logger.info("All tests completed successfully")


if __name__ == "__main__":
    asyncio.run(main())
