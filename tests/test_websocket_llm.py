#!/usr/bin/env python3
"""
Test script for the WebSocket-integrated LLM module.

This script tests the WebSocketOllamaLLM class with the WebSocket server.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from llm import WebSocketOllamaLLM
from websocket import CodaWebSocketServer, CodaWebSocketIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("websocket_llm_test")

async def test_llm(server, integration):
    """Test the WebSocketOllamaLLM class."""
    # Initialize the WebSocketOllamaLLM
    llm = WebSocketOllamaLLM(
        websocket_integration=integration,
        model_name="llama3",  # Use your preferred model
        host="http://localhost:11434"
    )
    
    try:
        # Test simple response generation
        logger.info("Testing generate_response method...")
        prompt = "What are three interesting facts about the moon?"
        system_prompt = "You are a helpful, concise assistant. Keep your answers brief and to the point."
        
        logger.info(f"Prompt: {prompt}")
        logger.info(f"System prompt: {system_prompt}")
        
        # Generate a response
        response = llm.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7
        )
        
        logger.info(f"Response: {response}")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Test chat method
        logger.info("Testing chat method...")
        messages = [
            {"role": "system", "content": "You are a helpful, concise assistant named Coda."},
            {"role": "user", "content": "Hello, who are you?"}
        ]
        
        logger.info(f"Messages: {messages}")
        
        # Generate a chat response
        response = llm.chat(
            messages=messages,
            temperature=0.7
        )
        
        logger.info(f"Chat response: {response}")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Test streaming
        logger.info("Testing streaming response...")
        prompt = "Write a short poem about artificial intelligence."
        
        logger.info(f"Prompt: {prompt}")
        
        # Generate a streaming response
        full_response = ""
        for chunk in llm.generate_response(
            prompt=prompt,
            system_prompt="You are a creative assistant who writes beautiful poetry.",
            temperature=0.7,
            stream=True
        ):
            full_response += chunk
            logger.info(f"Received chunk: {chunk}")
        
        logger.info(f"Full streaming response: {full_response}")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Test structured output
        logger.info("Testing structured output...")
        prompt = "What's the weather like in Paris today?"
        
        # Define the schema for the structured output
        output_schema = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["get_weather", "unknown_location", "need_more_info"]
                },
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"},
                        "date": {"type": "string"}
                    },
                    "required": ["location"]
                }
            },
            "required": ["action", "parameters"]
        }
        
        logger.info(f"Prompt: {prompt}")
        logger.info(f"Schema: {output_schema}")
        
        # Generate a structured output
        structured_output = llm.generate_structured_output(
            prompt=prompt,
            output_schema=output_schema,
            system_prompt="You are a helpful assistant who provides structured outputs.",
            temperature=0.5
        )
        
        logger.info(f"Structured output: {structured_output}")
    except Exception as e:
        logger.error(f"Error in LLM test: {e}", exc_info=True)

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
        
        # Test the LLM
        await test_llm(server, integration)
        
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
