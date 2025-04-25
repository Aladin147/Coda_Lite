"""
Base test class for memory system tests.

This module provides a base test class with common setup/teardown logic for memory system tests.
"""

import os
import sys
import unittest
import logging
import shutil
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("memory_test")

class MemoryTestBase(unittest.TestCase):
    """Base test class for memory system tests."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Ensure test directories exist
        cls.ensure_test_directories()
        
        # Create a unique test ID
        cls.test_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        logger.info(f"Starting memory test with ID: {cls.test_id}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        # Clean up test directories if needed
        # Note: We might want to keep test data for debugging
        logger.info(f"Completed memory test with ID: {cls.test_id}")
    
    def setUp(self):
        """Set up test case."""
        self.test_start_time = time.time()
        logger.info(f"Starting test: {self._testMethodName}")
    
    def tearDown(self):
        """Clean up after test case."""
        elapsed = time.time() - self.test_start_time
        logger.info(f"Completed test: {self._testMethodName} in {elapsed:.2f}s")
    
    @staticmethod
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
            logger.debug(f"Ensured directory exists: {directory}")
    
    @staticmethod
    def get_test_config():
        """Get test configuration."""
        return {
            "memory": {
                "long_term_enabled": True,
                "max_turns": 20,
                "max_tokens": 800,
                "long_term_path": "data/memory/test/long_term",
                "embedding_model": "all-MiniLM-L6-v2",
                "vector_db": "chroma",  # Use ChromaDB for tests
                "max_memories": 1000,
                "device": "cpu",
                "auto_persist": True,
                "persist_interval": 1,
                "chunk_size": 150,
                "chunk_overlap": 50,
                "min_chunk_length": 50
            }
        }
    
    def create_test_conversation(self):
        """Create a test conversation."""
        return [
            {"role": "system", "content": "You are Coda, a helpful assistant."},
            {"role": "user", "content": "Hello, who are you?"},
            {"role": "assistant", "content": "I'm Coda, your voice assistant. How can I help you today?"},
            {"role": "user", "content": "What can you do?"},
            {"role": "assistant", "content": "I can answer questions, provide information, and assist with various tasks."}
        ]
    
    def create_test_facts(self):
        """Create test facts with unique identifiers."""
        test_id = self.test_id
        return [
            f"My name is John Doe and I'm testing the memory system ({test_id}).",
            f"I live in New York City and work as a software engineer ({test_id}).",
            f"I have a dog named Max who is 5 years old ({test_id}).",
            f"My favorite color is blue and I enjoy hiking on weekends ({test_id}).",
            f"I'm working on a project called Coda Lite which is a voice assistant ({test_id})."
        ]
    
    def save_test_results(self, results: Dict[str, Any], name: str):
        """Save test results to a file."""
        results_path = f"data/memory/test/results/{name}_{self.test_id}.json"
        
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Saved test results to {results_path}")
        return results_path
