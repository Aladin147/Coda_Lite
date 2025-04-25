#!/usr/bin/env python3
"""
Test script for the fixed WebSocket implementation.

This script tests the thread-safe WebSocket server and integration.
"""

import asyncio
import logging
import sys
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List

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
logger = logging.getLogger("fixed_websocket_test")

# Global variables
server = None
integration = None
client_websocket = None

async def connect_test_client():
    """Connect a test client to the WebSocket server."""
    import websockets
    
    uri = f"ws://localhost:8765"
    websocket = await websockets.connect(uri)
    
    # Return the WebSocket connection
    return websocket

async def send_concurrent_events():
    """Send events concurrently from multiple threads."""
    # Define a function to send events
    def send_events(prefix, count):
        for i in range(count):
            integration.system_info({
                "message": f"{prefix} - Message {i}",
                "timestamp": time.time()
            })
            time.sleep(0.01)  # Small delay to increase chance of concurrency issues
    
    # Create threads to send events concurrently
    threads = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        for i in range(5):
            thread = executor.submit(send_events, f"Thread {i}", 20)
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.result()
    
    # Wait for the event queue to be processed
    await asyncio.sleep(1)
    
    logger.info("Concurrent events sent")

async def test_client_messages():
    """Test receiving messages from the client."""
    global client_websocket
    
    # Send a message from the client
    await client_websocket.send('{"type": "test_message", "data": {"message": "Hello from client"}}')
    
    # Wait for the server to process the message
    await asyncio.sleep(0.5)
    
    logger.info("Client message sent")

async def run_tests():
    """Run the tests."""
    global server, integration, client_websocket
    
    try:
        # Initialize the server
        logger.info("Initializing WebSocket server...")
        server = CodaWebSocketServer(host="localhost", port=8765)
        
        # Initialize the integration
        logger.info("Initializing WebSocket integration...")
        integration = CodaWebSocketIntegration(server)
        
        # Start the server
        await server.start()
        logger.info("WebSocket server started")
        
        # Connect a test client
        logger.info("Connecting test client...")
        client_websocket = await connect_test_client()
        logger.info("Test client connected")
        
        # Start a session
        integration.start_session()
        logger.info("Session started")
        
        # Send concurrent events
        logger.info("Sending concurrent events...")
        await send_concurrent_events()
        
        # Test client messages
        logger.info("Testing client messages...")
        await test_client_messages()
        
        # Test STT events
        logger.info("Testing STT events...")
        integration.stt_start("push_to_talk")
        await asyncio.sleep(0.5)
        integration.stt_interim_result("Hello", 0.8)
        await asyncio.sleep(0.5)
        integration.stt_result("Hello, world!", 0.9, 1.5)
        await asyncio.sleep(0.5)
        
        # Test LLM events
        logger.info("Testing LLM events...")
        integration.llm_start("llama3", 100, "You are a helpful assistant")
        await asyncio.sleep(0.5)
        for i in range(5):
            integration.llm_token(f"token_{i}", i)
            await asyncio.sleep(0.1)
        integration.llm_result("Hello! How can I help you today?", 150)
        await asyncio.sleep(0.5)
        
        # Test TTS events
        logger.info("Testing TTS events...")
        integration.tts_start("Hello! How can I help you today?", "alexandra", "elevenlabs")
        await asyncio.sleep(0.5)
        for i in range(5):
            integration.tts_progress((i + 1) * 20.0)
            await asyncio.sleep(0.1)
        integration.tts_result(2.5, 30)
        await asyncio.sleep(0.5)
        
        # Test memory events
        logger.info("Testing memory events...")
        integration.memory_store("This is a test memory", "fact", 0.8, "memory_1")
        await asyncio.sleep(0.5)
        integration.memory_retrieve("test", [{"content": "This is a test memory", "id": "memory_1"}])
        await asyncio.sleep(0.5)
        
        # Test tool events
        logger.info("Testing tool events...")
        integration.tool_call("get_weather", {"location": "New York"})
        await asyncio.sleep(0.5)
        integration.tool_result("get_weather", {"temperature": 72, "condition": "sunny"})
        await asyncio.sleep(0.5)
        
        # End the session
        integration.end_session()
        logger.info("Session ended")
        
        # Close the client
        await client_websocket.close()
        logger.info("Test client disconnected")
        
        # Wait for the server to process the disconnection
        await asyncio.sleep(0.5)
        
        logger.info("All tests completed successfully")
    except Exception as e:
        logger.error(f"Error in tests: {e}", exc_info=True)
    finally:
        # Stop the server
        if server:
            await server.stop()
            logger.info("WebSocket server stopped")

async def main():
    """Main function."""
    await run_tests()

if __name__ == "__main__":
    asyncio.run(main())
