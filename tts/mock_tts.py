"""
Mock TTS implementation for testing.
"""

from typing import Dict, List, Optional, Union, Any
import numpy as np
import logging

logger = logging.getLogger("coda.tts")

class MockTTS:
    """Mock TTS implementation for testing."""
    
    def __init__(self, **kwargs):
        """
        Initialize the MockTTS module.
        
        Args:
            **kwargs: Additional parameters (ignored)
        """
        logger.info("Initializing MockTTS")
        self.voices = ["default", "male", "female"]
        self.languages = ["en"]
    
    def synthesize(self, 
                  text: str, 
                  output_path: Optional[str] = None,
                  **kwargs) -> Optional[str]:
        """
        Mock synthesize method.
        
        Args:
            text: Text to synthesize
            output_path: Path to save the audio file (ignored)
            **kwargs: Additional parameters (ignored)
            
        Returns:
            str: Output path if provided, None otherwise
        """
        logger.info(f"MockTTS would say: {text[:50]}{'...' if len(text) > 50 else ''}")
        print(f"\n[MOCK TTS] Would say: {text}")
        
        return output_path
    
    def play_audio(self, audio: Union[str, np.ndarray]) -> None:
        """
        Mock play_audio method.
        
        Args:
            audio: Audio file path or array (ignored)
        """
        logger.info("MockTTS would play audio")
        print("[MOCK TTS] Would play audio")
    
    def get_available_voices(self) -> List[str]:
        """
        Get list of available voices.
        
        Returns:
            List[str]: List of available voice names
        """
        return self.voices
    
    def get_available_languages(self) -> List[str]:
        """
        Get list of available languages.
        
        Returns:
            List[str]: List of available language codes
        """
        return self.languages
