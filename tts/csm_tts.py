"""
CSM-1B TTS implementation for Coda Lite.
Uses MeloTTS (formerly CSM-1B) for high-quality speech synthesis.
"""

import os
import tempfile
import logging
import sys
from typing import Optional, Dict, Any, Union, List
from pathlib import Path

# Add the melotts directory to the Python path
melotts_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'melotts', 'MeloTTS-main')
if melotts_path not in sys.path:
    sys.path.append(melotts_path)

import numpy as np

# Try to import MeloTTS dependencies
try:
    import torch
    import torchaudio
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# Set up logging
logger = logging.getLogger("coda.tts")

# Try to import MeloTTS
try:
    # First try to import from the local melo directory
    sys.path.insert(0, melotts_path)
    from melo.api import TTS
    MELOTTS_AVAILABLE = True
    logger.info(f"Successfully imported MeloTTS from {melotts_path}")
except ImportError as e:
    print(f"Error importing MeloTTS: {e}")
    MELOTTS_AVAILABLE = False

from tts.speak import BaseTTS

class CSMTTS(BaseTTS):
    """
    Text-to-speech implementation using CSM-1B (MeloTTS).
    """

    def __init__(
        self,
        device: str = None,
        language: str = "EN",
        **kwargs
    ):
        # Set default device based on CUDA availability
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        """
        Initialize the CSM-1B TTS module.

        Args:
            device (str): Device to use for inference ("cuda" or "cpu")
            language (str): Language code (default: "EN")
        """
        logger.info(f"Initializing CSM-1B TTS on {device}")

        self.device = device
        self.language = language.upper()  # MeloTTS uses uppercase language codes
        self.use_cuda = device == "cuda"

        # Initialize MeloTTS model
        try:
            # Check if CUDA is available when requested
            if self.use_cuda and not torch.cuda.is_available():
                logger.warning("CUDA requested but not available. Falling back to CPU.")
                self.use_cuda = False
                self.device = "cpu"

            # Log device information
            if self.use_cuda:
                gpu_name = torch.cuda.get_device_name(0)
                logger.info(f"Using GPU: {gpu_name}")
                logger.info(f"CUDA version: {torch.version.cuda}")
            else:
                logger.info("Using CPU for TTS processing")

            # Initialize the MeloTTS model
            self.model = TTS(language=self.language, device=self.device)

            # Get available speakers
            self.speakers = self.model.hps.data.spk2id
            self.speaker_id = self.speakers[list(self.speakers.keys())[0]]  # Default speaker

            logger.info(f"CSM-1B TTS initialized successfully with language {self.language}")
            logger.info(f"Available speakers: {list(self.speakers.keys())}")
        except Exception as e:
            logger.error(f"Error initializing CSM-1B TTS: {e}")
            self.model = None

    def synthesize(
        self,
        text: str,
        output_path: Optional[str] = None,
        language: Optional[str] = None,
        speaker: Optional[str] = None,
        **kwargs
    ) -> Optional[str]:
        """
        Synthesize speech from text and save to a file.

        Args:
            text (str): Text to synthesize
            output_path (str, optional): Path to save the audio file
            language (str, optional): Language code (overrides the default)
            speaker (str, optional): Speaker ID (overrides the default)

        Returns:
            str: Path to the generated audio file, or None if synthesis failed
        """
        if not self.model:
            logger.error("CSM-1B TTS model not initialized")
            return None

        if not text or not text.strip():
            logger.warning("Empty text provided for synthesis")
            return None

        # Create a temporary file if output_path is not provided
        if not output_path:
            temp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            output_path = temp.name
            temp.close()

        # Use provided language or default
        lang = language.upper() if language else self.language

        # Use provided speaker or default
        if speaker and speaker in self.speakers:
            speaker_id = self.speakers[speaker]
        else:
            speaker_id = self.speaker_id

        try:
            logger.info(f"Synthesizing speech: {text[:50]}{'...' if len(text) > 50 else ''}")

            # Generate speech using MeloTTS
            self.model.tts_to_file(text, speaker_id, output_path)

            logger.info(f"Speech synthesized successfully to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")

            # Clean up the file if it was created
            if os.path.exists(output_path):
                try:
                    os.unlink(output_path)
                except:
                    pass

            return None

    def speak(self, text: str, **kwargs) -> bool:
        """
        Synthesize speech and play it directly.

        Args:
            text (str): Text to speak

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.model:
            logger.error("CSM-1B TTS model not initialized")
            return False

        try:
            # Synthesize speech to a temporary file
            temp_file = self.synthesize(text, **kwargs)

            if not temp_file:
                logger.error("Failed to synthesize speech")
                return False

            # Play the audio using simpleaudio
            try:
                import simpleaudio as sa
                wave_obj = sa.WaveObject.from_wave_file(temp_file)
                play_obj = wave_obj.play()
                play_obj.wait_done()  # Wait for audio to finish playing
                logger.info("Audio playback completed")
                return True
            except Exception as e:
                logger.error(f"Error playing audio: {e}")
                return False
            finally:
                # Clean up the temporary file
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except Exception as e:
                    logger.warning(f"Error removing temporary file: {e}")

        except Exception as e:
            logger.error(f"Error in speak method: {e}")
            return False

    def play_audio(self, audio: Union[str, np.ndarray]) -> None:
        """
        Play audio from file or numpy array.

        Args:
            audio (str or np.ndarray): Path to audio file or audio array
        """
        try:
            import simpleaudio as sa

            if isinstance(audio, str):
                # Play from file
                wave_obj = sa.WaveObject.from_wave_file(audio)
                play_obj = wave_obj.play()
                play_obj.wait_done()
            elif isinstance(audio, np.ndarray):
                # Convert numpy array to file and play
                temp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                temp_path = temp.name
                temp.close()

                try:
                    # Save numpy array to file
                    torchaudio.save(temp_path, torch.tensor(audio).unsqueeze(0), 22050)

                    # Play the audio
                    wave_obj = sa.WaveObject.from_wave_file(temp_path)
                    play_obj = wave_obj.play()
                    play_obj.wait_done()
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
            else:
                logger.error(f"Unsupported audio type: {type(audio)}")
        except Exception as e:
            logger.error(f"Error playing audio: {e}")

    def get_available_voices(self) -> List[str]:
        """
        Get list of available voices.

        Returns:
            List[str]: List of available voice names
        """
        if not self.model:
            return ["default"]

        # Return the available speakers from MeloTTS
        return list(self.speakers.keys())

    def get_available_languages(self) -> List[str]:
        """
        Get list of available languages.

        Returns:
            List[str]: List of available language codes
        """
        # MeloTTS supports multiple languages
        return ["EN", "ES", "FR", "ZH", "JP", "KR"]
