"""
Prompt management for Coda Lite.

This module handles loading and formatting prompts for the LLM,
including system prompts and tool descriptions.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger("coda.config")

# Import tool router (lazy import to avoid circular imports)
_tool_router = None

def _get_tool_router():
    """Get the tool router (lazy import)."""
    global _tool_router
    if _tool_router is None:
        from tools import get_tool_router
        _tool_router = get_tool_router()
    return _tool_router

# Default system prompt
DEFAULT_SYSTEM_PROMPT = """
You are Coda, a helpful and responsive voice assistant.
Your responses should be concise, natural, and conversational.
Aim to be helpful, accurate, and friendly in your interactions.

When the user asks you to perform an action that requires a tool:
1. Determine which tool is needed
2. Respond with a structured output that includes the tool name and parameters

Keep your responses brief and to the point, as they will be spoken aloud.
"""

# Default tool descriptions (will be replaced with actual tool descriptions)
DEFAULT_TOOL_DESCRIPTIONS = """
Available tools:
- get_time: Get the current time
- get_date: Get the current date
- tell_joke: Tell a random joke
- list_memory_files: List memory files in the data directory
- count_conversation_turns: Count the number of turns in the current conversation

To use a tool, respond with JSON in this format: { "tool_call": { "name": "tool_name", "args": {"arg1": "value1"} } }
"""

class Prompts:
    """Prompt management for Coda Lite."""

    def __init__(self, prompts_dir="config/prompts"):
        """
        Initialize Prompts.

        Args:
            prompts_dir (str): Directory containing prompt files
        """
        self.prompts_dir = prompts_dir
        self.system_prompt = DEFAULT_SYSTEM_PROMPT
        self.tool_descriptions = DEFAULT_TOOL_DESCRIPTIONS
        self._load_prompts()

    def _load_prompts(self):
        """Load prompts from files."""
        os.makedirs(self.prompts_dir, exist_ok=True)

        system_prompt_path = os.path.join(self.prompts_dir, "system.txt")
        # We don't need a separate tools.txt file anymore

        # Load system prompt if exists
        if os.path.exists(system_prompt_path):
            try:
                with open(system_prompt_path, 'r') as f:
                    self.system_prompt = f.read()
                logger.info(f"Loaded system prompt from {system_prompt_path}")
            except Exception as e:
                logger.error(f"Error loading system prompt: {e}", exc_info=True)
        else:
            # Create default system prompt file
            try:
                with open(system_prompt_path, 'w') as f:
                    f.write(DEFAULT_SYSTEM_PROMPT)
                logger.info(f"Created default system prompt at {system_prompt_path}")
            except Exception as e:
                logger.error(f"Error creating system prompt file: {e}", exc_info=True)

        # We'll generate tool descriptions dynamically

    def get_system_prompt(self, personality_traits: Optional[dict] = None) -> str:
        """
        Get the system prompt with tool descriptions.

        Args:
            personality_traits: Optional personality traits to include

        Returns:
            str: System prompt with tool descriptions
        """
        # Get tool descriptions from the tool router
        try:
            tool_router = _get_tool_router()
            tool_descriptions = tool_router.format_tool_descriptions()
        except Exception as e:
            logger.warning(f"Error getting tool descriptions: {e}")
            tool_descriptions = DEFAULT_TOOL_DESCRIPTIONS

        # Format the system prompt with tool descriptions
        formatted_prompt = self.system_prompt.format(tool_descriptions=tool_descriptions)

        # Add personality traits if provided
        if personality_traits:
            # This would be handled by the personality module
            pass

        return formatted_prompt
