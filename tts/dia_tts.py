"""
Dia TTS implementation for Coda Lite.
Uses Dia for high-quality, ultra-realistic dialogue synthesis.
"""

import os
import tempfile
import logging
import time
import numpy as np
from typing import Optional, Union, List
from pathlib import Path

# Set up logging
logger = logging.getLogger("coda.tts")

# Try to import Dia TTS dependencies
try:
    import torch
    import soundfile as sf
    import simpleaudio as sa
    TORCH_AVAILABLE = True
    AUDIO_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    AUDIO_AVAILABLE = False

# Try to import Dia
try:
    from dia.model import Dia
    DIA_AVAILABLE = True
    logger.info("Successfully imported Dia TTS")
except ImportError as e:
    logger.error(f"Error importing Dia TTS: {e}")
    DIA_AVAILABLE = False
except Exception as e:
    logger.error(f"Error importing Dia TTS: {e}")
    DIA_AVAILABLE = False

from tts.speak import BaseTTS

class DiaTTS(BaseTTS):
    """
    Text-to-speech implementation using Dia TTS.
    """

    def __init__(
        self,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        voice: Optional[str] = None,
        speed: float = 1.0,
        audio_prompt_path: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the Dia TTS engine.

        Args:
            device (str): Device to use for inference (cuda or cpu)
            voice (str, optional): Voice to use (not directly supported by Dia, but can be used with audio_prompt_path)
            speed (float): Speed factor for speech (not directly supported by Dia)
            audio_prompt_path (str, optional): Path to an audio file to use as a prompt for voice cloning
            **kwargs: Additional arguments
        """
        super().__init__()

        if not DIA_AVAILABLE:
            raise ImportError("Dia TTS is not available. Please install the dia package.")

        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is not available. Please install torch.")

        if not AUDIO_AVAILABLE:
            logger.warning("SimpleAudio is not available. Audio playback will not work.")

        self.device = device
        self.voice = voice
        self.speed = speed
        self.audio_prompt_path = audio_prompt_path
        self.model = None

        # Initialize the model
        try:
            # Force CUDA detection by checking for NVIDIA GPU
            import subprocess
            try:
                # Run nvidia-smi to check if NVIDIA GPU is available
                subprocess.check_output('nvidia-smi')
                cuda_available = True
                logger.info("NVIDIA GPU detected via nvidia-smi")
                # Force CUDA availability in PyTorch
                if not torch.cuda.is_available():
                    logger.warning("PyTorch doesn't detect CUDA, but NVIDIA GPU is available. Forcing CUDA usage.")
                    # We'll manually move tensors to CUDA
            except:
                cuda_available = False
                logger.warning("No NVIDIA GPU detected via nvidia-smi")

            if not cuda_available and device == "cuda":
                logger.warning(f"CUDA was requested but is not available. Falling back to CPU.")
                device = "cpu"
                self.device = "cpu"

            logger.info(f"Initializing Dia TTS on {device}")
            # Explicitly set the device when initializing the model
            torch_device = torch.device(device)
            self.model = Dia.from_pretrained("nari-labs/Dia-1.6B", device=torch_device)

            # Explicitly ensure all model components are on the correct device
            if device == "cuda" and cuda_available:
                logger.info("Explicitly moving all model components to GPU...")
                # Move the main model to GPU
                if hasattr(self.model, 'model'):
                    self.model.model = self.model.model.to(torch_device)
                    logger.info("- Main model moved to GPU")

                # Move the DAC model (vocoder) to GPU
                if hasattr(self.model, 'dac_model') and self.model.dac_model is not None:
                    self.model.dac_model = self.model.dac_model.to(torch_device)
                    logger.info("- DAC model (vocoder) moved to GPU")

                # Move encoder to GPU if it exists
                if hasattr(self.model.model, 'encoder'):
                    self.model.model.encoder = self.model.model.encoder.to(torch_device)
                    logger.info("- Encoder moved to GPU")

                # Move decoder to GPU if it exists
                if hasattr(self.model.model, 'decoder'):
                    self.model.model.decoder = self.model.model.decoder.to(torch_device)
                    logger.info("- Decoder moved to GPU")

                # Move any other components to GPU
                if hasattr(self.model, 'device'):
                    self.model.device = torch_device
                    logger.info("- Model device attribute set to GPU")

                # Log GPU memory usage after loading
                logger.info(f"GPU memory allocated: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
                logger.info(f"GPU memory reserved: {torch.cuda.memory_reserved() / 1024**2:.2f} MB")

            logger.info(f"Dia TTS initialized successfully on {device}")
        except Exception as e:
            logger.error(f"Error initializing Dia TTS: {e}")
            self.model = None

    def get_available_voices(self) -> List[str]:
        """
        Get a list of available voices.

        Note: Dia doesn't have predefined voices, but uses voice cloning instead.

        Returns:
            List[str]: List of available voices (empty list for Dia)
        """
        return []

    def get_available_languages(self) -> List[str]:
        """
        Get a list of available languages.

        Note: Dia currently only supports English.

        Returns:
            List[str]: List of available languages
        """
        return ["en"]

    def set_voice(self, voice: str) -> None:
        """
        Set the voice to use.

        Note: Dia doesn't have predefined voices, but this can be used to set the audio_prompt_path.

        Args:
            voice (str): Voice to use
        """
        self.voice = voice

    def set_language(self, language: str) -> None:
        """
        Set the language to use.

        Note: Dia currently only supports English.

        Args:
            language (str): Language to use
        """
        if language.lower() != "en":
            logger.warning(f"Dia TTS only supports English, but {language} was requested. Using English.")

    def synthesize(self, text: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Synthesize speech from text.

        Args:
            text (str): Text to synthesize
            output_path (str, optional): Path to save the audio file

        Returns:
            str: Path to the generated audio file, or None if synthesis failed
        """
        if self.model is None:
            logger.error("Dia TTS model is not initialized")
            return None

        try:
            logger.info(f"Synthesizing speech: {text[:50]}...")

            # Format text for Dia if it doesn't already have speaker tags
            if not text.startswith("[S1]") and not text.startswith("[S2]"):
                text = f"[S1] {text}"

            # Generate speech
            logger.info(f"Generating speech on {self.device}")

            # Log GPU memory usage before generation
            if self.device == "cuda" and torch.cuda.is_available():
                logger.info(f"GPU memory before generation: {torch.cuda.memory_allocated() / 1024**2:.2f} MB / {torch.cuda.memory_reserved() / 1024**2:.2f} MB")

                # Double-check that all components are on GPU before generation
                torch_device = torch.device("cuda")

                # Check and move main model to GPU
                if hasattr(self.model, 'model'):
                    if getattr(self.model.model, 'device', None) != torch_device:
                        logger.warning("Main model not on GPU, moving it now...")
                        self.model.model = self.model.model.to(torch_device)

                # Check and move DAC model to GPU
                if hasattr(self.model, 'dac_model') and self.model.dac_model is not None:
                    if getattr(self.model.dac_model, 'device', None) != torch_device:
                        logger.warning("DAC model not on GPU, moving it now...")
                        self.model.dac_model = self.model.dac_model.to(torch_device)

                # Check and move encoder to GPU
                if hasattr(self.model.model, 'encoder'):
                    if getattr(self.model.model.encoder, 'device', None) != torch_device:
                        logger.warning("Encoder not on GPU, moving it now...")
                        self.model.model.encoder = self.model.model.encoder.to(torch_device)

                # Check and move decoder to GPU
                if hasattr(self.model.model, 'decoder'):
                    if getattr(self.model.model.decoder, 'device', None) != torch_device:
                        logger.warning("Decoder not on GPU, moving it now...")
                        self.model.model.decoder = self.model.model.decoder.to(torch_device)

                # Set model device attribute
                if hasattr(self.model, 'device'):
                    self.model.device = torch_device

            # Start timing
            start_time = time.time()

            # Generate with appropriate parameters
            try:
                # First try with torch.compile for better performance
                audio = self.model.generate(
                    text,
                    audio_prompt_path=self.audio_prompt_path,
                    use_torch_compile=True,  # Try to enable torch.compile
                    temperature=1.0,         # Default temperature
                    top_p=0.95,              # Default top_p
                    cfg_scale=3.0            # Default cfg_scale
                )
            except Exception as e:
                logger.warning(f"Error with torch.compile, falling back to eager mode: {e}")
                # Fall back to eager mode if torch.compile fails
                audio = self.model.generate(
                    text,
                    audio_prompt_path=self.audio_prompt_path,
                    use_torch_compile=False,  # Disable torch.compile
                    temperature=1.0,          # Default temperature
                    top_p=0.95,               # Default top_p
                    cfg_scale=3.0             # Default cfg_scale
                )

            # End timing
            end_time = time.time()
            generation_time = end_time - start_time
            logger.info(f"Speech generation completed in {generation_time:.2f} seconds")

            # Log GPU memory usage after generation
            if self.device == "cuda" and torch.cuda.is_available():
                logger.info(f"GPU memory after generation: {torch.cuda.memory_allocated() / 1024**2:.2f} MB / {torch.cuda.memory_reserved() / 1024**2:.2f} MB")

            # Save to output path or temporary file
            if output_path is None:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    output_path = f.name

            # Save the audio
            sf.write(output_path, audio, 44100)
            logger.info(f"Speech synthesized successfully to {output_path}")

            return output_path
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            return None

    def play_audio(self, audio: Union[str, np.ndarray]) -> None:
        """
        Play audio from file or numpy array.

        Args:
            audio (str or np.ndarray): Path to audio file or audio array
        """
        try:
            if isinstance(audio, str):
                # Load audio from file
                audio_data, sample_rate = sf.read(audio)
            else:
                # Use the provided audio array
                audio_data = audio
                sample_rate = 44100  # Default sample rate

            # Convert to int16 for simpleaudio
            audio_int16 = (audio_data * 32767).astype(np.int16)

            # Play the audio
            if AUDIO_AVAILABLE:
                play_obj = sa.play_buffer(audio_int16, 1, 2, sample_rate)
                play_obj.wait_done()
            else:
                logger.warning("SimpleAudio not available. Cannot play audio.")
                # Sleep for a duration proportional to the audio length to simulate playback
                time.sleep(len(audio_data) / sample_rate)
        except Exception as e:
            logger.error(f"Error playing audio: {e}")

    def speak(self, text: str) -> bool:
        """
        Synthesize speech and play it directly.

        Args:
            text (str): Text to speak

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Synthesize to a temporary file
            temp_path = self.synthesize(text)
            if temp_path is None:
                return False

            # Play the audio
            logger.info("Playing audio directly...")
            self.play_audio(temp_path)

            # Clean up the temporary file
            try:
                os.unlink(temp_path)
            except:
                pass

            return True
        except Exception as e:
            logger.error(f"Error speaking text: {e}")
            return False
