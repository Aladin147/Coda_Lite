#!/usr/bin/env python3
"""
Test script for the memory manager.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("memory_test")

from memory import MemoryManager

def main():
    """Test the memory manager."""
    try:
        print("=" * 50)
        print("Coda Lite Memory Manager Test")
        print("=" * 50)
        
        # Create memory manager
        print("\nInitializing memory manager...")
        memory = MemoryManager(max_turns=5)
        
        # Add some turns
        print("\nAdding conversation turns...")
        memory.add_turn("system", "You are Coda, a helpful assistant with a direct and efficient personality.")
        memory.add_turn("user", "Hello, who are you?")
        memory.add_turn("assistant", "I'm Coda, your voice assistant. How can I help you today?")
        memory.add_turn("user", "What can you do?")
        memory.add_turn("assistant", "I can answer questions, provide information, and assist with various tasks.")
        
        # Get context with limited tokens
        print("\nGetting context with token limit 100:")
        context = memory.get_context(max_tokens=100)
        for turn in context:
            print(f"[{turn['role']}]: {turn['content']}")
        
        # Add one more turn (should push out oldest non-system turn)
        print("\nAdding one more turn (should push out oldest non-system turn)...")
        memory.add_turn("user", "Tell me a joke.")
        
        # Get full context
        print("\nGetting full context:")
        context = memory.get_context(max_tokens=1000)
        for turn in context:
            print(f"[{turn['role']}]: {turn['content']}")
        
        # Export memory
        print("\nExporting memory...")
        os.makedirs("data/memory", exist_ok=True)
        export_path = "data/memory/test_export.json"
        memory.export(export_path)
        print(f"Exported memory to {export_path}")
        
        # Reset memory
        print("\nResetting memory...")
        memory.reset()
        print(f"Memory reset, turn count: {memory.get_turn_count()}")
        
        # Import memory
        print("\nImporting memory...")
        count = memory.import_data(export_path)
        print(f"Imported {count} turns from {export_path}")
        
        # Get full context after import
        print("\nGetting full context after import:")
        context = memory.get_context(max_tokens=1000)
        for turn in context:
            print(f"[{turn['role']}]: {turn['content']}")
        
        # Test token limiting
        print("\nTesting token limiting with very long messages...")
        memory.reset()
        
        # Add system message
        memory.add_turn("system", "You are Coda, a helpful assistant.")
        
        # Add a very long user message
        long_message = "This is a very long message that should take up a lot of tokens. " * 20
        memory.add_turn("user", long_message)
        
        # Add a short assistant response
        memory.add_turn("assistant", "I understand. How can I help with that?")
        
        # Add another user message
        memory.add_turn("user", "What's the weather like today?")
        
        # Get context with limited tokens
        print("\nGetting context with token limit 200:")
        context = memory.get_context(max_tokens=200)
        for turn in context:
            role = turn['role']
            content = turn['content']
            # Truncate content for display
            if len(content) > 50:
                content = content[:47] + "..."
            print(f"[{role}]: {content}")
        
        print("\nTest completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
