"""
Tests for the temporal weighting system.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from memory.temporal_weighting import TemporalWeightingSystem

class TestTemporalWeighting(unittest.TestCase):
    """Test temporal weighting functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create a test config
        self.config = {
            "memory": {
                "default_decay_rate": 30.0,
                "conversation_decay_rate": 15.0,
                "fact_decay_rate": 60.0,
                "preference_decay_rate": 90.0,
                "feedback_decay_rate": 45.0,
                "summary_decay_rate": 30.0,
                "recency_bias": 1.0,
                "importance_retention": 0.8,
                "reinforcement_boost": 0.2,
                "max_reinforcement_count": 5
            }
        }

        # Create temporal weighting system
        self.temporal_weighting = TemporalWeightingSystem(config=self.config)

    def test_calculate_decay_factor(self):
        """Test calculating decay factor based on age and type."""
        # Create timestamps for different ages
        now = datetime.now()
        one_day_ago = (now - timedelta(days=1)).isoformat()
        one_week_ago = (now - timedelta(days=7)).isoformat()
        one_month_ago = (now - timedelta(days=30)).isoformat()
        three_months_ago = (now - timedelta(days=90)).isoformat()

        # Test decay for different memory types
        # Conversation (15-day half-life)
        decay_conv_1d = self.temporal_weighting.calculate_decay_factor(one_day_ago, "conversation")
        decay_conv_7d = self.temporal_weighting.calculate_decay_factor(one_week_ago, "conversation")
        decay_conv_30d = self.temporal_weighting.calculate_decay_factor(one_month_ago, "conversation")

        # Fact (60-day half-life)
        decay_fact_1d = self.temporal_weighting.calculate_decay_factor(one_day_ago, "fact")
        decay_fact_30d = self.temporal_weighting.calculate_decay_factor(one_month_ago, "fact")
        decay_fact_90d = self.temporal_weighting.calculate_decay_factor(three_months_ago, "fact")

        # Preference (90-day half-life)
        decay_pref_1d = self.temporal_weighting.calculate_decay_factor(one_day_ago, "preference")
        decay_pref_30d = self.temporal_weighting.calculate_decay_factor(one_month_ago, "preference")
        decay_pref_90d = self.temporal_weighting.calculate_decay_factor(three_months_ago, "preference")

        # Verify decay factors
        # Conversations decay faster
        self.assertGreater(decay_conv_1d, 0.9)  # 1 day old, still very relevant
        self.assertLess(decay_conv_30d, 0.3)    # 30 days old, much less relevant

        # Facts decay slower
        self.assertGreater(decay_fact_1d, 0.95)  # 1 day old, still very relevant
        self.assertGreater(decay_fact_30d, 0.6)  # 30 days old, still somewhat relevant
        self.assertLess(decay_fact_90d, 0.4)     # 90 days old, less relevant

        # Preferences decay very slowly
        self.assertGreater(decay_pref_1d, 0.95)   # 1 day old, still very relevant
        self.assertGreater(decay_pref_30d, 0.75)  # 30 days old, still quite relevant
        self.assertGreater(decay_pref_90d, 0.45)  # 90 days old, still somewhat relevant

        # Verify that reinforcement affects decay
        decay_no_reinforce = self.temporal_weighting.calculate_decay_factor(one_month_ago, "conversation")
        decay_with_reinforce = self.temporal_weighting.calculate_decay_factor(one_month_ago, "conversation", 3)

        # Reinforced memory should decay slower
        self.assertGreater(decay_with_reinforce, decay_no_reinforce)

    def test_apply_temporal_weighting(self):
        """Test applying temporal weighting to a list of memories."""
        # Create test memories
        now = datetime.now()
        memories = [
            {
                "content": "This is a recent conversation",
                "timestamp": now.isoformat(),
                "importance": 0.5,
                "source_type": "conversation"
            },
            {
                "content": "This is an older conversation",
                "timestamp": (now - timedelta(days=20)).isoformat(),
                "importance": 0.8,
                "source_type": "conversation"
            },
            {
                "content": "This is a recent fact",
                "timestamp": (now - timedelta(days=2)).isoformat(),
                "importance": 0.7,
                "source_type": "fact"
            },
            {
                "content": "This is an older fact",
                "timestamp": (now - timedelta(days=45)).isoformat(),
                "importance": 0.9,
                "source_type": "fact"
            },
            {
                "content": "This is a preference",
                "timestamp": (now - timedelta(days=60)).isoformat(),
                "importance": 0.6,
                "source_type": "preference"
            }
        ]

        # Apply temporal weighting
        weighted_memories = self.temporal_weighting.apply_temporal_weighting(memories)

        # Verify that memories are sorted by final score
        self.assertEqual(len(weighted_memories), 5)
        for i in range(1, len(weighted_memories)):
            self.assertGreaterEqual(
                weighted_memories[i-1].get("final_score", 0),
                weighted_memories[i].get("final_score", 0)
            )

        # Verify that each memory has the expected fields
        for memory in weighted_memories:
            self.assertIn("decay_factor", memory)
            self.assertIn("importance_weight", memory)
            self.assertIn("recency_score", memory)
            self.assertIn("final_score", memory)

        # Test without recency boost
        weighted_no_recency = self.temporal_weighting.apply_temporal_weighting(memories, recency_boost=False)

        # Verify that recency scores are all 0.5
        for memory in weighted_no_recency:
            self.assertEqual(memory.get("recency_score"), 0.5)

    def test_calculate_forgetting_threshold(self):
        """Test calculating forgetting threshold."""
        # Test thresholds for different memory types and ages
        threshold_conv_10d = self.temporal_weighting.calculate_forgetting_threshold(10, "conversation", 0.5)
        threshold_conv_30d = self.temporal_weighting.calculate_forgetting_threshold(30, "conversation", 0.5)

        threshold_fact_10d = self.temporal_weighting.calculate_forgetting_threshold(10, "fact", 0.5)
        threshold_fact_60d = self.temporal_weighting.calculate_forgetting_threshold(60, "fact", 0.5)

        threshold_pref_10d = self.temporal_weighting.calculate_forgetting_threshold(10, "preference", 0.5)
        threshold_pref_90d = self.temporal_weighting.calculate_forgetting_threshold(90, "preference", 0.5)

        # Verify that thresholds increase with age
        self.assertLess(threshold_conv_10d, threshold_conv_30d)
        self.assertLess(threshold_fact_10d, threshold_fact_60d)
        self.assertLess(threshold_pref_10d, threshold_pref_90d)

        # Verify that different memory types have different base thresholds
        self.assertLess(threshold_fact_10d, threshold_conv_10d)  # Facts harder to forget than conversations
        self.assertLess(threshold_pref_10d, threshold_fact_10d)  # Preferences harder to forget than facts

        # Test importance effect
        threshold_high_importance = self.temporal_weighting.calculate_forgetting_threshold(30, "conversation", 0.9)
        threshold_low_importance = self.temporal_weighting.calculate_forgetting_threshold(30, "conversation", 0.1)

        # Higher importance should have lower threshold (harder to forget)
        self.assertLess(threshold_high_importance, threshold_low_importance)

    def test_should_forget_memory(self):
        """Test determining if a memory should be forgotten."""
        now = datetime.now()

        # Create test memories
        recent_memory = {
            "content": "This is a recent memory",
            "timestamp": (now - timedelta(days=5)).isoformat(),
            "importance": 0.7,
            "source_type": "conversation"
        }

        old_memory = {
            "content": "This is an old memory",
            "timestamp": (now - timedelta(days=60)).isoformat(),
            "importance": 0.3,
            "source_type": "conversation"
        }

        important_old_memory = {
            "content": "This is an important old memory",
            "timestamp": (now - timedelta(days=60)).isoformat(),
            "importance": 0.9,
            "source_type": "fact"
        }

        # Test with different memory pressure
        # Low pressure (50% capacity)
        self.assertFalse(self.temporal_weighting.should_forget_memory(recent_memory, 500, 1000))
        self.assertFalse(self.temporal_weighting.should_forget_memory(important_old_memory, 500, 1000))

        # Medium pressure (80% capacity)
        self.assertFalse(self.temporal_weighting.should_forget_memory(recent_memory, 800, 1000))
        self.assertFalse(self.temporal_weighting.should_forget_memory(important_old_memory, 800, 1000))

        # High pressure (95% capacity)
        self.assertFalse(self.temporal_weighting.should_forget_memory(recent_memory, 950, 1000))
        self.assertFalse(self.temporal_weighting.should_forget_memory(important_old_memory, 950, 1000))

        # Old unimportant memories should be forgotten under high pressure
        forget_old = self.temporal_weighting.should_forget_memory(old_memory, 950, 1000)
        self.assertTrue(forget_old)

    def test_reinforce_memory(self):
        """Test reinforcing a memory."""
        now = datetime.now()
        old_time = now - timedelta(days=30)

        # Create a test memory
        memory = {
            "content": "This is a memory to reinforce",
            "timestamp": old_time.isoformat(),
            "importance": 0.5,
            "source_type": "conversation",
            "reinforcement_count": 0
        }

        # Reinforce the memory
        reinforced = self.temporal_weighting.reinforce_memory(memory, 1.0)

        # Verify reinforcement effects
        self.assertEqual(reinforced.get("reinforcement_count"), 1)
        self.assertGreater(reinforced.get("importance"), 0.5)

        # Timestamp should be updated
        reinforced_time = datetime.fromisoformat(reinforced.get("timestamp"))
        self.assertGreater(reinforced_time, old_time)

        # Test partial reinforcement
        memory2 = memory.copy()
        memory2["timestamp"] = old_time.isoformat()
        partial = self.temporal_weighting.reinforce_memory(memory2, 0.5)

        # Verify partial reinforcement
        partial_time = datetime.fromisoformat(partial.get("timestamp"))
        self.assertGreater(partial_time, old_time)
        self.assertLess(partial_time, reinforced_time)  # Should be between old and fully reinforced

if __name__ == "__main__":
    unittest.main()
