"""
Tests for the WebSocket-enhanced active recall system.
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import json

from memory.websocket_active_recall import WebSocketEnhancedActiveRecall

class TestWebSocketEnhancedActiveRecall(unittest.TestCase):
    """Test WebSocket-enhanced active recall functionality."""

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
        
        # Create mock WebSocket server
        self.ws = MagicMock()
        self.ws.emit_event = MagicMock()
        
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
        self.recall = WebSocketEnhancedActiveRecall(
            memory_manager=self.memory_manager,
            config=self.config,
            websocket_server=self.ws
        )
        
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
            }
        }
        
        # Set up memory manager to return test memories
        def get_memory_by_id(memory_id):
            return self.test_memories.get(memory_id)
        
        self.memory_manager.long_term.get_memory_by_id.side_effect = get_memory_by_id
        
        # Add test memories to metadata
        self.memory_manager.long_term.metadata["memories"] = {
            "memory1": {"content": "This is a test fact", "importance": 0.9},
            "memory2": {"content": "User prefers dark mode", "importance": 0.6}
        }

    def test_schedule_review(self):
        """Test scheduling a memory for review with WebSocket events."""
        # Schedule a review
        self.recall.schedule_review("memory1", 0.9)
        
        # Check that WebSocket event was emitted
        self.ws.emit_event.assert_called_with(
            "memory_review_scheduled",
            {
                "memory_id": "memory1",
                "importance": 0.9,
                "next_review": self.recall.scheduled_reviews["memory1"].isoformat(),
                "content_preview": "This is a test fact",
                "memory_type": "fact",
                "timestamp": unittest.mock.ANY
            }
        )

    def test_get_due_reviews(self):
        """Test getting memories due for review with WebSocket events."""
        # Schedule reviews
        now = datetime.now()
        
        # One due review
        self.recall.scheduled_reviews["memory1"] = now - timedelta(hours=1)
        
        # One future review
        self.recall.scheduled_reviews["memory2"] = now + timedelta(days=1)
        
        # Get due reviews
        due_reviews = self.recall.get_due_reviews()
        
        # Check that WebSocket event was emitted
        self.ws.emit_event.assert_called_with(
            "memory_reviews_due",
            {
                "count": 1,
                "memories": [
                    {
                        "memory_id": "memory1",
                        "content_preview": "This is a test fact",
                        "memory_type": "fact",
                        "importance": 0.9
                    }
                ],
                "timestamp": unittest.mock.ANY
            }
        )

    def test_record_review(self):
        """Test recording a memory review result with WebSocket events."""
        # Record a review
        self.recall.record_review("memory1", True)
        
        # Check that WebSocket event was emitted
        self.ws.emit_event.assert_called_with(
            "memory_review_recorded",
            {
                "memory_id": "memory1",
                "success": True,
                "content_preview": "This is a test fact",
                "memory_type": "fact",
                "importance": 0.9,
                "timestamp": unittest.mock.ANY
            }
        )
        
        # Check that memory was reinforced
        self.memory_manager.reinforce_memory.assert_called_with("memory1", reinforcement_strength=0.5)

    def test_run_scheduled_tasks(self):
        """Test running scheduled tasks with WebSocket events."""
        # Run scheduled tasks
        results = self.recall.run_scheduled_tasks()
        
        # Check that WebSocket event was emitted
        self.ws.emit_event.assert_called_with(
            "memory_maintenance_completed",
            {
                "active_recall": {
                    "reviews_scheduled": results.get("reviews_scheduled", 0),
                    "verification": results.get("verification", {}).get("verified", False)
                },
                "timestamp": unittest.mock.ANY
            }
        )

    def test_get_memory_health_metrics(self):
        """Test getting memory health metrics with WebSocket events."""
        # Get metrics
        metrics = self.recall.get_memory_health_metrics()
        
        # Check that WebSocket event was emitted
        self.ws.emit_event.assert_called_with(
            "memory_health_metrics",
            {
                "metrics": metrics,
                "timestamp": unittest.mock.ANY
            }
        )

if __name__ == "__main__":
    unittest.main()
