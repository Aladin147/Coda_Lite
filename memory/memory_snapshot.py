"""
Memory Snapshot System for Coda Lite.

This module provides functionality to create, save, and load snapshots of the memory system,
including both short-term and long-term memories.
"""

import os
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

# Import typing for type hints without circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from memory.enhanced_memory_manager import EnhancedMemoryManager

logger = logging.getLogger("coda.memory.snapshot")

class MemorySnapshotManager:
    """
    Manages memory snapshots for debugging and analysis.

    Responsibilities:
    - Create snapshots of the memory system
    - Save snapshots to disk
    - Load snapshots from disk
    - Provide metadata about snapshots
    """

    def __init__(self,
                 memory_manager: 'EnhancedMemoryManager',
                 snapshot_dir: str = "data/memory/snapshots",
                 auto_snapshot: bool = False,
                 snapshot_interval: int = 10):
        """
        Initialize the memory snapshot manager.

        Args:
            memory_manager: The memory manager to snapshot
            snapshot_dir: Directory to store snapshots
            auto_snapshot: Whether to automatically create snapshots
            snapshot_interval: Number of turns between automatic snapshots
        """
        self.memory_manager = memory_manager
        self.snapshot_dir = snapshot_dir
        self.auto_snapshot = auto_snapshot
        self.snapshot_interval = snapshot_interval
        self.last_snapshot_turn = 0
        self.snapshots = {}

        # Create snapshot directory if it doesn't exist
        os.makedirs(self.snapshot_dir, exist_ok=True)

        logger.info(f"MemorySnapshotManager initialized with snapshot_dir={snapshot_dir}")

    def create_snapshot(self, snapshot_id: Optional[str] = None) -> str:
        """
        Create a snapshot of the current memory state.

        Args:
            snapshot_id: Optional ID for the snapshot (generated if not provided)

        Returns:
            Snapshot ID
        """
        # Generate snapshot ID if not provided
        if snapshot_id is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_id = f"snapshot_{timestamp}_{str(uuid.uuid4())[:8]}"

        # Get short-term memory data
        short_term_data = {
            "turns": list(self.memory_manager.short_term.turns),
            "turn_count": self.memory_manager.short_term.turn_count,
            "session_start": self.memory_manager.short_term.session_start
        }

        # Get long-term memory data
        long_term_data = {
            "memories": self.memory_manager.long_term.metadata.get("memories", {}),
            "topics": self.memory_manager.long_term.metadata.get("topics", []),
            "memory_count": self.memory_manager.long_term.metadata.get("memory_count", 0)
        }

        # Create snapshot
        snapshot = {
            "snapshot_id": snapshot_id,
            "timestamp": datetime.now().isoformat(),
            "short_term": short_term_data,
            "long_term": long_term_data,
            "memory_stats": self.memory_manager.get_memory_stats()
        }

        # Store snapshot in memory
        self.snapshots[snapshot_id] = snapshot

        # Update last snapshot turn
        self.last_snapshot_turn = self.memory_manager.short_term.turn_count

        logger.info(f"Created memory snapshot {snapshot_id}")

        return snapshot_id

    def save_snapshot(self, snapshot_id: str, filepath: Optional[str] = None) -> str:
        """
        Save a snapshot to disk.

        Args:
            snapshot_id: ID of the snapshot to save
            filepath: Optional file path (generated if not provided)

        Returns:
            Path to the saved snapshot file
        """
        # Check if snapshot exists
        if snapshot_id not in self.snapshots:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        # Generate filepath if not provided
        if filepath is None:
            filename = f"{snapshot_id}.json"
            filepath = os.path.join(self.snapshot_dir, filename)

        # Save snapshot to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.snapshots[snapshot_id], f, indent=2, ensure_ascii=False)

        logger.info(f"Saved memory snapshot {snapshot_id} to {filepath}")

        return filepath

    def load_snapshot(self, filepath: str) -> str:
        """
        Load a snapshot from disk.

        Args:
            filepath: Path to the snapshot file

        Returns:
            Snapshot ID
        """
        # Load snapshot from file
        with open(filepath, 'r', encoding='utf-8') as f:
            snapshot = json.load(f)

        # Get snapshot ID
        snapshot_id = snapshot.get("snapshot_id")

        if not snapshot_id:
            # Generate a new ID if not found
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_id = f"loaded_snapshot_{timestamp}"
            snapshot["snapshot_id"] = snapshot_id

        # Store snapshot in memory
        self.snapshots[snapshot_id] = snapshot

        logger.info(f"Loaded memory snapshot {snapshot_id} from {filepath}")

        return snapshot_id

    def apply_snapshot(self, snapshot_id: str) -> bool:
        """
        Apply a snapshot to the memory system.

        Args:
            snapshot_id: ID of the snapshot to apply

        Returns:
            True if successful, False otherwise
        """
        # Check if snapshot exists
        if snapshot_id not in self.snapshots:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        snapshot = self.snapshots[snapshot_id]

        try:
            # Apply short-term memory
            short_term_data = snapshot.get("short_term", {})

            # Reset short-term memory
            self.memory_manager.short_term.reset()

            # Import turns
            for turn in short_term_data.get("turns", []):
                if "role" in turn and "content" in turn:
                    self.memory_manager.short_term.add_turn(turn["role"], turn["content"])

            # Apply long-term memory
            # Note: This is a simplified approach that doesn't fully restore the vector database
            # For a complete restoration, we would need to rebuild the vector database

            logger.info(f"Applied memory snapshot {snapshot_id}")

            return True
        except Exception as e:
            logger.error(f"Error applying snapshot {snapshot_id}: {e}")
            return False

    def get_snapshot_metadata(self, snapshot_id: str) -> Dict[str, Any]:
        """
        Get metadata about a snapshot.

        Args:
            snapshot_id: ID of the snapshot

        Returns:
            Snapshot metadata
        """
        # Check if snapshot exists
        if snapshot_id not in self.snapshots:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        snapshot = self.snapshots[snapshot_id]

        # Extract metadata
        metadata = {
            "snapshot_id": snapshot_id,
            "timestamp": snapshot.get("timestamp"),
            "short_term_turns": len(snapshot.get("short_term", {}).get("turns", [])),
            "long_term_memories": snapshot.get("long_term", {}).get("memory_count", 0),
            "topics": len(snapshot.get("long_term", {}).get("topics", []))
        }

        return metadata

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """
        List all snapshots with metadata.

        Returns:
            List of snapshot metadata
        """
        return [self.get_snapshot_metadata(snapshot_id) for snapshot_id in self.snapshots]

    def list_snapshot_files(self) -> List[str]:
        """
        List all snapshot files in the snapshot directory.

        Returns:
            List of snapshot file paths
        """
        if not os.path.exists(self.snapshot_dir):
            return []

        return [os.path.join(self.snapshot_dir, f) for f in os.listdir(self.snapshot_dir)
                if f.endswith('.json')]

    def check_auto_snapshot(self) -> Optional[str]:
        """
        Check if an automatic snapshot should be created.

        Returns:
            Snapshot ID if created, None otherwise
        """
        if not self.auto_snapshot:
            return None

        current_turn = self.memory_manager.short_term.turn_count

        if current_turn - self.last_snapshot_turn >= self.snapshot_interval:
            return self.create_snapshot()

        return None

    def enable_auto_snapshot(self, interval: int = 10) -> None:
        """
        Enable automatic snapshots.

        Args:
            interval: Number of turns between automatic snapshots
        """
        self.auto_snapshot = True
        self.snapshot_interval = interval
        logger.info(f"Enabled automatic snapshots every {interval} turns")

    def disable_auto_snapshot(self) -> None:
        """Disable automatic snapshots."""
        self.auto_snapshot = False
        logger.info("Disabled automatic snapshots")
