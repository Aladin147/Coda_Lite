#!/usr/bin/env python3
"""
Test script for the fixed WebSocket server.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test")

# Import the WebSocket server
from websocket.server_fixed import CodaWebSocketServer

async def main():
    """Main entry point."""
    # Initialize the server
    logger.info("Initializing WebSocket server...")
    server = CodaWebSocketServer(host="localhost", port=8765)
    
    # Start the server
    await server.start()
    logger.info("WebSocket server started at ws://localhost:8765")
    
    # Keep the server running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, stopping server...")
    finally:
        # Stop the server
        await server.stop()
        logger.info("WebSocket server stopped")

if __name__ == "__main__":
    asyncio.run(main())
