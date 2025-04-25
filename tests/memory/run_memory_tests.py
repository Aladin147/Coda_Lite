"""
Memory System Test Runner

This script runs all the memory system tests and generates a comprehensive report.
"""

import os
import sys
import unittest
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def ensure_test_directories():
    """Ensure test directories exist."""
    directories = [
        "data/memory/test",
        "data/memory/test/long_term",
        "data/memory/test/backups",
        "data/memory/test/results"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Ensured directory exists: {directory}")

# Ensure test directories exist first
ensure_test_directories()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"data/memory/test/results/memory_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("memory_test.runner")

# Import test modules
# Use relative imports since we're in the same package
from test_short_term_memory import ShortTermMemoryTest
from test_long_term_memory import LongTermMemoryTest
from test_enhanced_memory_manager import EnhancedMemoryManagerTest
from test_websocket_memory import WebSocketMemoryTest



def run_test_suite():
    """Run all memory system tests."""
    # Ensure test directories exist
    ensure_test_directories()

    # Create test suite
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(ShortTermMemoryTest))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(LongTermMemoryTest))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(EnhancedMemoryManagerTest))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(WebSocketMemoryTest))

    # Create test runner
    runner = unittest.TextTestRunner(verbosity=2)

    # Run tests
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()

    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": end_time - start_time,
        "total_tests": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "success_rate": (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100 if result.testsRun > 0 else 0,
        "failures_detail": [{"test": test, "message": message} for test, message in result.failures],
        "errors_detail": [{"test": test, "message": message} for test, message in result.errors],
        "skipped_detail": [{"test": test, "message": message} for test, message in result.skipped]
    }

    # Save report
    report_path = f"data/memory/test/results/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    logger.info(f"Test report saved to {report_path}")

    return report

def print_report_summary(report):
    """Print a summary of the test report."""
    print("\n" + "=" * 50)
    print("Memory System Test Summary")
    print("=" * 50)
    print(f"Total Tests: {report['total_tests']}")
    print(f"Passed: {report['total_tests'] - report['failures'] - report['errors']}")
    print(f"Failed: {report['failures']}")
    print(f"Errors: {report['errors']}")
    print(f"Skipped: {report['skipped']}")
    print(f"Success Rate: {report['success_rate']:.2f}%")
    print(f"Duration: {report['duration_seconds']:.2f} seconds")
    print("=" * 50)

    if report['failures'] > 0:
        print("\nFailures:")
        for i, failure in enumerate(report['failures_detail']):
            print(f"{i+1}. {failure['test']}")

    if report['errors'] > 0:
        print("\nErrors:")
        for i, error in enumerate(report['errors_detail']):
            print(f"{i+1}. {error['test']}")

if __name__ == "__main__":
    try:
        logger.info("Starting memory system tests")
        report = run_test_suite()
        logger.info("Memory system tests completed")

        # Print summary
        print_report_summary(report)

        # Exit with appropriate code
        if report['failures'] > 0 or report['errors'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
    except Exception as e:
        logger.error(f"Error running memory system tests: {e}", exc_info=True)
        sys.exit(1)
