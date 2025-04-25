"""
Tests for the WebSocket-enhanced self-testing framework.
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import json

from memory.websocket_self_testing import WebSocketEnhancedSelfTesting

class TestWebSocketEnhancedSelfTesting(unittest.TestCase):
    """Test WebSocket-enhanced self-testing functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create mock memory manager
        self.memory_manager = MagicMock()
        self.memory_manager.long_term = MagicMock()
        self.memory_manager.long_term.metadata = {
            "memories": {}
        }
        self.memory_manager.long_term._save_metadata = MagicMock()
        
        # Create mock WebSocket server
        self.ws = MagicMock()
        self.ws.emit_event = MagicMock()
        
        # Create test config
        self.config = {
            "memory": {
                "self_test_interval": 12,
                "self_test_batch_size": 5,
                "repair_threshold": 0.7
            }
        }
        
        # Create self-testing framework
        self.self_testing = WebSocketEnhancedSelfTesting(
            memory_manager=self.memory_manager,
            config=self.config,
            websocket_server=self.ws
        )
        
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
        """Test running a consistency check with WebSocket events."""
        # Run consistency check
        results = self.self_testing.run_consistency_check(["memory1", "memory2", "memory3"])
        
        # Check that WebSocket event was emitted
        self.ws.emit_event.assert_called_with(
            "memory_consistency_check",
            {
                "status": "completed",
                "memories_checked": 3,
                "inconsistencies_found": 1,  # memory3 is missing
                "repairs_attempted": 1,
                "repairs_successful": 1,
                "timestamp": unittest.mock.ANY
            }
        )

    def test_repair_inconsistencies(self):
        """Test repairing inconsistencies with WebSocket events."""
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
        
        # Check that WebSocket event was emitted
        self.ws.emit_event.assert_called_with(
            "memory_repairs",
            {
                "repairs_attempted": 2,
                "repairs_successful": unittest.mock.ANY,
                "repair_types": {
                    "missing": 1,
                    "importance_mismatch": 1
                },
                "timestamp": unittest.mock.ANY
            }
        )

    def test_test_memory_retrieval(self):
        """Test memory retrieval testing with WebSocket events."""
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
        
        # Check that WebSocket event was emitted
        self.ws.emit_event.assert_called_with(
            "memory_retrieval_test",
            {
                "query": "test query",
                "expected_count": 2,
                "retrieved_count": 2,
                "precision": 0.5,
                "recall": 0.5,
                "f1_score": 0.5,
                "timestamp": unittest.mock.ANY
            }
        )

    def test_run_retrieval_test_suite(self):
        """Test running a retrieval test suite with WebSocket events."""
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
        
        # Check that WebSocket event was emitted
        self.ws.emit_event.assert_called_with(
            "memory_test_suite",
            {
                "tests_run": 4,
                "average_precision": 1.0,
                "average_recall": 1.0,
                "average_f1": 1.0,
                "timestamp": unittest.mock.ANY
            }
        )

    def test_get_metrics(self):
        """Test getting metrics with WebSocket events."""
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
        
        # Check that WebSocket event was emitted
        self.ws.emit_event.assert_called_with(
            "memory_self_testing_metrics",
            {
                "metrics": metrics,
                "timestamp": unittest.mock.ANY
            }
        )

if __name__ == "__main__":
    unittest.main()
