#!/usr/bin/env python3
"""
Test script for the Tools Manifest and Help Command feature.
"""

import sys
import os
import logging

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("test.tools_manifest")

# Import the necessary modules
from tools import get_tool_router

def test_describe_tools():
    """Test the describe_tools method."""
    logger.info("Testing describe_tools method...")
    
    # Get the tool router
    tool_router = get_tool_router()
    
    # Test with default parameters
    logger.info("Testing with default parameters (text format):")
    result = tool_router.describe_tools()
    print("\n" + result + "\n")
    
    # Test with markdown format
    logger.info("Testing with markdown format:")
    result = tool_router.describe_tools(format="markdown")
    print("\n" + result + "\n")
    
    # Test with JSON format
    logger.info("Testing with JSON format:")
    result = tool_router.describe_tools(format="json")
    print("\n" + result + "\n")
    
    # Test with category filter
    logger.info("Testing with category filter (Time & Date):")
    result = tool_router.describe_tools(category="Time & Date")
    print("\n" + result + "\n")
    
    logger.info("describe_tools tests completed successfully")

def test_list_tools():
    """Test the list_tools tool."""
    logger.info("Testing list_tools tool...")
    
    # Get the tool router
    tool_router = get_tool_router()
    
    # Execute the list_tools tool
    logger.info("Executing list_tools tool:")
    result = tool_router.execute_tool("list_tools")
    print("\n" + result + "\n")
    
    # Test with category parameter
    logger.info("Testing with category parameter (Help):")
    result = tool_router.execute_tool("list_tools", {"category": "Help"})
    print("\n" + result + "\n")
    
    # Test with format parameter
    logger.info("Testing with format parameter (markdown):")
    result = tool_router.execute_tool("list_tools", {"format": "markdown"})
    print("\n" + result + "\n")
    
    logger.info("list_tools tests completed successfully")

def test_show_capabilities():
    """Test the show_capabilities tool."""
    logger.info("Testing show_capabilities tool...")
    
    # Get the tool router
    tool_router = get_tool_router()
    
    # Execute the show_capabilities tool with default parameters
    logger.info("Executing show_capabilities tool with default parameters:")
    result = tool_router.execute_tool("show_capabilities")
    print("\n" + result + "\n")
    
    # Test with detail_level parameter (detailed)
    logger.info("Testing with detail_level parameter (detailed):")
    result = tool_router.execute_tool("show_capabilities", {"detail_level": "detailed"})
    print("\n" + result + "\n")
    
    # Test with detail_level parameter (examples)
    logger.info("Testing with detail_level parameter (examples):")
    result = tool_router.execute_tool("show_capabilities", {"detail_level": "examples"})
    print("\n" + result + "\n")
    
    logger.info("show_capabilities tests completed successfully")

def main():
    """Run all tests."""
    logger.info("Starting Tools Manifest and Help Command tests...")
    
    # Run the tests
    test_describe_tools()
    test_list_tools()
    test_show_capabilities()
    
    logger.info("All tests completed successfully")

if __name__ == "__main__":
    main()
