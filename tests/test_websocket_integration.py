#!/usr/bin/env python3
"""
Test script for the WebSocket integration.

This script demonstrates how to integrate the WebSocket server with Coda's components.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from websocket import CodaWebSocketServer, CodaWebSocketIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("websocket_integration_test")

async def simulate_conversation(integration: CodaWebSocketIntegration):
    """Simulate a conversation with Coda."""
    # Start a new session
    integration.start_session()
    
    # Simulate STT
    integration.stt_start(mode="push_to_talk")
    await asyncio.sleep(0.5)
    integration.stt_interim_result("What is the", 0.8)
    await asyncio.sleep(0.3)
    integration.stt_interim_result("What is the weather", 0.85)
    await asyncio.sleep(0.3)
    integration.stt_interim_result("What is the weather like", 0.9)
    await asyncio.sleep(0.3)
    integration.stt_interim_result("What is the weather like today", 0.95)
    await asyncio.sleep(0.5)
    integration.stt_result("What is the weather like today?", 0.98, "en")
    
    # Simulate LLM
    integration.llm_start("llama3", 150, "You are Coda, a helpful assistant...")
    await asyncio.sleep(1.0)
    
    response = "I don't have real-time weather data, but I can help you find out. Would you like me to check a weather website for your location?"
    for i, token in enumerate(response.split()):
        integration.llm_token(token, i)
        await asyncio.sleep(0.1)
    
    integration.llm_result(response, 200)
    
    # Simulate TTS
    integration.tts_start(response, "alexandra", "elevenlabs")
    for i in range(5):
        integration.tts_progress((i + 1) * 20.0)
        await asyncio.sleep(0.2)
    integration.tts_result(3.5, len(response))
    
    # Simulate memory storage
    integration.memory_store(
        "User asked about the weather today",
        "conversation",
        0.7,
        "mem_12345"
    )
    
    # Simulate system metrics
    integration.system_metrics(350.5, 25.3, 1024.0)
    
    # Wait a bit
    await asyncio.sleep(2.0)
    
    # Simulate another turn
    integration.stt_start(mode="push_to_talk")
    await asyncio.sleep(0.5)
    integration.stt_result("Yes, please check the weather for New York.", 0.98, "en")
    
    # Simulate tool usage
    integration.tool_call("weather_lookup", {"location": "New York"})
    await asyncio.sleep(1.0)
    integration.tool_result("weather_lookup", {
        "location": "New York",
        "temperature": 72,
        "condition": "Partly Cloudy",
        "humidity": 65
    })
    
    # Simulate LLM with tool results
    integration.llm_start("llama3", 200, "You are Coda, a helpful assistant...")
    await asyncio.sleep(1.0)
    
    response = "I checked the weather for New York. It's currently 72°F and partly cloudy with 65% humidity."
    for i, token in enumerate(response.split()):
        integration.llm_token(token, i)
        await asyncio.sleep(0.1)
    
    integration.llm_result(response, 250)
    
    # Simulate TTS
    integration.tts_start(response, "alexandra", "elevenlabs")
    for i in range(5):
        integration.tts_progress((i + 1) * 20.0)
        await asyncio.sleep(0.2)
    integration.tts_result(3.0, len(response))
    
    # Simulate memory storage
    integration.memory_store(
        "User asked to check weather for New York. It was 72°F and partly cloudy.",
        "conversation",
        0.8,
        "mem_12346"
    )
    
    # Simulate memory retrieval
    integration.memory_retrieve("weather", [
        {"content": "User asked about the weather today", "importance": 0.7},
        {"content": "User asked to check weather for New York. It was 72°F and partly cloudy.", "importance": 0.8}
    ])
    
    # End the session
    integration.end_session()

async def main():
    """Main function."""
    # Create the WebSocket server
    server = CodaWebSocketServer()
    
    # Create the integration
    integration = CodaWebSocketIntegration(server)
    
    # Start the server
    await server.start()
    
    try:
        # Send system info
        integration.system_info({
            "version": "0.1.0",
            "platform": sys.platform,
            "python_version": sys.version,
        })
        
        # Simulate a conversation
        await simulate_conversation(integration)
        
        # Keep the server running
        logger.info("Server running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(1)
            
            # Send periodic system metrics
            integration.system_metrics(
                350.5 + (time.time() % 50),
                25.3 + (time.time() % 10),
                1024.0,
                time.time() - integration.perf_tracker.session_start_time
            )
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        # Stop the server
        await server.stop()
        logger.info("Server stopped")

if __name__ == "__main__":
    asyncio.run(main())
