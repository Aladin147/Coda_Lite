"""
Tool router for Coda Lite.
Routes structured LLM output to appropriate tool functions.
"""

import logging
import json
import re
from typing import Dict, Any, Optional

logger = logging.getLogger("coda.tools")

class ToolRouter:
    """Routes structured LLM output to appropriate tool functions."""

    def __init__(self):
        """Initialize the ToolRouter."""
        logger.info("Initializing ToolRouter")
        self.tools = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """Register default tools."""
        # TODO: Register default tools
        self.register_tool("get_time", self._get_time)

    def register_tool(self, tool_name, tool_function):
        """
        Register a new tool.

        Args:
            tool_name (str): Name of the tool
            tool_function (callable): Function to execute
        """
        logger.info(f"Registering tool: {tool_name}")
        self.tools[tool_name] = tool_function

    def execute_tool(self, tool_name, parameters=None):
        """
        Execute a tool by name.

        Args:
            tool_name (str): Name of the tool to execute
            parameters (dict, optional): Parameters for the tool

        Returns:
            Any: Result of the tool execution
        """
        if parameters is None:
            parameters = {}

        if tool_name not in self.tools:
            logger.warning(f"Unknown tool: {tool_name}")
            return f"Error: Unknown tool '{tool_name}'"

        logger.info(f"Executing tool: {tool_name} with parameters: {parameters}")
        try:
            return self.tools[tool_name](**parameters)
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
            return f"Error executing tool '{tool_name}': {str(e)}"

    def route_llm_output(self, llm_output: str) -> Optional[str]:
        """
        Route structured LLM output to appropriate tool.

        Args:
            llm_output (str): Raw text output from LLM that may contain a tool call

        Returns:
            Optional[str]: Result of the tool execution or None if no tool call was found
        """
        # Try to extract tool call from the LLM output
        tool_call = self._extract_tool_call(llm_output)
        if not tool_call:
            return None

        # Extract tool name and arguments
        tool_name = tool_call.get("name")
        args = tool_call.get("args", {})

        if not tool_name:
            logger.warning("Tool call missing 'name' field")
            return "Error: Tool call missing 'name' field"

        # Validate tool name (alphanumeric and underscores only)
        if not re.match(r'^[a-zA-Z0-9_]+$', tool_name):
            logger.warning(f"Invalid tool name format: {tool_name}")
            return f"Error: Invalid tool name format: {tool_name}"

        # Execute the tool
        return self.execute_tool(tool_name, args)

    def _extract_tool_call(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract tool call from LLM output text.

        Args:
            text (str): Raw text output from LLM

        Returns:
            Optional[Dict[str, Any]]: Extracted tool call or None if not found
        """
        # First try to parse the entire text as JSON
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict) and "tool_call" in parsed:
                return parsed.get("tool_call")
        except json.JSONDecodeError:
            pass

        # If that fails, try to extract JSON using regex
        json_pattern = r'\{\s*"tool_call"\s*:\s*\{(.+?)\}\s*\}'
        match = re.search(json_pattern, text, re.DOTALL)

        if match:
            try:
                # Try to parse the full JSON object
                json_str = '{"tool_call":{' + match.group(1) + '}}'
                parsed = json.loads(json_str)
                return parsed.get("tool_call")
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse tool call JSON: {match.group(0)}")

        # No more approaches to try
        return None

    # Default tool implementations
    def _get_time(self) -> str:
        """Get the current time."""
        from datetime import datetime
        now = datetime.now()
        return f"It's {now.strftime('%H:%M')}."

    def get_available_tools(self) -> Dict[str, str]:
        """
        Get a dictionary of available tools and their descriptions.

        Returns:
            Dict[str, str]: Dictionary mapping tool names to descriptions
        """
        tool_descriptions = {}
        for tool_name, tool_func in self.tools.items():
            if tool_func.__doc__:
                # Extract the first line of the docstring
                description = tool_func.__doc__.strip().split('\n')[0]
            else:
                description = "No description available"
            tool_descriptions[tool_name] = description

        return tool_descriptions

    def format_tool_descriptions(self) -> str:
        """
        Format tool descriptions for inclusion in the system prompt.

        Returns:
            str: Formatted tool descriptions
        """
        tools = self.get_available_tools()
        if not tools:
            return "No tools available."

        result = "Available tools:\n"
        for name, description in tools.items():
            result += f"- {name}: {description}\n"

        result += "\nTo use a tool, respond with JSON in this format: { \"tool_call\": { \"name\": \"tool_name\", \"args\": {\"arg1\": \"value1\"} } }"
        return result
