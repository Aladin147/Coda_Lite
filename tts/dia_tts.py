"""
Dia TTS implementation for Coda Lite.
Uses Dia for high-quality, ultra-realistic dialogue synthesis.
"""

import os
import tempfile
import logging
import time
import numpy as np
from typing import Optional, Union, List, Dict, Any

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
        temperature: float = 1.3,
        top_p: float = 0.95,
        cfg_scale: float = 3.0,
        use_torch_compile: bool = True,
        **kwargs
    ):
        """
        Initialize the Dia TTS engine.

        Args:
            device (str): Device to use for inference (cuda or cpu)
            voice (str, optional): Voice to use (not directly supported by Dia, but can be used with audio_prompt_path)
            speed (float): Speed factor for speech (not directly supported by Dia)
            audio_prompt_path (str, optional): Path to an audio file to use as a prompt for voice cloning
            temperature (float): Temperature for sampling (higher = more random, lower = more deterministic)
            top_p (float): Top-p sampling parameter (0-1)
            cfg_scale (float): Classifier-free guidance scale (higher = more adherence to the prompt)
            use_torch_compile (bool): Whether to use torch.compile for faster inference
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
        self.temperature = temperature
        self.top_p = top_p
        self.cfg_scale = cfg_scale
        self.use_torch_compile = use_torch_compile
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
            # Clear CUDA cache before loading model
            if device == "cuda" and cuda_available:
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
                logger.info(f"GPU memory before model load: {torch.cuda.memory_allocated() / 1024**2:.2f} MB / {torch.cuda.memory_reserved() / 1024**2:.2f} MB")

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

                    # Verify main model is on GPU
                    try:
                        main_model_device = next(self.model.model.parameters()).device
                        logger.info(f"- Main model device verified: {main_model_device}")
                    except StopIteration:
                        logger.warning("- Could not verify main model device - no parameters")

                # Move the DAC model (vocoder) to GPU
                if hasattr(self.model, 'dac_model') and self.model.dac_model is not None:
                    self.model.dac_model = self.model.dac_model.to(torch_device)
                    logger.info("- DAC model (vocoder) moved to GPU")

                    # Verify DAC model is on GPU
                    try:
                        dac_model_device = next(self.model.dac_model.parameters()).device
                        logger.info(f"- DAC model device verified: {dac_model_device}")
                    except StopIteration:
                        logger.warning("- Could not verify DAC model device - no parameters")

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

                # Synchronize CUDA to ensure all operations are complete
                torch.cuda.synchronize()

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

            # Optimize GPU memory and performance before generation
            if self.device == "cuda" and torch.cuda.is_available():
                # Clear CUDA cache
                torch.cuda.empty_cache()
                torch.cuda.synchronize()

                logger.info(f"GPU memory before generation: {torch.cuda.memory_allocated() / 1024**2:.2f} MB / {torch.cuda.memory_reserved() / 1024**2:.2f} MB")

                # Double-check that all components are on GPU before generation
                torch_device = torch.device("cuda")

                # Check and move main model to GPU
                if hasattr(self.model, 'model'):
                    # Check if model is on GPU by checking a parameter
                    try:
                        param_device = next(self.model.model.parameters()).device
                        if param_device != torch_device:
                            logger.warning(f"Main model on {param_device}, moving it to {torch_device}...")
                            self.model.model = self.model.model.to(torch_device)
                    except (StopIteration, AttributeError):
                        logger.warning("Main model not on GPU, moving it now...")
                        self.model.model = self.model.model.to(torch_device)

                # Check and move DAC model to GPU
                if hasattr(self.model, 'dac_model') and self.model.dac_model is not None:
                    try:
                        param_device = next(self.model.dac_model.parameters()).device
                        if param_device != torch_device:
                            logger.warning(f"DAC model on {param_device}, moving it to {torch_device}...")
                            self.model.dac_model = self.model.dac_model.to(torch_device)
                    except (StopIteration, AttributeError):
                        logger.warning("DAC model not on GPU, moving it now...")
                        self.model.dac_model = self.model.dac_model.to(torch_device)

                # Check and move encoder to GPU
                if hasattr(self.model.model, 'encoder'):
                    try:
                        param_device = next(self.model.model.encoder.parameters()).device
                        if param_device != torch_device:
                            logger.warning(f"Encoder on {param_device}, moving it to {torch_device}...")
                            self.model.model.encoder = self.model.model.encoder.to(torch_device)
                    except (StopIteration, AttributeError):
                        logger.warning("Encoder not on GPU, moving it now...")
                        self.model.model.encoder = self.model.model.encoder.to(torch_device)

                # Check and move decoder to GPU
                if hasattr(self.model.model, 'decoder'):
                    try:
                        param_device = next(self.model.model.decoder.parameters()).device
                        if param_device != torch_device:
                            logger.warning(f"Decoder on {param_device}, moving it to {torch_device}...")
                            self.model.model.decoder = self.model.model.decoder.to(torch_device)
                    except (StopIteration, AttributeError):
                        logger.warning("Decoder not on GPU, moving it now...")
                        self.model.model.decoder = self.model.model.decoder.to(torch_device)

                # Set model device attribute
                if hasattr(self.model, 'device'):
                    self.model.device = torch_device

                # Synchronize CUDA to ensure all operations are complete
                torch.cuda.synchronize()

            # Start timing
            start_time = time.time()

            # Generate with appropriate parameters
            try:
                # First try with torch.compile for better performance if enabled
                if self.use_torch_compile:
                    logger.info("Attempting generation with torch.compile enabled...")
                    audio = self.model.generate(
                        text,
                        audio_prompt_path=self.audio_prompt_path,
                        use_torch_compile=True,
                        temperature=self.temperature,
                        top_p=self.top_p,
                        cfg_scale=self.cfg_scale
                    )
                else:
                    logger.info("torch.compile disabled, using eager mode...")
                    audio = self.model.generate(
                        text,
                        audio_prompt_path=self.audio_prompt_path,
                        use_torch_compile=False,
                        temperature=self.temperature,
                        top_p=self.top_p,
                        cfg_scale=self.cfg_scale
                    )
            except Exception as e:
                logger.warning(f"Error with generation, falling back to eager mode: {e}")
                # Fall back to eager mode if generation fails
                try:
                    # Clear CUDA cache before retrying
                    if self.device == "cuda" and torch.cuda.is_available():
                        torch.cuda.empty_cache()
                        torch.cuda.synchronize()

                    logger.info("Retrying with eager mode (torch.compile disabled)...")
                    audio = self.model.generate(
                        text,
                        audio_prompt_path=self.audio_prompt_path,
                        use_torch_compile=False,  # Disable torch.compile
                        temperature=self.temperature,
                        top_p=self.top_p,
                        cfg_scale=self.cfg_scale
                    )
                except Exception as e2:
                    logger.error(f"Error in fallback generation: {e2}")
                    raise

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
