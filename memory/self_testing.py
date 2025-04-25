"""
Self-testing Framework for Coda Lite's Memory System.

This module provides functionality for self-testing and verifying memory integrity,
implementing consistency checks and validation mechanisms.
"""

import logging
import time
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set, Callable

logger = logging.getLogger("coda.memory.self_testing")

class MemorySelfTestingFramework:
    """
    Manages self-testing and verification of memory integrity.
    
    Responsibilities:
    - Verify memory consistency across storage systems
    - Detect and repair corrupted memories
    - Run periodic integrity checks
    - Generate test cases for memory operations
    - Validate memory retrieval accuracy
    """
    
    def __init__(self, memory_manager, config: Dict[str, Any] = None):
        """
        Initialize the self-testing framework.
        
        Args:
            memory_manager: The memory manager to test
            config: Configuration dictionary
        """
        self.memory_manager = memory_manager
        self.config = config or {}
        
        # Test settings
        self.test_interval = self.config.get("memory", {}).get("self_test_interval", 24)  # hours
        self.test_batch_size = self.config.get("memory", {}).get("self_test_batch_size", 10)
        self.repair_threshold = self.config.get("memory", {}).get("repair_threshold", 0.7)  # Repair if confidence > 70%
        
        # Test tracking
        self.last_test_time = datetime.now() - timedelta(hours=self.test_interval)  # Force initial test
        self.test_history = []
        self.repair_history = []
        
        # Test metrics
        self.metrics = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "repairs_attempted": 0,
            "repairs_successful": 0,
            "last_test_time": self.last_test_time.isoformat()
        }
        
        logger.info("MemorySelfTestingFramework initialized")
    
    def run_consistency_check(self, memory_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run a consistency check on memories.
        
        Args:
            memory_ids: Optional list of memory IDs to check (if None, selects random sample)
            
        Returns:
            Dictionary with check results
        """
        # Update last test time
        self.last_test_time = datetime.now()
        self.metrics["last_test_time"] = self.last_test_time.isoformat()
        
        # Select memories to check
        if memory_ids is None:
            all_memory_ids = list(self.memory_manager.long_term.metadata.get("memories", {}).keys())
            if not all_memory_ids:
                return {
                    "status": "skipped",
                    "reason": "No memories to check",
                    "timestamp": self.last_test_time.isoformat()
                }
            
            # Select a random sample
            sample_size = min(self.test_batch_size, len(all_memory_ids))
            memory_ids = random.sample(all_memory_ids, sample_size)
        
        # Initialize results
        results = {
            "status": "completed",
            "timestamp": self.last_test_time.isoformat(),
            "memories_checked": len(memory_ids),
            "inconsistencies": [],
            "repairs": []
        }
        
        # Check each memory
        for memory_id in memory_ids:
            # Get memory from long-term storage
            memory = self.memory_manager.long_term.get_memory_by_id(memory_id)
            
            # Check if memory exists
            if not memory:
                inconsistency = {
                    "memory_id": memory_id,
                    "type": "missing",
                    "description": "Memory exists in metadata but not in storage",
                    "severity": "high"
                }
                results["inconsistencies"].append(inconsistency)
                continue
            
            # Check metadata consistency
            metadata_memory = self.memory_manager.long_term.metadata.get("memories", {}).get(memory_id)
            if not metadata_memory:
                inconsistency = {
                    "memory_id": memory_id,
                    "type": "metadata_missing",
                    "description": "Memory exists in storage but not in metadata",
                    "severity": "medium"
                }
                results["inconsistencies"].append(inconsistency)
                continue
            
            # Check content consistency
            if "content" in memory and "content" in metadata_memory:
                # Check if content preview matches actual content
                content = memory["content"]
                preview = metadata_memory["content"]
                
                # If preview is truncated (ends with "..."), check if it matches the beginning of content
                if preview.endswith("..."):
                    preview_base = preview[:-3]
                    if not content.startswith(preview_base):
                        inconsistency = {
                            "memory_id": memory_id,
                            "type": "content_mismatch",
                            "description": "Content preview in metadata doesn't match actual content",
                            "severity": "low"
                        }
                        results["inconsistencies"].append(inconsistency)
            
            # Check importance consistency
            if "importance" in memory.get("metadata", {}) and "importance" in metadata_memory:
                if memory["metadata"]["importance"] != metadata_memory["importance"]:
                    inconsistency = {
                        "memory_id": memory_id,
                        "type": "importance_mismatch",
                        "description": "Importance in metadata doesn't match importance in memory",
                        "severity": "low"
                    }
                    results["inconsistencies"].append(inconsistency)
        
        # Update metrics
        self.metrics["tests_run"] += 1
        if results["inconsistencies"]:
            self.metrics["tests_failed"] += 1
        else:
            self.metrics["tests_passed"] += 1
        
        # Add to test history
        self.test_history.append({
            "timestamp": self.last_test_time.isoformat(),
            "memories_checked": len(memory_ids),
            "inconsistencies_found": len(results["inconsistencies"])
        })
        
        # Trim test history
        if len(self.test_history) > 100:
            self.test_history = self.test_history[-100:]
        
        # Attempt repairs if needed
        if results["inconsistencies"]:
            repair_results = self._repair_inconsistencies(results["inconsistencies"])
            results["repairs"] = repair_results
        
        return results
    
    def _repair_inconsistencies(self, inconsistencies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Attempt to repair inconsistencies.
        
        Args:
            inconsistencies: List of inconsistency dictionaries
            
        Returns:
            List of repair results
        """
        repairs = []
        
        for inconsistency in inconsistencies:
            memory_id = inconsistency["memory_id"]
            repair_result = {
                "memory_id": memory_id,
                "type": inconsistency["type"],
                "success": False,
                "action": "none"
            }
            
            # Update metrics
            self.metrics["repairs_attempted"] += 1
            
            try:
                # Handle different types of inconsistencies
                if inconsistency["type"] == "missing":
                    # Memory exists in metadata but not in storage
                    # Remove from metadata
                    if memory_id in self.memory_manager.long_term.metadata.get("memories", {}):
                        self.memory_manager.long_term.metadata["memories"].pop(memory_id)
                        self.memory_manager.long_term._save_metadata()
                        repair_result["success"] = True
                        repair_result["action"] = "removed_from_metadata"
                
                elif inconsistency["type"] == "metadata_missing":
                    # Memory exists in storage but not in metadata
                    # Get memory and add to metadata
                    memory = self.memory_manager.long_term.get_memory_by_id(memory_id)
                    if memory:
                        content = memory.get("content", "")
                        importance = memory.get("metadata", {}).get("importance", 0.5)
                        
                        # Add to metadata
                        self.memory_manager.long_term.metadata.setdefault("memories", {})[memory_id] = {
                            "content": content[:100] + "..." if len(content) > 100 else content,
                            "importance": importance,
                            "timestamp": memory.get("metadata", {}).get("timestamp", datetime.now().isoformat())
                        }
                        self.memory_manager.long_term._save_metadata()
                        repair_result["success"] = True
                        repair_result["action"] = "added_to_metadata"
                
                elif inconsistency["type"] == "content_mismatch":
                    # Content preview in metadata doesn't match actual content
                    # Update metadata preview
                    memory = self.memory_manager.long_term.get_memory_by_id(memory_id)
                    if memory and memory_id in self.memory_manager.long_term.metadata.get("memories", {}):
                        content = memory.get("content", "")
                        self.memory_manager.long_term.metadata["memories"][memory_id]["content"] = \
                            content[:100] + "..." if len(content) > 100 else content
                        self.memory_manager.long_term._save_metadata()
                        repair_result["success"] = True
                        repair_result["action"] = "updated_preview"
                
                elif inconsistency["type"] == "importance_mismatch":
                    # Importance in metadata doesn't match importance in memory
                    # Update metadata importance
                    memory = self.memory_manager.long_term.get_memory_by_id(memory_id)
                    if memory and memory_id in self.memory_manager.long_term.metadata.get("memories", {}):
                        importance = memory.get("metadata", {}).get("importance", 0.5)
                        self.memory_manager.long_term.metadata["memories"][memory_id]["importance"] = importance
                        self.memory_manager.long_term._save_metadata()
                        repair_result["success"] = True
                        repair_result["action"] = "updated_importance"
            
            except Exception as e:
                logger.error(f"Error repairing inconsistency: {e}")
                repair_result["error"] = str(e)
            
            # Update metrics if successful
            if repair_result["success"]:
                self.metrics["repairs_successful"] += 1
            
            # Add to repair history
            self.repair_history.append({
                "timestamp": datetime.now().isoformat(),
                "memory_id": memory_id,
                "type": inconsistency["type"],
                "success": repair_result["success"],
                "action": repair_result["action"]
            })
            
            # Trim repair history
            if len(self.repair_history) > 100:
                self.repair_history = self.repair_history[-100:]
            
            # Add to results
            repairs.append(repair_result)
        
        return repairs
    
    def test_memory_retrieval(self, query: str, expected_memory_ids: List[str]) -> Dict[str, Any]:
        """
        Test memory retrieval accuracy.
        
        Args:
            query: Query to test
            expected_memory_ids: List of memory IDs that should be retrieved
            
        Returns:
            Dictionary with test results
        """
        # Retrieve memories
        retrieved_memories = self.memory_manager.retrieve_relevant_memories(query)
        
        # Get retrieved memory IDs
        retrieved_ids = [memory.get("id") for memory in retrieved_memories]
        
        # Calculate metrics
        true_positives = set(retrieved_ids).intersection(expected_memory_ids)
        false_positives = set(retrieved_ids).difference(expected_memory_ids)
        false_negatives = set(expected_memory_ids).difference(retrieved_ids)
        
        precision = len(true_positives) / max(1, len(retrieved_ids))
        recall = len(true_positives) / max(1, len(expected_memory_ids))
        f1_score = 2 * precision * recall / max(0.001, precision + recall)
        
        # Create results
        results = {
            "query": query,
            "expected_count": len(expected_memory_ids),
            "retrieved_count": len(retrieved_ids),
            "true_positives": len(true_positives),
            "false_positives": len(false_positives),
            "false_negatives": len(false_negatives),
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "timestamp": datetime.now().isoformat()
        }
        
        return results
    
    def generate_test_memory(self, memory_type: str = "fact") -> Dict[str, Any]:
        """
        Generate a test memory for testing purposes.
        
        Args:
            memory_type: Type of memory to generate
            
        Returns:
            Dictionary with memory data
        """
        # Generate unique ID
        import uuid
        memory_id = f"test_{uuid.uuid4()}"
        
        # Generate content based on type
        if memory_type == "fact":
            content = f"Test fact: The capital of France is Paris. ID: {memory_id}"
        elif memory_type == "preference":
            content = f"Test preference: User prefers dark mode. ID: {memory_id}"
        elif memory_type == "conversation":
            content = f"Test conversation: User asked about the weather. ID: {memory_id}"
        else:
            content = f"Test memory of type {memory_type}. ID: {memory_id}"
        
        # Create memory
        memory = {
            "id": memory_id,
            "content": content,
            "metadata": {
                "source_type": memory_type,
                "timestamp": datetime.now().isoformat(),
                "importance": 0.5,
                "is_test": True
            }
        }
        
        return memory
    
    def run_retrieval_test_suite(self) -> Dict[str, Any]:
        """
        Run a suite of retrieval tests.
        
        Returns:
            Dictionary with test results
        """
        # Create test memories
        test_memories = []
        for memory_type in ["fact", "preference", "conversation"]:
            test_memories.append(self.generate_test_memory(memory_type))
        
        # Add test memories to storage
        added_ids = []
        for memory in test_memories:
            try:
                memory_id = self.memory_manager.long_term.add_memory(
                    content=memory["content"],
                    source_type=memory["metadata"]["source_type"],
                    importance=memory["metadata"]["importance"],
                    metadata=memory["metadata"]
                )
                added_ids.append(memory_id)
            except Exception as e:
                logger.error(f"Error adding test memory: {e}")
        
        # Run retrieval tests
        test_queries = [
            {"query": "capital of France", "expected_ids": [added_ids[0]]},  # Should match fact
            {"query": "user preferences", "expected_ids": [added_ids[1]]},   # Should match preference
            {"query": "weather", "expected_ids": [added_ids[2]]},            # Should match conversation
            {"query": "test memory", "expected_ids": added_ids}              # Should match all
        ]
        
        # Run tests
        results = {
            "timestamp": datetime.now().isoformat(),
            "tests_run": len(test_queries),
            "average_precision": 0,
            "average_recall": 0,
            "average_f1": 0,
            "test_results": []
        }
        
        for test in test_queries:
            test_result = self.test_memory_retrieval(test["query"], test["expected_ids"])
            results["test_results"].append(test_result)
            results["average_precision"] += test_result["precision"]
            results["average_recall"] += test_result["recall"]
            results["average_f1"] += test_result["f1_score"]
        
        # Calculate averages
        if results["tests_run"] > 0:
            results["average_precision"] /= results["tests_run"]
            results["average_recall"] /= results["tests_run"]
            results["average_f1"] /= results["tests_run"]
        
        # Clean up test memories
        for memory_id in added_ids:
            try:
                self.memory_manager.long_term.delete_memory(memory_id)
            except Exception as e:
                logger.error(f"Error deleting test memory: {e}")
        
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get metrics about self-testing.
        
        Returns:
            Dictionary with self-testing metrics
        """
        # Calculate success rates
        test_success_rate = self.metrics["tests_passed"] / max(1, self.metrics["tests_run"])
        repair_success_rate = self.metrics["repairs_successful"] / max(1, self.metrics["repairs_attempted"])
        
        # Create metrics dictionary
        metrics = {
            "tests_run": self.metrics["tests_run"],
            "tests_passed": self.metrics["tests_passed"],
            "tests_failed": self.metrics["tests_failed"],
            "test_success_rate": test_success_rate,
            "repairs_attempted": self.metrics["repairs_attempted"],
            "repairs_successful": self.metrics["repairs_successful"],
            "repair_success_rate": repair_success_rate,
            "last_test_time": self.metrics["last_test_time"],
            "test_history_count": len(self.test_history),
            "repair_history_count": len(self.repair_history),
            "timestamp": datetime.now().isoformat()
        }
        
        return metrics
