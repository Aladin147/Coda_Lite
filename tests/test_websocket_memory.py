#!/usr/bin/env python3
"""
Test script for the WebSocket-integrated memory module.

This script tests the WebSocketEnhancedMemoryManager class with the WebSocket server.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from memory import WebSocketEnhancedMemoryManager
from websocket import CodaWebSocketServer, CodaWebSocketIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("websocket_memory_test")

async def test_memory(server, integration):
    """Test the WebSocketEnhancedMemoryManager class."""
    # Initialize the WebSocketEnhancedMemoryManager
    memory_manager = WebSocketEnhancedMemoryManager(
        websocket_integration=integration,
        config={
            "memory": {
                "long_term_enabled": True,
                "max_turns": 20,
                "max_tokens": 800
            }
        },
        max_turns=20,
        memory_path="data/memory/long_term",
        embedding_model="all-MiniLM-L6-v2",
        device="cpu"
    )
    
    try:
        # Test adding conversation turns
        logger.info("Testing add_turn method...")
        
        # Add system turn
        memory_manager.add_turn(
            role="system",
            content="You are Coda, a helpful voice assistant."
        )
        
        # Add user turn
        memory_manager.add_turn(
            role="user",
            content="Hello, what can you do?"
        )
        
        # Add assistant turn
        memory_manager.add_turn(
            role="assistant",
            content="I'm Coda, your voice assistant. I can help you with various tasks, answer questions, and have conversations."
        )
        
        logger.info("Added conversation turns")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Test adding memories
        logger.info("Testing add_memory method...")
        
        # Add a fact
        fact_id = memory_manager.add_memory(
            content="The user's name is John.",
            memory_type="fact",
            importance=0.8,
            metadata={"category": "personal_info"}
        )
        
        # Add a preference
        pref_id = memory_manager.add_memory(
            content="The user prefers concise responses.",
            memory_type="preference",
            importance=0.7,
            metadata={"category": "communication_style"}
        )
        
        logger.info(f"Added memories: {fact_id}, {pref_id}")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Test retrieving memories
        logger.info("Testing get_memories method...")
        
        # Retrieve memories about the user
        user_memories = memory_manager.get_memories(
            query="What do I know about the user?",
            limit=5
        )
        
        logger.info(f"Retrieved {len(user_memories)} memories about the user")
        for i, memory in enumerate(user_memories):
            logger.info(f"  Memory {i+1}: {memory.get('content')}")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Test updating a memory
        logger.info("Testing update_memory method...")
        
        # Update the fact
        memory_manager.update_memory(
            memory_id=fact_id,
            content="The user's name is John Smith.",
            importance=0.9
        )
        
        logger.info(f"Updated memory: {fact_id}")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Test getting enhanced context
        logger.info("Testing get_enhanced_context method...")
        
        # Get enhanced context for a query
        context = memory_manager.get_enhanced_context(
            query="Tell me about yourself",
            max_tokens=800
        )
        
        logger.info(f"Retrieved context with {len(context)} messages")
        for i, msg in enumerate(context):
            logger.info(f"  Message {i+1}: role={msg['role']}, content={msg['content'][:50]}...")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Test getting memory stats
        logger.info("Testing get_memory_stats method...")
        
        # Get memory stats
        stats = memory_manager.get_memory_stats()
        
        logger.info(f"Memory stats: {stats}")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Test clearing short-term memory
        logger.info("Testing clear_short_term method...")
        
        # Clear short-term memory
        memory_manager.clear_short_term()
        
        logger.info("Cleared short-term memory")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Test deleting a memory
        logger.info("Testing delete_memory method...")
        
        # Delete the preference
        memory_manager.delete_memory(pref_id)
        
        logger.info(f"Deleted memory: {pref_id}")
    except Exception as e:
        logger.error(f"Error in memory test: {e}", exc_info=True)
    finally:
        # Close the memory manager
        memory_manager.close()
        logger.info("Closed memory manager")

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
        
        # Test the memory manager
        await test_memory(server, integration)
        
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
