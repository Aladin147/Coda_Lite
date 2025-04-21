"""
Settings management for Coda Lite.
"""

import os
import json
import logging
logger = logging.getLogger("coda.config")

# Default settings
DEFAULT_SETTINGS = {
    "stt": {
        "model_size": "base",
        "language": "en",
    },
    "llm": {
        "model_name": "llama3",
        "temperature": 0.7,
    },
    "tts": {
        "voice": "default",
        "speed": 1.0,
    },
    "tools": {
        "enabled": True,
    },
    "audio": {
        "input_device": None,  # None = default device
        "output_device": None,  # None = default device
    }
}

class Settings:
    """Settings management for Coda Lite."""
    
    def __init__(self, config_path="config/settings.json"):
        """
        Initialize Settings.
        
        Args:
            config_path (str): Path to the settings JSON file
        """
        self.config_path = config_path
        self.settings = DEFAULT_SETTINGS.copy()
        self._load_settings()
        
    def _load_settings(self):
        """Load settings from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded_settings = json.load(f)
                    # Update default settings with loaded settings
                    for section, values in loaded_settings.items():
                        if section in self.settings:
                            self.settings[section].update(values)
                        else:
                            self.settings[section] = values
                logger.info(f"Loaded settings from {self.config_path}")
            except Exception as e:
                logger.error(f"Error loading settings: {e}", exc_info=True)
        else:
            logger.info(f"Settings file not found at {self.config_path}, using defaults")
            self._save_settings()  # Create default settings file
            
    def _save_settings(self):
        """Save settings to file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
            logger.info(f"Saved settings to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)
            
    def get(self, section, key=None, default=None):
        """
        Get a setting value.
        
        Args:
            section (str): Settings section
            key (str, optional): Setting key within section.
                If None, returns the entire section.
            default: Default value if setting not found
            
        Returns:
            Any: Setting value or default
        """
        if section not in self.settings:
            return default
            
        if key is None:
            return self.settings[section]
            
        return self.settings[section].get(key, default)
        
    def set(self, section, key, value):
        """
        Set a setting value.
        
        Args:
            section (str): Settings section
            key (str): Setting key within section
            value: Setting value
        """
        if section not in self.settings:
            self.settings[section] = {}
            
        self.settings[section][key] = value
        self._save_settings()
        
    def get_all(self):
        """
        Get all settings.
        
        Returns:
            dict: All settings
        """
        return self.settings.copy()
