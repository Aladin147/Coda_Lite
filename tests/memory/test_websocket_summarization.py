"""
Tests for the WebSocket-enhanced summarization system.
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import json

from memory.websocket_summarization import WebSocketEnhancedSummarization

class TestWebSocketEnhancedSummarization(unittest.TestCase):
    """Test WebSocket-enhanced summarization functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create mock memory manager
        self.memory_manager = MagicMock()
        self.memory_manager.long_term = MagicMock()
        self.memory_manager.long_term.metadata = {
            "memories": {}
        }
        
        # Create mock WebSocket server
        self.ws = MagicMock()
        self.ws.emit_event = MagicMock()
        
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
        self.summarization = WebSocketEnhancedSummarization(
            memory_manager=self.memory_manager,
            config=self.config,
            websocket_server=self.ws
        )
        
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
            "memory3": {"content": "The user mentioned they want to learn Japanese", "importance": 0.6}
        }
        
        # Mock search_memories to return appropriate results
        def mock_search_memories(query, limit=10):
            if "source_type:preference" in query:
                return [self.test_memories["memory1"]]
            elif "source_type:fact" in query:
                return [self.test_memories["memory2"]]
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
            "interests": ["Japan", "Food", "Programming"]
        })
        
        # Mock get_memory_stats
        self.memory_manager.get_memory_stats = MagicMock(return_value={
            "short_term": {"turn_count": 10},
            "long_term": {"memory_count": 3}
        })

    def test_cluster_memories_by_topic(self):
        """Test clustering memories by topic with WebSocket events."""
        # Get topic clusters
        clusters = self.summarization.cluster_memories_by_topic(force_update=True)
        
        # Check that clusters were created
        self.assertGreater(len(clusters), 0)
        
        # Check that WebSocket event was emitted
        self.ws.emit_event.assert_called_with(
            "memory_topic_clusters",
            {
                "cluster_count": len(clusters),
                "clusters": {topic: len(memories) for topic, memories in clusters.items()},
                "timestamp": unittest.mock.ANY
            }
        )

    def test_summarize_topic_cluster(self):
        """Test summarizing a topic cluster with WebSocket events."""
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
        
        # Check that WebSocket event was emitted
        self.ws.emit_event.assert_called_with(
            "memory_topic_summary",
            {
                "topic": topic,
                "memory_count": len(memories),
                "summary_length": len(summary),
                "timestamp": unittest.mock.ANY
            }
        )

    def test_generate_topic_summaries(self):
        """Test generating summaries for all topic clusters with WebSocket events."""
        # Generate summaries
        summaries = self.summarization.generate_topic_summaries(force_update=True)
        
        # Check that summaries were created
        self.assertGreater(len(summaries), 0)
        
        # Check that WebSocket event was emitted
        self.ws.emit_event.assert_called_with(
            "memory_topic_summaries",
            {
                "summary_count": len(summaries),
                "topics": list(summaries.keys()),
                "timestamp": unittest.mock.ANY
            }
        )

    def test_generate_user_profile(self):
        """Test generating a user profile with WebSocket events."""
        # Generate profile
        profile = self.summarization.generate_user_profile(force_update=True)
        
        # Check that profile was created
        self.assertIsNotNone(profile)
        
        # Check that WebSocket event was emitted
        self.ws.emit_event.assert_called_with(
            "memory_user_profile",
            {
                "preferences_count": len(profile.get("preferences", [])),
                "personal_facts_count": len(profile.get("personal_facts", [])),
                "topics_of_interest_count": len(profile.get("topics_of_interest", [])),
                "timestamp": unittest.mock.ANY
            }
        )

    def test_summarize_recent_memories(self):
        """Test summarizing recent memories with WebSocket events."""
        # Summarize recent memories
        summary = self.summarization.summarize_recent_memories(days=7, limit=5)
        
        # Check that summary was created
        self.assertIsNotNone(summary)
        self.assertGreater(len(summary), 0)
        
        # Check that WebSocket event was emitted
        self.ws.emit_event.assert_called_with(
            "memory_recent_summary",
            {
                "days": 7,
                "limit": 5,
                "summary_length": len(summary),
                "timestamp": unittest.mock.ANY
            }
        )

    def test_summarize_memory_by_type(self):
        """Test summarizing memories by type with WebSocket events."""
        # Summarize preference memories
        summary = self.summarization.summarize_memory_by_type("preference", limit=5)
        
        # Check that summary was created
        self.assertIsNotNone(summary)
        self.assertGreater(len(summary), 0)
        
        # Check that WebSocket event was emitted
        self.ws.emit_event.assert_called_with(
            "memory_type_summary",
            {
                "memory_type": "preference",
                "limit": 5,
                "summary_length": len(summary),
                "timestamp": unittest.mock.ANY
            }
        )

    def test_clear_cache(self):
        """Test clearing the cache with WebSocket events."""
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
        
        # Check that WebSocket event was emitted
        self.ws.emit_event.assert_called_with(
            "memory_cache_cleared",
            {
                "timestamp": unittest.mock.ANY
            }
        )

    def test_get_memory_overview(self):
        """Test getting a memory overview with WebSocket events."""
        # Get overview
        overview = self.summarization.get_memory_overview()
        
        # Check that overview was created
        self.assertIsNotNone(overview)
        
        # Check that WebSocket event was emitted
        self.ws.emit_event.assert_called_with(
            "memory_overview",
            {
                "topic_cluster_count": len(overview.get("topic_clusters", {})),
                "memory_count": overview.get("memory_stats", {}).get("long_term", {}).get("memory_count", 0),
                "timestamp": unittest.mock.ANY
            }
        )

if __name__ == "__main__":
    unittest.main()
