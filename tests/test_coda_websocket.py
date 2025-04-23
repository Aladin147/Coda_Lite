#!/usr/bin/env python3
"""
Test script for the WebSocket-integrated Coda implementation.

This script runs the Coda assistant with WebSocket integration and connects a client to it.
"""

import asyncio
import logging
import sys
import time
import threading
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.config_loader import ConfigLoader
from websocket import CodaWebSocketServer, CodaWebSocketIntegration
from main_websocket import CodaAssistant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("coda_websocket_test")

async def run_client(uri: str = "ws://localhost:8765"):
    """
    Run a WebSocket client to connect to the Coda WebSocket server.
    
    Args:
        uri: The WebSocket URI to connect to
    """
    import websockets
    import json
    
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
                            if "data" in data:
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

async def main_async():
    """Async main function."""
    # Load configuration
    config = ConfigLoader()
    
    # Initialize WebSocket server
    logger.info("Initializing WebSocket server...")
    server = CodaWebSocketServer(
        host=config.get("websocket.host", "localhost"),
        port=config.get("websocket.port", 8765)
    )
    
    # Initialize WebSocket integration
    logger.info("Initializing WebSocket integration...")
    integration = CodaWebSocketIntegration(server)
    
    # Start the WebSocket server
    await server.start()
    logger.info("WebSocket server started")
    
    # Start the client in a separate task
    client_task = asyncio.create_task(run_client())
    
    try:
        # Initialize and run the assistant
        logger.info("Initializing Coda assistant...")
        assistant = CodaAssistant(config, integration)
        logger.info("Coda assistant initialized")
        
        # Run the assistant in a separate thread
        assistant_thread = threading.Thread(target=assistant.run, daemon=True)
        assistant_thread.start()
        
        # Wait for the assistant to initialize
        logger.info("Waiting for assistant to initialize...")
        await asyncio.sleep(5)
        
        # Simulate a user input
        logger.info("Simulating user input...")
        assistant.handle_transcription("What time is it?")
        
        # Wait for the assistant to process the input
        logger.info("Waiting for assistant to process input...")
        await asyncio.sleep(10)
        
        # Simulate another user input
        logger.info("Simulating another user input...")
        assistant.handle_transcription("What's the weather like today?")
        
        # Wait for the assistant to process the input
        logger.info("Waiting for assistant to process input...")
        await asyncio.sleep(10)
        
        # Stop the assistant
        logger.info("Stopping assistant...")
        assistant.stop()
        
        # Wait for the assistant to stop
        logger.info("Waiting for assistant to stop...")
        await asyncio.sleep(5)
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
    finally:
        # Cancel the client task
        client_task.cancel()
        try:
            await client_task
        except asyncio.CancelledError:
            pass
        
        # Stop the WebSocket server
        await server.stop()
        logger.info("WebSocket server stopped")

def main():
    """Main function."""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
