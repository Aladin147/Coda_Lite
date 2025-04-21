"""
Configuration loader for Coda Lite.
Handles loading configuration from YAML files and environment variables.
"""

import os
import yaml
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger("coda.config")

class ConfigLoader:
    """Configuration loader for Coda Lite."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize ConfigLoader.
        
        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self._load_config()
        
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f) or {}
                logger.info(f"Loaded configuration from {self.config_path}")
            except Exception as e:
                logger.error(f"Error loading configuration: {e}", exc_info=True)
                self.config = {}
        else:
            logger.info(f"Configuration file not found at {self.config_path}, using defaults")
            self.config = {}
            
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (can use dot notation for nested keys)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        # Check environment variable first (uppercase with CODA_ prefix)
        env_key = f"CODA_{key.upper().replace('.', '_')}"
        env_value = os.environ.get(env_key)
        if env_value is not None:
            return env_value
            
        # Then check config file
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
        
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (can use dot notation for nested keys)
            value: Configuration value
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to the nested dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        # Set the value
        config[keys[-1]] = value
        
    def save(self) -> None:
        """Save configuration to YAML file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            logger.info(f"Saved configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}", exc_info=True)
            
    def load_defaults(self, defaults: Dict[str, Any]) -> None:
        """
        Load default configuration values.
        
        Args:
            defaults: Dictionary of default configuration values
        """
        # Only set values that don't already exist
        for key, value in defaults.items():
            if isinstance(value, dict):
                # Recursively handle nested dictionaries
                for nested_key, nested_value in value.items():
                    full_key = f"{key}.{nested_key}"
                    if self.get(full_key) is None:
                        self.set(full_key, nested_value)
            else:
                if self.get(key) is None:
                    self.set(key, value)
