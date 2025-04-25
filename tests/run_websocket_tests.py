#!/usr/bin/env python3
"""
Test runner for WebSocket implementation tests.

This script runs all the WebSocket implementation tests.
"""

import os
import sys
import time
import unittest
import logging
import subprocess
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("run_websocket_tests")


def run_test_module(module_name):
    """
    Run a test module.
    
    Args:
        module_name: The name of the test module to run
        
    Returns:
        True if the test passed, False otherwise
    """
    logger.info(f"Running test module: {module_name}")
    
    try:
        # Run the test module as a subprocess
        result = subprocess.run(
            [sys.executable, f"tests/{module_name}.py"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Check if the test passed
        if result.returncode == 0:
            logger.info(f"Test module {module_name} passed")
            return True
        else:
            logger.error(f"Test module {module_name} failed with exit code {result.returncode}")
            logger.error(f"Stdout: {result.stdout}")
            logger.error(f"Stderr: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error running test module {module_name}: {e}")
        return False


def run_unittest_module(module_name):
    """
    Run a unittest module.
    
    Args:
        module_name: The name of the unittest module to run
        
    Returns:
        True if the test passed, False otherwise
    """
    logger.info(f"Running unittest module: {module_name}")
    
    try:
        # Run the unittest module
        result = unittest.main(module=module_name, exit=False)
        
        # Check if the test passed
        if result.result.wasSuccessful():
            logger.info(f"Unittest module {module_name} passed")
            return True
        else:
            logger.error(f"Unittest module {module_name} failed")
            return False
    except Exception as e:
        logger.error(f"Error running unittest module {module_name}: {e}")
        return False


def run_js_test(test_file):
    """
    Run a JavaScript test.
    
    Args:
        test_file: The path to the JavaScript test file
        
    Returns:
        True if the test passed, False otherwise
    """
    logger.info(f"Running JavaScript test: {test_file}")
    
    try:
        # Check if Node.js is installed
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Node.js is not installed or not in the PATH")
            return False
        
        # Run the JavaScript test
        result = subprocess.run(
            ["node", test_file],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Check if the test passed
        if result.returncode == 0:
            logger.info(f"JavaScript test {test_file} passed")
            return True
        else:
            logger.error(f"JavaScript test {test_file} failed with exit code {result.returncode}")
            logger.error(f"Stdout: {result.stdout}")
            logger.error(f"Stderr: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error running JavaScript test {test_file}: {e}")
        return False


def main():
    """Main function."""
    logger.info("Running WebSocket implementation tests...")
    
    # Define the test modules to run
    test_modules = [
        "test_event_loop_manager",
        "test_message_deduplication",
        "test_authentication",
        "test_websocket_server_fixed_v2",
        "test_websocket_client_server_auth"
    ]
    
    # Define the JavaScript tests to run
    js_tests = [
        "tests/test_dashboard_websocket.js"
    ]
    
    # Run the test modules
    results = {}
    
    for module in test_modules:
        results[module] = run_test_module(module)
    
    # Run the JavaScript tests
    for test in js_tests:
        results[test] = run_js_test(test)
    
    # Print the results
    logger.info("Test results:")
    
    for test, passed in results.items():
        logger.info(f"  {test}: {'PASSED' if passed else 'FAILED'}")
    
    # Check if all tests passed
    if all(results.values()):
        logger.info("All tests passed!")
        return 0
    else:
        logger.error("Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
