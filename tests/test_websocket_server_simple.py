#!/usr/bin/env python3
"""
Simple test script for the WebSocket server.

This script starts a WebSocket server and keeps it running.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from websocket.server_fixed import CodaWebSocketServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_websocket_server_simple")


async def main():
    """Main function."""
    logger.info("Starting WebSocket server...")
    
    # Initialize the server
    server = CodaWebSocketServer(host="localhost", port=8765)
    
    # Start the server
    await server.start()
    logger.info("WebSocket server started at ws://localhost:8765")
    
    try:
        # Keep the server running until interrupted
        while True:
            logger.info("Server is running. Press Ctrl+C to stop.")
            await asyncio.sleep(5)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Stopping server...")
    finally:
        # Stop the server
        await server.stop()
        logger.info("WebSocket server stopped")


if __name__ == "__main__":
    asyncio.run(main())
