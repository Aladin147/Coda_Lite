"""
Memory-related tools for Coda Lite.

This module provides tools for interacting with the memory system.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional

from memory import EnhancedMemoryManager

logger = logging.getLogger("coda.tools.memory")

# Reference to the memory manager
_memory_manager = None

def set_memory_manager(memory_manager):
    """Set the memory manager reference."""
    global _memory_manager
    _memory_manager = memory_manager
    logger.info("Memory manager reference set in memory tools")

def get_memory_stats() -> str:
    """
    Get statistics about the memory system.
    
    Returns:
        String with memory statistics
    """
    if not _memory_manager:
        return "Memory manager not initialized."
    
    try:
        # Get basic stats for any memory manager
        turn_count = _memory_manager.get_turn_count()
        session_duration = _memory_manager.get_session_duration()
        
        # Format duration
        hours, remainder = divmod(int(session_duration), 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{hours}h {minutes}m {seconds}s" if hours > 0 else f"{minutes}m {seconds}s"
        
        # Basic stats
        stats = f"Session duration: {duration_str}\nConversation turns: {turn_count}\n"
        
        # Enhanced stats for EnhancedMemoryManager
        if isinstance(_memory_manager, EnhancedMemoryManager):
            memory_stats = _memory_manager.get_memory_stats()
            
            # Add long-term memory stats
            long_term_stats = memory_stats.get("long_term", {})
            total_memories = long_term_stats.get("total_memories", 0)
            stats += f"\nLong-term memories: {total_memories}\n"
            
            # Add source type breakdown
            source_types = long_term_stats.get("source_types", {})
            if source_types:
                stats += "Memory types:\n"
                for source_type, count in source_types.items():
                    stats += f"- {source_type}: {count}\n"
            
            # Add topics
            topics = long_term_stats.get("topics", 0)
            stats += f"Known topics: {topics}\n"
            
            # Add recent topics
            recent_topics = memory_stats.get("recent_topics", [])
            if recent_topics:
                stats += "\nRecent topics: " + ", ".join(recent_topics[:5])
        
        return stats
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        return f"Error getting memory stats: {str(e)}"

def add_fact(fact: str, importance: Optional[float] = None) -> str:
    """
    Add a fact to long-term memory.
    
    Args:
        fact: The fact to remember
        importance: Optional importance score (0.0 to 1.0)
        
    Returns:
        Confirmation message
    """
    if not _memory_manager:
        return "Memory manager not initialized."
    
    try:
        # Check if we have an EnhancedMemoryManager
        if not isinstance(_memory_manager, EnhancedMemoryManager):
            return "Long-term memory is not enabled."
        
        # Set default importance if not provided
        if importance is None:
            importance = 0.7  # Default importance for explicitly added facts
        
        # Add the fact
        memory_id = _memory_manager.add_fact(fact, source="user_explicit", metadata={"importance": importance})
        
        return f"I've remembered that {fact}"
    except Exception as e:
        logger.error(f"Error adding fact: {e}")
        return f"Error adding fact: {str(e)}"

def add_preference(preference: str) -> str:
    """
    Add a user preference to long-term memory.
    
    Args:
        preference: The preference to remember
        
    Returns:
        Confirmation message
    """
    if not _memory_manager:
        return "Memory manager not initialized."
    
    try:
        # Check if we have an EnhancedMemoryManager
        if not isinstance(_memory_manager, EnhancedMemoryManager):
            return "Long-term memory is not enabled."
        
        # Add the preference
        memory_id = _memory_manager.add_preference(preference)
        
        return f"I've noted your preference: {preference}"
    except Exception as e:
        logger.error(f"Error adding preference: {e}")
        return f"Error adding preference: {str(e)}"

def get_user_summary() -> str:
    """
    Get a summary of what Coda knows about the user.
    
    Returns:
        User summary
    """
    if not _memory_manager:
        return "Memory manager not initialized."
    
    try:
        # Check if we have an EnhancedMemoryManager
        if not isinstance(_memory_manager, EnhancedMemoryManager):
            return "Long-term memory is not enabled."
        
        # Get user summary
        summary = _memory_manager.get_user_summary()
        
        if not summary:
            return "I don't have much information about you yet."
        
        # Format the summary
        result = "Here's what I know about you:\n\n"
        
        # Add interests if available
        interests = summary.get("interests", [])
        if interests:
            result += f"Interests: {', '.join(interests)}\n"
        
        # Add communication style if available
        comm_style = summary.get("communication_style")
        if comm_style:
            result += f"Communication style: {comm_style}\n"
        
        # Add other preferences
        for key, value in summary.items():
            if key not in ["interests", "communication_style"]:
                if isinstance(value, list):
                    result += f"{key.replace('_', ' ').title()}: {', '.join(value)}\n"
                else:
                    result += f"{key.replace('_', ' ').title()}: {value}\n"
        
        return result
    except Exception as e:
        logger.error(f"Error getting user summary: {e}")
        return f"Error getting user summary: {str(e)}"

def search_memories(query: str, limit: int = 3) -> str:
    """
    Search long-term memories.
    
    Args:
        query: The search query
        limit: Maximum number of results to return
        
    Returns:
        Search results
    """
    if not _memory_manager:
        return "Memory manager not initialized."
    
    try:
        # Check if we have an EnhancedMemoryManager
        if not isinstance(_memory_manager, EnhancedMemoryManager):
            return "Long-term memory is not enabled."
        
        # Search memories
        memories = _memory_manager.retrieve_relevant_memories(query, limit=limit)
        
        if not memories:
            return f"I couldn't find any memories related to '{query}'."
        
        # Format the results
        result = f"Here's what I remember about '{query}':\n\n"
        
        for i, memory in enumerate(memories):
            content = memory.get("content", "")
            similarity = memory.get("similarity", 0)
            result += f"{i+1}. {content} (relevance: {similarity:.2f})\n\n"
        
        return result
    except Exception as e:
        logger.error(f"Error searching memories: {e}")
        return f"Error searching memories: {str(e)}"

def forget_session() -> str:
    """
    Forget the current session (reset short-term memory).
    
    Returns:
        Confirmation message
    """
    if not _memory_manager:
        return "Memory manager not initialized."
    
    try:
        # For EnhancedMemoryManager, use reset_short_term
        if isinstance(_memory_manager, EnhancedMemoryManager):
            _memory_manager.reset_short_term()
        else:
            # For standard MemoryManager, use reset
            _memory_manager.reset()
        
        return "I've forgotten our current conversation. What would you like to talk about?"
    except Exception as e:
        logger.error(f"Error forgetting session: {e}")
        return f"Error forgetting session: {str(e)}"

# Register tools
def register_tools(router):
    """Register memory tools with the tool router."""
    router.register_tool(
        name="get_memory_stats",
        description="Get statistics about the memory system",
        function=get_memory_stats,
        category="Memory",
        examples=["How much do you remember?", "Show memory statistics"]
    )
    
    router.register_tool(
        name="add_fact",
        description="Add a fact to long-term memory",
        function=add_fact,
        category="Memory",
        examples=["Remember that my birthday is on May 15th", "Remember I have a meeting tomorrow at 3 PM"],
        parameters=[
            {
                "name": "fact",
                "description": "The fact to remember",
                "type": "string",
                "required": True
            },
            {
                "name": "importance",
                "description": "Importance score (0.0 to 1.0)",
                "type": "number",
                "required": False
            }
        ]
    )
    
    router.register_tool(
        name="add_preference",
        description="Add a user preference to long-term memory",
        function=add_preference,
        category="Memory",
        examples=["Remember that I prefer concise responses", "Note that I like detailed explanations"],
        parameters=[
            {
                "name": "preference",
                "description": "The preference to remember",
                "type": "string",
                "required": True
            }
        ]
    )
    
    router.register_tool(
        name="get_user_summary",
        description="Get a summary of what Coda knows about the user",
        function=get_user_summary,
        category="Memory",
        examples=["What do you know about me?", "Show my user profile"]
    )
    
    router.register_tool(
        name="search_memories",
        description="Search long-term memories",
        function=search_memories,
        category="Memory",
        examples=["What do you remember about my hobbies?", "Search your memory for information about my job"],
        parameters=[
            {
                "name": "query",
                "description": "The search query",
                "type": "string",
                "required": True
            },
            {
                "name": "limit",
                "description": "Maximum number of results to return",
                "type": "integer",
                "required": False
            }
        ]
    )
    
    router.register_tool(
        name="forget_session",
        description="Forget the current session (reset short-term memory)",
        function=forget_session,
        category="Memory",
        examples=["Forget this conversation", "Reset your short-term memory"]
    )
    
    logger.info("Registered memory tools")
