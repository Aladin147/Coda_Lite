"""
Tools module for Coda Lite.
Handles execution of tools based on structured LLM output.

This module provides a simple tool calling system for Coda Lite v0.0.2.
It includes a registry for tools, a dispatcher, and basic tool implementations.
"""

from tools.tool_router import ToolRouter
from tools.basic_tools import register_tools, set_memory_manager

# Create a singleton instance of the tool router
_tool_router = None

def get_tool_router():
    """Get the singleton tool router instance."""
    global _tool_router

    if _tool_router is None:
        _tool_router = ToolRouter()
        register_tools(_tool_router)

    return _tool_router
