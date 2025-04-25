#!/usr/bin/env python3
"""
Test script for the WebSocket-integrated STT module.

This script tests the WebSocketWhisperSTT class with the WebSocket server.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from stt import WebSocketWhisperSTT
from websocket import CodaWebSocketServer, CodaWebSocketIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("websocket_stt_test")

async def test_stt(server, integration):
    """Test the WebSocketWhisperSTT class."""
    # Initialize the WebSocketWhisperSTT
    stt = WebSocketWhisperSTT(
        websocket_integration=integration,
        model_size="tiny",  # Use tiny model for quick testing
        device="cpu",
        compute_type="float32",
        language="en",
        vad_filter=True
    )
    
    try:
        # Test listening
        logger.info("Testing listen method...")
        print("\nPlease speak for 5 seconds...")
        transcription = stt.listen(duration=5)
        logger.info(f"Transcription: {transcription}")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Test continuous listening
        logger.info("Testing continuous listening...")
        print("\nPlease speak naturally with pauses. Press Ctrl+C to stop.")
        
        # Set up a callback to handle transcriptions
        def handle_transcription(text):
            logger.info(f"Continuous transcription: {text}")
            print(f"\nTranscription: {text}")
        
        # Set up a stop callback to limit the duration
        start_time = time.time()
        def should_stop():
            return time.time() - start_time > 30  # Stop after 30 seconds
        
        # Start continuous listening
        stt.listen_continuous(
            callback=handle_transcription,
            stop_callback=should_stop,
            silence_threshold=0.1,
            silence_duration=1.0
        )
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        # Clean up
        stt.close()
        logger.info("STT test completed")

async def main():
    """Main function."""
    # Create the WebSocket server
    server = CodaWebSocketServer()
    
    # Create the integration
    integration = CodaWebSocketIntegration(server)
    
    # Start the server
    await server.start()
    
    try:
        # Start a session
        integration.start_session()
        
        # Test the STT
        await test_stt(server, integration)
        
        # End the session
        integration.end_session()
        
        # Keep the server running for a bit
        logger.info("Test completed. Server will stop in 5 seconds.")
        await asyncio.sleep(5)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        # Stop the server
        await server.stop()
        logger.info("Server stopped")

if __name__ == "__main__":
    asyncio.run(main())
