"""
Active Recall System for Coda Lite.

This module provides functionality for active recall and self-testing of memories,
implementing spaced repetition and memory reinforcement through recall.
"""

import logging
import time
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set, Callable

logger = logging.getLogger("coda.memory.active_recall")

class ActiveRecallSystem:
    """
    Manages active recall and self-testing of memories.
    
    Responsibilities:
    - Schedule memory reviews based on importance and age
    - Implement spaced repetition algorithm for optimal recall
    - Track recall success and adjust review intervals
    - Generate self-testing questions for memories
    - Verify memory consistency and integrity
    """
    
    def __init__(self, memory_manager, config: Dict[str, Any] = None):
        """
        Initialize the active recall system.
        
        Args:
            memory_manager: The memory manager to use
            config: Configuration dictionary
        """
        self.memory_manager = memory_manager
        self.config = config or {}
        
        # Review schedule settings
        self.min_review_interval = self.config.get("memory", {}).get("min_review_interval", 1)  # days
        self.max_review_interval = self.config.get("memory", {}).get("max_review_interval", 60)  # days
        self.initial_interval = self.config.get("memory", {}).get("initial_interval", 1)  # days
        self.interval_multiplier = self.config.get("memory", {}).get("interval_multiplier", 2.0)
        
        # Importance thresholds for review
        self.high_importance_threshold = self.config.get("memory", {}).get("high_importance_threshold", 0.8)
        self.medium_importance_threshold = self.config.get("memory", {}).get("medium_importance_threshold", 0.5)
        self.low_importance_threshold = self.config.get("memory", {}).get("low_importance_threshold", 0.3)
        
        # Review tracking
        self.review_history = {}  # memory_id -> list of review timestamps and results
        self.scheduled_reviews = {}  # memory_id -> next review timestamp
        self.last_review_time = datetime.now()
        
        # Memory verification settings
        self.verification_batch_size = self.config.get("memory", {}).get("verification_batch_size", 10)
        self.verification_interval = self.config.get("memory", {}).get("verification_interval", 24)  # hours
        self.last_verification_time = datetime.now() - timedelta(hours=self.verification_interval)  # Force initial verification
        
        # Load review history if available
        self._load_review_history()
        
        logger.info("ActiveRecallSystem initialized")
    
    def _load_review_history(self) -> None:
        """
        Load review history from storage.
        """
        try:
            # Try to get review history from memory manager's metadata
            if hasattr(self.memory_manager, "long_term") and hasattr(self.memory_manager.long_term, "metadata"):
                review_history = self.memory_manager.long_term.metadata.get("review_history", {})
                scheduled_reviews = self.memory_manager.long_term.metadata.get("scheduled_reviews", {})
                
                # Convert string timestamps to datetime objects
                for memory_id, reviews in review_history.items():
                    for review in reviews:
                        if isinstance(review["timestamp"], str):
                            review["timestamp"] = datetime.fromisoformat(review["timestamp"])
                
                for memory_id, timestamp in scheduled_reviews.items():
                    if isinstance(timestamp, str):
                        scheduled_reviews[memory_id] = datetime.fromisoformat(timestamp)
                
                self.review_history = review_history
                self.scheduled_reviews = scheduled_reviews
                
                logger.info(f"Loaded review history for {len(review_history)} memories")
        except Exception as e:
            logger.error(f"Error loading review history: {e}")
    
    def _save_review_history(self) -> None:
        """
        Save review history to storage.
        """
        try:
            # Convert datetime objects to strings for serialization
            serializable_history = {}
            for memory_id, reviews in self.review_history.items():
                serializable_history[memory_id] = []
                for review in reviews:
                    serializable_review = review.copy()
                    if isinstance(review["timestamp"], datetime):
                        serializable_review["timestamp"] = review["timestamp"].isoformat()
                    serializable_history[memory_id].append(serializable_review)
            
            serializable_scheduled = {}
            for memory_id, timestamp in self.scheduled_reviews.items():
                if isinstance(timestamp, datetime):
                    serializable_scheduled[memory_id] = timestamp.isoformat()
                else:
                    serializable_scheduled[memory_id] = timestamp
            
            # Save to memory manager's metadata
            if hasattr(self.memory_manager, "long_term") and hasattr(self.memory_manager.long_term, "metadata"):
                self.memory_manager.long_term.metadata["review_history"] = serializable_history
                self.memory_manager.long_term.metadata["scheduled_reviews"] = serializable_scheduled
                self.memory_manager.long_term._save_metadata()
                
                logger.info(f"Saved review history for {len(serializable_history)} memories")
        except Exception as e:
            logger.error(f"Error saving review history: {e}")
    
    def schedule_review(self, memory_id: str, importance: float, force_schedule: bool = False) -> datetime:
        """
        Schedule a memory for review based on its importance.
        
        Args:
            memory_id: The memory ID
            importance: The memory importance (0.0 to 1.0)
            force_schedule: Whether to force scheduling even if already scheduled
            
        Returns:
            Scheduled review time
        """
        # Check if already scheduled and not forcing
        if not force_schedule and memory_id in self.scheduled_reviews:
            return self.scheduled_reviews[memory_id]
        
        # Get review interval based on importance and review history
        interval = self._calculate_review_interval(memory_id, importance)
        
        # Calculate next review time
        next_review = datetime.now() + timedelta(days=interval)
        
        # Store in scheduled reviews
        self.scheduled_reviews[memory_id] = next_review
        
        # Save review history
        self._save_review_history()
        
        logger.debug(f"Scheduled review for memory {memory_id} at {next_review.isoformat()}")
        
        return next_review
    
    def _calculate_review_interval(self, memory_id: str, importance: float) -> float:
        """
        Calculate the review interval based on importance and review history.
        
        Args:
            memory_id: The memory ID
            importance: The memory importance (0.0 to 1.0)
            
        Returns:
            Review interval in days
        """
        # Get review history for this memory
        reviews = self.review_history.get(memory_id, [])
        
        # Base interval on importance
        if importance >= self.high_importance_threshold:
            base_interval = self.initial_interval * 0.5  # More frequent for high importance
        elif importance >= self.medium_importance_threshold:
            base_interval = self.initial_interval
        else:
            base_interval = self.initial_interval * 1.5  # Less frequent for low importance
        
        # If no previous reviews, return base interval
        if not reviews:
            return base_interval
        
        # Get the most recent review
        last_review = max(reviews, key=lambda r: r["timestamp"])
        
        # Calculate interval based on SuperMemo-2 algorithm
        # If last review was successful, increase interval
        # If last review was unsuccessful, decrease interval
        if last_review.get("success", False):
            # Get the previous interval
            prev_interval = last_review.get("interval", base_interval)
            
            # Calculate new interval using SM-2 algorithm
            new_interval = prev_interval * self.interval_multiplier
        else:
            # Reset interval on failure
            new_interval = base_interval * 0.5
        
        # Ensure interval is within bounds
        new_interval = max(self.min_review_interval, min(self.max_review_interval, new_interval))
        
        return new_interval
    
    def get_due_reviews(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get memories due for review.
        
        Args:
            limit: Maximum number of memories to return
            
        Returns:
            List of memories due for review
        """
        now = datetime.now()
        due_memories = []
        
        # Find memories due for review
        for memory_id, review_time in self.scheduled_reviews.items():
            if review_time <= now:
                # Get the memory
                memory = self.memory_manager.long_term.get_memory_by_id(memory_id)
                if memory:
                    due_memories.append(memory)
        
        # Sort by importance (highest first)
        due_memories.sort(key=lambda m: m.get("importance", 0), reverse=True)
        
        # Return up to the limit
        return due_memories[:limit]
    
    def record_review(self, memory_id: str, success: bool, interval: Optional[float] = None) -> None:
        """
        Record a memory review result.
        
        Args:
            memory_id: The memory ID
            success: Whether the review was successful
            interval: Optional override for the review interval
        """
        # Get current time
        now = datetime.now()
        
        # Create review record
        review = {
            "timestamp": now,
            "success": success,
            "interval": interval or self._calculate_review_interval(memory_id, 0.5)  # Default to medium importance
        }
        
        # Add to review history
        if memory_id not in self.review_history:
            self.review_history[memory_id] = []
        self.review_history[memory_id].append(review)
        
        # Update last review time
        self.last_review_time = now
        
        # If successful, reinforce the memory
        if success:
            self.memory_manager.reinforce_memory(memory_id, reinforcement_strength=0.5)
        
        # Schedule next review
        memory = self.memory_manager.long_term.get_memory_by_id(memory_id)
        if memory:
            importance = memory.get("importance", 0.5)
            self.schedule_review(memory_id, importance, force_schedule=True)
        
        # Save review history
        self._save_review_history()
        
        logger.info(f"Recorded review for memory {memory_id}: success={success}")
    
    def generate_review_question(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a review question for a memory.
        
        Args:
            memory: The memory to generate a question for
            
        Returns:
            Dictionary with question, answer, and metadata
        """
        content = memory.get("content", "")
        memory_type = memory.get("metadata", {}).get("source_type", "fact")
        
        # Generate question based on memory type
        if memory_type == "fact":
            question = f"Do you remember this fact: {content}?"
            answer = content
        elif memory_type == "preference":
            question = f"What is your preference regarding: {content.split(':')[0] if ':' in content else content}?"
            answer = content
        elif memory_type == "conversation":
            question = f"Do you recall this conversation: {content[:50]}...?"
            answer = content
        else:
            question = f"Do you remember: {content[:50]}...?"
            answer = content
        
        return {
            "memory_id": memory.get("id"),
            "question": question,
            "answer": answer,
            "memory_type": memory_type,
            "timestamp": datetime.now().isoformat()
        }
    
    def verify_memory_integrity(self, batch_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Verify the integrity of memories by checking for inconsistencies.
        
        Args:
            batch_size: Number of memories to verify (default: self.verification_batch_size)
            
        Returns:
            Dictionary with verification results
        """
        batch_size = batch_size or self.verification_batch_size
        now = datetime.now()
        
        # Check if it's time for verification
        if (now - self.last_verification_time).total_seconds() < self.verification_interval * 3600:
            return {
                "verified": False,
                "reason": "Verification interval not reached",
                "next_verification": self.last_verification_time + timedelta(hours=self.verification_interval)
            }
        
        # Get a random sample of memories
        all_memory_ids = list(self.memory_manager.long_term.metadata.get("memories", {}).keys())
        if not all_memory_ids:
            return {
                "verified": False,
                "reason": "No memories to verify",
                "count": 0
            }
        
        # Select a random sample
        sample_size = min(batch_size, len(all_memory_ids))
        sample_ids = random.sample(all_memory_ids, sample_size)
        
        # Verify each memory
        results = {
            "verified": True,
            "count": sample_size,
            "timestamp": now.isoformat(),
            "issues": []
        }
        
        for memory_id in sample_ids:
            # Get the memory
            memory = self.memory_manager.long_term.get_memory_by_id(memory_id)
            
            # Check if memory exists
            if not memory:
                results["issues"].append({
                    "memory_id": memory_id,
                    "issue": "Memory not found",
                    "severity": "high"
                })
                results["verified"] = False
                continue
            
            # Check for required fields
            required_fields = ["content", "metadata"]
            for field in required_fields:
                if field not in memory:
                    results["issues"].append({
                        "memory_id": memory_id,
                        "issue": f"Missing required field: {field}",
                        "severity": "medium"
                    })
                    results["verified"] = False
            
            # Check metadata fields
            metadata = memory.get("metadata", {})
            required_metadata = ["source_type", "timestamp", "importance"]
            for field in required_metadata:
                if field not in metadata:
                    results["issues"].append({
                        "memory_id": memory_id,
                        "issue": f"Missing required metadata: {field}",
                        "severity": "low"
                    })
            
            # Check content is not empty
            if not memory.get("content", "").strip():
                results["issues"].append({
                    "memory_id": memory_id,
                    "issue": "Empty content",
                    "severity": "medium"
                })
                results["verified"] = False
        
        # Update last verification time
        self.last_verification_time = now
        
        # If issues were found, schedule affected memories for review
        for issue in results["issues"]:
            if issue["severity"] in ["high", "medium"]:
                memory_id = issue["memory_id"]
                self.schedule_review(memory_id, 1.0, force_schedule=True)  # High importance for issues
        
        return results
    
    def run_scheduled_tasks(self) -> Dict[str, Any]:
        """
        Run scheduled tasks for the active recall system.
        
        Returns:
            Dictionary with task results
        """
        results = {
            "verification": None,
            "reviews_scheduled": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Run memory verification if due
        if (datetime.now() - self.last_verification_time).total_seconds() >= self.verification_interval * 3600:
            results["verification"] = self.verify_memory_integrity()
        
        # Schedule reviews for memories that don't have a scheduled review
        all_memory_ids = list(self.memory_manager.long_term.metadata.get("memories", {}).keys())
        for memory_id in all_memory_ids:
            if memory_id not in self.scheduled_reviews:
                memory = self.memory_manager.long_term.get_memory_by_id(memory_id)
                if memory:
                    importance = memory.get("importance", 0.5)
                    self.schedule_review(memory_id, importance)
                    results["reviews_scheduled"] += 1
        
        return results
    
    def get_memory_health_metrics(self) -> Dict[str, Any]:
        """
        Get metrics about memory health and review status.
        
        Returns:
            Dictionary with memory health metrics
        """
        now = datetime.now()
        
        # Count memories by review status
        total_memories = len(self.memory_manager.long_term.metadata.get("memories", {}))
        scheduled_count = len(self.scheduled_reviews)
        due_count = sum(1 for review_time in self.scheduled_reviews.values() if review_time <= now)
        
        # Calculate review success rate
        success_count = 0
        review_count = 0
        for reviews in self.review_history.values():
            for review in reviews:
                review_count += 1
                if review.get("success", False):
                    success_count += 1
        
        success_rate = success_count / max(1, review_count)
        
        # Calculate average review interval
        intervals = []
        for reviews in self.review_history.values():
            for review in reviews:
                interval = review.get("interval")
                if interval is not None:
                    intervals.append(interval)
        
        avg_interval = sum(intervals) / max(1, len(intervals)) if intervals else 0
        
        return {
            "total_memories": total_memories,
            "scheduled_reviews": scheduled_count,
            "due_reviews": due_count,
            "review_count": review_count,
            "success_rate": success_rate,
            "avg_interval": avg_interval,
            "last_verification": self.last_verification_time.isoformat(),
            "last_review": self.last_review_time.isoformat(),
            "timestamp": now.isoformat()
        }
