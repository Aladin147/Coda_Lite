"""
Long-term memory management for Coda Lite.

This module provides a LongTermMemory class for handling persistent memory across sessions.
"""

import os
import json
import logging
import time
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer

# Try to import different vector database options
try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    import sqlite3
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

logger = logging.getLogger("coda.memory.long_term")

class LongTermMemory:
    """
    Manages long-term memory for Coda using vector embeddings.

    Responsibilities:
    - Store conversation chunks with semantic embeddings
    - Retrieve relevant memories based on semantic similarity
    - Maintain metadata about memories (time, importance, etc.)
    - Support time-based decay and relevance weighting

    Features:
    - Vector-based semantic search
    - Metadata filtering (time, topic, etc.)
    - Memory importance scoring
    - Time decay for older memories
    """

    def __init__(self,
                 storage_path: str = "data/memory/long_term",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 vector_db_type: str = "chroma",
                 max_memories: int = 1000,
                 device: str = "cpu"):
        """
        Initialize the long-term memory system.

        Args:
            storage_path: Path to store the vector database
            embedding_model: Name of the sentence-transformers model to use
            vector_db_type: Type of vector database to use ("chroma" or "sqlite")
            max_memories: Maximum number of memories to store
            device: Device to run the embedding model on ("cpu" or "cuda")
        """
        self.storage_path = storage_path
        self.max_memories = max_memories
        self.vector_db_type = vector_db_type

        # Create storage directory if it doesn't exist
        os.makedirs(storage_path, exist_ok=True)

        # Initialize embedding model
        logger.info(f"Initializing embedding model {embedding_model} on {device}")
        self.embedding_model = SentenceTransformer(embedding_model, device=device)

        # Initialize vector database
        self._init_vector_db()

        # Initialize memory metadata
        self.metadata_path = os.path.join(storage_path, "metadata.json")
        self.metadata = self._load_metadata()

        logger.info(f"LongTermMemory initialized with {len(self.metadata['memories'])} memories")

    def _init_vector_db(self):
        """Initialize the vector database based on the selected type."""
        if self.vector_db_type == "chroma" and CHROMA_AVAILABLE:
            logger.info(f"Initializing ChromaDB at {self.storage_path}")
            self.vector_db = chromadb.PersistentClient(path=self.storage_path)
            self.collection = self.vector_db.get_or_create_collection(
                name="memories",
                metadata={"description": "Coda's long-term memories"}
            )
        elif self.vector_db_type == "sqlite" and SQLITE_AVAILABLE:
            logger.info(f"Initializing SQLite vector database at {self.storage_path}")
            db_path = os.path.join(self.storage_path, "memories.db")
            self.conn = sqlite3.connect(db_path)
            self._init_sqlite_db()
        else:
            logger.warning(f"Vector database type {self.vector_db_type} not available, falling back to in-memory")
            self.vector_db_type = "in_memory"
            self.vectors = {}
            self.contents = {}
            self.vector_metadata = {}

    def _init_sqlite_db(self):
        """Initialize the SQLite database schema."""
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            embedding BLOB NOT NULL,
            timestamp TEXT NOT NULL,
            importance REAL NOT NULL,
            metadata TEXT NOT NULL
        )
        ''')
        self.conn.commit()

    def _load_metadata(self) -> Dict[str, Any]:
        """Load memory metadata from file or create default."""
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                logger.info(f"Loaded metadata with {len(metadata.get('memories', []))} memories")
                return metadata
            except Exception as e:
                logger.error(f"Error loading metadata: {e}")

        # Create default metadata
        metadata = {
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "memory_count": 0,
            "memories": {},
            "user_summary": {},
            "topics": []
        }

        # Save default metadata
        self._save_metadata(metadata)

        return metadata

    def _save_metadata(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Save memory metadata to file."""
        if metadata is None:
            metadata = self.metadata

        metadata["last_updated"] = datetime.now().isoformat()

        try:
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            logger.debug("Saved metadata")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")

    def add_memory(self,
                  content: str,
                  source_type: str = "conversation",
                  importance: float = 0.5,
                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a new memory to long-term storage.

        Args:
            content: The text content to store
            source_type: Type of memory (conversation, fact, preference, etc.)
            importance: Importance score (0.0 to 1.0)
            metadata: Additional metadata about the memory

        Returns:
            ID of the stored memory
        """
        # Generate a unique ID for the memory
        memory_id = str(uuid.uuid4())

        # Create timestamp
        timestamp = datetime.now().isoformat()

        # Create default metadata if not provided
        if metadata is None:
            metadata = {}

        # Add standard metadata
        full_metadata = {
            "source_type": source_type,
            "timestamp": timestamp,
            "importance": importance,
            **metadata
        }

        # Generate embedding
        embedding = self.embedding_model.encode(content)

        # Store in vector database
        if self.vector_db_type == "chroma":
            self.collection.add(
                ids=[memory_id],
                embeddings=[embedding.tolist()],
                metadatas=[full_metadata],
                documents=[content]
            )
        elif self.vector_db_type == "sqlite":
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO memories VALUES (?, ?, ?, ?, ?, ?)",
                (
                    memory_id,
                    content,
                    embedding.tobytes(),
                    timestamp,
                    importance,
                    json.dumps(full_metadata)
                )
            )
            self.conn.commit()
        else:  # in-memory
            self.vectors[memory_id] = embedding
            self.contents[memory_id] = content
            self.vector_metadata[memory_id] = full_metadata

        # Update metadata
        self.metadata["memories"][memory_id] = {
            "content": content[:100] + "..." if len(content) > 100 else content,  # Store preview
            "timestamp": timestamp,
            "importance": importance,
            "metadata": full_metadata
        }
        self.metadata["memory_count"] = len(self.metadata["memories"])

        # Save metadata
        self._save_metadata()

        logger.info(f"Added memory {memory_id} with {len(content)} chars")

        # Check if we need to prune memories
        if self.metadata["memory_count"] > self.max_memories:
            self._prune_memories()

        return memory_id

    def retrieve_memories(self,
                         query: str,
                         limit: int = 5,
                         min_similarity: float = 0.5,
                         filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories based on semantic similarity.

        Args:
            query: The query text to find relevant memories for
            limit: Maximum number of memories to retrieve
            min_similarity: Minimum similarity score (0.0 to 1.0)
            filter_criteria: Additional criteria to filter memories

        Returns:
            List of relevant memories with metadata
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)

        # Retrieve from vector database
        if self.vector_db_type == "chroma":
            # Prepare filter if provided
            where_filter = None
            if filter_criteria:
                where_filter = {}
                for key, value in filter_criteria.items():
                    where_filter[key] = value

            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=limit,
                where=where_filter
            )

            memories = []
            for i, (memory_id, content, metadata, distance) in enumerate(zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                # Convert distance to similarity (ChromaDB returns L2 distance)
                similarity = 1.0 / (1.0 + distance)

                # Skip if below minimum similarity
                if similarity < min_similarity:
                    continue

                # Add to results
                memories.append({
                    "id": memory_id,
                    "content": content,
                    "similarity": similarity,
                    "timestamp": metadata.get("timestamp"),
                    "importance": metadata.get("importance", 0.5),
                    "metadata": metadata
                })

        elif self.vector_db_type == "sqlite":
            # Retrieve all memories from SQLite
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, content, embedding, timestamp, importance, metadata FROM memories")
            rows = cursor.fetchall()

            # Calculate similarities
            similarities = []
            for row in rows:
                memory_id, content, embedding_bytes, timestamp, importance, metadata_str = row
                embedding = np.frombuffer(embedding_bytes, dtype=np.float32)

                # Calculate cosine similarity
                similarity = np.dot(query_embedding, embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(embedding))

                # Apply filter if provided
                if filter_criteria:
                    metadata = json.loads(metadata_str)
                    if not all(metadata.get(k) == v for k, v in filter_criteria.items()):
                        continue

                # Skip if below minimum similarity
                if similarity < min_similarity:
                    continue

                similarities.append((memory_id, content, similarity, timestamp, importance, metadata_str))

            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[2], reverse=True)

            # Take top results
            memories = []
            for memory_id, content, similarity, timestamp, importance, metadata_str in similarities[:limit]:
                memories.append({
                    "id": memory_id,
                    "content": content,
                    "similarity": similarity,
                    "timestamp": timestamp,
                    "importance": importance,
                    "metadata": json.loads(metadata_str)
                })

        else:  # in-memory
            # Calculate similarities for all vectors
            similarities = []
            for memory_id, embedding in self.vectors.items():
                # Calculate cosine similarity
                similarity = np.dot(query_embedding, embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(embedding))

                # Apply filter if provided
                if filter_criteria:
                    metadata = self.vector_metadata.get(memory_id, {})
                    if not all(metadata.get(k) == v for k, v in filter_criteria.items()):
                        continue

                # Skip if below minimum similarity
                if similarity < min_similarity:
                    continue

                similarities.append((memory_id, similarity))

            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)

            # Take top results
            memories = []
            for memory_id, similarity in similarities[:limit]:
                content = self.contents.get(memory_id, "")
                metadata = self.vector_metadata.get(memory_id, {})
                memories.append({
                    "id": memory_id,
                    "content": content,
                    "similarity": similarity,
                    "timestamp": metadata.get("timestamp"),
                    "importance": metadata.get("importance", 0.5),
                    "metadata": metadata
                })

        # Apply time decay to adjust relevance
        memories = self._apply_time_decay(memories)

        logger.info(f"Retrieved {len(memories)} memories for query: {query[:50]}...")

        return memories

    def _apply_time_decay(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply time decay to memory relevance scores.

        Args:
            memories: List of memories with metadata

        Returns:
            Memories with adjusted relevance scores
        """
        now = datetime.now()

        for memory in memories:
            # Parse timestamp
            timestamp = memory.get("timestamp")
            if not timestamp:
                continue

            try:
                memory_time = datetime.fromisoformat(timestamp)

                # Calculate age in days
                age_days = (now - memory_time).total_seconds() / (24 * 3600)

                # Apply decay factor (half-life of 30 days)
                decay_factor = 2 ** (-age_days / 30)

                # Adjust similarity score
                original_similarity = memory.get("similarity", 0.5)
                importance = memory.get("importance", 0.5)

                # Final score combines similarity, importance, and time decay
                adjusted_score = original_similarity * importance * decay_factor

                # Update memory
                memory["adjusted_score"] = adjusted_score
                memory["decay_factor"] = decay_factor

            except Exception as e:
                logger.error(f"Error applying time decay: {e}")
                memory["adjusted_score"] = memory.get("similarity", 0.5)

        # Re-sort by adjusted score
        memories.sort(key=lambda x: x.get("adjusted_score", 0), reverse=True)

        return memories

    def _prune_memories(self) -> None:
        """
        Prune least important memories when we exceed the maximum.
        """
        if len(self.metadata["memories"]) <= self.max_memories:
            return

        logger.info(f"Pruning memories (current: {len(self.metadata['memories'])}, max: {self.max_memories})")

        # Sort memories by importance and recency
        memories_with_scores = []
        for memory_id, memory in self.metadata["memories"].items():
            # Calculate age in days
            try:
                timestamp = memory.get("timestamp", datetime.now().isoformat())
                memory_time = datetime.fromisoformat(timestamp)
                now = datetime.now()
                age_days = (now - memory_time).total_seconds() / (24 * 3600)

                # Score combines importance and recency
                importance = memory.get("importance", 0.5)
                score = importance * (2 ** (-age_days / 30))  # Same decay as retrieval

                memories_with_scores.append((memory_id, score))
            except Exception as e:
                logger.error(f"Error calculating memory score: {e}")
                memories_with_scores.append((memory_id, 0))

        # Sort by score (ascending, so lowest scores first)
        memories_with_scores.sort(key=lambda x: x[1])

        # Determine how many to remove
        to_remove = len(self.metadata["memories"]) - self.max_memories

        # Get IDs to remove
        remove_ids = [memory_id for memory_id, _ in memories_with_scores[:to_remove]]

        # Remove from vector database
        if self.vector_db_type == "chroma":
            self.collection.delete(ids=remove_ids)
        elif self.vector_db_type == "sqlite":
            cursor = self.conn.cursor()
            for memory_id in remove_ids:
                cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            self.conn.commit()
        else:  # in-memory
            for memory_id in remove_ids:
                self.vectors.pop(memory_id, None)
                self.contents.pop(memory_id, None)
                self.vector_metadata.pop(memory_id, None)

        # Remove from metadata
        for memory_id in remove_ids:
            self.metadata["memories"].pop(memory_id, None)

        self.metadata["memory_count"] = len(self.metadata["memories"])

        # Save metadata
        self._save_metadata()

        logger.info(f"Pruned {len(remove_ids)} memories")

    def update_user_summary(self, key: str, value: Any) -> None:
        """
        Update user summary information.

        Args:
            key: Summary key (e.g., "preferred_topics", "communication_style")
            value: Summary value
        """
        self.metadata["user_summary"][key] = value
        self.metadata["last_updated"] = datetime.now().isoformat()
        self._save_metadata()
        logger.info(f"Updated user summary: {key} = {value}")

    def get_user_summary(self, key: Optional[str] = None) -> Any:
        """
        Get user summary information.

        Args:
            key: Optional key to retrieve specific summary item

        Returns:
            User summary or specific item
        """
        if key:
            return self.metadata["user_summary"].get(key)
        return self.metadata["user_summary"]

    def add_topic(self, topic: str) -> None:
        """
        Add a topic to the list of known topics.

        Args:
            topic: Topic name
        """
        if topic not in self.metadata["topics"]:
            self.metadata["topics"].append(topic)
            self._save_metadata()
            logger.info(f"Added topic: {topic}")

    def get_topics(self) -> List[str]:
        """
        Get list of known topics.

        Returns:
            List of topics
        """
        return self.metadata["topics"]

    def get_memory_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific memory by ID.

        Args:
            memory_id: Memory ID

        Returns:
            Memory data or None if not found
        """
        # Check metadata first
        if memory_id not in self.metadata["memories"]:
            return None

        # Get from vector database
        if self.vector_db_type == "chroma":
            results = self.collection.get(ids=[memory_id])
            if not results["ids"]:
                return None

            return {
                "id": memory_id,
                "content": results["documents"][0],
                "metadata": results["metadatas"][0]
            }

        elif self.vector_db_type == "sqlite":
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT content, timestamp, importance, metadata FROM memories WHERE id = ?",
                (memory_id,)
            )
            row = cursor.fetchone()

            if not row:
                return None

            content, timestamp, importance, metadata_str = row

            return {
                "id": memory_id,
                "content": content,
                "timestamp": timestamp,
                "importance": importance,
                "metadata": json.loads(metadata_str)
            }

        else:  # in-memory
            if memory_id not in self.contents:
                return None

            return {
                "id": memory_id,
                "content": self.contents[memory_id],
                "metadata": self.vector_metadata.get(memory_id, {})
            }

    def update_memory(self,
                     memory_id: str,
                     updated_memory: Dict[str, Any]) -> bool:
        """
        Update a memory with new data.

        Args:
            memory_id: ID of the memory to update
            updated_memory: Updated memory data

        Returns:
            True if successful, False otherwise
        """
        # Check if memory exists
        if memory_id not in self.metadata["memories"]:
            logger.warning(f"Memory {memory_id} not found for update")
            return False

        try:
            # Get current content and metadata
            current_memory = self.get_memory_by_id(memory_id)
            if not current_memory:
                logger.warning(f"Memory {memory_id} not found in vector database")
                return False

            # Extract updated fields
            content = updated_memory.get("content", current_memory.get("content", ""))
            importance = updated_memory.get("importance", current_memory.get("importance", 0.5))

            # Get metadata
            current_metadata = current_memory.get("metadata", {})
            updated_metadata = updated_memory.get("metadata", {})

            # Merge metadata
            merged_metadata = {**current_metadata, **updated_metadata}

            # Update timestamp if not explicitly provided
            if "timestamp" in updated_memory:
                merged_metadata["timestamp"] = updated_memory["timestamp"]

            # Update reinforcement count if provided
            if "reinforcement_count" in updated_memory:
                merged_metadata["reinforcement_count"] = updated_memory["reinforcement_count"]

            # Generate new embedding if content changed
            if content != current_memory.get("content", ""):
                embedding = self.embedding_model.encode(content)
            else:
                embedding = None

            # Update in vector database
            if self.vector_db_type == "chroma":
                update_data = {
                    "ids": [memory_id],
                    "metadatas": [merged_metadata]
                }

                if embedding is not None:
                    update_data["embeddings"] = [embedding.tolist()]

                if content != current_memory.get("content", ""):
                    update_data["documents"] = [content]

                self.collection.update(**update_data)

            elif self.vector_db_type == "sqlite":
                cursor = self.conn.cursor()

                if embedding is not None:
                    # Update everything
                    cursor.execute(
                        "UPDATE memories SET content = ?, embedding = ?, importance = ?, metadata = ? WHERE id = ?",
                        (
                            content,
                            embedding.tobytes(),
                            importance,
                            json.dumps(merged_metadata),
                            memory_id
                        )
                    )
                else:
                    # Update without changing embedding
                    cursor.execute(
                        "UPDATE memories SET content = ?, importance = ?, metadata = ? WHERE id = ?",
                        (
                            content,
                            importance,
                            json.dumps(merged_metadata),
                            memory_id
                        )
                    )

                self.conn.commit()

            else:  # in-memory
                if embedding is not None:
                    self.vectors[memory_id] = embedding

                self.contents[memory_id] = content
                self.vector_metadata[memory_id] = merged_metadata

            # Update metadata
            self.metadata["memories"][memory_id] = {
                "content": content[:100] + "..." if len(content) > 100 else content,
                "timestamp": merged_metadata.get("timestamp", datetime.now().isoformat()),
                "importance": importance,
                "metadata": merged_metadata
            }

            # Save metadata
            self._save_metadata()

            logger.info(f"Updated memory {memory_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating memory {memory_id}: {e}", exc_info=True)
            return False

    def remove_memory(self, memory_id: str) -> bool:
        """
        Remove a memory by ID (alias for delete_memory).

        Args:
            memory_id: Memory ID

        Returns:
            True if removed, False if not found
        """
        return self.delete_memory(memory_id)

    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory by ID.

        Args:
            memory_id: Memory ID

        Returns:
            True if deleted, False if not found
        """
        # Check if memory exists
        if memory_id not in self.metadata["memories"]:
            return False

        # Delete from vector database
        if self.vector_db_type == "chroma":
            self.collection.delete(ids=[memory_id])
        elif self.vector_db_type == "sqlite":
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            self.conn.commit()
        else:  # in-memory
            self.vectors.pop(memory_id, None)
            self.contents.pop(memory_id, None)
            self.vector_metadata.pop(memory_id, None)

        # Delete from metadata
        self.metadata["memories"].pop(memory_id, None)
        self.metadata["memory_count"] = len(self.metadata["memories"])

        # Save metadata
        self._save_metadata()

        logger.info(f"Deleted memory: {memory_id}")

        return True

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the memory store.

        Returns:
            Dictionary of statistics
        """
        # Count memories by source type
        source_types = {}
        for memory in self.metadata["memories"].values():
            source_type = memory.get("metadata", {}).get("source_type", "unknown")
            source_types[source_type] = source_types.get(source_type, 0) + 1

        # Calculate average importance
        importance_values = [m.get("importance", 0.5) for m in self.metadata["memories"].values()]
        avg_importance = sum(importance_values) / len(importance_values) if importance_values else 0

        # Get oldest and newest memory timestamps
        timestamps = [datetime.fromisoformat(m.get("timestamp", datetime.now().isoformat()))
                     for m in self.metadata["memories"].values()]
        oldest = min(timestamps).isoformat() if timestamps else None
        newest = max(timestamps).isoformat() if timestamps else None

        return {
            "total_memories": len(self.metadata["memories"]),
            "source_types": source_types,
            "average_importance": avg_importance,
            "oldest_memory": oldest,
            "newest_memory": newest,
            "topics": len(self.metadata["topics"]),
            "user_summary_keys": list(self.metadata["user_summary"].keys())
        }

    def close(self) -> None:
        """Close connections and save state."""
        self._save_metadata()

        if self.vector_db_type == "sqlite" and hasattr(self, 'conn'):
            self.conn.close()

        logger.info("Long-term memory closed")
