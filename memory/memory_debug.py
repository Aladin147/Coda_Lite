"""
Memory Debug System for Coda Lite.

This module provides functionality for debugging and visualizing the memory system,
including both short-term and long-term memories.
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

logger = logging.getLogger("coda.memory.debug")

class MemoryDebugSystem:
    """
    Manages memory debugging and visualization.

    Responsibilities:
    - Track memory operations for debugging
    - Provide memory statistics and metrics
    - Support memory visualization
    - Enable memory search and filtering
    """

    def __init__(self, memory_manager, websocket_integration=None):
        """
        Initialize the memory debug system.

        Args:
            memory_manager: The memory manager to debug
            websocket_integration: Optional WebSocket integration for event emission
        """
        self.memory_manager = memory_manager
        self.ws = websocket_integration
        self.operations_log = []
        self.max_log_entries = 100
        self.memory_stats_cache = {}
        self.last_stats_update = 0
        self.stats_update_interval = 5  # seconds

        logger.info("MemoryDebugSystem initialized")

    def log_operation(self, operation_type: str, details: Dict[str, Any]) -> None:
        """
        Log a memory operation for debugging.

        Args:
            operation_type: Type of operation (add, retrieve, update, delete, etc.)
            details: Operation details
        """
        # Create operation log entry
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "operation_type": operation_type,
            "details": details
        }

        # Add to operations log
        self.operations_log.append(log_entry)

        # Trim log if needed
        if len(self.operations_log) > self.max_log_entries:
            self.operations_log = self.operations_log[-self.max_log_entries:]

        # Emit WebSocket event if available
        if self.ws:
            self.ws.memory_debug_operation(
                operation_type=operation_type,
                timestamp=timestamp,
                details=details
            )

        logger.debug(f"Memory operation logged: {operation_type}")

    def get_operations_log(self,
                          operation_type: Optional[str] = None,
                          limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get the memory operations log.

        Args:
            operation_type: Optional filter by operation type
            limit: Maximum number of log entries to return

        Returns:
            List of operation log entries
        """
        # Filter by operation type if specified
        if operation_type:
            filtered_log = [entry for entry in self.operations_log
                           if entry["operation_type"] == operation_type]
        else:
            filtered_log = self.operations_log

        # Return the most recent entries up to the limit
        return filtered_log[-limit:]

    def get_memory_stats(self, force_update: bool = False) -> Dict[str, Any]:
        """
        Get memory statistics.

        Args:
            force_update: Whether to force a stats update

        Returns:
            Dictionary of memory statistics
        """
        current_time = time.time()

        # Check if we need to update the stats
        if force_update or current_time - self.last_stats_update > self.stats_update_interval:
            # Get stats from memory manager
            self.memory_stats_cache = self.memory_manager.get_memory_stats()
            self.last_stats_update = current_time

            # Add additional debug stats
            self.memory_stats_cache["debug"] = {
                "operations_count": len(self.operations_log),
                "operations_by_type": self._count_operations_by_type(),
                "last_update": current_time
            }

            # Emit WebSocket event if available
            if self.ws:
                self.ws.memory_debug_stats(self.memory_stats_cache)

        return self.memory_stats_cache

    def _count_operations_by_type(self) -> Dict[str, int]:
        """
        Count operations by type.

        Returns:
            Dictionary mapping operation types to counts
        """
        counts = {}
        for entry in self.operations_log:
            op_type = entry["operation_type"]
            counts[op_type] = counts.get(op_type, 0) + 1
        return counts

    def search_memories(self,
                       query: str,
                       memory_type: Optional[str] = None,
                       min_importance: float = 0.0,
                       max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search for memories.

        Args:
            query: Search query
            memory_type: Optional filter by memory type
            min_importance: Minimum importance score
            max_results: Maximum number of results

        Returns:
            List of matching memories
        """
        # Get memories from memory manager
        memories = self.memory_manager.search_memories(query, limit=max_results * 2)

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

        # Log the operation
        self.log_operation(
            operation_type="search",
            details={
                "query": query,
                "memory_type": memory_type,
                "min_importance": min_importance,
                "results_count": len(memories)
            }
        )

        # Return top results
        return memories[:max_results]

    def get_memory_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a memory by ID.

        Args:
            memory_id: Memory ID

        Returns:
            Memory data or None if not found
        """
        # Get memory from memory manager
        memory = self.memory_manager.long_term.get_memory_by_id(memory_id)

        # Log the operation
        self.log_operation(
            operation_type="get",
            details={
                "memory_id": memory_id,
                "found": memory is not None
            }
        )

        return memory

    def update_memory_importance(self,
                                memory_id: str,
                                importance: float) -> bool:
        """
        Update a memory's importance.

        Args:
            memory_id: Memory ID
            importance: New importance score

        Returns:
            True if successful, False otherwise
        """
        # Get the original memory
        original_memory = self.memory_manager.long_term.get_memory_by_id(memory_id)
        if not original_memory:
            return False

        # Update the memory
        result = self.memory_manager.update_memory(
            memory_id=memory_id,
            importance=importance
        )

        # Log the operation
        self.log_operation(
            operation_type="update_importance",
            details={
                "memory_id": memory_id,
                "old_importance": original_memory.get("importance", 0),
                "new_importance": importance,
                "success": result
            }
        )

        return result

    def reinforce_memory(self,
                        memory_id: str,
                        strength: float = 1.0) -> bool:
        """
        Reinforce a memory.

        Args:
            memory_id: Memory ID
            strength: Reinforcement strength

        Returns:
            True if successful, False otherwise
        """
        # Get the original memory
        original_memory = self.memory_manager.long_term.get_memory_by_id(memory_id)
        if not original_memory:
            return False

        # Reinforce the memory
        result = self.memory_manager.reinforce_memory(
            memory_id=memory_id,
            reinforcement_strength=strength
        )

        # Log the operation
        self.log_operation(
            operation_type="reinforce",
            details={
                "memory_id": memory_id,
                "strength": strength,
                "success": result
            }
        )

        return result

    def forget_memory(self, memory_id: str) -> bool:
        """
        Forget (delete) a memory.

        Args:
            memory_id: Memory ID

        Returns:
            True if successful, False otherwise
        """
        # Get the original memory
        original_memory = self.memory_manager.long_term.get_memory_by_id(memory_id)
        if not original_memory:
            return False

        # Delete the memory
        result = self.memory_manager.long_term.delete_memory(memory_id)

        # Log the operation
        self.log_operation(
            operation_type="forget",
            details={
                "memory_id": memory_id,
                "content_preview": original_memory.get("content", "")[:50],
                "success": result
            }
        )

        return result

    def apply_forgetting_mechanism(self, max_memories: Optional[int] = None) -> int:
        """
        Apply the forgetting mechanism.

        Args:
            max_memories: Optional maximum number of memories to keep

        Returns:
            Number of memories forgotten
        """
        # Apply forgetting mechanism
        forgotten_count = self.memory_manager.forget_memories(max_memories)

        # Log the operation
        self.log_operation(
            operation_type="apply_forgetting",
            details={
                "max_memories": max_memories,
                "forgotten_count": forgotten_count
            }
        )

        return forgotten_count

    def create_memory_snapshot(self, snapshot_id: Optional[str] = None) -> str:
        """
        Create a memory snapshot.

        Args:
            snapshot_id: Optional snapshot ID

        Returns:
            Snapshot ID
        """
        # Create snapshot
        snapshot_id = self.memory_manager.create_snapshot(snapshot_id)

        # Log the operation
        self.log_operation(
            operation_type="create_snapshot",
            details={
                "snapshot_id": snapshot_id
            }
        )

        return snapshot_id

    def apply_memory_snapshot(self, snapshot_id: str) -> bool:
        """
        Apply a memory snapshot.

        Args:
            snapshot_id: Snapshot ID

        Returns:
            True if successful, False otherwise
        """
        # Apply snapshot
        result = self.memory_manager.apply_snapshot(snapshot_id)

        # Log the operation
        self.log_operation(
            operation_type="apply_snapshot",
            details={
                "snapshot_id": snapshot_id,
                "success": result
            }
        )

        return result
