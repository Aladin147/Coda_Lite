"""
Memory Summarization System for Coda Lite.

This module provides functionality for summarizing memories, implementing topic clustering,
and generating user profiles.
"""

import logging
import time
import re
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set, Counter
from collections import defaultdict, Counter

logger = logging.getLogger("coda.memory.summarization")

class MemorySummarizationSystem:
    """
    Manages memory summarization and topic clustering.
    
    Responsibilities:
    - Cluster related memories by topic
    - Generate summaries of memory clusters
    - Create user profile summaries
    - Provide temporal and importance-weighted summaries
    """
    
    def __init__(self, memory_manager, config: Dict[str, Any] = None):
        """
        Initialize the memory summarization system.
        
        Args:
            memory_manager: The memory manager to use
            config: Configuration dictionary
        """
        self.memory_manager = memory_manager
        self.config = config or {}
        
        # Summarization settings
        self.min_cluster_size = self.config.get("memory", {}).get("min_cluster_size", 3)
        self.max_summary_length = self.config.get("memory", {}).get("max_summary_length", 200)
        self.summary_cache_ttl = self.config.get("memory", {}).get("summary_cache_ttl", 3600)  # 1 hour
        
        # Topic clustering settings
        self.similarity_threshold = self.config.get("memory", {}).get("topic_similarity_threshold", 0.7)
        self.max_topics_per_cluster = self.config.get("memory", {}).get("max_topics_per_cluster", 5)
        
        # User profile settings
        self.profile_update_interval = self.config.get("memory", {}).get("profile_update_interval", 86400)  # 1 day
        
        # Cache for summaries
        self.summary_cache = {}
        self.topic_clusters_cache = {}
        self.profile_cache = {}
        
        # Cache timestamps
        self.last_topic_clustering = datetime.now() - timedelta(days=1)  # Force initial clustering
        self.last_profile_update = datetime.now() - timedelta(days=1)  # Force initial profile update
        
        logger.info("MemorySummarizationSystem initialized")
    
    def cluster_memories_by_topic(self, force_update: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """
        Cluster memories by topic.
        
        Args:
            force_update: Whether to force a cache update
            
        Returns:
            Dictionary mapping topic clusters to lists of memories
        """
        # Check if we have a cached result that's still valid
        cache_age = (datetime.now() - self.last_topic_clustering).total_seconds()
        if not force_update and self.topic_clusters_cache and cache_age < self.summary_cache_ttl:
            return self.topic_clusters_cache
        
        # Get all memories
        all_memories = []
        try:
            # Get all memory IDs from metadata
            memory_ids = list(self.memory_manager.long_term.metadata.get("memories", {}).keys())
            
            # Get memory objects
            for memory_id in memory_ids:
                memory = self.memory_manager.long_term.get_memory_by_id(memory_id)
                if memory:
                    all_memories.append(memory)
        except Exception as e:
            logger.error(f"Error retrieving memories for clustering: {e}")
            return {}
        
        # Extract topics from memories
        memory_topics = {}
        for memory in all_memories:
            memory_id = memory.get("id")
            if not memory_id:
                continue
                
            # Get topics from metadata
            topics_str = memory.get("metadata", {}).get("topics", "")
            if isinstance(topics_str, list):
                topics = topics_str
            else:
                topics = topics_str.split(",") if topics_str else []
            
            # Store topics for this memory
            if topics:
                memory_topics[memory_id] = topics
        
        # Count topic occurrences
        topic_counts = Counter()
        for topics in memory_topics.values():
            topic_counts.update(topics)
        
        # Filter out rare topics (mentioned only once)
        common_topics = {topic for topic, count in topic_counts.items() if count > 1 and topic}
        
        # Group memories by topic
        topic_memories = defaultdict(list)
        for memory in all_memories:
            memory_id = memory.get("id")
            if not memory_id or memory_id not in memory_topics:
                continue
                
            # Get topics for this memory
            topics = memory_topics[memory_id]
            
            # Add memory to each of its topics
            for topic in topics:
                if topic in common_topics:
                    topic_memories[topic].append(memory)
        
        # Merge similar topics
        merged_topics = self._merge_similar_topics(topic_memories)
        
        # Filter out small clusters
        clusters = {topic: memories for topic, memories in merged_topics.items() 
                   if len(memories) >= self.min_cluster_size}
        
        # Update cache
        self.topic_clusters_cache = clusters
        self.last_topic_clustering = datetime.now()
        
        logger.info(f"Clustered memories into {len(clusters)} topic clusters")
        
        return clusters
    
    def _merge_similar_topics(self, topic_memories: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Merge similar topics based on memory overlap.
        
        Args:
            topic_memories: Dictionary mapping topics to lists of memories
            
        Returns:
            Dictionary with merged topics
        """
        # Calculate topic similarity based on memory overlap
        topic_similarity = {}
        topics = list(topic_memories.keys())
        
        for i, topic1 in enumerate(topics):
            for topic2 in topics[i+1:]:
                # Get memory IDs for each topic
                memories1 = {m.get("id") for m in topic_memories[topic1] if m.get("id")}
                memories2 = {m.get("id") for m in topic_memories[topic2] if m.get("id")}
                
                # Calculate Jaccard similarity
                intersection = len(memories1.intersection(memories2))
                union = len(memories1.union(memories2))
                
                if union > 0:
                    similarity = intersection / union
                    
                    # Store similarity if above threshold
                    if similarity >= self.similarity_threshold:
                        topic_similarity[(topic1, topic2)] = similarity
        
        # Merge topics based on similarity
        merged_topics = {}
        merged_sets = {}
        
        # Sort similarities in descending order
        sorted_similarities = sorted(topic_similarity.items(), key=lambda x: x[1], reverse=True)
        
        # Process each topic pair
        for (topic1, topic2), similarity in sorted_similarities:
            # Check if either topic has already been merged
            merged1 = None
            merged2 = None
            
            for merged_set_id, merged_set in merged_sets.items():
                if topic1 in merged_set:
                    merged1 = merged_set_id
                if topic2 in merged_set:
                    merged2 = merged_set_id
            
            if merged1 is None and merged2 is None:
                # Create a new merged set
                merged_set_id = f"{topic1}_{topic2}"
                merged_sets[merged_set_id] = {topic1, topic2}
                
                # Merge memories
                merged_topics[merged_set_id] = topic_memories[topic1] + topic_memories[topic2]
                
            elif merged1 is not None and merged2 is None:
                # Add topic2 to merged1
                merged_sets[merged1].add(topic2)
                
                # Add memories from topic2
                merged_topics[merged1].extend(topic_memories[topic2])
                
            elif merged1 is None and merged2 is not None:
                # Add topic1 to merged2
                merged_sets[merged2].add(topic1)
                
                # Add memories from topic1
                merged_topics[merged2].extend(topic_memories[topic1])
                
            elif merged1 != merged2:
                # Merge the two merged sets
                merged_sets[merged1].update(merged_sets[merged2])
                merged_topics[merged1].extend(merged_topics[merged2])
                
                # Remove the second merged set
                del merged_sets[merged2]
                del merged_topics[merged2]
        
        # Add topics that weren't merged
        for topic, memories in topic_memories.items():
            # Check if topic was merged
            merged = False
            for merged_set in merged_sets.values():
                if topic in merged_set:
                    merged = True
                    break
            
            # If not merged, add as is
            if not merged:
                merged_topics[topic] = memories
        
        # Create readable cluster names
        readable_clusters = {}
        for cluster_id, memories in merged_topics.items():
            # Get topics in this cluster
            if "_" in cluster_id:
                topics = cluster_id.split("_")
            else:
                topics = [cluster_id]
            
            # Limit to max_topics_per_cluster
            if len(topics) > self.max_topics_per_cluster:
                topics = topics[:self.max_topics_per_cluster]
            
            # Create readable name
            readable_name = ", ".join(topics)
            
            # Remove duplicates from memories
            unique_memories = []
            seen_ids = set()
            for memory in memories:
                memory_id = memory.get("id")
                if memory_id and memory_id not in seen_ids:
                    unique_memories.append(memory)
                    seen_ids.add(memory_id)
            
            readable_clusters[readable_name] = unique_memories
        
        return readable_clusters
    
    def summarize_topic_cluster(self, topic: str, memories: List[Dict[str, Any]]) -> str:
        """
        Generate a summary for a topic cluster.
        
        Args:
            topic: The topic name
            memories: List of memories in the cluster
            
        Returns:
            Summary text
        """
        # Check if we have a cached summary
        cache_key = f"topic_{topic}"
        if cache_key in self.summary_cache:
            cache_time, summary = self.summary_cache[cache_key]
            if (datetime.now() - cache_time).total_seconds() < self.summary_cache_ttl:
                return summary
        
        # Sort memories by importance (highest first)
        sorted_memories = sorted(memories, key=lambda m: m.get("metadata", {}).get("importance", 0), reverse=True)
        
        # Get top memories (most important)
        top_memories = sorted_memories[:5]
        
        # Count memory types
        memory_types = Counter()
        for memory in memories:
            memory_type = memory.get("metadata", {}).get("source_type", "unknown")
            memory_types[memory_type] += 1
        
        # Generate summary
        summary = f"Topic: {topic}\n"
        summary += f"Contains {len(memories)} memories "
        summary += f"({', '.join(f'{count} {type}' for type, count in memory_types.items())})\n"
        
        # Add key points from top memories
        summary += "Key points:\n"
        for i, memory in enumerate(top_memories):
            content = memory.get("content", "")
            # Truncate long content
            if len(content) > 100:
                content = content[:97] + "..."
            summary += f"- {content}\n"
        
        # Truncate if too long
        if len(summary) > self.max_summary_length:
            summary = summary[:self.max_summary_length - 3] + "..."
        
        # Cache the summary
        self.summary_cache[cache_key] = (datetime.now(), summary)
        
        return summary
    
    def generate_topic_summaries(self, force_update: bool = False) -> Dict[str, str]:
        """
        Generate summaries for all topic clusters.
        
        Args:
            force_update: Whether to force a cache update
            
        Returns:
            Dictionary mapping topics to summaries
        """
        # Get topic clusters
        clusters = self.cluster_memories_by_topic(force_update)
        
        # Generate summaries
        summaries = {}
        for topic, memories in clusters.items():
            summaries[topic] = self.summarize_topic_cluster(topic, memories)
        
        logger.info(f"Generated {len(summaries)} topic summaries")
        
        return summaries
    
    def generate_user_profile(self, force_update: bool = False) -> Dict[str, Any]:
        """
        Generate a user profile summary.
        
        Args:
            force_update: Whether to force a cache update
            
        Returns:
            User profile dictionary
        """
        # Check if we have a cached profile that's still valid
        cache_age = (datetime.now() - self.last_profile_update).total_seconds()
        if not force_update and self.profile_cache and cache_age < self.profile_update_interval:
            return self.profile_cache
        
        # Get user summary from memory manager
        user_summary = {}
        try:
            # Get existing user summary
            if hasattr(self.memory_manager, "get_user_summary"):
                user_summary = self.memory_manager.get_user_summary() or {}
        except Exception as e:
            logger.error(f"Error retrieving user summary: {e}")
        
        # Get preference memories
        preferences = []
        try:
            # Search for preference memories
            preference_memories = self.memory_manager.long_term.search_memories("source_type:preference", limit=50)
            
            # Extract preference content
            for memory in preference_memories:
                content = memory.get("content", "")
                if content:
                    preferences.append(content)
        except Exception as e:
            logger.error(f"Error retrieving preference memories: {e}")
        
        # Get fact memories about the user
        personal_facts = []
        try:
            # Search for fact memories with personal information
            personal_memories = self.memory_manager.long_term.search_memories("source_type:fact AND (I OR my OR name OR user)", limit=50)
            
            # Extract fact content
            for memory in personal_memories:
                content = memory.get("content", "")
                if content:
                    personal_facts.append(content)
        except Exception as e:
            logger.error(f"Error retrieving personal fact memories: {e}")
        
        # Get topic clusters
        topic_clusters = self.cluster_memories_by_topic()
        
        # Count memories by type
        memory_types = Counter()
        try:
            # Get all memory IDs from metadata
            memory_ids = list(self.memory_manager.long_term.metadata.get("memories", {}).keys())
            
            # Get memory objects and count types
            for memory_id in memory_ids:
                memory = self.memory_manager.long_term.get_memory_by_id(memory_id)
                if memory:
                    memory_type = memory.get("metadata", {}).get("source_type", "unknown")
                    memory_types[memory_type] += 1
        except Exception as e:
            logger.error(f"Error counting memory types: {e}")
        
        # Create profile
        profile = {
            "preferences": preferences,
            "personal_facts": personal_facts,
            "topics_of_interest": list(topic_clusters.keys()),
            "memory_counts": dict(memory_types),
            "user_summary": user_summary,
            "generated_at": datetime.now().isoformat()
        }
        
        # Cache the profile
        self.profile_cache = profile
        self.last_profile_update = datetime.now()
        
        logger.info(f"Generated user profile with {len(preferences)} preferences and {len(personal_facts)} personal facts")
        
        return profile
    
    def summarize_recent_memories(self, days: int = 1, limit: int = 10) -> str:
        """
        Summarize recent memories from the past N days.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of memories to include
            
        Returns:
            Summary text
        """
        # Check if we have a cached summary
        cache_key = f"recent_{days}_{limit}"
        if cache_key in self.summary_cache:
            cache_time, summary = self.summary_cache[cache_key]
            if (datetime.now() - cache_time).total_seconds() < self.summary_cache_ttl:
                return summary
        
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.isoformat()
        
        # Get recent memories
        recent_memories = []
        try:
            # Get all memory IDs from metadata
            memory_ids = list(self.memory_manager.long_term.metadata.get("memories", {}).keys())
            
            # Get memory objects and filter by date
            for memory_id in memory_ids:
                memory = self.memory_manager.long_term.get_memory_by_id(memory_id)
                if memory:
                    timestamp = memory.get("metadata", {}).get("timestamp", "")
                    if timestamp and timestamp > cutoff_str:
                        recent_memories.append(memory)
        except Exception as e:
            logger.error(f"Error retrieving recent memories: {e}")
            return f"Error retrieving recent memories: {e}"
        
        # Sort by importance and recency (most important and recent first)
        sorted_memories = sorted(
            recent_memories,
            key=lambda m: (
                m.get("metadata", {}).get("importance", 0),
                m.get("metadata", {}).get("timestamp", "")
            ),
            reverse=True
        )
        
        # Limit to requested number
        top_memories = sorted_memories[:limit]
        
        # Count memory types
        memory_types = Counter()
        for memory in recent_memories:
            memory_type = memory.get("metadata", {}).get("source_type", "unknown")
            memory_types[memory_type] += 1
        
        # Extract topics
        topics = set()
        for memory in recent_memories:
            topics_str = memory.get("metadata", {}).get("topics", "")
            if isinstance(topics_str, list):
                memory_topics = topics_str
            else:
                memory_topics = topics_str.split(",") if topics_str else []
            topics.update(memory_topics)
        
        # Generate summary
        summary = f"Recent memories from the past {days} day(s):\n"
        summary += f"Found {len(recent_memories)} memories "
        summary += f"({', '.join(f'{count} {type}' for type, count in memory_types.items())})\n"
        
        # Add topics
        if topics:
            summary += f"Topics: {', '.join(sorted(topics)[:10])}"
            if len(topics) > 10:
                summary += f" and {len(topics) - 10} more"
            summary += "\n"
        
        # Add key points from top memories
        summary += "Key points:\n"
        for i, memory in enumerate(top_memories):
            content = memory.get("content", "")
            memory_type = memory.get("metadata", {}).get("source_type", "unknown")
            
            # Truncate long content
            if len(content) > 100:
                content = content[:97] + "..."
            
            summary += f"- [{memory_type}] {content}\n"
        
        # Truncate if too long
        if len(summary) > self.max_summary_length:
            summary = summary[:self.max_summary_length - 3] + "..."
        
        # Cache the summary
        self.summary_cache[cache_key] = (datetime.now(), summary)
        
        return summary
    
    def summarize_memory_by_type(self, memory_type: str, limit: int = 10) -> str:
        """
        Summarize memories of a specific type.
        
        Args:
            memory_type: Type of memory to summarize (fact, preference, conversation)
            limit: Maximum number of memories to include
            
        Returns:
            Summary text
        """
        # Check if we have a cached summary
        cache_key = f"type_{memory_type}_{limit}"
        if cache_key in self.summary_cache:
            cache_time, summary = self.summary_cache[cache_key]
            if (datetime.now() - cache_time).total_seconds() < self.summary_cache_ttl:
                return summary
        
        # Get memories of the specified type
        type_memories = []
        try:
            # Search for memories of the specified type
            type_memories = self.memory_manager.long_term.search_memories(f"source_type:{memory_type}", limit=50)
        except Exception as e:
            logger.error(f"Error retrieving {memory_type} memories: {e}")
            return f"Error retrieving {memory_type} memories: {e}"
        
        # Sort by importance (most important first)
        sorted_memories = sorted(
            type_memories,
            key=lambda m: m.get("metadata", {}).get("importance", 0),
            reverse=True
        )
        
        # Limit to requested number
        top_memories = sorted_memories[:limit]
        
        # Extract topics
        topics = set()
        for memory in type_memories:
            topics_str = memory.get("metadata", {}).get("topics", "")
            if isinstance(topics_str, list):
                memory_topics = topics_str
            else:
                memory_topics = topics_str.split(",") if topics_str else []
            topics.update(memory_topics)
        
        # Generate summary
        summary = f"{memory_type.capitalize()} memories:\n"
        summary += f"Found {len(type_memories)} {memory_type} memories\n"
        
        # Add topics
        if topics:
            summary += f"Topics: {', '.join(sorted(topics)[:10])}"
            if len(topics) > 10:
                summary += f" and {len(topics) - 10} more"
            summary += "\n"
        
        # Add key points from top memories
        summary += "Key points:\n"
        for i, memory in enumerate(top_memories):
            content = memory.get("content", "")
            
            # Truncate long content
            if len(content) > 100:
                content = content[:97] + "..."
            
            summary += f"- {content}\n"
        
        # Truncate if too long
        if len(summary) > self.max_summary_length:
            summary = summary[:self.max_summary_length - 3] + "..."
        
        # Cache the summary
        self.summary_cache[cache_key] = (datetime.now(), summary)
        
        return summary
    
    def clear_cache(self) -> None:
        """
        Clear all summary caches.
        """
        self.summary_cache = {}
        self.topic_clusters_cache = {}
        self.profile_cache = {}
        self.last_topic_clustering = datetime.now() - timedelta(days=1)
        self.last_profile_update = datetime.now() - timedelta(days=1)
        
        logger.info("Cleared all summary caches")
    
    def get_memory_overview(self) -> Dict[str, Any]:
        """
        Get a comprehensive overview of the memory system.
        
        Returns:
            Dictionary with memory overview
        """
        # Get memory statistics
        memory_stats = self.memory_manager.get_memory_stats()
        
        # Get topic clusters
        topic_clusters = self.cluster_memories_by_topic()
        
        # Get user profile
        user_profile = self.generate_user_profile()
        
        # Create overview
        overview = {
            "memory_stats": memory_stats,
            "topic_clusters": {topic: len(memories) for topic, memories in topic_clusters.items()},
            "user_profile": {
                "preferences_count": len(user_profile.get("preferences", [])),
                "personal_facts_count": len(user_profile.get("personal_facts", [])),
                "topics_of_interest": user_profile.get("topics_of_interest", []),
                "memory_counts": user_profile.get("memory_counts", {})
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return overview
