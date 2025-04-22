"""
Memory-based personality conditioning system for Coda Lite.

This module provides a system for learning from user feedback stored in memory
and adjusting personality parameters accordingly.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Set
from enum import Enum, auto
from collections import Counter

logger = logging.getLogger("coda.personality.memory_conditioning")

class FeedbackPattern(Enum):
    """Enum for different feedback patterns."""
    CONSISTENT_NEGATIVE = auto()  # Consistently negative feedback
    CONSISTENT_POSITIVE = auto()  # Consistently positive feedback
    MIXED = auto()                # Mixed feedback
    IMPROVING = auto()            # Improving feedback over time
    DECLINING = auto()            # Declining feedback over time
    INSUFFICIENT = auto()         # Not enough data

class MemoryConditioner:
    """
    Learns from user feedback stored in memory and adjusts personality accordingly.
    
    This class:
    - Analyzes feedback patterns from memory
    - Identifies consistent preferences
    - Adjusts personality parameters based on feedback history
    - Provides insights into user preferences
    """
    
    def __init__(self, 
                 memory_manager=None, 
                 personality_manager=None,
                 behavioral_conditioner=None,
                 config=None):
        """
        Initialize the memory conditioner.
        
        Args:
            memory_manager: Memory manager for accessing stored feedback
            personality_manager: Personality manager for adjusting parameters
            behavioral_conditioner: Behavioral conditioner for applying learned patterns
            config: Configuration dictionary
        """
        self.memory_manager = memory_manager
        self.personality_manager = personality_manager
        self.behavioral_conditioner = behavioral_conditioner
        self.config = config or {}
        
        # Configuration
        self.min_feedback_threshold = self.config.get("memory_conditioning.min_feedback", 3)
        self.feedback_recency_days = self.config.get("memory_conditioning.recency_days", 7)
        self.adjustment_strength = self.config.get("memory_conditioning.adjustment_strength", 0.15)
        
        # Parameter mapping for different feedback types
        self.parameter_mapping = {
            "TONE": ["formality", "assertiveness"],
            "VERBOSITY": ["verbosity"],
            "HELPFULNESS": ["proactivity"],
            "ACCURACY": ["assertiveness"],
            "MEMORY": [],  # No direct parameter mapping
            "GENERAL": ["verbosity", "formality", "humor", "assertiveness", "proactivity"]
        }
        
        # Last analysis timestamp
        self.last_analysis = None
        
        # Analysis results cache
        self.cached_analysis = {}
        
        logger.info("Memory conditioner initialized")
    
    def analyze_feedback_patterns(self, force_refresh=False) -> Dict[str, Any]:
        """
        Analyze feedback patterns from memory.
        
        Args:
            force_refresh: Force a refresh of the analysis
            
        Returns:
            Dictionary of feedback patterns and insights
        """
        # Check if we have a recent cached analysis
        if not force_refresh and self.cached_analysis and self.last_analysis:
            # Use cache if it's less than 1 hour old
            if datetime.now() - self.last_analysis < timedelta(hours=1):
                return self.cached_analysis
        
        # Get feedback from memory
        feedback_items = self._get_feedback_from_memory()
        
        if not feedback_items or len(feedback_items) < self.min_feedback_threshold:
            logger.info(f"Insufficient feedback for analysis: {len(feedback_items) if feedback_items else 0} items")
            return {"pattern": FeedbackPattern.INSUFFICIENT.name, "insights": {}}
        
        # Group feedback by type
        feedback_by_type = {}
        for item in feedback_items:
            feedback_type = item.get("type")
            if not feedback_type:
                continue
                
            # Convert to string if it's an enum
            type_str = feedback_type.name if hasattr(feedback_type, "name") else str(feedback_type)
            
            if type_str not in feedback_by_type:
                feedback_by_type[type_str] = []
            
            feedback_by_type[type_str].append(item)
        
        # Analyze patterns for each type
        patterns = {}
        insights = {}
        
        for feedback_type, items in feedback_by_type.items():
            if len(items) < 2:  # Need at least 2 items for pattern analysis
                continue
                
            # Analyze sentiment pattern
            pattern = self._analyze_sentiment_pattern(items)
            patterns[feedback_type] = pattern
            
            # Generate insights
            type_insights = self._generate_insights(feedback_type, items, pattern)
            if type_insights:
                insights[feedback_type] = type_insights
        
        # Determine overall pattern
        overall_pattern = self._determine_overall_pattern(patterns)
        
        # Update cache
        self.cached_analysis = {
            "pattern": overall_pattern.name,
            "type_patterns": {k: v.name for k, v in patterns.items()},
            "insights": insights,
            "feedback_count": len(feedback_items)
        }
        self.last_analysis = datetime.now()
        
        logger.info(f"Analyzed {len(feedback_items)} feedback items, overall pattern: {overall_pattern.name}")
        return self.cached_analysis
    
    def _get_feedback_from_memory(self) -> List[Dict[str, Any]]:
        """
        Get feedback items from memory.
        
        Returns:
            List of feedback items
        """
        if not self.memory_manager or not hasattr(self.memory_manager, 'long_term'):
            return []
        
        try:
            # Get recent feedback from memory
            cutoff_date = datetime.now() - timedelta(days=self.feedback_recency_days)
            cutoff_str = cutoff_date.strftime("%Y-%m-%d")
            
            # Search for feedback memories
            memories = self.memory_manager.long_term.search_memories(
                f"source_type:feedback date:>{cutoff_str}", 
                limit=50
            )
            
            # Extract feedback items
            feedback_items = []
            for memory in memories:
                # Check if it's a feedback memory
                if memory.get("source_type") != "feedback":
                    continue
                
                # Extract metadata
                metadata = memory.get("metadata", {})
                
                # Create feedback item
                feedback_item = {
                    "content": memory.get("content", ""),
                    "type": metadata.get("feedback_type"),
                    "prompt": metadata.get("prompt"),
                    "sentiment": metadata.get("sentiment"),
                    "intent_type": metadata.get("intent_type"),
                    "timestamp": metadata.get("timestamp", memory.get("created_at", "")),
                }
                
                feedback_items.append(feedback_item)
            
            return feedback_items
            
        except Exception as e:
            logger.error(f"Error getting feedback from memory: {e}")
            return []
    
    def _analyze_sentiment_pattern(self, feedback_items: List[Dict[str, Any]]) -> FeedbackPattern:
        """
        Analyze sentiment pattern in feedback items.
        
        Args:
            feedback_items: List of feedback items
            
        Returns:
            FeedbackPattern enum value
        """
        if len(feedback_items) < 2:
            return FeedbackPattern.INSUFFICIENT
        
        # Count sentiments
        sentiments = [item.get("sentiment", "neutral") for item in feedback_items]
        sentiment_counts = Counter(sentiments)
        
        # Calculate percentages
        total = len(sentiments)
        positive_pct = sentiment_counts.get("positive", 0) / total
        negative_pct = sentiment_counts.get("negative", 0) / total
        neutral_pct = sentiment_counts.get("neutral", 0) / total
        
        # Sort by timestamp
        sorted_items = sorted(feedback_items, key=lambda x: x.get("timestamp", ""))
        
        # Check for trends
        if len(sorted_items) >= 3:
            # Check first half vs second half
            midpoint = len(sorted_items) // 2
            first_half = sorted_items[:midpoint]
            second_half = sorted_items[midpoint:]
            
            first_half_positive = sum(1 for item in first_half if item.get("sentiment") == "positive")
            first_half_negative = sum(1 for item in first_half if item.get("sentiment") == "negative")
            second_half_positive = sum(1 for item in second_half if item.get("sentiment") == "positive")
            second_half_negative = sum(1 for item in second_half if item.get("sentiment") == "negative")
            
            # Calculate trend
            first_half_ratio = first_half_positive / (first_half_positive + first_half_negative) if (first_half_positive + first_half_negative) > 0 else 0.5
            second_half_ratio = second_half_positive / (second_half_positive + second_half_negative) if (second_half_positive + second_half_negative) > 0 else 0.5
            
            if second_half_ratio > first_half_ratio + 0.2:
                return FeedbackPattern.IMPROVING
            elif first_half_ratio > second_half_ratio + 0.2:
                return FeedbackPattern.DECLINING
        
        # Check for consistent patterns
        if positive_pct >= 0.7:
            return FeedbackPattern.CONSISTENT_POSITIVE
        elif negative_pct >= 0.7:
            return FeedbackPattern.CONSISTENT_NEGATIVE
        else:
            return FeedbackPattern.MIXED
    
    def _determine_overall_pattern(self, type_patterns: Dict[str, FeedbackPattern]) -> FeedbackPattern:
        """
        Determine overall feedback pattern from type patterns.
        
        Args:
            type_patterns: Dictionary of feedback types and their patterns
            
        Returns:
            Overall FeedbackPattern
        """
        if not type_patterns:
            return FeedbackPattern.INSUFFICIENT
        
        # Count pattern occurrences
        pattern_counts = Counter(type_patterns.values())
        
        # Check for dominant pattern
        most_common = pattern_counts.most_common(1)[0]
        pattern, count = most_common
        
        if count >= len(type_patterns) * 0.6:
            # If a pattern appears in 60% or more of types, use it as overall pattern
            return pattern
        else:
            # Otherwise, use MIXED
            return FeedbackPattern.MIXED
    
    def _generate_insights(self, 
                          feedback_type: str, 
                          items: List[Dict[str, Any]], 
                          pattern: FeedbackPattern) -> Dict[str, Any]:
        """
        Generate insights from feedback items.
        
        Args:
            feedback_type: Type of feedback
            items: List of feedback items
            pattern: Detected pattern
            
        Returns:
            Dictionary of insights
        """
        insights = {
            "count": len(items),
            "pattern": pattern.name,
            "sentiment_distribution": {},
            "recommendations": []
        }
        
        # Calculate sentiment distribution
        sentiments = [item.get("sentiment", "neutral") for item in items]
        sentiment_counts = Counter(sentiments)
        
        for sentiment in ["positive", "negative", "neutral"]:
            insights["sentiment_distribution"][sentiment] = sentiment_counts.get(sentiment, 0) / len(items)
        
        # Generate recommendations based on pattern
        if pattern == FeedbackPattern.CONSISTENT_NEGATIVE:
            # For consistently negative feedback, recommend parameter adjustments
            parameters = self.parameter_mapping.get(feedback_type, [])
            
            for param in parameters:
                if param == "verbosity":
                    insights["recommendations"].append({
                        "parameter": param,
                        "action": "Try adjusting verbosity in the opposite direction",
                        "confidence": 0.8
                    })
                elif param == "formality":
                    insights["recommendations"].append({
                        "parameter": param,
                        "action": "Try adjusting formality in the opposite direction",
                        "confidence": 0.8
                    })
                elif param == "humor":
                    insights["recommendations"].append({
                        "parameter": param,
                        "action": "Try adjusting humor in the opposite direction",
                        "confidence": 0.7
                    })
                elif param == "assertiveness":
                    insights["recommendations"].append({
                        "parameter": param,
                        "action": "Try adjusting assertiveness in the opposite direction",
                        "confidence": 0.7
                    })
                elif param == "proactivity":
                    insights["recommendations"].append({
                        "parameter": param,
                        "action": "Try adjusting proactivity in the opposite direction",
                        "confidence": 0.7
                    })
        
        elif pattern == FeedbackPattern.DECLINING:
            # For declining feedback, recommend reverting recent changes
            insights["recommendations"].append({
                "action": "Consider reverting recent personality changes",
                "confidence": 0.6
            })
        
        return insights
    
    def apply_feedback_patterns(self) -> Dict[str, Any]:
        """
        Apply feedback patterns to personality parameters.
        
        Returns:
            Dictionary with application results
        """
        # Analyze feedback patterns
        analysis = self.analyze_feedback_patterns()
        
        if analysis.get("pattern") == FeedbackPattern.INSUFFICIENT.name:
            logger.info("Insufficient feedback for conditioning")
            return {"applied": False, "reason": "insufficient_feedback"}
        
        # Check if we have a behavioral conditioner
        if not self.behavioral_conditioner:
            logger.info("No behavioral conditioner available")
            return {"applied": False, "reason": "no_behavioral_conditioner"}
        
        # Apply patterns for each feedback type
        applied_changes = []
        
        for feedback_type, type_insights in analysis.get("insights", {}).items():
            pattern = type_insights.get("pattern")
            
            if pattern == FeedbackPattern.CONSISTENT_NEGATIVE.name:
                # Apply parameter adjustments for consistently negative feedback
                parameters = self.parameter_mapping.get(feedback_type, [])
                
                for param in parameters:
                    # Get current value
                    current_value = self.behavioral_conditioner.behavior_profile.get(param, 0.5)
                    
                    # Calculate new value (move in opposite direction)
                    if current_value > 0.5:
                        new_value = max(0.1, current_value - self.adjustment_strength)
                    else:
                        new_value = min(0.9, current_value + self.adjustment_strength)
                    
                    # Update behavior profile
                    self.behavioral_conditioner.behavior_profile[param] = new_value
                    
                    applied_changes.append({
                        "parameter": param,
                        "old_value": current_value,
                        "new_value": new_value,
                        "reason": f"consistent_negative_{feedback_type.lower()}_feedback"
                    })
                    
                    logger.info(f"Adjusted {param} from {current_value:.2f} to {new_value:.2f} based on negative {feedback_type} feedback")
            
            elif pattern == FeedbackPattern.CONSISTENT_POSITIVE.name:
                # For consistently positive feedback, reinforce current settings
                parameters = self.parameter_mapping.get(feedback_type, [])
                
                for param in parameters:
                    # Increase confidence in current value
                    self.behavioral_conditioner.behavior_profile["confidence"] = min(
                        self.behavioral_conditioner.behavior_profile.get("confidence", 0.5) + 0.1,
                        0.9
                    )
                    
                    applied_changes.append({
                        "parameter": "confidence",
                        "old_value": self.behavioral_conditioner.behavior_profile.get("confidence", 0.5) - 0.1,
                        "new_value": self.behavioral_conditioner.behavior_profile.get("confidence", 0.5),
                        "reason": f"consistent_positive_{feedback_type.lower()}_feedback"
                    })
                    
                    logger.info(f"Increased confidence based on positive {feedback_type} feedback")
        
        # Save updated behavior profile
        if applied_changes:
            # Update metadata
            self.behavioral_conditioner.behavior_profile["last_updated"] = datetime.now().isoformat()
            self.behavioral_conditioner.behavior_profile["observation_count"] = self.behavioral_conditioner.behavior_profile.get("observation_count", 0) + 1
            
            # Save profile
            self.behavioral_conditioner._save_behavior_profile()
            
            # Apply to parameters if confidence is high enough
            if self.behavioral_conditioner.behavior_profile.get("confidence", 0) >= 0.3:
                self.behavioral_conditioner._apply_to_parameters()
            
            logger.info(f"Applied {len(applied_changes)} changes based on feedback patterns")
            
            return {
                "applied": True,
                "changes": applied_changes,
                "confidence": self.behavioral_conditioner.behavior_profile.get("confidence", 0)
            }
        else:
            logger.info("No changes applied from feedback patterns")
            return {"applied": False, "reason": "no_actionable_patterns"}
    
    def get_user_preference_insights(self) -> Dict[str, Any]:
        """
        Get insights into user preferences based on feedback.
        
        Returns:
            Dictionary with user preference insights
        """
        # Analyze feedback patterns
        analysis = self.analyze_feedback_patterns()
        
        if analysis.get("pattern") == FeedbackPattern.INSUFFICIENT.name:
            return {"available": False, "reason": "insufficient_feedback"}
        
        # Generate insights
        insights = {
            "available": True,
            "overall_pattern": analysis.get("pattern"),
            "feedback_count": analysis.get("feedback_count", 0),
            "preferences": {},
            "recommendations": []
        }
        
        # Extract preferences from type insights
        for feedback_type, type_insights in analysis.get("insights", {}).items():
            pattern = type_insights.get("pattern")
            sentiment_distribution = type_insights.get("sentiment_distribution", {})
            
            # Only include clear preferences
            if pattern in [FeedbackPattern.CONSISTENT_POSITIVE.name, FeedbackPattern.CONSISTENT_NEGATIVE.name]:
                parameters = self.parameter_mapping.get(feedback_type, [])
                
                for param in parameters:
                    if param not in insights["preferences"]:
                        insights["preferences"][param] = []
                    
                    if pattern == FeedbackPattern.CONSISTENT_POSITIVE.name:
                        # For positive feedback, user likely prefers current setting
                        current_value = self.behavioral_conditioner.behavior_profile.get(param, 0.5) if self.behavioral_conditioner else 0.5
                        
                        if current_value > 0.7:
                            preference = "high"
                        elif current_value < 0.3:
                            preference = "low"
                        else:
                            preference = "moderate"
                        
                        insights["preferences"][param].append({
                            "preference": preference,
                            "confidence": sentiment_distribution.get("positive", 0),
                            "source": feedback_type
                        })
                    
                    elif pattern == FeedbackPattern.CONSISTENT_NEGATIVE.name:
                        # For negative feedback, user likely prefers opposite of current setting
                        current_value = self.behavioral_conditioner.behavior_profile.get(param, 0.5) if self.behavioral_conditioner else 0.5
                        
                        if current_value > 0.5:
                            preference = "low"
                        else:
                            preference = "high"
                        
                        insights["preferences"][param].append({
                            "preference": preference,
                            "confidence": sentiment_distribution.get("negative", 0),
                            "source": feedback_type
                        })
            
            # Include recommendations
            for recommendation in type_insights.get("recommendations", []):
                if recommendation not in insights["recommendations"]:
                    insights["recommendations"].append(recommendation)
        
        return insights
    
    def reset(self) -> None:
        """Reset the memory conditioner."""
        self.last_analysis = None
        self.cached_analysis = {}
        logger.info("Reset memory conditioner")
