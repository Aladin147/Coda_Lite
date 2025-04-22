"""
Memory encoding for Coda Lite.

This module provides utilities for encoding memories from conversations.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger("coda.memory.encoder")

class MemoryEncoder:
    """
    Encodes memories from conversations for long-term storage.

    Responsibilities:
    - Extract meaningful chunks from conversations
    - Identify important information
    - Assign metadata and importance scores
    - Format memories for storage
    """

    def __init__(self,
                 chunk_size: int = 200,
                 overlap: int = 50,
                 min_chunk_length: int = 50):
        """
        Initialize the memory encoder.

        Args:
            chunk_size: Target size of memory chunks in characters
            overlap: Overlap between chunks in characters
            min_chunk_length: Minimum length of a chunk to be stored
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_length = min_chunk_length

        # Patterns for identifying important information
        self.importance_patterns = {
            "preference": r"(?:prefer|like|love|hate|dislike|favorite|enjoy)",
            "personal_info": r"(?:my|I|name|age|birthday|address|phone|email)",
            "question": r"\?",
            "instruction": r"(?:please|could you|can you|would you)",
            "fact": r"(?:is|are|was|were|has|have|had|will be|won't be)"
        }

        logger.info(f"MemoryEncoder initialized with chunk_size={chunk_size}, overlap={overlap}")

    def encode_conversation(self,
                           turns: List[Dict[str, Any]],
                           include_system: bool = False) -> List[Dict[str, Any]]:
        """
        Encode a conversation into memory chunks.

        Args:
            turns: List of conversation turns
            include_system: Whether to include system messages

        Returns:
            List of memory chunks with metadata
        """
        # Filter turns if needed
        if not include_system:
            turns = [t for t in turns if t.get("role") != "system"]

        # Group turns by speaker
        grouped_turns = self._group_turns(turns)

        # Create chunks from grouped turns
        chunks = []
        for group in grouped_turns:
            group_chunks = self._create_chunks(group)
            chunks.extend(group_chunks)

        # Assign importance scores and metadata
        encoded_memories = []
        for chunk in chunks:
            importance = self._calculate_importance(chunk["content"])

            # Create memory
            memory = {
                "content": chunk["content"],
                "source_type": "conversation",
                "importance": importance,
                "metadata": {
                    "speakers": chunk["speakers"],
                    "turn_ids": chunk["turn_ids"],
                    "timestamp": chunk["timestamp"],
                    "topics": self._extract_topics(chunk["content"])
                }
            }

            encoded_memories.append(memory)

        logger.info(f"Encoded {len(encoded_memories)} memories from {len(turns)} turns")

        return encoded_memories

    def _group_turns(self, turns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Group consecutive turns by the same speaker.

        Args:
            turns: List of conversation turns

        Returns:
            List of grouped turns
        """
        if not turns:
            return []

        grouped = []
        current_group = {
            "role": turns[0]["role"],
            "content": turns[0]["content"],
            "turn_ids": [turns[0].get("turn_id", 0)],
            "timestamp": turns[0].get("timestamp", "")
        }

        for turn in turns[1:]:
            if turn["role"] == current_group["role"]:
                # Same speaker, append content
                current_group["content"] += "\n" + turn["content"]
                current_group["turn_ids"].append(turn.get("turn_id", 0))
                # Update timestamp to the latest
                current_group["timestamp"] = turn.get("timestamp", current_group["timestamp"])
            else:
                # New speaker, start a new group
                grouped.append(current_group)
                current_group = {
                    "role": turn["role"],
                    "content": turn["content"],
                    "turn_ids": [turn.get("turn_id", 0)],
                    "timestamp": turn.get("timestamp", "")
                }

        # Add the last group
        grouped.append(current_group)

        return grouped

    def _create_chunks(self, group: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create chunks from a grouped turn.

        Args:
            group: Grouped turn

        Returns:
            List of chunks
        """
        content = group["content"]
        role = group["role"]

        # If content is short enough, keep it as one chunk
        if len(content) <= self.chunk_size:
            return [{
                "content": content,
                "speakers": [role],
                "turn_ids": group["turn_ids"],
                "timestamp": group["timestamp"]
            }]

        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', content)

        chunks = []
        current_chunk = ""
        current_turn_ids = []

        for sentence in sentences:
            # If adding this sentence would exceed chunk size, save current chunk and start a new one
            if len(current_chunk) + len(sentence) > self.chunk_size and len(current_chunk) >= self.min_chunk_length:
                chunks.append({
                    "content": current_chunk.strip(),
                    "speakers": [role],
                    "turn_ids": group["turn_ids"],
                    "timestamp": group["timestamp"]
                })

                # Start new chunk with overlap
                words = current_chunk.split()
                overlap_words = words[-min(len(words), self.overlap // 4):]  # Roughly estimate words in overlap
                current_chunk = " ".join(overlap_words) + " " + sentence
            else:
                # Add sentence to current chunk
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence

        # Add the last chunk if it's not empty and meets minimum length
        if current_chunk and len(current_chunk) >= self.min_chunk_length:
            chunks.append({
                "content": current_chunk.strip(),
                "speakers": [role],
                "turn_ids": group["turn_ids"],
                "timestamp": group["timestamp"]
            })

        return chunks

    def _calculate_importance(self, text: str) -> float:
        """
        Calculate importance score for a text chunk.

        Args:
            text: Text content

        Returns:
            Importance score (0.0 to 1.0)
        """
        # Base importance
        importance = 0.5

        # Check for important patterns
        for pattern_name, pattern in self.importance_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Different patterns have different weights
                if pattern_name == "preference":
                    importance += 0.2
                elif pattern_name == "personal_info":
                    importance += 0.3
                elif pattern_name == "question":
                    importance += 0.1
                elif pattern_name == "instruction":
                    importance += 0.1
                elif pattern_name == "fact":
                    importance += 0.1

        # Cap at 1.0
        importance = min(importance, 1.0)

        return importance

    def _extract_topics(self, text: str) -> List[str]:
        """
        Extract potential topics from text.

        Args:
            text: Text content

        Returns:
            List of potential topics
        """
        # This is a simple implementation that could be improved with NLP
        # For now, just extract nouns and noun phrases

        # Split into words and remove punctuation
        words = re.findall(r'\b\w+\b', text.lower())

        # Filter out common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "is", "are", "was", "were",
                     "be", "been", "being", "have", "has", "had", "do", "does", "did",
                     "i", "you", "he", "she", "it", "we", "they", "my", "your", "his", "her",
                     "its", "our", "their", "this", "that", "these", "those", "am", "is", "are",
                     "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
                     "did", "doing", "can", "could", "will", "would", "shall", "should", "may",
                     "might", "must", "to", "for", "with", "about", "against", "between", "into",
                     "through", "during", "before", "after", "above", "below", "from", "up", "down",
                     "in", "out", "on", "off", "over", "under", "again", "further", "then", "once",
                     "here", "there", "when", "where", "why", "how", "all", "any", "both", "each",
                     "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only",
                     "own", "same", "so", "than", "too", "very", "s", "t", "just", "don", "now"}

        filtered_words = [w for w in words if w not in stop_words and len(w) > 3]

        # Count word frequencies
        word_counts = {}
        for word in filtered_words:
            word_counts[word] = word_counts.get(word, 0) + 1

        # Get top words by frequency
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        top_words = [word for word, count in sorted_words[:5] if count > 1]

        return top_words

    def encode_fact(self,
                   fact: str,
                   source: str = "user",
                   metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Encode a fact for long-term storage.

        Args:
            fact: The fact text
            source: Source of the fact
            metadata: Additional metadata

        Returns:
            Encoded memory
        """
        if metadata is None:
            metadata = {}

        importance = self._calculate_importance(fact)

        # Increase importance for facts
        importance = min(importance + 0.2, 1.0)

        memory = {
            "content": fact,
            "source_type": "fact",
            "importance": importance,
            "metadata": {
                "source": source,
                "topics": self._extract_topics(fact),
                **metadata
            }
        }

        return memory

    def encode_preference(self,
                         preference: str,
                         metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Encode a user preference for long-term storage.

        Args:
            preference: The preference text
            metadata: Additional metadata

        Returns:
            Encoded memory
        """
        if metadata is None:
            metadata = {}

        # Preferences are important
        importance = 0.8

        memory = {
            "content": preference,
            "source_type": "preference",
            "importance": importance,
            "metadata": {
                "topics": self._extract_topics(preference),
                **metadata
            }
        }

        return memory

    def encode_feedback(self,
                       feedback: Dict[str, Any],
                       metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Encode user feedback for long-term storage.

        Args:
            feedback: Feedback dictionary with type, prompt, response, sentiment, etc.
            metadata: Additional metadata

        Returns:
            Encoded memory
        """
        if metadata is None:
            metadata = {}

        # Create content from response
        content = f"Feedback: {feedback.get('response')}"

        # Feedback importance varies by type and sentiment
        importance = 0.7  # Base importance

        # Adjust importance based on sentiment
        sentiment = feedback.get("sentiment", "neutral")
        if sentiment == "positive":
            importance += 0.1
        elif sentiment == "negative":
            importance += 0.2  # Negative feedback is more important to learn from

        # Create metadata
        feedback_metadata = {
            "feedback_type": str(feedback.get("type")),
            "prompt": feedback.get("prompt"),
            "sentiment": sentiment,
            "intent_type": feedback.get("intent_type"),
            "timestamp": feedback.get("timestamp"),
            "turn": feedback.get("turn"),
            "topics": self._extract_topics(content),
            **metadata
        }

        memory = {
            "content": content,
            "source_type": "feedback",
            "importance": min(importance, 1.0),
            "metadata": feedback_metadata
        }

        return memory
