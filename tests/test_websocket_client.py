#!/usr/bin/env python3
"""
Test client for the WebSocket server.

This script connects to the WebSocket server and displays received events.
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
            
            while True:
                try:
                    # Receive a message
                    message = await websocket.recv()
                    
                    # Parse the message
                    try:
                        data = json.loads(message)
                        event_type = data.get("type", "unknown")
                        
                        # Format the output based on event type
                        if event_type == "replay":
                            events = data.get("events", [])
                            logger.info(f"Received replay with {len(events)} events")
                            for i, event in enumerate(events):
                                event_type = event.get("type", "unknown")
                                logger.info(f"  Replay event {i+1}: {event_type}")
                        else:
                            # Pretty print the event
                            logger.info(f"Received event: {event_type}")
                            logger.info(f"  Data: {json.dumps(data.get('data', {}), indent=2)}")
                    except json.JSONDecodeError:
                        logger.warning(f"Received invalid JSON: {message}")
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("Connection closed")
                    break
                except Exception as e:
                    logger.error(f"Error: {e}")
                    break
    except Exception as e:
        logger.error(f"Connection error: {e}")

async def main():
    """Main function."""
    uri = "ws://localhost:8765"
    
    # Connect to the server
    try:
        await connect_to_server(uri)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")

if __name__ == "__main__":
    asyncio.run(main())
