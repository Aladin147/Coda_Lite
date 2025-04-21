"""
Prompt management for Coda Lite.
"""

import os
import logging
logger = logging.getLogger("coda.config")

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

# Default tool calling prompt
DEFAULT_TOOL_PROMPT = """
You can use the following tools to help answer the user's query:
- get_time(): Get the current time
- tell_joke(): Tell a random joke
- get_weather(location): Get the current weather for a location

To use a tool, respond with a structured output in this format:
{
  "action": "tool_name",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  }
}

If no tool is needed, respond with:
{
  "action": "none",
  "parameters": {}
}
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
        self.tool_prompt = DEFAULT_TOOL_PROMPT
        self._load_prompts()
        
    def _load_prompts(self):
        """Load prompts from files."""
        os.makedirs(self.prompts_dir, exist_ok=True)
        
        system_prompt_path = os.path.join(self.prompts_dir, "system.txt")
        tool_prompt_path = os.path.join(self.prompts_dir, "tools.txt")
        
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
                
        # Load tool prompt if exists
        if os.path.exists(tool_prompt_path):
            try:
                with open(tool_prompt_path, 'r') as f:
                    self.tool_prompt = f.read()
                logger.info(f"Loaded tool prompt from {tool_prompt_path}")
            except Exception as e:
                logger.error(f"Error loading tool prompt: {e}", exc_info=True)
        else:
            # Create default tool prompt file
            try:
                with open(tool_prompt_path, 'w') as f:
                    f.write(DEFAULT_TOOL_PROMPT)
                logger.info(f"Created default tool prompt at {tool_prompt_path}")
            except Exception as e:
                logger.error(f"Error creating tool prompt file: {e}", exc_info=True)
                
    def get_system_prompt(self):
        """
        Get the system prompt.
        
        Returns:
            str: System prompt
        """
        return self.system_prompt
        
    def get_tool_prompt(self):
        """
        Get the tool prompt.
        
        Returns:
            str: Tool prompt
        """
        return self.tool_prompt
        
    def get_combined_prompt(self):
        """
        Get the combined system and tool prompt.
        
        Returns:
            str: Combined prompt
        """
        return f"{self.system_prompt}\n\n{self.tool_prompt}"
