"""
Temporal Weighting System for Coda Lite's Memory.

This module provides functionality to apply time-based decay to memory importance,
implement recency bias in memory retrieval, and configure decay rates for different
types of memories.
"""

import math
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union

logger = logging.getLogger("coda.memory.temporal")

class TemporalWeightingSystem:
    """
    Manages temporal weighting for memories.
    
    Responsibilities:
    - Apply time-based decay to memory importance
    - Implement recency bias in memory retrieval
    - Configure decay rates for different types of memories
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the temporal weighting system.
        
        Args:
            config: Configuration dictionary with temporal weighting settings
        """
        # Default decay rates (half-life in days)
        self.default_decay_rate = config.get("memory", {}).get("default_decay_rate", 30.0)
        
        # Decay rates for different memory types (half-life in days)
        self.decay_rates = {
            "conversation": config.get("memory", {}).get("conversation_decay_rate", 15.0),
            "fact": config.get("memory", {}).get("fact_decay_rate", 60.0),
            "preference": config.get("memory", {}).get("preference_decay_rate", 90.0),
            "feedback": config.get("memory", {}).get("feedback_decay_rate", 45.0),
            "summary": config.get("memory", {}).get("summary_decay_rate", 30.0)
        }
        
        # Recency bias factor (higher = more bias towards recent memories)
        self.recency_bias = config.get("memory", {}).get("recency_bias", 1.0)
        
        # Importance retention factor (higher = importance decays slower)
        self.importance_retention = config.get("memory", {}).get("importance_retention", 0.8)
        
        # Reinforcement settings
        self.reinforcement_boost = config.get("memory", {}).get("reinforcement_boost", 0.2)
        self.max_reinforcement_count = config.get("memory", {}).get("max_reinforcement_count", 5)
        
        logger.info(f"TemporalWeightingSystem initialized with default_decay_rate={self.default_decay_rate}")
    
    def calculate_decay_factor(self, 
                              timestamp: str, 
                              source_type: str = "conversation",
                              reinforcement_count: int = 0) -> float:
        """
        Calculate the decay factor for a memory based on its age and type.
        
        Args:
            timestamp: ISO format timestamp of the memory
            source_type: Type of memory (conversation, fact, preference, etc.)
            reinforcement_count: Number of times the memory has been reinforced
            
        Returns:
            Decay factor (0.0 to 1.0)
        """
        try:
            # Parse timestamp
            memory_time = datetime.fromisoformat(timestamp)
            now = datetime.now()
            
            # Calculate age in days
            age_days = (now - memory_time).total_seconds() / (24 * 3600)
            
            # Get decay rate for this memory type
            decay_rate = self.decay_rates.get(source_type, self.default_decay_rate)
            
            # Adjust decay rate based on reinforcement
            if reinforcement_count > 0:
                # Each reinforcement extends the half-life
                reinforcement_factor = min(reinforcement_count, self.max_reinforcement_count) / self.max_reinforcement_count
                adjusted_decay_rate = decay_rate * (1 + reinforcement_factor * self.reinforcement_boost)
            else:
                adjusted_decay_rate = decay_rate
            
            # Apply exponential decay formula: 2^(-age/half_life)
            decay_factor = 2 ** (-age_days / adjusted_decay_rate)
            
            return decay_factor
        except Exception as e:
            logger.error(f"Error calculating decay factor: {e}")
            return 1.0  # Default to no decay on error
    
    def apply_temporal_weighting(self, 
                               memories: List[Dict[str, Any]],
                               recency_boost: bool = True) -> List[Dict[str, Any]]:
        """
        Apply temporal weighting to a list of memories.
        
        Args:
            memories: List of memory dictionaries
            recency_boost: Whether to apply additional recency bias
            
        Returns:
            List of memories with updated scores
        """
        now = datetime.now()
        weighted_memories = []
        
        for memory in memories:
            # Get memory metadata
            timestamp = memory.get("timestamp", now.isoformat())
            source_type = memory.get("source_type", "conversation")
            importance = memory.get("importance", 0.5)
            reinforcement_count = memory.get("reinforcement_count", 0)
            similarity = memory.get("similarity", 0.0)
            
            # Calculate decay factor
            decay_factor = self.calculate_decay_factor(timestamp, source_type, reinforcement_count)
            
            # Calculate weighted importance
            # Importance decays slower than recency
            importance_weight = importance ** (1 - self.importance_retention)
            
            # Calculate recency score
            if recency_boost:
                try:
                    memory_time = datetime.fromisoformat(timestamp)
                    age_days = (now - memory_time).total_seconds() / (24 * 3600)
                    # Recency score: 1.0 for now, approaches 0.0 as age increases
                    recency_score = 1.0 / (1.0 + age_days * self.recency_bias / 10.0)
                except Exception as e:
                    logger.error(f"Error calculating recency score: {e}")
                    recency_score = 0.5
            else:
                recency_score = 0.5
            
            # Calculate final score
            # If similarity is provided, include it in the score
            if similarity > 0:
                final_score = (similarity * 0.4 + importance_weight * 0.3 + recency_score * 0.3) * decay_factor
            else:
                final_score = (importance_weight * 0.5 + recency_score * 0.5) * decay_factor
            
            # Update memory with temporal weighting information
            weighted_memory = memory.copy()
            weighted_memory.update({
                "decay_factor": decay_factor,
                "importance_weight": importance_weight,
                "recency_score": recency_score,
                "final_score": final_score
            })
            
            weighted_memories.append(weighted_memory)
        
        # Sort by final score (descending)
        weighted_memories.sort(key=lambda x: x.get("final_score", 0), reverse=True)
        
        return weighted_memories
    
    def calculate_forgetting_threshold(self, 
                                     memory_age_days: float,
                                     source_type: str = "conversation",
                                     importance: float = 0.5) -> float:
        """
        Calculate the forgetting threshold for a memory.
        
        Args:
            memory_age_days: Age of the memory in days
            source_type: Type of memory
            importance: Original importance of the memory
            
        Returns:
            Forgetting threshold (0.0 to 1.0)
        """
        # Get decay rate for this memory type
        decay_rate = self.decay_rates.get(source_type, self.default_decay_rate)
        
        # Base threshold depends on memory type
        if source_type == "fact":
            base_threshold = 0.1  # Facts are harder to forget
        elif source_type == "preference":
            base_threshold = 0.05  # Preferences are very hard to forget
        else:
            base_threshold = 0.2  # Conversations are easier to forget
        
        # Adjust threshold based on importance
        # Higher importance = lower threshold (harder to forget)
        importance_factor = 1.0 - importance
        
        # Adjust threshold based on age
        # Older memories have lower thresholds (easier to forget)
        age_factor = min(memory_age_days / decay_rate, 1.0)
        
        # Calculate final threshold
        threshold = base_threshold * (1.0 + importance_factor) * (1.0 + age_factor)
        
        # Cap at 0.9 (we always keep some chance of remembering)
        threshold = min(threshold, 0.9)
        
        return threshold
    
    def should_forget_memory(self, 
                           memory: Dict[str, Any],
                           current_memory_count: int,
                           max_memories: int) -> bool:
        """
        Determine if a memory should be forgotten based on its age, importance, and system load.
        
        Args:
            memory: Memory dictionary
            current_memory_count: Current number of memories in the system
            max_memories: Maximum number of memories allowed
            
        Returns:
            True if the memory should be forgotten, False otherwise
        """
        # If we're under the memory limit, be more conservative about forgetting
        memory_pressure = current_memory_count / max_memories
        
        # If we're over 90% capacity, be more aggressive about forgetting
        if memory_pressure > 0.9:
            pressure_factor = 1.5
        elif memory_pressure > 0.7:
            pressure_factor = 1.2
        else:
            pressure_factor = 1.0
        
        # Get memory metadata
        timestamp = memory.get("timestamp", datetime.now().isoformat())
        source_type = memory.get("source_type", "conversation")
        importance = memory.get("importance", 0.5)
        
        try:
            # Calculate age in days
            memory_time = datetime.fromisoformat(timestamp)
            now = datetime.now()
            age_days = (now - memory_time).total_seconds() / (24 * 3600)
            
            # Calculate forgetting threshold
            threshold = self.calculate_forgetting_threshold(age_days, source_type, importance)
            
            # Adjust threshold based on memory pressure
            adjusted_threshold = threshold * pressure_factor
            
            # Calculate decay factor
            decay_factor = self.calculate_decay_factor(timestamp, source_type)
            
            # If decay factor is below threshold, forget the memory
            return decay_factor < adjusted_threshold
            
        except Exception as e:
            logger.error(f"Error determining if memory should be forgotten: {e}")
            return False  # Default to keeping the memory on error
    
    def reinforce_memory(self, 
                        memory: Dict[str, Any],
                        reinforcement_strength: float = 1.0) -> Dict[str, Any]:
        """
        Reinforce a memory to make it more resistant to forgetting.
        
        Args:
            memory: Memory dictionary
            reinforcement_strength: Strength of reinforcement (0.0 to 1.0)
            
        Returns:
            Updated memory dictionary
        """
        # Create a copy of the memory
        updated_memory = memory.copy()
        
        # Get current reinforcement count
        reinforcement_count = updated_memory.get("reinforcement_count", 0)
        
        # Increment reinforcement count
        updated_memory["reinforcement_count"] = reinforcement_count + 1
        
        # Update timestamp to now (partial update based on strength)
        try:
            old_timestamp = updated_memory.get("timestamp", datetime.now().isoformat())
            old_time = datetime.fromisoformat(old_timestamp)
            now = datetime.now()
            
            # Calculate time difference
            time_diff = now - old_time
            
            # Apply partial update based on strength
            # strength=1.0 means full update to now
            # strength=0.0 means no update
            new_time = old_time + time_diff * reinforcement_strength
            
            # Update timestamp
            updated_memory["timestamp"] = new_time.isoformat()
            
            # Boost importance
            importance = updated_memory.get("importance", 0.5)
            boost = self.reinforcement_boost * reinforcement_strength
            updated_memory["importance"] = min(importance + boost, 1.0)
            
            logger.info(f"Reinforced memory with strength {reinforcement_strength}")
            
        except Exception as e:
            logger.error(f"Error reinforcing memory: {e}")
        
        return updated_memory
