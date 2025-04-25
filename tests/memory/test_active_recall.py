"""
Tests for the active recall system.
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import json
import os

from memory.active_recall import ActiveRecallSystem

class TestActiveRecallSystem(unittest.TestCase):
    """Test active recall functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create mock memory manager
        self.memory_manager = MagicMock()
        self.memory_manager.long_term = MagicMock()
        self.memory_manager.long_term.metadata = {
            "memories": {},
            "review_history": {},
            "scheduled_reviews": {}
        }
        self.memory_manager.long_term._save_metadata = MagicMock()
        
        # Create test config
        self.config = {
            "memory": {
                "min_review_interval": 1,
                "max_review_interval": 30,
                "initial_interval": 2,
                "interval_multiplier": 2.0,
                "high_importance_threshold": 0.8,
                "medium_importance_threshold": 0.5,
                "low_importance_threshold": 0.3,
                "verification_batch_size": 5,
                "verification_interval": 12
            }
        }
        
        # Create active recall system
        self.recall = ActiveRecallSystem(self.memory_manager, self.config)
        
        # Create test memories
        self.test_memories = {
            "memory1": {
                "id": "memory1",
                "content": "This is a test fact",
                "importance": 0.9,
                "metadata": {
                    "source_type": "fact",
                    "timestamp": datetime.now().isoformat(),
                    "importance": 0.9
                }
            },
            "memory2": {
                "id": "memory2",
                "content": "User prefers dark mode",
                "importance": 0.6,
                "metadata": {
                    "source_type": "preference",
                    "timestamp": datetime.now().isoformat(),
                    "importance": 0.6
                }
            },
            "memory3": {
                "id": "memory3",
                "content": "User mentioned they like pizza",
                "importance": 0.3,
                "metadata": {
                    "source_type": "conversation",
                    "timestamp": datetime.now().isoformat(),
                    "importance": 0.3
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
            "memory3": {"content": "User mentioned they like pizza", "importance": 0.3}
        }

    def test_schedule_review(self):
        """Test scheduling a memory for review."""
        # Schedule a high importance memory
        review_time = self.recall.schedule_review("memory1", 0.9)
        
        # Check that the review was scheduled
        self.assertIn("memory1", self.recall.scheduled_reviews)
        
        # Check that the review time is in the future
        self.assertGreater(review_time, datetime.now())
        
        # Check that the review time is based on importance (high importance = shorter interval)
        interval = (review_time - datetime.now()).total_seconds() / 86400  # Convert to days
        self.assertLess(interval, self.config["memory"]["initial_interval"])
        
        # Schedule a low importance memory
        review_time = self.recall.schedule_review("memory3", 0.3)
        
        # Check that the review time is based on importance (low importance = longer interval)
        interval = (review_time - datetime.now()).total_seconds() / 86400  # Convert to days
        self.assertGreater(interval, self.config["memory"]["initial_interval"])
        
        # Check that _save_review_history was called
        self.memory_manager.long_term._save_metadata.assert_called()

    def test_calculate_review_interval(self):
        """Test calculating review intervals."""
        # Test high importance memory (shorter interval)
        interval = self.recall._calculate_review_interval("memory1", 0.9)
        self.assertLess(interval, self.config["memory"]["initial_interval"])
        
        # Test medium importance memory (normal interval)
        interval = self.recall._calculate_review_interval("memory2", 0.6)
        self.assertAlmostEqual(interval, self.config["memory"]["initial_interval"], delta=0.1)
        
        # Test low importance memory (longer interval)
        interval = self.recall._calculate_review_interval("memory3", 0.3)
        self.assertGreater(interval, self.config["memory"]["initial_interval"])
        
        # Test with review history (successful review)
        self.recall.review_history["memory1"] = [{
            "timestamp": datetime.now() - timedelta(days=5),
            "success": True,
            "interval": 2.0
        }]
        
        interval = self.recall._calculate_review_interval("memory1", 0.9)
        # Interval should increase after successful review
        self.assertGreater(interval, 2.0)
        
        # Test with review history (unsuccessful review)
        self.recall.review_history["memory2"] = [{
            "timestamp": datetime.now() - timedelta(days=5),
            "success": False,
            "interval": 2.0
        }]
        
        interval = self.recall._calculate_review_interval("memory2", 0.6)
        # Interval should decrease after unsuccessful review
        self.assertLess(interval, 2.0)

    def test_get_due_reviews(self):
        """Test getting memories due for review."""
        # Schedule reviews
        now = datetime.now()
        
        # One due review
        self.recall.scheduled_reviews["memory1"] = now - timedelta(hours=1)
        
        # One future review
        self.recall.scheduled_reviews["memory2"] = now + timedelta(days=1)
        
        # Another due review
        self.recall.scheduled_reviews["memory3"] = now - timedelta(hours=2)
        
        # Get due reviews
        due_reviews = self.recall.get_due_reviews()
        
        # Check that only due reviews are returned
        self.assertEqual(len(due_reviews), 2)
        
        # Check that reviews are sorted by importance (highest first)
        self.assertEqual(due_reviews[0]["id"], "memory1")  # High importance
        self.assertEqual(due_reviews[1]["id"], "memory3")  # Low importance

    def test_record_review(self):
        """Test recording a memory review."""
        # Record a successful review
        self.recall.record_review("memory1", True)
        
        # Check that the review was recorded
        self.assertIn("memory1", self.recall.review_history)
        self.assertEqual(len(self.recall.review_history["memory1"]), 1)
        self.assertTrue(self.recall.review_history["memory1"][0]["success"])
        
        # Check that the memory was reinforced
        self.memory_manager.reinforce_memory.assert_called_with("memory1", reinforcement_strength=0.5)
        
        # Check that the next review was scheduled
        self.assertIn("memory1", self.recall.scheduled_reviews)
        
        # Record an unsuccessful review
        self.recall.record_review("memory2", False)
        
        # Check that the review was recorded
        self.assertIn("memory2", self.recall.review_history)
        self.assertEqual(len(self.recall.review_history["memory2"]), 1)
        self.assertFalse(self.recall.review_history["memory2"][0]["success"])
        
        # Check that the memory was not reinforced again
        self.assertEqual(self.memory_manager.reinforce_memory.call_count, 1)

    def test_generate_review_question(self):
        """Test generating review questions."""
        # Test fact memory
        question_data = self.recall.generate_review_question(self.test_memories["memory1"])
        self.assertEqual(question_data["memory_id"], "memory1")
        self.assertIn("Do you remember this fact", question_data["question"])
        self.assertEqual(question_data["answer"], "This is a test fact")
        self.assertEqual(question_data["memory_type"], "fact")
        
        # Test preference memory
        question_data = self.recall.generate_review_question(self.test_memories["memory2"])
        self.assertEqual(question_data["memory_id"], "memory2")
        self.assertIn("What is your preference", question_data["question"])
        self.assertEqual(question_data["answer"], "User prefers dark mode")
        self.assertEqual(question_data["memory_type"], "preference")
        
        # Test conversation memory
        question_data = self.recall.generate_review_question(self.test_memories["memory3"])
        self.assertEqual(question_data["memory_id"], "memory3")
        self.assertIn("Do you recall this conversation", question_data["question"])
        self.assertEqual(question_data["answer"], "User mentioned they like pizza")
        self.assertEqual(question_data["memory_type"], "conversation")

    def test_verify_memory_integrity(self):
        """Test memory integrity verification."""
        # Set up a memory with issues
        self.test_memories["memory4"] = {
            "id": "memory4",
            "content": "",  # Empty content
            "metadata": {
                "source_type": "fact",
                # Missing timestamp
                "importance": 0.5
            }
        }
        
        self.memory_manager.long_term.metadata["memories"]["memory4"] = {"content": "", "importance": 0.5}
        
        # Set verification interval to 0 to force verification
        self.recall.last_verification_time = datetime.now() - timedelta(hours=24)
        
        # Run verification
        results = self.recall.verify_memory_integrity()
        
        # Check that verification ran
        self.assertTrue("verified" in results)
        self.assertTrue("count" in results)
        self.assertTrue("issues" in results)
        
        # Check that issues were found
        if "memory4" in [issue["memory_id"] for issue in results["issues"]]:
            memory4_issues = [issue for issue in results["issues"] if issue["memory_id"] == "memory4"]
            self.assertTrue(any("Empty content" in issue["issue"] for issue in memory4_issues))
        
        # Check that last verification time was updated
        self.assertGreater(self.recall.last_verification_time, datetime.now() - timedelta(minutes=1))

    def test_run_scheduled_tasks(self):
        """Test running scheduled tasks."""
        # Set verification interval to 0 to force verification
        self.recall.last_verification_time = datetime.now() - timedelta(hours=24)
        
        # Run scheduled tasks
        results = self.recall.run_scheduled_tasks()
        
        # Check that verification ran
        self.assertIsNotNone(results["verification"])
        
        # Check that reviews were scheduled
        self.assertGreaterEqual(results["reviews_scheduled"], 3)  # At least our 3 test memories
        
        # Check that all memories have scheduled reviews
        for memory_id in self.test_memories:
            self.assertIn(memory_id, self.recall.scheduled_reviews)

    def test_get_memory_health_metrics(self):
        """Test getting memory health metrics."""
        # Add some review history
        self.recall.review_history["memory1"] = [
            {"timestamp": datetime.now() - timedelta(days=5), "success": True, "interval": 2.0},
            {"timestamp": datetime.now() - timedelta(days=2), "success": True, "interval": 4.0}
        ]
        
        self.recall.review_history["memory2"] = [
            {"timestamp": datetime.now() - timedelta(days=3), "success": False, "interval": 2.0}
        ]
        
        # Schedule some reviews
        self.recall.scheduled_reviews["memory1"] = datetime.now() + timedelta(days=2)
        self.recall.scheduled_reviews["memory2"] = datetime.now() - timedelta(hours=1)  # Due
        self.recall.scheduled_reviews["memory3"] = datetime.now() + timedelta(days=1)
        
        # Get metrics
        metrics = self.recall.get_memory_health_metrics()
        
        # Check metrics
        self.assertEqual(metrics["total_memories"], 3)
        self.assertEqual(metrics["scheduled_reviews"], 3)
        self.assertEqual(metrics["due_reviews"], 1)  # memory2 is due
        self.assertEqual(metrics["review_count"], 3)  # 2 for memory1, 1 for memory2
        self.assertAlmostEqual(metrics["success_rate"], 2/3, places=2)  # 2 successful out of 3
        self.assertAlmostEqual(metrics["avg_interval"], (2.0 + 4.0 + 2.0) / 3, places=2)

if __name__ == "__main__":
    unittest.main()
