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
from .memory_snapshot import MemorySnapshotManager
from .temporal_weighting import TemporalWeightingSystem
from .active_recall import ActiveRecallSystem
from .self_testing import MemorySelfTestingFramework

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

        # Initialize memory snapshot manager
        snapshot_dir = config.get("memory", {}).get("snapshot_dir", "data/memory/snapshots")
        auto_snapshot = config.get("memory", {}).get("auto_snapshot", False)
        snapshot_interval = config.get("memory", {}).get("snapshot_interval", 10)

        self.snapshot_manager = MemorySnapshotManager(
            memory_manager=self,
            snapshot_dir=snapshot_dir,
            auto_snapshot=auto_snapshot,
            snapshot_interval=snapshot_interval
        )

        # Initialize temporal weighting system
        self.temporal_weighting = TemporalWeightingSystem(config)

        # Initialize active recall system
        self.active_recall = ActiveRecallSystem(memory_manager=self, config=config)

        # Initialize self-testing framework
        self.self_testing = MemorySelfTestingFramework(memory_manager=self, config=config)

        # Track recent topics and tools
        self.recent_topics = []
        self.last_tool_used = None

        # Memory persistence settings
        self.auto_persist = config.get("memory", {}).get("auto_persist", True)
        self.persist_interval = config.get("memory", {}).get("persist_interval", 5)
        self.turn_count_at_last_persist = 0

        logger.info("EnhancedMemoryManager initialized with active recall and self-testing")

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

        # Check if we should create an automatic snapshot
        if role == "assistant":
            self.snapshot_manager.check_auto_snapshot()

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
                            max_memories: int = 5,  # Increased from 3 to 5 for better recall
                            include_system: bool = True) -> List[Dict[str, str]]:
        """
        Get enhanced conversation context with relevant long-term memories.

        Args:
            user_input: Current user input
            max_tokens: Maximum number of tokens for short-term context
            max_memories: Maximum number of long-term memories to include
            include_system: Whether to include system messages in the context

        Returns:
            Enhanced context with relevant memories
        """
        # Get short-term context
        context = self.short_term.get_context(max_tokens=max_tokens)

        try:
            # Retrieve relevant memories with a lower similarity threshold for better recall
            memories = self.retrieve_relevant_memories(
                query=user_input,
                limit=max_memories,
                min_similarity=0.3  # Lower threshold for better recall
            )

            # Store the retrieved memories for later access
            self.last_retrieved_memories = memories

            # If we have memories, add them to the context
            if memories:
                # Find position to insert memories (after system message if present)
                insert_pos = 1 if context and context[0]["role"] == "system" else 0

                # Group memories by type for better organization
                memory_types = {}
                for memory in memories:
                    memory_type = memory.get("metadata", {}).get("source_type", "general")
                    if memory_type not in memory_types:
                        memory_types[memory_type] = []
                    memory_types[memory_type].append(memory)

                # Format memories as a system message with type grouping
                memory_content = "Relevant information from your memory:\n\n"

                # Add facts first (if any)
                if "fact" in memory_types:
                    memory_content += "Facts:\n"
                    for i, memory in enumerate(memory_types["fact"]):
                        memory_content += f"- {memory['content']}\n"
                    memory_content += "\n"

                # Add preferences next (if any)
                if "preference" in memory_types:
                    memory_content += "Preferences:\n"
                    for i, memory in enumerate(memory_types["preference"]):
                        memory_content += f"- {memory['content']}\n"
                    memory_content += "\n"

                # Add conversation memories last (if any)
                if "conversation" in memory_types:
                    memory_content += "From previous conversations:\n"
                    for i, memory in enumerate(memory_types["conversation"]):
                        memory_content += f"- {memory['content']}\n"
                    memory_content += "\n"

                # Add any other memory types
                for memory_type, memories_list in memory_types.items():
                    if memory_type not in ["fact", "preference", "conversation"]:
                        memory_content += f"{memory_type.capitalize()}:\n"
                        for memory in memories_list:
                            memory_content += f"- {memory['content']}\n"
                        memory_content += "\n"

                # Insert memories
                context.insert(insert_pos, {
                    "role": "system",
                    "content": memory_content
                })

                logger.info(f"Added {len(memories)} memories to context, grouped by type")

        except Exception as e:
            logger.error(f"Error retrieving memories: {e}", exc_info=True)
            # Continue with just the short-term context if there's an error

        return context

    def retrieve_relevant_memories(self,
                                 query: str,
                                 limit: int = 5,  # Increased from 3 to 5
                                 min_similarity: float = 0.3,
                                 apply_temporal_weighting: bool = True) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories based on the query.

        Args:
            query: The query text
            limit: Maximum number of memories to retrieve
            min_similarity: Minimum similarity score (lowered for better recall)
            apply_temporal_weighting: Whether to apply temporal weighting to the results

        Returns:
            List of relevant memories
        """
        try:
            # Try to retrieve memories from long-term memory
            # Retrieve more memories than needed for better filtering with temporal weighting
            retrieve_limit = limit * 2 if apply_temporal_weighting else limit

            memories = self.long_term.retrieve_memories(
                query=query,
                limit=retrieve_limit,
                min_similarity=min_similarity
            )

            # Log the results
            if memories:
                logger.info(f"Retrieved {len(memories)} memories for query: {query[:50]}...")
                for i, memory in enumerate(memories):
                    similarity = memory.get('similarity', 0)
                    content_preview = memory.get('content', '')[:50] + '...'
                    logger.debug(f"Memory {i+1}: similarity={similarity:.2f}, content={content_preview}")
            else:
                logger.info(f"No memories found for query: {query[:50]}...")

                # If no memories found with semantic search, try keyword search
                # This is a fallback mechanism to ensure we get some results
                logger.debug("Attempting keyword-based fallback search")

                # Extract keywords from the query (simple approach)
                keywords = [word.lower() for word in query.split() if len(word) > 3]

                if keywords:
                    # Get all memories and filter manually
                    all_memories = []
                    for memory_id in self.long_term.metadata["memories"]:
                        memory = self.long_term.get_memory_by_id(memory_id)
                        if memory:
                            all_memories.append(memory)

                    # Score memories based on keyword matches
                    scored_memories = []
                    for memory in all_memories:
                        content = memory.get('content', '').lower()
                        score = sum(1 for keyword in keywords if keyword in content)
                        if score > 0:
                            memory['similarity'] = score / len(keywords)  # Normalize score
                            scored_memories.append(memory)

                    # Sort by score and take top results
                    scored_memories.sort(key=lambda x: x.get('similarity', 0), reverse=True)
                    memories = scored_memories[:retrieve_limit]

                    if memories:
                        logger.info(f"Found {len(memories)} memories using keyword search")

            # Apply temporal weighting if requested and memories were found
            if apply_temporal_weighting and memories:
                # Apply temporal weighting to adjust scores based on recency and importance
                weighted_memories = self.temporal_weighting.apply_temporal_weighting(
                    memories=memories,
                    recency_boost=True
                )

                # Take the top memories after weighting
                memories = weighted_memories[:limit]

                logger.info(f"Applied temporal weighting to {len(weighted_memories)} memories, returning top {len(memories)}")

                # Log the weighted results
                for i, memory in enumerate(memories):
                    final_score = memory.get('final_score', 0)
                    decay_factor = memory.get('decay_factor', 1.0)
                    recency_score = memory.get('recency_score', 0.5)
                    content_preview = memory.get('content', '')[:50] + '...'
                    logger.debug(f"Weighted Memory {i+1}: final_score={final_score:.2f}, decay={decay_factor:.2f}, recency={recency_score:.2f}, content={content_preview}")
            elif memories and len(memories) > limit:
                # If not applying temporal weighting, just take the top memories by similarity
                memories = memories[:limit]

            return memories

        except Exception as e:
            logger.error(f"Error retrieving memories: {e}", exc_info=True)
            return []  # Return empty list on error

    def persist_short_term_memory(self) -> int:
        """
        Persist short-term memory to long-term storage.

        Returns:
            Number of memories stored
        """
        try:
            # Get all turns from short-term memory
            turns = list(self.short_term.turns)

            # Skip if no turns
            if not turns:
                logger.info("No turns to persist")
                return 0

            # Skip if we've already persisted these turns
            if self.turn_count_at_last_persist >= self.short_term.turn_count:
                logger.info("Turns already persisted")
                return 0

            # Log the turns we're about to persist
            logger.debug(f"Persisting {len(turns)} turns from short-term memory")
            for i, turn in enumerate(turns):
                role = turn.get('role', 'unknown')
                content_preview = turn.get('content', '')[:50] + '...' if len(turn.get('content', '')) > 50 else turn.get('content', '')
                logger.debug(f"Turn {i+1}: role={role}, content={content_preview}")

            # Encode conversation into memory chunks
            memories = self.encoder.encode_conversation(turns)
            logger.debug(f"Encoded {len(memories)} memory chunks from {len(turns)} turns")

            # Store memories
            stored_count = 0
            for memory in memories:
                try:
                    # Ensure memory has required fields
                    if "content" not in memory:
                        logger.warning(f"Skipping memory chunk without content: {memory}")
                        continue

                    # Add memory to long-term storage
                    memory_id = self.long_term.add_memory(
                        content=memory["content"],
                        source_type=memory.get("source_type", "conversation"),
                        importance=memory.get("importance", 0.5),
                        metadata=memory.get("metadata", {})
                    )

                    # Log the persisted memory
                    content_preview = memory["content"][:50] + '...' if len(memory["content"]) > 50 else memory["content"]
                    logger.debug(f"Persisted memory {memory_id}: {content_preview}")

                    stored_count += 1
                except Exception as e:
                    logger.error(f"Error persisting memory chunk: {e}", exc_info=True)

            # Update last persist turn count
            self.turn_count_at_last_persist = self.short_term.turn_count

            logger.info(f"Persisted {stored_count} memories from short-term memory")
            return stored_count

        except Exception as e:
            logger.error(f"Error persisting short-term memory: {e}", exc_info=True)
            return 0

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

    def search_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant memories based on a query.

        Args:
            query: The search query
            limit: Maximum number of results to return

        Returns:
            List of memory dictionaries
        """
        return self.long_term.retrieve_memories(query, limit=limit)

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

        # Get active recall stats
        try:
            active_recall_stats = self.active_recall.get_memory_health_metrics()
        except Exception as e:
            logger.error(f"Error getting active recall stats: {e}")
            active_recall_stats = {"error": str(e)}

        # Get self-testing stats
        try:
            self_testing_stats = self.self_testing.get_metrics()
        except Exception as e:
            logger.error(f"Error getting self-testing stats: {e}")
            self_testing_stats = {"error": str(e)}

        return {
            "short_term": short_term_stats,
            "long_term": long_term_stats,
            "recent_topics": self.recent_topics,
            "last_tool_used": self.last_tool_used,
            "active_recall": active_recall_stats,
            "self_testing": self_testing_stats
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

    def create_snapshot(self, snapshot_id: Optional[str] = None) -> str:
        """
        Create a snapshot of the current memory state.

        Args:
            snapshot_id: Optional ID for the snapshot

        Returns:
            Snapshot ID
        """
        return self.snapshot_manager.create_snapshot(snapshot_id)

    def save_snapshot(self, snapshot_id: Optional[str] = None, filepath: Optional[str] = None) -> str:
        """
        Create and save a snapshot to disk.

        Args:
            snapshot_id: Optional ID for the snapshot (created if None)
            filepath: Optional file path (generated if None)

        Returns:
            Path to the saved snapshot file
        """
        # Create snapshot if ID not provided
        if snapshot_id is None:
            snapshot_id = self.snapshot_manager.create_snapshot()

        # Save snapshot
        return self.snapshot_manager.save_snapshot(snapshot_id, filepath)

    def load_snapshot(self, filepath: str) -> str:
        """
        Load a snapshot from disk.

        Args:
            filepath: Path to the snapshot file

        Returns:
            Snapshot ID
        """
        return self.snapshot_manager.load_snapshot(filepath)

    def apply_snapshot(self, snapshot_id: str) -> bool:
        """
        Apply a snapshot to the memory system.

        Args:
            snapshot_id: ID of the snapshot to apply

        Returns:
            True if successful
        """
        return self.snapshot_manager.apply_snapshot(snapshot_id)

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """
        List all snapshots with metadata.

        Returns:
            List of snapshot metadata
        """
        return self.snapshot_manager.list_snapshots()

    def enable_auto_snapshot(self, interval: int = 10) -> None:
        """
        Enable automatic snapshots.

        Args:
            interval: Number of turns between automatic snapshots
        """
        self.snapshot_manager.enable_auto_snapshot(interval)

    def disable_auto_snapshot(self) -> None:
        """Disable automatic snapshots."""
        self.snapshot_manager.disable_auto_snapshot()

    def update_memory(self,
                      memory_id: str,
                      content: Optional[str] = None,
                      importance: Optional[float] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update a memory in long-term storage.

        Args:
            memory_id: The memory ID
            content: New content (if updating)
            importance: New importance score (if updating)
            metadata: New metadata (if updating)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the original memory
            original_memory = self.long_term.get_memory_by_id(memory_id)
            if not original_memory:
                logger.warning(f"Memory {memory_id} not found for update")
                return False

            # Create updated memory
            updated_memory = original_memory.copy()

            # Update fields if provided
            if content is not None:
                updated_memory["content"] = content

            if importance is not None:
                updated_memory["importance"] = importance

            if metadata is not None:
                # Get current metadata
                current_metadata = updated_memory.get("metadata", {})

                # Merge metadata
                merged_metadata = {**current_metadata, **metadata}
                updated_memory["metadata"] = merged_metadata

            # Update the memory
            result = self.long_term.update_memory(memory_id, updated_memory)

            if result:
                logger.info(f"Updated memory {memory_id}")

            return result

        except Exception as e:
            logger.error(f"Error updating memory: {e}", exc_info=True)
            return False

    def reinforce_memory(self,
                        memory_id: str,
                        reinforcement_strength: float = 1.0) -> bool:
        """
        Reinforce a memory to make it more resistant to forgetting.

        Args:
            memory_id: ID of the memory to reinforce
            reinforcement_strength: Strength of reinforcement (0.0 to 1.0)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the memory
            memory = self.long_term.get_memory_by_id(memory_id)
            if not memory:
                logger.warning(f"Memory {memory_id} not found for reinforcement")
                return False

            # Apply reinforcement
            updated_memory = self.temporal_weighting.reinforce_memory(
                memory=memory,
                reinforcement_strength=reinforcement_strength
            )

            # Update the memory in long-term storage
            self.long_term.update_memory(memory_id, updated_memory)

            logger.info(f"Reinforced memory {memory_id} with strength {reinforcement_strength}")
            return True

        except Exception as e:
            logger.error(f"Error reinforcing memory: {e}", exc_info=True)
            return False

    def search_memories(self,
                       query: str,
                       memory_type: Optional[str] = None,
                       min_importance: float = 0.0,
                       limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for memories based on a query.

        Args:
            query: Search query
            memory_type: Optional filter by memory type
            min_importance: Minimum importance score
            limit: Maximum number of results

        Returns:
            List of matching memories
        """
        try:
            # First try semantic search
            memories = self.retrieve_relevant_memories(
                query=query,
                limit=limit,
                min_similarity=0.2,  # Lower threshold for search
                apply_temporal_weighting=True
            )

            # If no results, try keyword search
            if not memories:
                # Extract keywords from the query
                keywords = self._extract_keywords(query)

                if keywords:
                    # Get all memories and filter manually
                    all_memories = []
                    for memory_id in self.long_term.metadata["memories"]:
                        memory = self.long_term.get_memory_by_id(memory_id)
                        if memory:
                            all_memories.append(memory)

                    # Score memories based on keyword matches
                    scored_memories = []
                    for memory in all_memories:
                        content = memory.get('content', '').lower()
                        score = sum(1 for keyword in keywords if keyword in content)
                        if score > 0:
                            memory['similarity'] = score / len(keywords)  # Normalize score
                            scored_memories.append(memory)

                    # Sort by score and take top results
                    scored_memories.sort(key=lambda x: x.get('similarity', 0), reverse=True)
                    memories = scored_memories[:limit]

            # Filter by memory type and importance
            if memory_type or min_importance > 0:
                filtered_memories = []
                for memory in memories:
                    # Check memory type
                    if memory_type and memory.get("source_type") != memory_type:
                        continue

                    # Check importance
                    if memory.get("importance", 0) < min_importance:
                        continue

                    filtered_memories.append(memory)

                memories = filtered_memories

            return memories

        except Exception as e:
            logger.error(f"Error searching memories: {e}", exc_info=True)
            return []

    def forget_memories(self, max_memories: Optional[int] = None) -> int:
        """
        Apply forgetting mechanism to remove less important memories.

        Args:
            max_memories: Optional maximum number of memories to keep
                         (if None, uses the configured max_memories)

        Returns:
            Number of memories forgotten
        """
        try:
            # Get current memory count
            memory_count = len(self.long_term.metadata.get("memories", {}))

            # Get maximum memories
            if max_memories is None:
                max_memories = self.long_term.max_memories

            # If we're under the limit, no need to forget
            if memory_count <= max_memories:
                logger.info(f"Memory count {memory_count} is under limit {max_memories}, no forgetting needed")
                return 0

            # Get all memories
            memories = []
            for memory_id, memory_data in self.long_term.metadata.get("memories", {}).items():
                memory = self.long_term.get_memory_by_id(memory_id)
                if memory:
                    memory["id"] = memory_id
                    memories.append(memory)

            # Apply temporal weighting to determine which memories to forget
            forgotten_count = 0
            for memory in memories:
                # Check if we should forget this memory
                if self.temporal_weighting.should_forget_memory(
                    memory=memory,
                    current_memory_count=memory_count - forgotten_count,
                    max_memories=max_memories
                ):
                    # Remove the memory
                    memory_id = memory.get("id")
                    if memory_id:
                        self.long_term.remove_memory(memory_id)
                        forgotten_count += 1
                        logger.debug(f"Forgot memory {memory_id}: {memory.get('content', '')[:50]}...")

            logger.info(f"Forgot {forgotten_count} memories based on temporal weighting")
            return forgotten_count

        except Exception as e:
            logger.error(f"Error applying forgetting mechanism: {e}", exc_info=True)
            return 0

    def get_due_reviews(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get memories due for review.

        Args:
            limit: Maximum number of memories to return

        Returns:
            List of memories due for review
        """
        return self.active_recall.get_due_reviews(limit)

    def generate_review_question(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a review question for a memory.

        Args:
            memory: The memory to generate a question for

        Returns:
            Dictionary with question, answer, and metadata
        """
        return self.active_recall.generate_review_question(memory)

    def record_review(self, memory_id: str, success: bool) -> None:
        """
        Record a memory review result.

        Args:
            memory_id: The memory ID
            success: Whether the review was successful
        """
        self.active_recall.record_review(memory_id, success)

    def run_memory_maintenance(self) -> Dict[str, Any]:
        """
        Run memory maintenance tasks.

        This includes:
        - Active recall scheduled tasks
        - Self-testing consistency checks
        - Memory forgetting mechanism

        Returns:
            Dictionary with maintenance results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "active_recall": None,
            "self_testing": None,
            "forgetting": None
        }

        # Run active recall tasks
        try:
            results["active_recall"] = self.active_recall.run_scheduled_tasks()
        except Exception as e:
            logger.error(f"Error running active recall tasks: {e}")
            results["active_recall"] = {"error": str(e)}

        # Run self-testing tasks
        try:
            results["self_testing"] = self.self_testing.run_consistency_check()
        except Exception as e:
            logger.error(f"Error running self-testing tasks: {e}")
            results["self_testing"] = {"error": str(e)}

        # Run forgetting mechanism
        try:
            forgotten_count = self.forget_memories()
            results["forgetting"] = {
                "forgotten_count": forgotten_count,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error running forgetting mechanism: {e}")
            results["forgetting"] = {"error": str(e)}

        return results

    def test_memory_retrieval(self, query: str, expected_memory_ids: List[str]) -> Dict[str, Any]:
        """
        Test memory retrieval accuracy.

        Args:
            query: Query to test
            expected_memory_ids: List of memory IDs that should be retrieved

        Returns:
            Dictionary with test results
        """
        return self.self_testing.test_memory_retrieval(query, expected_memory_ids)

    def run_retrieval_test_suite(self) -> Dict[str, Any]:
        """
        Run a suite of retrieval tests.

        Returns:
            Dictionary with test results
        """
        return self.self_testing.run_retrieval_test_suite()

    def close(self) -> None:
        """Close memory manager and save state."""
        # Create final snapshot if auto-snapshot is enabled
        if self.snapshot_manager.auto_snapshot:
            self.create_snapshot("final_snapshot")

        # Persist any remaining short-term memory
        if self.auto_persist:
            self.persist_short_term_memory()

        # Close long-term memory
        self.long_term.close()

        logger.info("EnhancedMemoryManager closed")
