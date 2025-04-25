#!/usr/bin/env python3
"""
Test script for the message deduplication system.

This script tests the message deduplication implementation.
"""

import logging
import sys
import time
import unittest
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from websocket.message_deduplication import (
    MessageDeduplicator,
    get_message_deduplicator,
    is_duplicate_message
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_message_deduplication")


class TestMessageDeduplication(unittest.TestCase):
    """Test cases for the message deduplication system."""

    def test_is_duplicate_message(self):
        """Test the is_duplicate_message function."""
        # Check a new message
        is_duplicate, count = is_duplicate_message("test_type", {"data": "test"})

        # It should not be a duplicate
        self.assertFalse(is_duplicate)
        self.assertEqual(count, 1)

        # Check the same message again
        is_duplicate, count = is_duplicate_message("test_type", {"data": "test"})

        # It should be a duplicate
        self.assertTrue(is_duplicate)
        self.assertEqual(count, 2)

        # Check a different message
        is_duplicate, count = is_duplicate_message("test_type", {"data": "different"})

        # It should not be a duplicate
        self.assertFalse(is_duplicate)
        self.assertEqual(count, 1)

    def test_message_deduplicator(self):
        """Test the MessageDeduplicator class."""
        # Create a deduplicator
        deduplicator = MessageDeduplicator(expiration_seconds=1.0)

        # Check a new message
        is_duplicate, count = deduplicator.is_duplicate("test_type", {"data": "test"})

        # It should not be a duplicate
        self.assertFalse(is_duplicate)
        self.assertEqual(count, 1)

        # Check the same message again
        is_duplicate, count = deduplicator.is_duplicate("test_type", {"data": "test"})

        # It should be a duplicate
        self.assertTrue(is_duplicate)
        self.assertEqual(count, 2)

        # Wait for the message to expire
        time.sleep(1.1)

        # Check the same message again
        is_duplicate, count = deduplicator.is_duplicate("test_type", {"data": "test"})

        # It should not be a duplicate anymore
        self.assertFalse(is_duplicate)
        self.assertEqual(count, 1)

    def test_get_message_deduplicator(self):
        """Test the get_message_deduplicator function."""
        # Get the deduplicator
        deduplicator = get_message_deduplicator()

        # Check that it's a valid deduplicator
        self.assertIsInstance(deduplicator, MessageDeduplicator)

        # Get it again
        deduplicator2 = get_message_deduplicator()

        # Check that it's the same instance
        self.assertIs(deduplicator, deduplicator2)

    def test_different_message_types(self):
        """Test deduplication with different message types."""
        # Create a deduplicator
        deduplicator = MessageDeduplicator()

        # Check a message with type A
        is_duplicate, count = deduplicator.is_duplicate("type_a", {"data": "test"})

        # It should not be a duplicate
        self.assertFalse(is_duplicate)
        self.assertEqual(count, 1)

        # Check a message with type B but same data
        is_duplicate, count = deduplicator.is_duplicate("type_b", {"data": "test"})

        # It should not be a duplicate (different type)
        self.assertFalse(is_duplicate)
        self.assertEqual(count, 1)

        # Check the message with type A again
        is_duplicate, count = deduplicator.is_duplicate("type_a", {"data": "test"})

        # It should be a duplicate
        self.assertTrue(is_duplicate)
        self.assertEqual(count, 2)

    def test_cache_size_limit(self):
        """Test the cache size limit."""
        # Create a deduplicator with a small cache size and no expiration
        deduplicator = MessageDeduplicator(max_cache_size=3, expiration_seconds=3600)

        # Add 5 different messages
        for i in range(5):
            is_duplicate, count = deduplicator.is_duplicate(f"type_{i}", {"data": f"test_{i}"})

            # None should be duplicates
            self.assertFalse(is_duplicate)
            self.assertEqual(count, 1)

        # The cache should only contain the 3 most recent messages
        # So the first 2 messages should not be considered duplicates anymore
        for i in range(2):
            is_duplicate, count = deduplicator.is_duplicate(f"type_{i}", {"data": f"test_{i}"})

            # They should not be duplicates
            self.assertFalse(is_duplicate)
            self.assertEqual(count, 1)

        # But the last 3 messages should still be in the cache
        # We need to check them in reverse order to ensure they're still in the cache
        for i in range(4, 1, -1):
            is_duplicate, count = deduplicator.is_duplicate(f"type_{i}", {"data": f"test_{i}"})

            # They should be duplicates
            self.assertTrue(is_duplicate)
            self.assertEqual(count, 2)

    def test_clear(self):
        """Test clearing the cache."""
        # Create a deduplicator
        deduplicator = MessageDeduplicator()

        # Add a message
        is_duplicate, count = deduplicator.is_duplicate("test_type", {"data": "test"})

        # It should not be a duplicate
        self.assertFalse(is_duplicate)
        self.assertEqual(count, 1)

        # Clear the cache
        deduplicator.clear()

        # Check the same message again
        is_duplicate, count = deduplicator.is_duplicate("test_type", {"data": "test"})

        # It should not be a duplicate anymore
        self.assertFalse(is_duplicate)
        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
