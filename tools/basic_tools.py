"""
Basic tools for Coda Lite.

This module provides a set of simple tools for Coda Lite v0.0.2:
- get_time(): Get the current time
- get_date(): Get the current date
- tell_joke(): Tell a random joke
- list_memory_files(): List memory files in the data directory
- count_conversation_turns(): Count the number of turns in the current conversation
"""

import os
import random
from datetime import datetime
from typing import Optional

import logging
logger = logging.getLogger("coda.tools")

# Global variable to store memory manager reference
_memory_manager = None

def set_memory_manager(memory_manager):
    """Set the memory manager reference for tools that need it."""
    global _memory_manager
    _memory_manager = memory_manager
    logger.info("Memory manager reference set for tools")

# Time and Date Tools

def get_time() -> str:
    """Get the current time."""
    now = datetime.now()
    return f"It's {now.strftime('%H:%M')}."

def get_date() -> str:
    """Get the current date."""
    now = datetime.now()
    return f"Today is {now.strftime('%A, %B %d, %Y')}."

# Entertainment Tools

def tell_joke() -> str:
    """Tell a random joke."""
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "Why don't skeletons fight each other? They don't have the guts!",
        "What do you call a fake noodle? An impasta!",
        "How does a penguin build its house? Igloos it together!",
        "Why did the bicycle fall over? Because it was two-tired!",
        "What's orange and sounds like a parrot? A carrot!",
        "Why can't you give Elsa a balloon? Because she will let it go!",
        "What do you call a bear with no teeth? A gummy bear!",
        "Why did the golfer bring two pairs of pants? In case he got a hole in one!"
    ]
    return random.choice(jokes)

# Memory Tools

def list_memory_files() -> str:
    """List memory files in the data directory."""
    memory_dir = "data/memory"

    if not os.path.exists(memory_dir):
        return "No memory directory found."

    files = [f for f in os.listdir(memory_dir) if f.endswith('.json')]

    if not files:
        return "No memory files found."

    file_count = len(files)
    file_list = ", ".join(files[:5])

    if file_count > 5:
        return f"{file_count} memory files found. Most recent: {file_list}..."
    else:
        return f"{file_count} memory files found: {file_list}"

def count_conversation_turns() -> str:
    """Count the number of turns in the current conversation."""
    global _memory_manager

    if not _memory_manager:
        return "Memory manager not available."

    try:
        turn_count = _memory_manager.get_turn_count()

        if turn_count == 0:
            return "We haven't had any conversation turns yet."
        elif turn_count == 1:
            return "We've had 1 turn in this conversation."
        else:
            return f"We've had {turn_count} turns in this conversation."
    except Exception as e:
        logger.error(f"Error counting conversation turns: {e}")
        return "I couldn't count our conversation turns due to an error."

# Register all tools with the tool router
def register_tools(tool_router):
    """Register all tools with the given tool router."""
    # Register tools with aliases
    tool_router.register_tool("get_time", get_time, aliases=["get_system_time", "time", "current_time"])
    tool_router.register_tool("get_date", get_date, aliases=["get_system_date", "date", "current_date"])
    tool_router.register_tool("tell_joke", tell_joke, aliases=["joke", "tell_a_joke"])
    tool_router.register_tool("list_memory_files", list_memory_files, aliases=["memory_files", "list_files"])
    tool_router.register_tool("count_conversation_turns", count_conversation_turns, aliases=["count_turns", "conversation_turns"])

    logger.info(f"Registered {len(tool_router.tools)} tools")
    return tool_router
