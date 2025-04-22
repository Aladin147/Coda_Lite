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
        self.tool_aliases = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """Register default tools."""
        # TODO: Register default tools
        self.register_tool("get_time", self._get_time)

    def register_tool(self, tool_name, tool_function, aliases=None):
        """
        Register a new tool.

        Args:
            tool_name (str): Name of the tool
            tool_function (callable): Function to execute
            aliases (list, optional): List of alternative names for the tool
        """
        logger.info(f"Registering tool: {tool_name}")
        self.tools[tool_name] = tool_function

        # Register aliases if provided
        if aliases:
            for alias in aliases:
                logger.info(f"Registering alias: {alias} -> {tool_name}")
                self.tool_aliases[alias] = tool_name

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

        # Check if the tool name is an alias
        if tool_name in self.tool_aliases:
            actual_tool_name = self.tool_aliases[tool_name]
            logger.info(f"Using alias: {tool_name} -> {actual_tool_name}")
            tool_name = actual_tool_name

        if tool_name not in self.tools:
            logger.warning(f"Unknown tool: {tool_name}")
            return f"Error: Unknown tool '{tool_name}'"

        logger.info(f"Executing tool: {tool_name} with parameters: {parameters}")
        try:
            return self.tools[tool_name](**parameters)
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
            return f"Error executing tool '{tool_name}': {str(e)}"

    def extract_tool_call(self, llm_output: str) -> Optional[Dict[str, Any]]:
        """
        Extract tool call information from LLM output.

        Args:
            llm_output (str): Raw text output from LLM that may contain a tool call

        Returns:
            Optional[Dict[str, Any]]: Tool call information or None if no tool call was found
        """
        logger.info(f"Extracting tool call from: {llm_output[:100]}{'...' if len(llm_output) > 100 else ''}")

        # Check for common date/time patterns without tool calls
        date_time_patterns = [
            r'\b(?:today|current date|the date)\s+is\s+\w+\s+\d{1,2}\b',
            r'\b(?:now|current time|the time)\s+is\s+\d{1,2}:\d{2}\b',
            r'\b\d{1,2}:\d{2}\s+(?:am|pm|AM|PM)\b',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\b'
        ]

        for pattern in date_time_patterns:
            if re.search(pattern, llm_output):
                logger.warning(f"Detected date/time information without tool call: {llm_output}")

                # Determine if it's about date or time
                if re.search(r'\b(?:date|today|day)\b', llm_output, re.IGNORECASE):
                    logger.info("Forcing get_date tool call")
                    return {"name": "get_date", "args": {}}
                elif re.search(r'\b(?:time|hour|minute)\b', llm_output, re.IGNORECASE):
                    logger.info("Forcing get_time tool call")
                    return {"name": "get_time", "args": {}}

        # Try to extract tool call from the LLM output
        tool_call = self._extract_tool_call(llm_output)
        if not tool_call:
            logger.info("No tool call found in LLM output")
            return None

        # Extract tool name and arguments
        tool_name = tool_call.get("name")
        args = tool_call.get("args", {})

        if not tool_name:
            logger.warning("Tool call missing 'name' field")
            return None

        # Validate tool name (alphanumeric and underscores only)
        if not re.match(r'^[a-zA-Z0-9_]+$', tool_name):
            logger.warning(f"Invalid tool name format: {tool_name}")
            return None

        # Special handling for date/time tools
        if tool_name in ["get_time", "time", "current_time", "get_system_time"]:
            logger.info("Using get_time tool")
            return {"name": "get_time", "args": {}}
        elif tool_name in ["get_date", "date", "current_date", "get_system_date"]:
            logger.info("Using get_date tool")
            return {"name": "get_date", "args": {}}

        # Return the tool call information
        return {"name": tool_name, "args": args}

    def route_llm_output(self, llm_output: str) -> Optional[str]:
        """
        Route structured LLM output to appropriate tool.

        Args:
            llm_output (str): Raw text output from LLM that may contain a tool call

        Returns:
            Optional[str]: Result of the tool execution or None if no tool call was found
        """
        logger.info(f"Routing LLM output: {llm_output[:100]}{'...' if len(llm_output) > 100 else ''}")

        # Extract tool call information
        tool_call = self.extract_tool_call(llm_output)
        if not tool_call:
            return None

        # Extract tool name and arguments
        tool_name = tool_call.get("name")
        args = tool_call.get("args", {})

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
        # Log the raw text for debugging
        logger.debug(f"Extracting tool call from: {text}")

        # First try to parse the entire text as JSON
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict) and "tool_call" in parsed:
                logger.info(f"Successfully parsed complete JSON tool call: {parsed['tool_call']}")
                return parsed.get("tool_call")
        except json.JSONDecodeError:
            logger.debug("Text is not a complete JSON object, trying regex extraction")

        # If that fails, try to extract JSON using regex
        json_pattern = r'\{\s*"tool_call"\s*:\s*\{(.+?)\}\s*\}'
        match = re.search(json_pattern, text, re.DOTALL)

        if match:
            try:
                # Try to parse the full JSON object
                json_str = '{"tool_call":{' + match.group(1) + '}}'
                parsed = json.loads(json_str)
                logger.info(f"Successfully extracted and parsed JSON tool call: {parsed['tool_call']}")
                return parsed.get("tool_call")
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse tool call JSON: {match.group(0)}")

        # Try a more lenient approach with a broader pattern
        broader_pattern = r'\{[^\{\}]*"name"\s*:\s*"([^"]+)"[^\{\}]*"args"\s*:\s*\{([^\{\}]*)\}[^\{\}]*\}'
        match = re.search(broader_pattern, text, re.DOTALL)

        if match:
            try:
                tool_name = match.group(1)
                args_str = match.group(2).strip()

                # Handle empty args
                if not args_str:
                    args = {}
                else:
                    # Try to parse args as JSON
                    args_json = '{' + args_str + '}'
                    args = json.loads(args_json)

                logger.info(f"Extracted tool call using broader pattern: {tool_name} with args {args}")
                return {"name": tool_name, "args": args}
            except Exception as e:
                logger.warning(f"Failed to parse tool call with broader pattern: {e}")

        # No more approaches to try
        logger.debug("No tool call found in text")
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
