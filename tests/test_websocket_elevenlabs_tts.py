#!/usr/bin/env python3
"""
Test script for the WebSocket-integrated ElevenLabs TTS module.

This script tests the WebSocketElevenLabsTTS class with the WebSocket server.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tts import WebSocketElevenLabsTTS
from websocket import CodaWebSocketServer, CodaWebSocketIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("websocket_tts_test")

async def test_tts(server, integration):
    """Test the WebSocketElevenLabsTTS class."""
    # Initialize the WebSocketElevenLabsTTS
    tts = WebSocketElevenLabsTTS(
        websocket_integration=integration,
        # Use your API key here or set it as an environment variable
        api_key="sk_7b576d29574b14a97150b864497d937c4e1fdd2d6b3a1e4d",
        # Use the 'Alexandra' voice as requested by the user
        voice_id="21m00Tcm4TlvDq8ikWAM",  # Alexandra voice ID
        model_id="eleven_multilingual_v2"
    )
    
    try:
        # Test synthesize method
        logger.info("Testing synthesize method...")
        text = "Hello, I am Coda. I'm using ElevenLabs for text to speech with WebSocket integration."
        
        logger.info(f"Synthesizing text: {text}")
        
        # Synthesize speech
        audio = tts.synthesize(text)
        
        logger.info("Speech synthesized successfully")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Test speak method
        logger.info("Testing speak method...")
        text = "This is another test of the ElevenLabs TTS with WebSocket integration."
        
        logger.info(f"Speaking text: {text}")
        
        # Speak the text
        tts.speak(text)
        
        logger.info("Speech played successfully")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Test stream_synthesize method
        logger.info("Testing stream_synthesize method...")
        text = "This is a streaming test of the ElevenLabs TTS with WebSocket integration."
        
        logger.info(f"Streaming text: {text}")
        
        # Stream synthesize the text
        audio_stream = tts.stream_synthesize(text)
        
        # Collect chunks
        chunks = []
        for chunk in audio_stream:
            chunks.append(chunk)
            logger.info(f"Received chunk of size {len(chunk)} bytes")
        
        logger.info(f"Received {len(chunks)} chunks")
        
        # List available voices
        logger.info("Fetching available voices...")
        voices = tts.get_available_voices()
        logger.info(f"Available voices: {len(voices)}")
        for i, voice in enumerate(voices[:5]):  # Show only first 5 voices
            logger.info(f"Voice {i+1}: {voice['name']} (ID: {voice['id']})")
        if len(voices) > 5:
            logger.info(f"... and {len(voices) - 5} more voices")
    except Exception as e:
        logger.error(f"Error in TTS test: {e}", exc_info=True)

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
        
        # Test the TTS
        await test_tts(server, integration)
        
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
