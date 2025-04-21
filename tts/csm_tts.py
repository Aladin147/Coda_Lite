"""
Text-to-speech implementation for Coda Lite.
Uses TTS for efficient local speech synthesis.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np
import torch
from TTS.api import TTS
import sounddevice as sd
import soundfile as sf

import logging
logger = logging.getLogger("coda.tts")

class CSMTTS:
    """Text-to-speech implementation using TTS."""

    def __init__(
        self,
        model_name: str = "tts_models/en/ljspeech/tacotron2-DDC",
        device: str = "cpu",
        use_cuda: bool = False,
        download_dir: Optional[str] = None,
        speaker_idx: Optional[int] = None,
        language_idx: Optional[int] = None,
    ):
        """
        Initialize the CSMTTS module.

        Args:
            model_name (str): Name of the TTS model to use
            device (str): Device to use ("cpu" or "cuda")
            use_cuda (bool): Whether to use CUDA
            download_dir (str, optional): Directory to download models
            speaker_idx (int, optional): Speaker index for multi-speaker models
            language_idx (int, optional): Language index for multi-language models
        """
        self.model_name = model_name
        self.device = device
        self.use_cuda = use_cuda and torch.cuda.is_available()
        self.download_dir = download_dir
        self.speaker_idx = speaker_idx
        self.language_idx = language_idx

        logger.info(f"Initializing CSMTTS with model: {model_name} on {device}")

        # Initialize TTS model
        self.tts = TTS(model_name=model_name, progress_bar=False)

        # Set device
        if self.use_cuda:
            self.tts.to(device)

        # Get available speakers and languages
        self.speakers = self.tts.speakers if hasattr(self.tts, "speakers") else None
        self.languages = self.tts.languages if hasattr(self.tts, "languages") else None

        if self.speakers:
            logger.info(f"Available speakers: {self.speakers}")
        if self.languages:
            logger.info(f"Available languages: {self.languages}")

        logger.info("CSMTTS initialized successfully")

    def synthesize(
        self,
        text: str,
        output_path: Optional[str] = None,
        speaker: Optional[str] = None,
        language: Optional[str] = None,
        speed: float = 1.0,
    ) -> Optional[str]:
        """
        Synthesize speech from text.

        Args:
            text (str): Text to synthesize
            output_path (str, optional): Path to save the audio file.
                If None, audio will be played directly.
            speaker (str, optional): Speaker name for multi-speaker models
            language (str, optional): Language for multi-language models
            speed (float): Speech speed factor (1.0 is normal speed)

        Returns:
            str: Path to the generated audio file if output_path is provided,
                 None otherwise
        """
        logger.info(f"Synthesizing speech: {text[:50]}{'...' if len(text) > 50 else ''}")

        try:
            # Create a temporary file if output_path is not provided
            temp_file = None
            if not output_path:
                temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                output_path = temp_file.name
                temp_file.close()

            # Synthesize speech
            self.tts.tts_to_file(
                text=text,
                file_path=output_path,
                speaker=speaker,
                language=language,
                speed=speed,
            )

            logger.info(f"Speech synthesized successfully")

            # Play audio directly if no output_path was provided
            if temp_file:
                self.play_audio(output_path)
                # Clean up temporary file
                os.unlink(output_path)
                return None
            else:
                logger.info(f"Saved audio to: {output_path}")
                return output_path

        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}", exc_info=True)
            if temp_file and os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            return None

    def play_audio(self, audio_path: Union[str, np.ndarray]) -> None:
        """
        Play audio from file or numpy array.

        Args:
            audio_path (str or np.ndarray): Path to audio file or audio array
        """
        try:
            if isinstance(audio_path, str):
                logger.info(f"Playing audio from: {audio_path}")
                data, samplerate = sf.read(audio_path)
            else:
                logger.info("Playing audio from array")
                data = audio_path
                samplerate = 22050  # Default sample rate for TTS

            # Play audio
            sd.play(data, samplerate)
            sd.wait()  # Wait until audio is finished playing
            logger.info("Audio playback completed")
        except Exception as e:
            logger.error(f"Error playing audio: {e}", exc_info=True)

    def list_available_models(self) -> List[str]:
        """
        List all available TTS models.

        Returns:
            List[str]: List of available model names
        """
        return TTS().list_models()

    def list_speakers(self) -> Optional[List[str]]:
        """
        List available speakers for the current model.

        Returns:
            List[str] or None: List of available speakers or None if not applicable
        """
        return self.speakers

    def list_languages(self) -> Optional[List[str]]:
        """
        List available languages for the current model.

        Returns:
            List[str] or None: List of available languages or None if not applicable
        """
        return self.languages
