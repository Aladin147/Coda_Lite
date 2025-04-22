"""
Enhanced memory management for Coda Lite.

This module provides an EnhancedMemoryManager class that integrates short-term and long-term memory.
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Tuple

from .short_term import MemoryManager as ShortTermMemory
from .long_term import LongTermMemory
from .encoder import MemoryEncoder

logger = logging.getLogger("coda.memory.enhanced")

class EnhancedMemoryManager:
    """
    Enhanced memory manager that integrates short-term and long-term memory.

    Responsibilities:
    - Manage short-term conversation context
    - Store and retrieve long-term memories
    - Provide relevant memories for LLM prompts
    - Track user preferences and conversation history
    """

    def __init__(self,
                 config: Dict[str, Any],
                 short_term_memory: Optional[ShortTermMemory] = None,
                 long_term_memory: Optional[LongTermMemory] = None):
        """
        Initialize the enhanced memory manager.

        Args:
            config: Configuration dictionary
            short_term_memory: Optional existing short-term memory instance
            long_term_memory: Optional existing long-term memory instance
        """
        self.config = config

        # Initialize short-term memory
        if short_term_memory:
            self.short_term = short_term_memory
        else:
            max_turns = config.get("memory", {}).get("max_turns", 20)
            self.short_term = ShortTermMemory(max_turns=max_turns)

        # Initialize long-term memory
        if long_term_memory:
            self.long_term = long_term_memory
        else:
            storage_path = config.get("memory", {}).get("long_term_path", "data/memory/long_term")
            embedding_model = config.get("memory", {}).get("embedding_model", "all-MiniLM-L6-v2")
            vector_db_type = config.get("memory", {}).get("vector_db", "chroma")
            max_memories = config.get("memory", {}).get("max_memories", 1000)
            device = config.get("memory", {}).get("device", "cpu")

            self.long_term = LongTermMemory(
                storage_path=storage_path,
                embedding_model=embedding_model,
                vector_db_type=vector_db_type,
                max_memories=max_memories,
                device=device
            )

        # Initialize memory encoder
        chunk_size = config.get("memory", {}).get("chunk_size", 200)
        overlap = config.get("memory", {}).get("chunk_overlap", 50)
        min_chunk_length = config.get("memory", {}).get("min_chunk_length", 50)

        self.encoder = MemoryEncoder(
            chunk_size=chunk_size,
            overlap=overlap,
            min_chunk_length=min_chunk_length
        )

        # Track recent topics and tools
        self.recent_topics = []
        self.last_tool_used = None

        # Memory persistence settings
        self.auto_persist = config.get("memory", {}).get("auto_persist", True)
        self.persist_interval = config.get("memory", {}).get("persist_interval", 5)
        self.turn_count_at_last_persist = 0

        logger.info("EnhancedMemoryManager initialized")

    def add_turn(self, role: str, content: str) -> Dict[str, Any]:
        """
        Add a new conversation turn.

        Args:
            role: The speaker role ("system", "user", or "assistant")
            content: The message content

        Returns:
            The created turn object
        """
        # Add to short-term memory
        turn = self.short_term.add_turn(role, content)

        # Extract topics if it's a user message
        if role == "user":
            self._extract_and_update_topics(content)

        # Check if we should persist to long-term memory
        if self.auto_persist and role == "assistant":
            turns_since_persist = self.short_term.turn_count - self.turn_count_at_last_persist
            if turns_since_persist >= self.persist_interval:
                self.persist_short_term_memory()

        return turn

    def get_context(self, max_tokens: int = 800) -> List[Dict[str, str]]:
        """
        Get conversation context from short-term memory.

        Args:
            max_tokens: Maximum number of tokens to include

        Returns:
            List of {"role": "...", "content": "..."} dicts for LLM context
        """
        return self.short_term.get_context(max_tokens=max_tokens)

    def get_enhanced_context(self,
                            user_input: str,
                            max_tokens: int = 800,
                            max_memories: int = 3) -> List[Dict[str, str]]:
        """
        Get enhanced conversation context with relevant long-term memories.

        Args:
            user_input: Current user input
            max_tokens: Maximum number of tokens for short-term context
            max_memories: Maximum number of long-term memories to include

        Returns:
            Enhanced context with relevant memories
        """
        # Get short-term context
        context = self.short_term.get_context(max_tokens=max_tokens)

        # Retrieve relevant memories
        memories = self.retrieve_relevant_memories(user_input, limit=max_memories)

        # If we have memories, add them to the context
        if memories:
            # Find position to insert memories (after system message if present)
            insert_pos = 1 if context and context[0]["role"] == "system" else 0

            # Format memories as a system message
            memory_content = "Relevant information from previous conversations:\n\n"
            for i, memory in enumerate(memories):
                memory_content += f"{i+1}. {memory['content']}\n\n"

            # Insert memories
            context.insert(insert_pos, {
                "role": "system",
                "content": memory_content
            })

            logger.info(f"Added {len(memories)} memories to context")

        return context

    def retrieve_relevant_memories(self,
                                 query: str,
                                 limit: int = 3,
                                 min_similarity: float = 0.5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories based on the query.

        Args:
            query: The query text
            limit: Maximum number of memories to retrieve
            min_similarity: Minimum similarity score

        Returns:
            List of relevant memories
        """
        return self.long_term.retrieve_memories(
            query=query,
            limit=limit,
            min_similarity=min_similarity
        )

    def persist_short_term_memory(self) -> int:
        """
        Persist short-term memory to long-term storage.

        Returns:
            Number of memories stored
        """
        # Get all turns from short-term memory
        turns = list(self.short_term.turns)

        # Skip if no turns
        if not turns:
            return 0

        # Encode conversation into memory chunks
        memories = self.encoder.encode_conversation(turns)

        # Store memories
        stored_count = 0
        for memory in memories:
            self.long_term.add_memory(
                content=memory["content"],
                source_type=memory["source_type"],
                importance=memory["importance"],
                metadata=memory["metadata"]
            )
            stored_count += 1

        # Update last persist turn count
        self.turn_count_at_last_persist = self.short_term.turn_count

        logger.info(f"Persisted {stored_count} memories from short-term memory")

        return stored_count

    def add_fact(self,
                fact: str,
                source: str = "user",
                metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a fact to long-term memory.

        Args:
            fact: The fact text
            source: Source of the fact
            metadata: Additional metadata

        Returns:
            ID of the stored memory
        """
        # Encode fact
        memory = self.encoder.encode_fact(fact, source, metadata)

        # Store in long-term memory
        memory_id = self.long_term.add_memory(
            content=memory["content"],
            source_type=memory["source_type"],
            importance=memory["importance"],
            metadata=memory["metadata"]
        )

        # Extract and update topics
        for topic in memory["metadata"].get("topics", []):
            self.long_term.add_topic(topic)

        logger.info(f"Added fact to long-term memory: {fact[:50]}...")

        return memory_id

    def add_preference(self,
                      preference: str,
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a user preference to long-term memory.

        Args:
            preference: The preference text
            metadata: Additional metadata

        Returns:
            ID of the stored memory
        """
        # Encode preference
        memory = self.encoder.encode_preference(preference, metadata)

        # Store in long-term memory
        memory_id = self.long_term.add_memory(
            content=memory["content"],
            source_type=memory["source_type"],
            importance=memory["importance"],
            metadata=memory["metadata"]
        )

        logger.info(f"Added preference to long-term memory: {preference[:50]}...")

        return memory_id

    def add_feedback(self,
                    feedback: Dict[str, Any]) -> str:
        """
        Add user feedback to long-term memory.

        Args:
            feedback: Feedback dictionary with type, prompt, response, sentiment, etc.

        Returns:
            ID of the stored memory
        """
        # Encode feedback
        memory = self.encoder.encode_feedback(feedback)

        # Store in long-term memory
        memory_id = self.long_term.add_memory(
            content=memory["content"],
            source_type=memory["source_type"],
            importance=memory["importance"],
            metadata=memory["metadata"]
        )

        # Update user summary with feedback statistics
        feedback_stats = self.get_user_summary("feedback_stats") or {
            "total": 0,
            "positive": 0,
            "negative": 0,
            "neutral": 0
        }

        # Update counts
        feedback_stats["total"] = feedback_stats.get("total", 0) + 1
        sentiment = feedback.get("sentiment", "neutral")
        feedback_stats[sentiment] = feedback_stats.get(sentiment, 0) + 1

        # Update user summary
        self.update_user_summary("feedback_stats", feedback_stats)

        logger.info(f"Added feedback to long-term memory: {memory['content'][:50]}...")

        return memory_id

    def update_user_summary(self, key: str, value: Any) -> None:
        """
        Update user summary information.

        Args:
            key: Summary key (e.g., "preferred_topics", "communication_style")
            value: Summary value
        """
        self.long_term.update_user_summary(key, value)

    def get_user_summary(self, key: Optional[str] = None) -> Any:
        """
        Get user summary information.

        Args:
            key: Optional key to retrieve specific summary item

        Returns:
            User summary or specific item
        """
        return self.long_term.get_user_summary(key)

    def get_user_preferences(self) -> Dict[str, Any]:
        """
        Get user preferences from summary.

        Returns:
            Dictionary of user preferences
        """
        # Get all preferences from user summary
        preferences = {}

        # Add known preference keys
        for key in ["voice", "response_length", "communication_style", "interests"]:
            value = self.long_term.get_user_summary(key)
            if value is not None:
                preferences[key] = value

        return preferences

    def _extract_and_update_topics(self, text: str) -> List[str]:
        """
        Extract topics from text and update recent topics.

        Args:
            text: Text to extract topics from

        Returns:
            List of extracted topics
        """
        # Use the encoder to extract topics
        topics = self.encoder._extract_topics(text)

        # Update recent topics
        for topic in topics:
            if topic not in self.recent_topics:
                self.recent_topics.insert(0, topic)

        # Keep only the most recent topics
        self.recent_topics = self.recent_topics[:10]

        # Add topics to long-term memory
        for topic in topics:
            self.long_term.add_topic(topic)

        return topics

    def get_recent_topics(self, limit: int = 5) -> List[str]:
        """
        Get recent conversation topics.

        Args:
            limit: Maximum number of topics to return

        Returns:
            List of recent topics
        """
        return self.recent_topics[:limit]

    def set_last_tool_used(self, tool_name: str) -> None:
        """
        Set the last tool used.

        Args:
            tool_name: Name of the tool
        """
        self.last_tool_used = tool_name

    def get_last_tool_used(self) -> Optional[str]:
        """
        Get the last tool used.

        Returns:
            Name of the last tool used, or None
        """
        return self.last_tool_used

    def get_turn_count(self) -> int:
        """
        Get the number of turns in memory.

        Returns:
            Number of turns
        """
        return self.short_term.get_turn_count()

    def get_session_duration(self) -> float:
        """
        Get the duration of the current session in seconds.

        Returns:
            Session duration in seconds
        """
        return self.short_term.get_session_duration()

    def reset_short_term(self) -> bool:
        """
        Reset short-term memory.

        Returns:
            True if successful
        """
        # Persist current memory before resetting
        if self.auto_persist:
            self.persist_short_term_memory()

        return self.short_term.reset()

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about memory usage.

        Returns:
            Dictionary of memory statistics
        """
        short_term_stats = {
            "turn_count": self.short_term.get_turn_count(),
            "session_duration": self.short_term.get_session_duration()
        }

        long_term_stats = self.long_term.get_memory_stats()

        return {
            "short_term": short_term_stats,
            "long_term": long_term_stats,
            "recent_topics": self.recent_topics,
            "last_tool_used": self.last_tool_used
        }

    def get_day_summary(self) -> str:
        """
        Generate a summary of the day's interactions.

        Returns:
            Summary text or empty string if not enough data
        """
        # Check if we have enough turns to generate a summary
        if len(self.turns) < 3:
            return ""

        # Get today's date
        today = datetime.now().date()

        # Filter turns from today
        today_turns = []
        for turn in self.turns:
            # Check if turn has timestamp
            if "timestamp" in turn:
                try:
                    # Parse timestamp and check if it's from today
                    turn_date = datetime.fromisoformat(turn["timestamp"]).date()
                    if turn_date == today:
                        today_turns.append(turn)
                except (ValueError, TypeError):
                    # If timestamp parsing fails, assume it's from today
                    today_turns.append(turn)
            else:
                # If no timestamp, assume it's from today
                today_turns.append(turn)

        # If we don't have enough turns from today, return empty string
        if len(today_turns) < 3:
            return ""

        # Extract topics from today's turns
        topics = set()
        for turn in today_turns:
            if turn["role"] == "user" and "content" in turn:
                # Extract topics from user input
                extracted_topics = self.encoder._extract_topics(turn["content"])
                topics.update(extracted_topics)

        # Get facts and preferences from long-term memory
        facts = []
        preferences = []
        if self.long_term:
            # Get memories from today
            try:
                # Search for memories from today
                today_str = today.strftime("%Y-%m-%d")
                memories = self.long_term.search_memories(f"date:{today_str}", limit=50)

                # Categorize memories
                for memory in memories:
                    if memory.get("source_type") == "fact":
                        facts.append(memory.get("content", ""))
                    elif memory.get("source_type") == "preference":
                        preferences.append(memory.get("content", ""))
            except Exception as e:
                logger.error(f"Error getting memories by date: {e}")

        # Generate summary
        summary = f"Today we had {len(today_turns) // 2} exchanges. "

        # Add topics
        if topics:
            summary += f"We discussed topics including {', '.join(list(topics)[:5])}. "

        # Add facts
        if facts:
            summary += f"\n\nI learned {len(facts)} new facts, including:\n"
            for i, fact in enumerate(facts[:5]):
                summary += f"- {fact}\n"
            if len(facts) > 5:
                summary += f"- ...and {len(facts) - 5} more\n"

        # Add preferences
        if preferences:
            summary += f"\nI noted {len(preferences)} preferences, including:\n"
            for i, preference in enumerate(preferences[:3]):
                summary += f"- {preference}\n"
            if len(preferences) > 3:
                summary += f"- ...and {len(preferences) - 3} more\n"

        return summary

    def add_feedback(self, feedback: Dict[str, Any]) -> bool:
        """
        Add feedback to memory.

        Args:
            feedback: Feedback dictionary

        Returns:
            True if successful
        """
        if not self.long_term:
            logger.warning("Long-term memory not available for storing feedback")
            return False

        try:
            # Extract feedback type
            feedback_type = feedback.get("type")
            feedback_type_str = feedback_type.name if hasattr(feedback_type, "name") else str(feedback_type)

            # Create memory content
            content = f"User feedback on {feedback_type_str.lower()}: {feedback.get('response', '')}"

            # Create metadata
            metadata = {
                "feedback_id": feedback.get("id"),
                "feedback_type": feedback_type_str,
                "prompt": feedback.get("prompt"),
                "sentiment": feedback.get("sentiment"),
                "intent_type": feedback.get("intent_type"),
                "timestamp": feedback.get("timestamp", datetime.now().isoformat())
            }

            # Add to long-term memory
            self.long_term.add_memory(
                content=content,
                source_type="feedback",
                metadata=metadata,
                importance=0.7  # Feedback is relatively important
            )

            logger.info(f"Added feedback to memory: {feedback.get('id')}")
            return True

        except Exception as e:
            logger.error(f"Error adding feedback to memory: {e}")
            return False

    def get_feedback_memories(self, feedback_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get feedback memories from long-term memory.

        Args:
            feedback_type: Optional type of feedback to filter by
            limit: Maximum number of memories to return

        Returns:
            List of feedback memories
        """
        if not self.long_term:
            logger.warning("Long-term memory not available for retrieving feedback")
            return []

        try:
            # Build search query
            query = "source_type:feedback"
            if feedback_type:
                query += f" metadata.feedback_type:{feedback_type}"

            # Search for feedback memories
            memories = self.long_term.search_memories(query, limit=limit)

            # Format results
            results = []
            for memory in memories:
                metadata = memory.get("metadata", {})

                result = {
                    "id": metadata.get("feedback_id"),
                    "content": memory.get("content", ""),
                    "type": metadata.get("feedback_type"),
                    "prompt": metadata.get("prompt"),
                    "sentiment": metadata.get("sentiment"),
                    "intent_type": metadata.get("intent_type"),
                    "timestamp": metadata.get("timestamp"),
                    "created_at": memory.get("created_at")
                }

                results.append(result)

            return results

        except Exception as e:
            logger.error(f"Error getting feedback memories: {e}")
            return []

    def close(self) -> None:
        """Close memory manager and save state."""
        # Persist any remaining short-term memory
        if self.auto_persist:
            self.persist_short_term_memory()

        # Close long-term memory
        self.long_term.close()

        logger.info("EnhancedMemoryManager closed")
