"""
Tests for the memory self-testing framework.
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import json
import os

from memory.self_testing import MemorySelfTestingFramework

class TestMemorySelfTestingFramework(unittest.TestCase):
    """Test memory self-testing functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create mock memory manager
        self.memory_manager = MagicMock()
        self.memory_manager.long_term = MagicMock()
        self.memory_manager.long_term.metadata = {
            "memories": {}
        }
        self.memory_manager.long_term._save_metadata = MagicMock()
        
        # Create test config
        self.config = {
            "memory": {
                "self_test_interval": 12,
                "self_test_batch_size": 5,
                "repair_threshold": 0.7
            }
        }
        
        # Create self-testing framework
        self.self_testing = MemorySelfTestingFramework(self.memory_manager, self.config)
        
        # Create test memories
        self.test_memories = {
            "memory1": {
                "id": "memory1",
                "content": "This is a test fact",
                "metadata": {
                    "source_type": "fact",
                    "timestamp": datetime.now().isoformat(),
                    "importance": 0.9
                }
            },
            "memory2": {
                "id": "memory2",
                "content": "User prefers dark mode",
                "metadata": {
                    "source_type": "preference",
                    "timestamp": datetime.now().isoformat(),
                    "importance": 0.6
                }
            }
        }
        
        # Set up memory manager to return test memories
        def get_memory_by_id(memory_id):
            return self.test_memories.get(memory_id)
        
        self.memory_manager.long_term.get_memory_by_id.side_effect = get_memory_by_id
        
        # Add test memories to metadata
        self.memory_manager.long_term.metadata["memories"] = {
            "memory1": {"content": "This is a test fact", "importance": 0.9},
            "memory2": {"content": "User prefers dark mode", "importance": 0.6},
            "memory3": {"content": "This memory doesn't exist in storage", "importance": 0.5}  # Inconsistency
        }

    def test_run_consistency_check(self):
        """Test running a consistency check."""
        # Run consistency check on specific memories
        results = self.self_testing.run_consistency_check(["memory1", "memory2", "memory3"])
        
        # Check that the check ran
        self.assertEqual(results["status"], "completed")
        self.assertEqual(results["memories_checked"], 3)
        
        # Check that inconsistencies were found
        self.assertTrue(any(inc["memory_id"] == "memory3" and inc["type"] == "missing" 
                           for inc in results["inconsistencies"]))
        
        # Check that metrics were updated
        self.assertEqual(self.self_testing.metrics["tests_run"], 1)
        self.assertEqual(self.self_testing.metrics["tests_failed"], 1)
        
        # Check that test history was updated
        self.assertEqual(len(self.self_testing.test_history), 1)
        self.assertEqual(self.self_testing.test_history[0]["memories_checked"], 3)
        self.assertGreater(self.self_testing.test_history[0]["inconsistencies_found"], 0)

    def test_repair_inconsistencies(self):
        """Test repairing inconsistencies."""
        # Create inconsistencies
        inconsistencies = [
            {
                "memory_id": "memory3",
                "type": "missing",
                "description": "Memory exists in metadata but not in storage",
                "severity": "high"
            },
            {
                "memory_id": "memory1",
                "type": "importance_mismatch",
                "description": "Importance in metadata doesn't match importance in memory",
                "severity": "low"
            }
        ]
        
        # Repair inconsistencies
        repairs = self.self_testing._repair_inconsistencies(inconsistencies)
        
        # Check that repairs were attempted
        self.assertEqual(len(repairs), 2)
        
        # Check that metrics were updated
        self.assertEqual(self.self_testing.metrics["repairs_attempted"], 2)
        
        # Check that repair history was updated
        self.assertEqual(len(self.self_testing.repair_history), 2)
        
        # Check specific repairs
        memory3_repair = next((r for r in repairs if r["memory_id"] == "memory3"), None)
        self.assertIsNotNone(memory3_repair)
        self.assertEqual(memory3_repair["type"], "missing")
        
        # Check that memory3 was removed from metadata
        self.memory_manager.long_term._save_metadata.assert_called()

    def test_test_memory_retrieval(self):
        """Test memory retrieval testing."""
        # Mock retrieve_relevant_memories to return specific memories
        self.memory_manager.retrieve_relevant_memories.return_value = [
            {"id": "memory1"},
            {"id": "memory4"}  # Not in expected list
        ]
        
        # Test retrieval
        results = self.self_testing.test_memory_retrieval(
            query="test query",
            expected_memory_ids=["memory1", "memory2"]  # memory2 not retrieved
        )
        
        # Check results
        self.assertEqual(results["expected_count"], 2)
        self.assertEqual(results["retrieved_count"], 2)
        self.assertEqual(results["true_positives"], 1)  # memory1
        self.assertEqual(results["false_positives"], 1)  # memory4
        self.assertEqual(results["false_negatives"], 1)  # memory2
        
        # Check metrics
        self.assertEqual(results["precision"], 0.5)  # 1/2
        self.assertEqual(results["recall"], 0.5)    # 1/2
        self.assertEqual(results["f1_score"], 0.5)  # 2 * 0.5 * 0.5 / (0.5 + 0.5)

    def test_generate_test_memory(self):
        """Test generating test memories."""
        # Generate test memories
        fact_memory = self.self_testing.generate_test_memory("fact")
        preference_memory = self.self_testing.generate_test_memory("preference")
        conversation_memory = self.self_testing.generate_test_memory("conversation")
        
        # Check that memories were generated
        self.assertTrue(fact_memory["id"].startswith("test_"))
        self.assertIn("Test fact", fact_memory["content"])
        self.assertEqual(fact_memory["metadata"]["source_type"], "fact")
        self.assertTrue(fact_memory["metadata"]["is_test"])
        
        self.assertTrue(preference_memory["id"].startswith("test_"))
        self.assertIn("Test preference", preference_memory["content"])
        self.assertEqual(preference_memory["metadata"]["source_type"], "preference")
        
        self.assertTrue(conversation_memory["id"].startswith("test_"))
        self.assertIn("Test conversation", conversation_memory["content"])
        self.assertEqual(conversation_memory["metadata"]["source_type"], "conversation")

    def test_run_retrieval_test_suite(self):
        """Test running a retrieval test suite."""
        # Mock add_memory to return predictable IDs
        self.memory_manager.long_term.add_memory.side_effect = ["test1", "test2", "test3"]
        
        # Mock retrieve_relevant_memories to return specific results for different queries
        def mock_retrieve(query):
            if "capital of France" in query:
                return [{"id": "test1"}]
            elif "user preferences" in query:
                return [{"id": "test2"}]
            elif "weather" in query:
                return [{"id": "test3"}]
            elif "test memory" in query:
                return [{"id": "test1"}, {"id": "test2"}, {"id": "test3"}]
            return []
        
        self.memory_manager.retrieve_relevant_memories.side_effect = mock_retrieve
        
        # Run test suite
        results = self.self_testing.run_retrieval_test_suite()
        
        # Check results
        self.assertEqual(results["tests_run"], 4)
        self.assertEqual(len(results["test_results"]), 4)
        
        # Check that test memories were added and deleted
        self.assertEqual(self.memory_manager.long_term.add_memory.call_count, 3)
        self.assertEqual(self.memory_manager.long_term.delete_memory.call_count, 3)
        
        # Check metrics
        self.assertEqual(results["average_precision"], 1.0)  # All perfect matches
        self.assertEqual(results["average_recall"], 1.0)     # All perfect matches
        self.assertEqual(results["average_f1"], 1.0)         # All perfect matches

    def test_get_metrics(self):
        """Test getting metrics."""
        # Set up some metrics
        self.self_testing.metrics["tests_run"] = 10
        self.self_testing.metrics["tests_passed"] = 8
        self.self_testing.metrics["tests_failed"] = 2
        self.self_testing.metrics["repairs_attempted"] = 5
        self.self_testing.metrics["repairs_successful"] = 4
        
        # Add some test history
        self.self_testing.test_history = [{"timestamp": datetime.now().isoformat()} for _ in range(3)]
        self.self_testing.repair_history = [{"timestamp": datetime.now().isoformat()} for _ in range(2)]
        
        # Get metrics
        metrics = self.self_testing.get_metrics()
        
        # Check metrics
        self.assertEqual(metrics["tests_run"], 10)
        self.assertEqual(metrics["tests_passed"], 8)
        self.assertEqual(metrics["tests_failed"], 2)
        self.assertEqual(metrics["test_success_rate"], 0.8)
        self.assertEqual(metrics["repairs_attempted"], 5)
        self.assertEqual(metrics["repairs_successful"], 4)
        self.assertEqual(metrics["repair_success_rate"], 0.8)
        self.assertEqual(metrics["test_history_count"], 3)
        self.assertEqual(metrics["repair_history_count"], 2)

if __name__ == "__main__":
    unittest.main()
