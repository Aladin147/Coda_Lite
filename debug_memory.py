#!/usr/bin/env python3
"""
Debug script for memory system.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("memory_debug")

# Add the parent directory to the path so we can import the memory module
sys.path.insert(0, str(Path(__file__).resolve().parent))

from memory import EnhancedMemoryManager
from config.config_loader import ConfigLoader

def main():
    """Main function."""
    # Create necessary directories
    os.makedirs("data/memory/long_term", exist_ok=True)
    
    # Load configuration
    config = ConfigLoader("config/config.yaml")
    
    # Print memory configuration
    memory_config = config.get("memory", {})
    print("Memory Configuration:")
    for key, value in memory_config.items():
        print(f"  {key}: {value}")
    
    # Initialize memory system
    try:
        print("\nInitializing EnhancedMemoryManager...")
        memory = EnhancedMemoryManager(config.get_all())
        print("EnhancedMemoryManager initialized successfully")
        
        # Add some test memories
        print("\nAdding test memories...")
        
        # Add system message
        memory.add_turn("system", "You are Coda, a helpful AI assistant.")
        print("Added system message")
        
        # Add user message
        memory.add_turn("user", "My name is Aladin and your name, Coda, stands for Core Operations and Digital Assistant.")
        print("Added user message")
        
        # Add assistant message
        memory.add_turn("assistant", "Thank you for letting me know, Aladin! I'll remember that my name, Coda, stands for Core Operations and Digital Assistant. Is there anything else you'd like to tell me about yourself?")
        print("Added assistant message")
        
        # Persist memories
        print("\nPersisting memories to long-term storage...")
        stored_count = memory.persist_short_term_memory()
        print(f"Persisted {stored_count} memories")
        
        # Add a fact explicitly
        print("\nAdding explicit fact...")
        fact_id = memory.add_fact("Coda stands for Core Operations and Digital Assistant", source="user")
        print(f"Added fact with ID: {fact_id}")
        
        # Add a preference explicitly
        print("\nAdding explicit preference...")
        pref_id = memory.add_preference("Aladin is my user's name", metadata={"importance": 0.9})
        print(f"Added preference with ID: {pref_id}")
        
        # Search for memories
        print("\nSearching for memories about 'Coda'...")
        coda_memories = memory.search_memories("What does Coda stand for?", limit=5)
        print(f"Found {len(coda_memories)} memories about Coda:")
        for i, mem in enumerate(coda_memories):
            print(f"  Memory {i+1}: {mem.get('content', '')[:100]}...")
        
        print("\nSearching for memories about 'Aladin'...")
        aladin_memories = memory.search_memories("What is my name?", limit=5)
        print(f"Found {len(aladin_memories)} memories about Aladin:")
        for i, mem in enumerate(aladin_memories):
            print(f"  Memory {i+1}: {mem.get('content', '')[:100]}...")
        
        # Close memory system
        print("\nClosing memory system...")
        memory.close()
        print("Memory system closed")
        
        return 0
    except Exception as e:
        logger.error(f"Error in memory system: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
