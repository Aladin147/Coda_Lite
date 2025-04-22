"""
Personality parameter system for Coda Lite.

This module provides a flexible system for managing personality parameters
that can be adjusted based on user preferences, context, and patterns.
"""

import os
import json
import logging
import copy
from typing import Dict, Any, List, Optional, Union, Tuple

logger = logging.getLogger("coda.personality.parameters")

class PersonalityParameters:
    """
    Manages configurable personality parameters with context-aware adjustments.
    
    This class provides:
    - Storage and retrieval of personality parameters
    - Parameter adjustment based on context
    - Validation of parameter values
    - Persistence of parameter settings
    """
    
    def __init__(self, config_path: str = "config/personality/parameters.json"):
        """
        Initialize personality parameters.
        
        Args:
            config_path: Path to the parameters configuration file
        """
        self.config_path = config_path
        self.parameters = {}
        self.default_parameters = {}
        self.load_parameters()
        
        # Track parameter adjustments for explainability
        self.adjustment_history = []
        
        logger.info(f"Initialized personality parameters with {len(self.parameters)} parameters")
    
    def load_parameters(self) -> bool:
        """
        Load parameters from configuration file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                self.parameters = config.get("parameters", {})
                self.default_parameters = copy.deepcopy(self.parameters)
                logger.info(f"Loaded {len(self.parameters)} personality parameters")
                return True
            else:
                logger.warning(f"Parameters file not found: {self.config_path}")
                self._create_default_parameters()
                return False
        except Exception as e:
            logger.error(f"Error loading parameters: {e}")
            self._create_default_parameters()
            return False
    
    def _create_default_parameters(self) -> None:
        """Create default parameters if configuration file doesn't exist."""
        self.parameters = {
            "verbosity": {
                "value": 0.5,
                "range": [0.0, 1.0],
                "description": "Controls length and detail of responses",
                "context_adjustments": {
                    "technical_topic": 0.2,
                    "casual_conversation": -0.1,
                    "formal_context": 0.1
                }
            },
            "assertiveness": {
                "value": 0.5,
                "range": [0.0, 1.0],
                "description": "Controls how assertive or tentative responses are",
                "context_adjustments": {
                    "information_request": 0.2,
                    "creative_task": -0.1,
                    "emergency": 0.3
                }
            },
            "humor": {
                "value": 0.3,
                "range": [0.0, 1.0],
                "description": "Controls the level of humor in responses",
                "context_adjustments": {
                    "entertainment": 0.3,
                    "technical_topic": -0.2,
                    "formal_context": -0.2
                }
            },
            "formality": {
                "value": 0.5,
                "range": [0.0, 1.0],
                "description": "Controls the formality of language",
                "context_adjustments": {
                    "formal_context": 0.3,
                    "casual_conversation": -0.3,
                    "entertainment": -0.2
                }
            },
            "proactivity": {
                "value": 0.4,
                "range": [0.0, 1.0],
                "description": "Controls how proactive vs. reactive responses are",
                "context_adjustments": {
                    "information_request": -0.2,
                    "problem_solving": 0.2,
                    "idle_time": 0.3
                }
            }
        }
        
        self.default_parameters = copy.deepcopy(self.parameters)
        
        # Save the default parameters
        self.save_parameters()
        
        logger.info("Created default personality parameters")
    
    def save_parameters(self) -> bool:
        """
        Save parameters to configuration file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Save parameters
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({"parameters": self.parameters}, f, indent=2)
                
            logger.info(f"Saved personality parameters to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving parameters: {e}")
            return False
    
    def get_parameter(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a parameter by name.
        
        Args:
            name: Parameter name
            
        Returns:
            Parameter configuration or None if not found
        """
        return self.parameters.get(name)
    
    def get_parameter_value(self, name: str) -> Optional[float]:
        """
        Get a parameter's current value.
        
        Args:
            name: Parameter name
            
        Returns:
            Parameter value or None if not found
        """
        param = self.parameters.get(name)
        if param:
            return param.get("value")
        return None
    
    def set_parameter_value(self, name: str, value: float, reason: str = "manual") -> bool:
        """
        Set a parameter's value.
        
        Args:
            name: Parameter name
            value: New parameter value
            reason: Reason for the change
            
        Returns:
            True if successful, False otherwise
        """
        if name not in self.parameters:
            logger.warning(f"Unknown parameter: {name}")
            return False
            
        param = self.parameters[name]
        param_range = param.get("range", [0.0, 1.0])
        
        # Clamp value to valid range
        clamped_value = max(param_range[0], min(value, param_range[1]))
        
        if clamped_value != value:
            logger.warning(f"Parameter value {value} out of range {param_range}, clamped to {clamped_value}")
        
        # Record the adjustment
        old_value = param.get("value")
        self.adjustment_history.append({
            "parameter": name,
            "old_value": old_value,
            "new_value": clamped_value,
            "reason": reason,
            "timestamp": import_time()
        })
        
        # Update the parameter
        param["value"] = clamped_value
        
        logger.info(f"Set parameter {name} to {clamped_value} (reason: {reason})")
        return True
    
    def adjust_for_context(self, context_type: str) -> Dict[str, float]:
        """
        Adjust parameters for a specific context.
        
        Args:
            context_type: Type of context (e.g., "technical_topic", "formal_context")
            
        Returns:
            Dictionary of adjusted parameters
        """
        adjustments = {}
        
        for name, param in self.parameters.items():
            context_adjustments = param.get("context_adjustments", {})
            adjustment = context_adjustments.get(context_type, 0.0)
            
            if adjustment != 0.0:
                current_value = param.get("value", 0.5)
                param_range = param.get("range", [0.0, 1.0])
                
                # Apply adjustment with clamping
                new_value = max(param_range[0], min(current_value + adjustment, param_range[1]))
                
                # Record the adjustment
                self.adjustment_history.append({
                    "parameter": name,
                    "old_value": current_value,
                    "new_value": new_value,
                    "reason": f"context:{context_type}",
                    "adjustment": adjustment,
                    "timestamp": import_time()
                })
                
                # Update the parameter
                param["value"] = new_value
                adjustments[name] = new_value
                
                logger.info(f"Adjusted parameter {name} from {current_value} to {new_value} for context {context_type}")
        
        return adjustments
    
    def reset_to_defaults(self) -> None:
        """Reset all parameters to their default values."""
        self.parameters = copy.deepcopy(self.default_parameters)
        logger.info("Reset all parameters to defaults")
    
    def get_adjustment_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent parameter adjustments.
        
        Args:
            limit: Maximum number of adjustments to return
            
        Returns:
            List of recent adjustments
        """
        return self.adjustment_history[-limit:]
    
    def get_all_parameters(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all parameters.
        
        Returns:
            Dictionary of all parameters
        """
        return self.parameters
    
    def explain_parameter(self, name: str) -> Dict[str, Any]:
        """
        Get an explanation of a parameter.
        
        Args:
            name: Parameter name
            
        Returns:
            Dictionary with parameter explanation
        """
        if name not in self.parameters:
            return {"error": f"Unknown parameter: {name}"}
            
        param = self.parameters[name]
        
        # Get recent adjustments for this parameter
        recent_adjustments = [
            adj for adj in self.adjustment_history[-5:]
            if adj["parameter"] == name
        ]
        
        return {
            "name": name,
            "description": param.get("description", "No description available"),
            "current_value": param.get("value", 0.5),
            "range": param.get("range", [0.0, 1.0]),
            "context_adjustments": param.get("context_adjustments", {}),
            "recent_adjustments": recent_adjustments
        }

def import_time():
    """Import time module and return current time as ISO format string."""
    from datetime import datetime
    return datetime.now().isoformat()
