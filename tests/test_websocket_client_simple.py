#!/usr/bin/env python3
"""
Simple test script for the WebSocket client.

This script connects to a WebSocket server and tests the authentication flow.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_websocket_client_simple")


async def connect_to_server(uri="ws://localhost:8765"):
    """
    Connect to a WebSocket server.
    
    Args:
        uri: The WebSocket URI to connect to
    """
    import websockets
    
    logger.info(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info(f"Connected to {uri}")
            
            # Wait for the authentication challenge
            message = await websocket.recv()
            data = json.loads(message)
            
            logger.info(f"Received message: {data}")
            
            if data["type"] == "auth_challenge":
                logger.info("Received authentication challenge")
                
                # Get the token
                token = data["data"]["token"]
                logger.info(f"Token: {token}")
                
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
                
                logger.info(f"Received message: {data}")
                
                if data["type"] == "auth_result":
                    logger.info("Received authentication result")
                    
                    if data["data"]["success"]:
                        logger.info(f"Authentication successful, client ID: {data['data']['client_id']}")
                        
                        # Send a test message
                        await websocket.send(json.dumps({
                            "type": "client_message",
                            "data": {
                                "message_type": "test",
                                "message_data": {
                                    "content": "Hello, world!"
                                }
                            }
                        }))
                        logger.info("Sent test message")
                        
                        # Wait for a response
                        for i in range(5):
                            try:
                                message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                                data = json.loads(message)
                                logger.info(f"Received message: {data}")
                            except asyncio.TimeoutError:
                                logger.info("Timeout waiting for message")
                    else:
                        logger.error(f"Authentication failed: {data['data'].get('message', 'Unknown error')}")
            
            logger.info("Test completed")
    except Exception as e:
        logger.error(f"Error: {e}")


async def main():
    """Main function."""
    logger.info("Starting WebSocket client test...")
    
    # Connect to the server
    await connect_to_server()
    
    logger.info("Test completed")


if __name__ == "__main__":
    asyncio.run(main())
