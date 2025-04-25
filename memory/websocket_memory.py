"""
WebSocket-integrated memory implementation for Coda Lite.
Extends EnhancedMemoryManager to emit events via WebSocket.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple

from memory.enhanced_memory_manager import EnhancedMemoryManager
from memory.short_term import MemoryManager as ShortTermMemory
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
        short_term_memory: Optional[ShortTermMemory] = None,
        long_term_memory: Optional[LongTermMemory] = None
    ):
        """
        Initialize the WebSocketEnhancedMemoryManager.

        Args:
            websocket_integration: The WebSocket integration instance
            config: Configuration dictionary
            short_term_memory: Optional existing short-term memory instance
            long_term_memory: Optional existing long-term memory instance
        """
        # Ensure config has the expected structure
        if not isinstance(config, dict):
            logger.warning(f"Config is not a dictionary, got {type(config)}. Creating empty config.")
            config = {}

        # Ensure memory section exists
        if "memory" not in config:
            logger.warning("Memory section missing from config, creating default memory config")
            config["memory"] = {
                "long_term_enabled": True,
                "max_turns": 20,
                "max_tokens": 800,
                "long_term_path": "data/memory/long_term",
                "embedding_model": "all-MiniLM-L6-v2",
                "vector_db": "in_memory",  # Fallback to in-memory if chroma not available
                "max_memories": 1000,
                "device": "cpu",
                "auto_persist": True,
                "persist_interval": 1,
                "chunk_size": 150,
                "chunk_overlap": 50,
                "min_chunk_length": 50
            }

        # Initialize parent class
        super().__init__(
            config=config,
            short_term_memory=short_term_memory,
            long_term_memory=long_term_memory
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
        # Get the enhanced context - parent method uses user_input parameter name
        context = super().get_enhanced_context(
            user_input=query,
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

    def create_snapshot(self, snapshot_id: Optional[str] = None) -> str:
        """
        Create a snapshot of the current memory state with WebSocket events.

        Args:
            snapshot_id: Optional ID for the snapshot

        Returns:
            Snapshot ID
        """
        # Create the snapshot
        snapshot_id = super().create_snapshot(snapshot_id)

        # Get snapshot metadata
        metadata = self.snapshot_manager.get_snapshot_metadata(snapshot_id)

        # Emit memory snapshot event
        self.ws.system_info({
            "memory_snapshot": {
                "action": "create",
                "snapshot_id": snapshot_id,
                "metadata": metadata
            }
        })

        logger.debug(f"Created memory snapshot: {snapshot_id}")

        return snapshot_id

    def save_snapshot(self, snapshot_id: Optional[str] = None, filepath: Optional[str] = None) -> str:
        """
        Create and save a snapshot to disk with WebSocket events.

        Args:
            snapshot_id: Optional ID for the snapshot (created if None)
            filepath: Optional file path (generated if None)

        Returns:
            Path to the saved snapshot file
        """
        # Save the snapshot
        filepath = super().save_snapshot(snapshot_id, filepath)

        # Emit memory snapshot event
        self.ws.system_info({
            "memory_snapshot": {
                "action": "save",
                "snapshot_id": snapshot_id,
                "filepath": filepath
            }
        })

        logger.debug(f"Saved memory snapshot to: {filepath}")

        return filepath

    def load_snapshot(self, filepath: str) -> str:
        """
        Load a snapshot from disk with WebSocket events.

        Args:
            filepath: Path to the snapshot file

        Returns:
            Snapshot ID
        """
        # Load the snapshot
        snapshot_id = super().load_snapshot(filepath)

        # Get snapshot metadata
        metadata = self.snapshot_manager.get_snapshot_metadata(snapshot_id)

        # Emit memory snapshot event
        self.ws.system_info({
            "memory_snapshot": {
                "action": "load",
                "snapshot_id": snapshot_id,
                "filepath": filepath,
                "metadata": metadata
            }
        })

        logger.debug(f"Loaded memory snapshot from: {filepath}")

        return snapshot_id

    def apply_snapshot(self, snapshot_id: str) -> bool:
        """
        Apply a snapshot to the memory system with WebSocket events.

        Args:
            snapshot_id: ID of the snapshot to apply

        Returns:
            True if successful
        """
        # Apply the snapshot
        result = super().apply_snapshot(snapshot_id)

        if result:
            # Get snapshot metadata
            metadata = self.snapshot_manager.get_snapshot_metadata(snapshot_id)

            # Emit memory snapshot event
            self.ws.system_info({
                "memory_snapshot": {
                    "action": "apply",
                    "snapshot_id": snapshot_id,
                    "success": True,
                    "metadata": metadata
                }
            })

            logger.debug(f"Applied memory snapshot: {snapshot_id}")
        else:
            # Emit memory snapshot event (failure)
            self.ws.system_info({
                "memory_snapshot": {
                    "action": "apply",
                    "snapshot_id": snapshot_id,
                    "success": False
                }
            })

            logger.debug(f"Failed to apply memory snapshot: {snapshot_id}")

        return result

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """
        List all snapshots with metadata and emit WebSocket events.

        Returns:
            List of snapshot metadata
        """
        # Get the snapshots
        snapshots = super().list_snapshots()

        # Emit memory snapshot event
        self.ws.system_info({
            "memory_snapshot": {
                "action": "list",
                "snapshots": snapshots
            }
        })

        logger.debug(f"Listed {len(snapshots)} memory snapshots")

        return snapshots
