"""
Tests for the memory snapshot functionality.
"""

import os
import json
import unittest
import tempfile
import shutil
from datetime import datetime
from unittest.mock import MagicMock, patch

from memory import EnhancedMemoryManager, MemorySnapshotManager
from memory.short_term import MemoryManager as ShortTermMemory
from memory.long_term import LongTermMemory

class TestMemorySnapshot(unittest.TestCase):
    """Test memory snapshot functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.snapshot_dir = os.path.join(self.test_dir, "snapshots")
        os.makedirs(self.snapshot_dir, exist_ok=True)
        
        # Create a test config
        self.config = {
            "memory": {
                "max_turns": 10,
                "long_term_path": os.path.join(self.test_dir, "long_term"),
                "vector_db": "in_memory",
                "snapshot_dir": self.snapshot_dir,
                "auto_snapshot": False,
                "snapshot_interval": 5
            }
        }
        
        # Create memory manager
        self.memory = EnhancedMemoryManager(config=self.config)
        
        # Add some test data
        self.memory.add_turn("system", "You are Coda.")
        self.memory.add_turn("user", "Hello, who are you?")
        self.memory.add_turn("assistant", "I'm Coda, your voice assistant. How can I help you today?")
        self.memory.add_fact("The user's name is Alice.")
        self.memory.add_preference("The user prefers brief responses.")

    def tearDown(self):
        """Clean up after tests."""
        # Close memory manager
        self.memory.close()
        
        # Remove temporary directory
        shutil.rmtree(self.test_dir)

    def test_create_snapshot(self):
        """Test creating a memory snapshot."""
        # Create a snapshot
        snapshot_id = self.memory.create_snapshot()
        
        # Check that the snapshot exists
        self.assertIn(snapshot_id, self.memory.snapshot_manager.snapshots)
        
        # Check snapshot content
        snapshot = self.memory.snapshot_manager.snapshots[snapshot_id]
        self.assertEqual(snapshot["snapshot_id"], snapshot_id)
        self.assertIn("timestamp", snapshot)
        self.assertIn("short_term", snapshot)
        self.assertIn("long_term", snapshot)
        self.assertIn("memory_stats", snapshot)
        
        # Check short-term memory content
        self.assertEqual(len(snapshot["short_term"]["turns"]), 3)
        self.assertEqual(snapshot["short_term"]["turn_count"], 3)
        
        # Check long-term memory content
        self.assertGreaterEqual(snapshot["long_term"]["memory_count"], 2)

    def test_save_and_load_snapshot(self):
        """Test saving and loading a memory snapshot."""
        # Create a snapshot
        snapshot_id = self.memory.create_snapshot()
        
        # Save the snapshot
        filepath = self.memory.save_snapshot(snapshot_id)
        
        # Check that the file exists
        self.assertTrue(os.path.exists(filepath))
        
        # Create a new memory manager
        new_memory = EnhancedMemoryManager(config=self.config)
        
        # Load the snapshot
        loaded_id = new_memory.load_snapshot(filepath)
        
        # Check that the loaded snapshot exists
        self.assertIn(loaded_id, new_memory.snapshot_manager.snapshots)
        
        # Check that the loaded snapshot has the same content
        original = self.memory.snapshot_manager.snapshots[snapshot_id]
        loaded = new_memory.snapshot_manager.snapshots[loaded_id]
        
        self.assertEqual(original["snapshot_id"], loaded["snapshot_id"])
        self.assertEqual(len(original["short_term"]["turns"]), len(loaded["short_term"]["turns"]))
        self.assertEqual(original["short_term"]["turn_count"], loaded["short_term"]["turn_count"])
        self.assertEqual(original["long_term"]["memory_count"], loaded["long_term"]["memory_count"])
        
        # Clean up
        new_memory.close()

    def test_apply_snapshot(self):
        """Test applying a memory snapshot."""
        # Create initial state
        self.memory.add_turn("user", "What's the weather today?")
        self.memory.add_turn("assistant", "I don't have access to real-time weather information.")
        
        # Create a snapshot of the initial state
        snapshot_id = self.memory.create_snapshot()
        
        # Modify the memory
        self.memory.add_turn("user", "Tell me a joke.")
        self.memory.add_turn("assistant", "Why did the chicken cross the road? To get to the other side!")
        self.memory.add_fact("The user likes jokes.")
        
        # Check that the memory has changed
        self.assertEqual(self.memory.short_term.get_turn_count(), 7)
        
        # Apply the snapshot
        result = self.memory.apply_snapshot(snapshot_id)
        
        # Check that the snapshot was applied successfully
        self.assertTrue(result)
        
        # Check that the memory has been restored to the initial state
        self.assertEqual(self.memory.short_term.get_turn_count(), 5)
        
        # Check the content of the last turn
        last_turn = list(self.memory.short_term.turns)[-1]
        self.assertEqual(last_turn["role"], "assistant")
        self.assertEqual(last_turn["content"], "I don't have access to real-time weather information.")

    def test_auto_snapshot(self):
        """Test automatic snapshots."""
        # Enable auto-snapshot
        self.memory.enable_auto_snapshot(interval=2)
        
        # Add turns to trigger auto-snapshot
        self.memory.add_turn("user", "What's your favorite color?")
        self.memory.add_turn("assistant", "I don't have preferences, but I can help you with yours!")
        
        # Check that a snapshot was created
        self.assertGreaterEqual(len(self.memory.snapshot_manager.snapshots), 1)
        
        # Add more turns to trigger another auto-snapshot
        self.memory.add_turn("user", "Tell me about yourself.")
        self.memory.add_turn("assistant", "I'm Coda, your voice assistant.")
        
        # Check that another snapshot was created
        self.assertGreaterEqual(len(self.memory.snapshot_manager.snapshots), 2)

    def test_list_snapshots(self):
        """Test listing snapshots."""
        # Create multiple snapshots
        self.memory.create_snapshot("snapshot1")
        self.memory.create_snapshot("snapshot2")
        self.memory.create_snapshot("snapshot3")
        
        # List snapshots
        snapshots = self.memory.list_snapshots()
        
        # Check that all snapshots are listed
        self.assertEqual(len(snapshots), 3)
        
        # Check that the snapshots have the expected IDs
        snapshot_ids = [s["snapshot_id"] for s in snapshots]
        self.assertIn("snapshot1", snapshot_ids)
        self.assertIn("snapshot2", snapshot_ids)
        self.assertIn("snapshot3", snapshot_ids)

    def test_snapshot_metadata(self):
        """Test snapshot metadata."""
        # Create a snapshot
        snapshot_id = self.memory.create_snapshot()
        
        # Get snapshot metadata
        metadata = self.memory.snapshot_manager.get_snapshot_metadata(snapshot_id)
        
        # Check metadata content
        self.assertEqual(metadata["snapshot_id"], snapshot_id)
        self.assertIn("timestamp", metadata)
        self.assertEqual(metadata["short_term_turns"], 3)
        self.assertGreaterEqual(metadata["long_term_memories"], 2)

    def test_final_snapshot_on_close(self):
        """Test that a final snapshot is created when closing with auto-snapshot enabled."""
        # Enable auto-snapshot
        self.memory.enable_auto_snapshot()
        
        # Close the memory manager
        self.memory.close()
        
        # Check that a final snapshot was created
        final_snapshots = [s for s in self.memory.snapshot_manager.snapshots.keys() if "final_snapshot" in s]
        self.assertEqual(len(final_snapshots), 1)

if __name__ == "__main__":
    unittest.main()
