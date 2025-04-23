"""
WebSocket-integrated memory implementation for Coda Lite.
Extends EnhancedMemoryManager to emit events via WebSocket.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple

from memory.enhanced_memory_manager import EnhancedMemoryManager
from memory.long_term import LongTermMemory
from memory.encoder import MemoryEncoder
from websocket.integration import CodaWebSocketIntegration

logger = logging.getLogger("coda.memory.websocket")

class WebSocketEnhancedMemoryManager(EnhancedMemoryManager):
    """Memory manager with WebSocket integration for event emission."""

    def __init__(
        self,
        websocket_integration: CodaWebSocketIntegration,
        config: Dict[str, Any],
        max_turns: int = 20,
        memory_path: str = "data/memory/long_term",
        embedding_model: str = "all-MiniLM-L6-v2",
        device: str = "cpu",
        chunk_size: int = 200,
        chunk_overlap: int = 50
    ):
        """
        Initialize the WebSocketEnhancedMemoryManager.

        Args:
            websocket_integration: The WebSocket integration instance
            config: Configuration dictionary
            max_turns: Maximum number of conversation turns to keep in short-term memory
            memory_path: Path to store long-term memories
            embedding_model: Model to use for embeddings
            device: Device to use for embeddings ("cpu" or "cuda")
            chunk_size: Size of text chunks for memory encoding
            chunk_overlap: Overlap between chunks
        """
        super().__init__(
            config=config,
            max_turns=max_turns,
            memory_path=memory_path,
            embedding_model=embedding_model,
            device=device,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        self.ws = websocket_integration
        logger.info("WebSocketEnhancedMemoryManager initialized with WebSocket integration")

    def add_turn(self, role: str, content: str) -> None:
        """
        Add a conversation turn to short-term memory with WebSocket events.

        Args:
            role: The role of the speaker ("user", "assistant", "system")
            content: The content of the message
        """
        # Add the turn to memory
        super().add_turn(role, content)

        # Emit conversation turn event
        self.ws.add_conversation_turn(role, content)

        logger.debug(f"Added conversation turn: {role}")

    def add_memory(
        self,
        content: str,
        memory_type: str = "fact",
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a memory to long-term storage with WebSocket events.

        Args:
            content: The memory content
            memory_type: The type of memory
            importance: The importance score (0.0 to 1.0)
            metadata: Additional metadata

        Returns:
            The memory ID
        """
        # Add the memory
        memory_id = super().add_memory(
            content=content,
            memory_type=memory_type,
            importance=importance,
            metadata=metadata
        )

        # Emit memory store event
        self.ws.memory_store(
            content=content,
            memory_type=memory_type,
            importance=importance,
            memory_id=memory_id
        )

        logger.debug(f"Added memory: {memory_id} - {content[:30]}...")

        return memory_id

    def get_memories(
        self,
        query: str,
        limit: int = 5,
        min_relevance: float = 0.0,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories from long-term storage with WebSocket events.

        Args:
            query: The search query
            limit: Maximum number of memories to retrieve
            min_relevance: Minimum relevance score
            memory_type: Filter by memory type

        Returns:
            List of memories
        """
        # Get the memories
        memories = super().get_memories(
            query=query,
            limit=limit,
            min_relevance=min_relevance,
            memory_type=memory_type
        )

        # Emit memory retrieve event
        self.ws.memory_retrieve(
            query=query,
            results=memories
        )

        logger.debug(f"Retrieved {len(memories)} memories for query: {query}")

        return memories

    def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        importance: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update a memory in long-term storage with WebSocket events.

        Args:
            memory_id: The memory ID
            content: New content (if updating)
            importance: New importance score (if updating)
            metadata: New metadata (if updating)

        Returns:
            True if successful, False otherwise
        """
        # Get the original memory
        original_memory = self.long_term.get_memory_by_id(memory_id)

        # Update the memory
        result = super().update_memory(
            memory_id=memory_id,
            content=content,
            importance=importance,
            metadata=metadata
        )

        if result:
            # Emit memory update events for each changed field
            if content is not None and original_memory and original_memory.get("content") != content:
                self.ws.memory_update(
                    memory_id=memory_id,
                    field="content",
                    old_value=original_memory.get("content"),
                    new_value=content
                )

            if importance is not None and original_memory and original_memory.get("importance") != importance:
                self.ws.memory_update(
                    memory_id=memory_id,
                    field="importance",
                    old_value=original_memory.get("importance"),
                    new_value=importance
                )

            if metadata is not None and original_memory:
                original_metadata = original_memory.get("metadata", {})
                for key, value in metadata.items():
                    if key not in original_metadata or original_metadata[key] != value:
                        self.ws.memory_update(
                            memory_id=memory_id,
                            field=f"metadata.{key}",
                            old_value=original_metadata.get(key),
                            new_value=value
                        )

            logger.debug(f"Updated memory: {memory_id}")

        return result

    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory from long-term storage with WebSocket events.

        Args:
            memory_id: The memory ID

        Returns:
            True if successful, False otherwise
        """
        # Get the original memory
        original_memory = self.long_term.get_memory_by_id(memory_id)

        # Delete the memory
        result = super().delete_memory(memory_id)

        if result and original_memory:
            # Emit memory update event (deletion)
            self.ws.memory_update(
                memory_id=memory_id,
                field="deleted",
                old_value=False,
                new_value=True
            )

            logger.debug(f"Deleted memory: {memory_id}")

        return result

    def get_enhanced_context(
        self,
        query: str,
        max_tokens: int = 800,
        include_system: bool = True
    ) -> List[Dict[str, str]]:
        """
        Get enhanced context for a query with WebSocket events.

        Args:
            query: The query to get context for
            max_tokens: Maximum number of tokens to include
            include_system: Whether to include system messages

        Returns:
            List of messages for context
        """
        # Get the enhanced context
        context = super().get_enhanced_context(
            query=query,
            max_tokens=max_tokens,
            include_system=include_system
        )

        # If we have retrieved memories, emit memory retrieve event
        if hasattr(self, 'last_retrieved_memories') and self.last_retrieved_memories:
            self.ws.memory_retrieve(
                query=query,
                results=self.last_retrieved_memories
            )

            logger.debug(f"Retrieved {len(self.last_retrieved_memories)} memories for context: {query}")

        return context

    def clear_short_term(self) -> None:
        """Clear short-term memory with WebSocket events."""
        # Clear short-term memory
        super().clear_short_term()

        # Emit memory update event (clear short-term)
        self.ws.memory_update(
            memory_id="short_term",
            field="cleared",
            old_value=False,
            new_value=True
        )

        logger.debug("Cleared short-term memory")

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics with WebSocket events.

        Returns:
            Dictionary of memory statistics
        """
        # Get memory statistics
        stats = super().get_memory_stats()

        # Emit system info event with memory stats
        self.ws.system_info({
            "memory_stats": stats
        })

        logger.debug(f"Memory stats: {stats}")

        return stats
