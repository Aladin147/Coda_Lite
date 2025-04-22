"""
Test script for Coda Lite tool calling system.

This script demonstrates the basic tool calling functionality in Coda Lite v0.0.2.
It simulates LLM outputs with tool calls and shows how the tool router processes them.
"""

import sys
import os
import json
import logging

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import the tool router
from tools import get_tool_router

def test_tool_calling():
    """Test the tool calling system."""
    print("\n===== Testing Coda Lite Tool Calling System =====\n")

    # Get the tool router
    tool_router = get_tool_router()

    # Print available tools
    print("Available Tools:")
    print("-" * 50)
    for name, description in tool_router.get_available_tools().items():
        print(f"- {name}: {description}")
    print("-" * 50)

    # Test cases - simulated LLM outputs with tool calls
    test_cases = [
        # Valid tool calls
        {
            "name": "Simple get_time call",
            "llm_output": '{"tool_call": {"name": "get_time", "args": {}}}'
        },
        {
            "name": "get_date call",
            "llm_output": '{"tool_call": {"name": "get_date", "args": {}}}'
        },
        {
            "name": "tell_joke call",
            "llm_output": '{"tool_call": {"name": "tell_joke", "args": {}}}'
        },
        {
            "name": "list_memory_files call",
            "llm_output": '{"tool_call": {"name": "list_memory_files", "args": {}}}'
        },
        {
            "name": "count_conversation_turns call",
            "llm_output": '{"tool_call": {"name": "count_conversation_turns", "args": {}}}'
        },

        # Tool call embedded in text
        {
            "name": "Tool call embedded in text",
            "llm_output": 'I need to check the time. {"tool_call": {"name": "get_time", "args": {}}} Let me do that for you.'
        },

        # Invalid tool calls
        {
            "name": "Unknown tool",
            "llm_output": '{"tool_call": {"name": "unknown_tool", "args": {}}}'
        },
        {
            "name": "Invalid JSON",
            "llm_output": 'This is not a valid JSON: {"tool_call": {"name": "get_time", "args": {}'
        },
        {
            "name": "No tool call",
            "llm_output": 'This is a regular response without a tool call.'
        },
        {
            "name": "Date hallucination",
            "llm_output": 'Today\'s date is March 13, 2023.'
        },
        {
            "name": "Time hallucination",
            "llm_output": 'The current time is 3:45 PM.'
        }
    ]

    # Run the test cases
    for i, test_case in enumerate(test_cases):
        print(f"\nTest Case {i+1}: {test_case['name']}")
        print(f"LLM Output: {test_case['llm_output']}")

        # Extract tool call
        tool_call = tool_router.extract_tool_call(test_case['llm_output'])

        if tool_call is None:
            print("Result: No tool call detected")
        else:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})
            print(f"Extracted tool call: {tool_name} with args {tool_args}")

            # Execute the tool
            tool_result = tool_router.execute_tool(tool_name, tool_args)
            print(f"Tool result: {tool_result}")

            # Simulate the second LLM call with the tool result
            print(f"Final response: Here's the information you requested: {tool_result}")

    # Print the tool descriptions for the system prompt
    print("\nTool Descriptions for System Prompt:")
    print("-" * 50)
    print(tool_router.format_tool_descriptions())
    print("-" * 50)

if __name__ == "__main__":
    test_tool_calling()
