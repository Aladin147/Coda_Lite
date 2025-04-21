"""
Tool router for Coda Lite.
Routes structured LLM output to appropriate tool functions.
"""

import logging
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
    
    def route_llm_output(self, llm_output):
        """
        Route structured LLM output to appropriate tool.
        
        Args:
            llm_output (dict): Structured output from LLM
            
        Returns:
            Any: Result of the tool execution
        """
        if not isinstance(llm_output, dict):
            logger.warning(f"Invalid LLM output format: {type(llm_output)}")
            return "Error: Invalid LLM output format"
            
        action = llm_output.get("action", "none")
        parameters = llm_output.get("parameters", {})
        
        if action == "none":
            return None
            
        return self.execute_tool(action, parameters)
    
    # Default tool implementations
    def _get_time(self):
        """Get the current time."""
        from datetime import datetime
        now = datetime.now()
        return f"The current time is {now.strftime('%H:%M:%S')}"
