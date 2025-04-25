"""
WebSocket integration for the memory summarization system.

This module provides a WebSocketEnhancedSummarization class that extends the MemorySummarizationSystem
with WebSocket event emission.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .summarization import MemorySummarizationSystem

logger = logging.getLogger("coda.memory.websocket_summarization")

class WebSocketEnhancedSummarization(MemorySummarizationSystem):
    """
    MemorySummarizationSystem with WebSocket event emission.
    
    This class extends the MemorySummarizationSystem to emit WebSocket events
    for summarization operations.
    """
    
    def __init__(self, memory_manager, config: Dict[str, Any] = None, websocket_server=None):
        """
        Initialize the WebSocket-enhanced summarization system.
        
        Args:
            memory_manager: The memory manager to use
            config: Configuration dictionary
            websocket_server: WebSocket server for event emission
        """
        super().__init__(memory_manager, config)
        self.ws = websocket_server
        logger.info("WebSocketEnhancedSummarization initialized")
    
    def cluster_memories_by_topic(self, force_update: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """
        Cluster memories by topic and emit WebSocket event.
        
        Args:
            force_update: Whether to force a cache update
            
        Returns:
            Dictionary mapping topic clusters to lists of memories
        """
        # Call parent method
        clusters = super().cluster_memories_by_topic(force_update)
        
        # Emit WebSocket event
        if self.ws:
            self.ws.emit_event("memory_topic_clusters", {
                "cluster_count": len(clusters),
                "clusters": {topic: len(memories) for topic, memories in clusters.items()},
                "timestamp": datetime.now().isoformat()
            })
        
        return clusters
    
    def summarize_topic_cluster(self, topic: str, memories: List[Dict[str, Any]]) -> str:
        """
        Generate a summary for a topic cluster and emit WebSocket event.
        
        Args:
            topic: The topic name
            memories: List of memories in the cluster
            
        Returns:
            Summary text
        """
        # Call parent method
        summary = super().summarize_topic_cluster(topic, memories)
        
        # Emit WebSocket event
        if self.ws:
            self.ws.emit_event("memory_topic_summary", {
                "topic": topic,
                "memory_count": len(memories),
                "summary_length": len(summary),
                "timestamp": datetime.now().isoformat()
            })
        
        return summary
    
    def generate_topic_summaries(self, force_update: bool = False) -> Dict[str, str]:
        """
        Generate summaries for all topic clusters and emit WebSocket event.
        
        Args:
            force_update: Whether to force a cache update
            
        Returns:
            Dictionary mapping topics to summaries
        """
        # Call parent method
        summaries = super().generate_topic_summaries(force_update)
        
        # Emit WebSocket event
        if self.ws:
            self.ws.emit_event("memory_topic_summaries", {
                "summary_count": len(summaries),
                "topics": list(summaries.keys()),
                "timestamp": datetime.now().isoformat()
            })
        
        return summaries
    
    def generate_user_profile(self, force_update: bool = False) -> Dict[str, Any]:
        """
        Generate a user profile summary and emit WebSocket event.
        
        Args:
            force_update: Whether to force a cache update
            
        Returns:
            User profile dictionary
        """
        # Call parent method
        profile = super().generate_user_profile(force_update)
        
        # Emit WebSocket event
        if self.ws:
            self.ws.emit_event("memory_user_profile", {
                "preferences_count": len(profile.get("preferences", [])),
                "personal_facts_count": len(profile.get("personal_facts", [])),
                "topics_of_interest_count": len(profile.get("topics_of_interest", [])),
                "timestamp": datetime.now().isoformat()
            })
        
        return profile
    
    def summarize_recent_memories(self, days: int = 1, limit: int = 10) -> str:
        """
        Summarize recent memories from the past N days and emit WebSocket event.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of memories to include
            
        Returns:
            Summary text
        """
        # Call parent method
        summary = super().summarize_recent_memories(days, limit)
        
        # Emit WebSocket event
        if self.ws:
            self.ws.emit_event("memory_recent_summary", {
                "days": days,
                "limit": limit,
                "summary_length": len(summary),
                "timestamp": datetime.now().isoformat()
            })
        
        return summary
    
    def summarize_memory_by_type(self, memory_type: str, limit: int = 10) -> str:
        """
        Summarize memories of a specific type and emit WebSocket event.
        
        Args:
            memory_type: Type of memory to summarize (fact, preference, conversation)
            limit: Maximum number of memories to include
            
        Returns:
            Summary text
        """
        # Call parent method
        summary = super().summarize_memory_by_type(memory_type, limit)
        
        # Emit WebSocket event
        if self.ws:
            self.ws.emit_event("memory_type_summary", {
                "memory_type": memory_type,
                "limit": limit,
                "summary_length": len(summary),
                "timestamp": datetime.now().isoformat()
            })
        
        return summary
    
    def clear_cache(self) -> None:
        """
        Clear all summary caches and emit WebSocket event.
        """
        # Call parent method
        super().clear_cache()
        
        # Emit WebSocket event
        if self.ws:
            self.ws.emit_event("memory_cache_cleared", {
                "timestamp": datetime.now().isoformat()
            })
    
    def get_memory_overview(self) -> Dict[str, Any]:
        """
        Get a comprehensive overview of the memory system and emit WebSocket event.
        
        Returns:
            Dictionary with memory overview
        """
        # Call parent method
        overview = super().get_memory_overview()
        
        # Emit WebSocket event
        if self.ws:
            self.ws.emit_event("memory_overview", {
                "topic_cluster_count": len(overview.get("topic_clusters", {})),
                "memory_count": overview.get("memory_stats", {}).get("long_term", {}).get("memory_count", 0),
                "timestamp": datetime.now().isoformat()
            })
        
        return overview
