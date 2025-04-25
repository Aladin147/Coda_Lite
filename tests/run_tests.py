#!/usr/bin/env python3
"""
Test runner for Coda Lite.
"""

import os
import sys
import unittest
import logging

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Disable logging during tests
logging.disable(logging.CRITICAL)

def run_tests():
    """Run all tests."""
    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(os.path.dirname(__file__), pattern="test_*.py")
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return the result
    return result.wasSuccessful()

if __name__ == "__main__":
    # Run the tests
    success = run_tests()
    
    # Exit with the appropriate code
    sys.exit(0 if success else 1)
