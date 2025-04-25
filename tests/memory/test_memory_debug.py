"""
Tests for the memory debug system.
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from memory.memory_debug import MemoryDebugSystem

class TestMemoryDebug(unittest.TestCase):
    """Test memory debug functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create mock memory manager
        self.memory_manager = MagicMock()
        self.memory_manager.long_term = MagicMock()
        self.memory_manager.get_memory_stats.return_value = {
            "short_term": {"turn_count": 5},
            "long_term": {"memory_count": 10}
        }

        # Create mock WebSocket integration
        self.ws = MagicMock()

        # Create memory debug system
        self.debug = MemoryDebugSystem(
            memory_manager=self.memory_manager,
            websocket_integration=self.ws
        )

    def test_log_operation(self):
        """Test logging a memory operation."""
        # Log an operation
        self.debug.log_operation(
            operation_type="test_operation",
            details={"test_key": "test_value"}
        )

        # Check that the operation was logged
        self.assertEqual(len(self.debug.operations_log), 1)
        self.assertEqual(self.debug.operations_log[0]["operation_type"], "test_operation")
        self.assertEqual(self.debug.operations_log[0]["details"]["test_key"], "test_value")

        # Check that the WebSocket event was emitted
        self.ws.memory_debug_operation.assert_called_once()
        args, kwargs = self.ws.memory_debug_operation.call_args
        self.assertEqual(kwargs["operation_type"], "test_operation")
        self.assertEqual(kwargs["details"]["test_key"], "test_value")

    def test_get_operations_log(self):
        """Test getting the operations log."""
        # Log multiple operations
        self.debug.log_operation("operation1", {"key1": "value1"})
        self.debug.log_operation("operation2", {"key2": "value2"})
        self.debug.log_operation("operation1", {"key3": "value3"})

        # Get all operations
        all_ops = self.debug.get_operations_log()
        self.assertEqual(len(all_ops), 3)

        # Get operations of a specific type
        type_ops = self.debug.get_operations_log(operation_type="operation1")
        self.assertEqual(len(type_ops), 2)
        self.assertEqual(type_ops[0]["operation_type"], "operation1")
        self.assertEqual(type_ops[1]["operation_type"], "operation1")

        # Get operations with a limit
        limited_ops = self.debug.get_operations_log(limit=2)
        self.assertEqual(len(limited_ops), 2)
        # The most recent operations are returned, so the order is reversed
        self.assertEqual(limited_ops[0]["operation_type"], "operation2")
        self.assertEqual(limited_ops[1]["operation_type"], "operation1")

    def test_get_memory_stats(self):
        """Test getting memory statistics."""
        # Get memory stats
        stats = self.debug.get_memory_stats()

        # Check that the stats were retrieved
        self.assertEqual(stats["short_term"]["turn_count"], 5)
        self.assertEqual(stats["long_term"]["memory_count"], 10)
        self.assertIn("debug", stats)
        self.assertIn("operations_count", stats["debug"])
        self.assertIn("operations_by_type", stats["debug"])
        self.assertIn("last_update", stats["debug"])

        # Check that the WebSocket event was emitted
        self.ws.memory_debug_stats.assert_called_once()
        args, kwargs = self.ws.memory_debug_stats.call_args
        self.assertEqual(args[0], stats)

    def test_search_memories(self):
        """Test searching for memories."""
        # Set up mock memory manager
        self.memory_manager.search_memories.return_value = [
            {"id": "memory1", "content": "Test memory 1", "importance": 0.8},
            {"id": "memory2", "content": "Test memory 2", "importance": 0.5}
        ]

        # Mock the log_operation method to avoid side effects
        original_log_operation = self.debug.log_operation
        self.debug.log_operation = MagicMock()

        try:
            # Search for memories
            results = self.debug.search_memories(
                query="test query",
                memory_type="fact",
                min_importance=0.5,
                max_results=20
            )

            # Check that the search was performed
            self.memory_manager.search_memories.assert_called_once()

            # Check that the operation was logged
            self.debug.log_operation.assert_called_once()
            call_args = self.debug.log_operation.call_args
            self.assertEqual(call_args[1]["operation_type"], "search")
            self.assertEqual(call_args[1]["details"]["query"], "test query")

        finally:
            # Restore the original method
            self.debug.log_operation = original_log_operation

    def test_get_memory_by_id(self):
        """Test getting a memory by ID."""
        # Set up mock memory manager
        self.memory_manager.long_term.get_memory_by_id.return_value = {
            "id": "memory1",
            "content": "Test memory 1",
            "importance": 0.8
        }

        # Get a memory by ID
        memory = self.debug.get_memory_by_id("memory1")

        # Check that the memory was retrieved
        self.memory_manager.long_term.get_memory_by_id.assert_called_once_with("memory1")

        # Check that the memory was returned
        self.assertEqual(memory["id"], "memory1")
        self.assertEqual(memory["content"], "Test memory 1")

        # Check that the operation was logged
        self.assertEqual(len(self.debug.operations_log), 1)
        self.assertEqual(self.debug.operations_log[0]["operation_type"], "get")
        self.assertEqual(self.debug.operations_log[0]["details"]["memory_id"], "memory1")
        self.assertEqual(self.debug.operations_log[0]["details"]["found"], True)

    def test_update_memory_importance(self):
        """Test updating a memory's importance."""
        # Set up mock memory manager
        self.memory_manager.long_term.get_memory_by_id.return_value = {
            "id": "memory1",
            "content": "Test memory 1",
            "importance": 0.5
        }
        self.memory_manager.update_memory.return_value = True

        # Update a memory's importance
        result = self.debug.update_memory_importance("memory1", 0.8)

        # Check that the memory was updated
        self.memory_manager.update_memory.assert_called_once_with(
            memory_id="memory1",
            importance=0.8
        )

        # Check that the result was returned
        self.assertTrue(result)

        # Check that the operation was logged
        self.assertEqual(len(self.debug.operations_log), 1)
        self.assertEqual(self.debug.operations_log[0]["operation_type"], "update_importance")
        self.assertEqual(self.debug.operations_log[0]["details"]["memory_id"], "memory1")
        self.assertEqual(self.debug.operations_log[0]["details"]["old_importance"], 0.5)
        self.assertEqual(self.debug.operations_log[0]["details"]["new_importance"], 0.8)
        self.assertEqual(self.debug.operations_log[0]["details"]["success"], True)

    def test_reinforce_memory(self):
        """Test reinforcing a memory."""
        # Set up mock memory manager
        self.memory_manager.long_term.get_memory_by_id.return_value = {
            "id": "memory1",
            "content": "Test memory 1",
            "importance": 0.5
        }
        self.memory_manager.reinforce_memory.return_value = True

        # Reinforce a memory
        result = self.debug.reinforce_memory("memory1", 0.8)

        # Check that the memory was reinforced
        self.memory_manager.reinforce_memory.assert_called_once_with(
            memory_id="memory1",
            reinforcement_strength=0.8
        )

        # Check that the result was returned
        self.assertTrue(result)

        # Check that the operation was logged
        self.assertEqual(len(self.debug.operations_log), 1)
        self.assertEqual(self.debug.operations_log[0]["operation_type"], "reinforce")
        self.assertEqual(self.debug.operations_log[0]["details"]["memory_id"], "memory1")
        self.assertEqual(self.debug.operations_log[0]["details"]["strength"], 0.8)
        self.assertEqual(self.debug.operations_log[0]["details"]["success"], True)

    def test_forget_memory(self):
        """Test forgetting a memory."""
        # Set up mock memory manager
        self.memory_manager.long_term.get_memory_by_id.return_value = {
            "id": "memory1",
            "content": "Test memory 1",
            "importance": 0.5
        }
        self.memory_manager.long_term.delete_memory.return_value = True

        # Forget a memory
        result = self.debug.forget_memory("memory1")

        # Check that the memory was forgotten
        self.memory_manager.long_term.delete_memory.assert_called_once_with("memory1")

        # Check that the result was returned
        self.assertTrue(result)

        # Check that the operation was logged
        self.assertEqual(len(self.debug.operations_log), 1)
        self.assertEqual(self.debug.operations_log[0]["operation_type"], "forget")
        self.assertEqual(self.debug.operations_log[0]["details"]["memory_id"], "memory1")
        self.assertEqual(self.debug.operations_log[0]["details"]["success"], True)

    def test_apply_forgetting_mechanism(self):
        """Test applying the forgetting mechanism."""
        # Set up mock memory manager
        self.memory_manager.forget_memories.return_value = 5

        # Apply forgetting mechanism
        result = self.debug.apply_forgetting_mechanism(max_memories=100)

        # Check that the forgetting mechanism was applied
        self.memory_manager.forget_memories.assert_called_once_with(100)

        # Check that the result was returned
        self.assertEqual(result, 5)

        # Check that the operation was logged
        self.assertEqual(len(self.debug.operations_log), 1)
        self.assertEqual(self.debug.operations_log[0]["operation_type"], "apply_forgetting")
        self.assertEqual(self.debug.operations_log[0]["details"]["max_memories"], 100)
        self.assertEqual(self.debug.operations_log[0]["details"]["forgotten_count"], 5)

    def test_create_memory_snapshot(self):
        """Test creating a memory snapshot."""
        # Set up mock memory manager
        self.memory_manager.create_snapshot.return_value = "snapshot1"

        # Create a memory snapshot
        result = self.debug.create_memory_snapshot()

        # Check that the snapshot was created
        self.memory_manager.create_snapshot.assert_called_once_with(None)

        # Check that the result was returned
        self.assertEqual(result, "snapshot1")

        # Check that the operation was logged
        self.assertEqual(len(self.debug.operations_log), 1)
        self.assertEqual(self.debug.operations_log[0]["operation_type"], "create_snapshot")
        self.assertEqual(self.debug.operations_log[0]["details"]["snapshot_id"], "snapshot1")

    def test_apply_memory_snapshot(self):
        """Test applying a memory snapshot."""
        # Set up mock memory manager
        self.memory_manager.apply_snapshot.return_value = True

        # Apply a memory snapshot
        result = self.debug.apply_memory_snapshot("snapshot1")

        # Check that the snapshot was applied
        self.memory_manager.apply_snapshot.assert_called_once_with("snapshot1")

        # Check that the result was returned
        self.assertTrue(result)

        # Check that the operation was logged
        self.assertEqual(len(self.debug.operations_log), 1)
        self.assertEqual(self.debug.operations_log[0]["operation_type"], "apply_snapshot")
        self.assertEqual(self.debug.operations_log[0]["details"]["snapshot_id"], "snapshot1")
        self.assertEqual(self.debug.operations_log[0]["details"]["success"], True)

if __name__ == "__main__":
    unittest.main()
