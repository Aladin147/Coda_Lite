#!/usr/bin/env python3
"""
Simple WebSocket client to test the Coda WebSocket server.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path

import websockets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("websocket_client")

async def connect_to_server(uri: str = "ws://localhost:8765"):
    """
    Connect to the WebSocket server and display received events.
    
    Args:
        uri: The WebSocket URI to connect to
    """
    logger.info(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info(f"Connected to {uri}")
            
            # Send a test message
            test_message = {
                "type": "test",
                "data": {
                    "message": "Hello from Python client"
                },
                "timestamp": int(time.time() * 1000)
            }
            await websocket.send(json.dumps(test_message))
            logger.info(f"Sent test message: {test_message}")
            
            # Wait for messages
            while True:
                try:
                    message = await websocket.recv()
                    logger.info(f"Received: {message}")
                    
                    # Parse the message
                    try:
                        data = json.loads(message)
                        logger.info(f"Parsed: {json.dumps(data, indent=2)}")
                    except json.JSONDecodeError:
                        logger.error(f"Error parsing message: {message}")
                except websockets.exceptions.ConnectionClosed:
                    logger.info("Connection closed")
                    break
    except Exception as e:
        logger.error(f"Error connecting to {uri}: {e}")

if __name__ == "__main__":
    asyncio.run(connect_to_server())
