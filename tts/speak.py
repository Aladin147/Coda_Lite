# NOTE:
# This module uses Coqui TTS for MVP implementation.
# Swap to CSM or streaming TTS post-0.0.1 milestone.
#
# Coqui is only used for initial testing and will be replaced with a higher-quality,
# lower-latency solution like CSM-1B for production use. The current implementation
# prioritizes rapid development and testing over production-quality voice synthesis.

"""
Text-to-Speech interface for Coda Lite.
Provides a common interface for different TTS implementations.
"""

import abc
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np

import logging
logger = logging.getLogger("coda.tts")

class BaseTTS(abc.ABC):
    """Base class for all TTS implementations."""
    
    @abc.abstractmethod
    def synthesize(
        self, 
        text: str, 
        output_path: Optional[str] = None,
        **kwargs
    ) -> Optional[str]:
        """
        Synthesize speech from text.
        
        Args:
            text (str): Text to synthesize
            output_path (str, optional): Path to save the audio file.
                If None, audio will be played directly.
            **kwargs: Additional implementation-specific parameters
                
        Returns:
            str: Path to the generated audio file if output_path is provided,
                 None otherwise
        """
        pass
    
    @abc.abstractmethod
    def play_audio(self, audio: Union[str, np.ndarray]) -> None:
        """
        Play audio from file or numpy array.
        
        Args:
            audio (str or np.ndarray): Path to audio file or audio array
        """
        pass
    
    def get_available_voices(self) -> List[str]:
        """
        Get list of available voices.
        
        Returns:
            List[str]: List of available voice names
        """
        return []
    
    def get_available_languages(self) -> List[str]:
        """
        Get list of available languages.
        
        Returns:
            List[str]: List of available language codes
        """
        return []
    
    def get_info(self) -> Dict[str, any]:
        """
        Get information about the TTS implementation.
        
        Returns:
            Dict[str, any]: Information about the TTS implementation
        """
        return {
            "name": self.__class__.__name__,
            "voices": self.get_available_voices(),
            "languages": self.get_available_languages(),
        }


# Factory function to create TTS instances
def create_tts(
    engine: str = "coqui",
    model_name: Optional[str] = None,
    device: str = "cpu",
    **kwargs
) -> BaseTTS:
    """
    Create a TTS instance.
    
    Args:
        engine (str): TTS engine to use ("coqui", "csm", etc.)
        model_name (str, optional): Model name to use
        device (str): Device to use ("cpu", "cuda")
        **kwargs: Additional engine-specific parameters
        
    Returns:
        BaseTTS: TTS instance
    """
    if engine.lower() == "coqui":
        from tts.coqui_tts import CoquiTTS
        return CoquiTTS(model_name=model_name, device=device, **kwargs)
    elif engine.lower() == "csm":
        # This will be implemented in the future
        raise NotImplementedError("CSM TTS engine not yet implemented")
    else:
        raise ValueError(f"Unknown TTS engine: {engine}")
