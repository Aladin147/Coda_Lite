"""
Tests for the memory summarization system.
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import json
import os

from memory.summarization import MemorySummarizationSystem

class TestMemorySummarizationSystem(unittest.TestCase):
    """Test memory summarization functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create mock memory manager
        self.memory_manager = MagicMock()
        self.memory_manager.long_term = MagicMock()
        self.memory_manager.long_term.metadata = {
            "memories": {}
        }

        # Create test config
        self.config = {
            "memory": {
                "min_cluster_size": 2,
                "max_summary_length": 200,
                "summary_cache_ttl": 3600,
                "topic_similarity_threshold": 0.7,
                "max_topics_per_cluster": 3,
                "profile_update_interval": 86400
            }
        }

        # Create summarization system
        self.summarization = MemorySummarizationSystem(self.memory_manager, self.config)

        # Create test memories
        self.test_memories = {
            "memory1": {
                "id": "memory1",
                "content": "The user likes Japanese food, especially sushi and ramen.",
                "metadata": {
                    "source_type": "preference",
                    "timestamp": datetime.now().isoformat(),
                    "importance": 0.8,
                    "topics": "food,japan,preferences"
                }
            },
            "memory2": {
                "id": "memory2",
                "content": "The user is planning a trip to Japan next year.",
                "metadata": {
                    "source_type": "fact",
                    "timestamp": datetime.now().isoformat(),
                    "importance": 0.7,
                    "topics": "travel,japan,plans"
                }
            },
            "memory3": {
                "id": "memory3",
                "content": "The user mentioned they want to learn Japanese language.",
                "metadata": {
                    "source_type": "conversation",
                    "timestamp": datetime.now().isoformat(),
                    "importance": 0.6,
                    "topics": "language,japan,learning"
                }
            },
            "memory4": {
                "id": "memory4",
                "content": "The user's favorite food is pizza.",
                "metadata": {
                    "source_type": "preference",
                    "timestamp": datetime.now().isoformat(),
                    "importance": 0.7,
                    "topics": "food,preferences"
                }
            },
            "memory5": {
                "id": "memory5",
                "content": "The user is a software developer who works with Python.",
                "metadata": {
                    "source_type": "fact",
                    "timestamp": datetime.now().isoformat(),
                    "importance": 0.8,
                    "topics": "profession,software,python"
                }
            }
        }

        # Set up memory manager to return test memories
        def get_memory_by_id(memory_id):
            return self.test_memories.get(memory_id)

        self.memory_manager.long_term.get_memory_by_id.side_effect = get_memory_by_id

        # Add test memories to metadata
        self.memory_manager.long_term.metadata["memories"] = {
            "memory1": {"content": "The user likes Japanese food", "importance": 0.8},
            "memory2": {"content": "The user is planning a trip to Japan", "importance": 0.7},
            "memory3": {"content": "The user mentioned they want to learn Japanese", "importance": 0.6},
            "memory4": {"content": "The user's favorite food is pizza", "importance": 0.7},
            "memory5": {"content": "The user is a software developer", "importance": 0.8}
        }

        # Mock search_memories to return appropriate results
        def mock_search_memories(query, limit=10):
            if "source_type:preference" in query:
                return [self.test_memories["memory1"], self.test_memories["memory4"]]
            elif "source_type:fact" in query:
                return [self.test_memories["memory2"], self.test_memories["memory5"]]
            elif "source_type:conversation" in query:
                return [self.test_memories["memory3"]]
            elif "japan" in query.lower():
                return [self.test_memories["memory1"], self.test_memories["memory2"], self.test_memories["memory3"]]
            else:
                return list(self.test_memories.values())[:limit]

        self.memory_manager.long_term.search_memories.side_effect = mock_search_memories

        # Mock get_user_summary to return a test summary
        self.memory_manager.get_user_summary = MagicMock(return_value={
            "name": "Test User",
            "interests": ["Japan", "Food", "Programming"],
            "feedback_stats": {
                "total": 10,
                "positive": 8,
                "negative": 1,
                "neutral": 1
            }
        })

    def test_cluster_memories_by_topic(self):
        """Test clustering memories by topic."""
        # Get topic clusters
        clusters = self.summarization.cluster_memories_by_topic(force_update=True)

        # Check that clusters were created
        self.assertGreater(len(clusters), 0)

        # Check that japan cluster exists and has all three japan-related memories
        japan_cluster = None
        for topic, memories in clusters.items():
            if "japan" in topic.lower():
                japan_cluster = memories
                break

        self.assertIsNotNone(japan_cluster)
        self.assertEqual(len(japan_cluster), 3)

        # Check that food cluster exists
        food_cluster = None
        for topic, memories in clusters.items():
            if "food" in topic.lower():
                food_cluster = memories
                break

        self.assertIsNotNone(food_cluster)

        # Check that cache was updated
        self.assertGreater(len(self.summarization.topic_clusters_cache), 0)
        self.assertAlmostEqual(
            self.summarization.last_topic_clustering.timestamp(),
            datetime.now().timestamp(),
            delta=5
        )

    def test_summarize_topic_cluster(self):
        """Test summarizing a topic cluster."""
        # Create a test cluster
        topic = "japan, travel, language"
        memories = [
            self.test_memories["memory1"],
            self.test_memories["memory2"],
            self.test_memories["memory3"]
        ]

        # Generate summary
        summary = self.summarization.summarize_topic_cluster(topic, memories)

        # Check that summary was created
        self.assertIsNotNone(summary)
        self.assertGreater(len(summary), 0)

        # Check that summary contains topic name
        self.assertIn(topic, summary)

        # Check that summary contains memory count
        self.assertIn("3 memories", summary)

        # Check that summary contains key points
        self.assertIn("Key points:", summary)

        # Check that cache was updated
        cache_key = f"topic_{topic}"
        self.assertIn(cache_key, self.summarization.summary_cache)

    def test_generate_topic_summaries(self):
        """Test generating summaries for all topic clusters."""
        # Generate summaries
        summaries = self.summarization.generate_topic_summaries(force_update=True)

        # Check that summaries were created
        self.assertGreater(len(summaries), 0)

        # Check that each summary is a string
        for topic, summary in summaries.items():
            self.assertIsInstance(summary, str)
            self.assertGreater(len(summary), 0)

    def test_generate_user_profile(self):
        """Test generating a user profile."""
        # Generate profile
        profile = self.summarization.generate_user_profile(force_update=True)

        # Check that profile was created
        self.assertIsNotNone(profile)

        # Check that profile contains preferences
        self.assertIn("preferences", profile)
        self.assertIsInstance(profile["preferences"], list)

        # Check that profile contains personal facts
        self.assertIn("personal_facts", profile)
        self.assertIsInstance(profile["personal_facts"], list)

        # Check that profile contains topics of interest
        self.assertIn("topics_of_interest", profile)
        self.assertIsInstance(profile["topics_of_interest"], list)

        # Check that profile contains memory counts
        self.assertIn("memory_counts", profile)
        self.assertIsInstance(profile["memory_counts"], dict)

        # Check that profile contains user summary
        self.assertIn("user_summary", profile)
        self.assertIsInstance(profile["user_summary"], dict)

        # Check that cache was updated
        self.assertIsNotNone(self.summarization.profile_cache)
        self.assertAlmostEqual(
            self.summarization.last_profile_update.timestamp(),
            datetime.now().timestamp(),
            delta=5
        )

    def test_summarize_recent_memories(self):
        """Test summarizing recent memories."""
        # Summarize recent memories
        summary = self.summarization.summarize_recent_memories(days=7, limit=5)

        # Check that summary was created
        self.assertIsNotNone(summary)
        self.assertGreater(len(summary), 0)

        # Check that summary contains memory count
        self.assertIn("memories", summary)

        # Check that summary contains key points
        self.assertIn("Key", summary)

        # Check that cache was updated
        cache_key = "recent_7_5"
        self.assertIn(cache_key, self.summarization.summary_cache)

    def test_summarize_memory_by_type(self):
        """Test summarizing memories by type."""
        # Summarize preference memories
        summary = self.summarization.summarize_memory_by_type("preference", limit=5)

        # Check that summary was created
        self.assertIsNotNone(summary)
        self.assertGreater(len(summary), 0)

        # Check that summary contains memory type
        self.assertIn("Preference memories", summary)

        # Check that summary contains memory count
        self.assertIn("memories", summary)

        # Check that summary contains key points
        self.assertIn("Key points:", summary)

        # Check that cache was updated
        cache_key = "type_preference_5"
        self.assertIn(cache_key, self.summarization.summary_cache)

    def test_clear_cache(self):
        """Test clearing the cache."""
        # Add some items to cache
        self.summarization.summary_cache = {"test": (datetime.now(), "test summary")}
        self.summarization.topic_clusters_cache = {"test": []}
        self.summarization.profile_cache = {"test": "test profile"}

        # Clear cache
        self.summarization.clear_cache()

        # Check that cache was cleared
        self.assertEqual(len(self.summarization.summary_cache), 0)
        self.assertEqual(len(self.summarization.topic_clusters_cache), 0)
        self.assertEqual(len(self.summarization.profile_cache), 0)

    def test_get_memory_overview(self):
        """Test getting a memory overview."""
        # Mock get_memory_stats
        self.memory_manager.get_memory_stats.return_value = {
            "short_term": {"turn_count": 10},
            "long_term": {"memory_count": 5}
        }

        # Get overview
        overview = self.summarization.get_memory_overview()

        # Check that overview was created
        self.assertIsNotNone(overview)

        # Check that overview contains memory stats
        self.assertIn("memory_stats", overview)
        self.assertIsInstance(overview["memory_stats"], dict)

        # Check that overview contains topic clusters
        self.assertIn("topic_clusters", overview)
        self.assertIsInstance(overview["topic_clusters"], dict)

        # Check that overview contains user profile
        self.assertIn("user_profile", overview)
        self.assertIsInstance(overview["user_profile"], dict)

        # Check that overview contains timestamp
        self.assertIn("timestamp", overview)
        self.assertIsInstance(overview["timestamp"], str)

if __name__ == "__main__":
    unittest.main()
