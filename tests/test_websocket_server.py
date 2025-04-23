#!/usr/bin/env python3
"""
Test script for the WebSocket server.

This script starts a WebSocket server and sends some test events.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from websocket import CodaWebSocketServer, EventType, create_event

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("websocket_test")

async def send_test_events(server: CodaWebSocketServer):
    """Send some test events to the server."""
    # Wait for the server to start
    await asyncio.sleep(1)
    
    # System info event
    await server.broadcast_event(
        EventType.SYSTEM_INFO,
        {
            "version": "0.1.0",
            "platform": sys.platform,
            "python_version": sys.version,
        },
        high_priority=True
    )
    logger.info("Sent system info event")
    
    # STT start event
    await server.broadcast_event(
        EventType.STT_START,
        {
            "mode": "push_to_talk"
        }
    )
    logger.info("Sent STT start event")
    
    # STT interim events
    for i in range(3):
        await server.broadcast_event(
            EventType.STT_INTERIM,
            {
                "text": f"This is a test {i+1}",
                "confidence": 0.8 + (i * 0.05)
            }
        )
        logger.info(f"Sent STT interim event {i+1}")
        await asyncio.sleep(0.5)
    
    # STT result event
    await server.broadcast_event(
        EventType.STT_RESULT,
        {
            "text": "This is a test 3",
            "confidence": 0.95,
            "duration_seconds": 1.5,
            "language": "en"
        }
    )
    logger.info("Sent STT result event")
    
    # LLM start event
    await server.broadcast_event(
        EventType.LLM_START,
        {
            "model": "llama3",
            "prompt_tokens": 150,
            "system_prompt_preview": "You are Coda, a helpful assistant..."
        }
    )
    logger.info("Sent LLM start event")
    
    # LLM token events
    response = "Hello! How can I help you today?"
    for i, token in enumerate(response.split()):
        await server.broadcast_event(
            EventType.LLM_TOKEN,
            {
                "token": token,
                "token_index": i
            }
        )
        logger.info(f"Sent LLM token event: {token}")
        await asyncio.sleep(0.2)
    
    # LLM result event
    await server.broadcast_event(
        EventType.LLM_RESULT,
        {
            "text": response,
            "total_tokens": 200,
            "duration_seconds": 2.0,
            "has_tool_calls": False
        }
    )
    logger.info("Sent LLM result event")
    
    # TTS start event
    await server.broadcast_event(
        EventType.TTS_START,
        {
            "text": response,
            "voice": "alexandra",
            "provider": "elevenlabs"
        }
    )
    logger.info("Sent TTS start event")
    
    # TTS progress events
    for i in range(5):
        await server.broadcast_event(
            EventType.TTS_PROGRESS,
            {
                "percent_complete": (i + 1) * 20.0
            }
        )
        logger.info(f"Sent TTS progress event: {(i + 1) * 20.0}%")
        await asyncio.sleep(0.2)
    
    # TTS result event
    await server.broadcast_event(
        EventType.TTS_RESULT,
        {
            "duration_seconds": 1.0,
            "audio_duration_seconds": 2.5,
            "char_count": len(response)
        }
    )
    logger.info("Sent TTS result event")
    
    # Memory store event
    await server.broadcast_event(
        EventType.MEMORY_STORE,
        {
            "content_preview": "User asked about the weather",
            "memory_type": "conversation",
            "importance": 0.7,
            "memory_id": "mem_12345"
        },
        high_priority=True
    )
    logger.info("Sent memory store event")
    
    # Latency trace event
    await server.broadcast_event(
        EventType.LATENCY_TRACE,
        {
            "stt_seconds": 1.5,
            "llm_seconds": 2.0,
            "tts_seconds": 1.0,
            "total_seconds": 4.5
        }
    )
    logger.info("Sent latency trace event")
    
    # System metrics event
    await server.broadcast_event(
        EventType.SYSTEM_METRICS,
        {
            "memory_mb": 350.5,
            "cpu_percent": 25.3,
            "gpu_vram_mb": 1024.0,
            "uptime_seconds": 3600.0
        }
    )
    logger.info("Sent system metrics event")
    
    logger.info("All test events sent")

async def main():
    """Main function."""
    # Create the WebSocket server
    server = CodaWebSocketServer()
    
    # Register connect/disconnect handlers
    server.register_connect_handler(
        lambda client_id: logger.info(f"Client connected: {client_id}")
    )
    server.register_disconnect_handler(
        lambda client_id: logger.info(f"Client disconnected: {client_id}")
    )
    
    # Start the server
    await server.start()
    
    try:
        # Send test events
        await send_test_events(server)
        
        # Keep the server running
        logger.info("Server running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(1)
            
            # Send periodic system metrics
            await server.broadcast_event(
                EventType.SYSTEM_METRICS,
                {
                    "memory_mb": 350.5 + (time.time() % 50),
                    "cpu_percent": 25.3 + (time.time() % 10),
                    "gpu_vram_mb": 1024.0,
                    "uptime_seconds": 3600.0 + (time.time() % 3600)
                }
            )
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        # Stop the server
        await server.stop()
        logger.info("Server stopped")

if __name__ == "__main__":
    asyncio.run(main())
