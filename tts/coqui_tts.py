"""
Coqui TTS implementation for Coda Lite.
Uses Coqui TTS for efficient local speech synthesis.
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

from tts.speak import BaseTTS

import logging
logger = logging.getLogger("coda.tts")

class CoquiTTS(BaseTTS):
    """Text-to-speech implementation using Coqui TTS."""

    def __init__(
        self,
        model_name: str = "tts_models/en/ljspeech/tacotron2-DDC",
        device: str = "cpu",
        use_cuda: bool = False,
        download_dir: Optional[str] = None,
        speaker_idx: Optional[int] = None,
        language_idx: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize the CoquiTTS module.

        Args:
            model_name (str): Name of the TTS model to use
            device (str): Device to use ("cpu" or "cuda")
            use_cuda (bool): Whether to use CUDA
            download_dir (str, optional): Directory to download models
            speaker_idx (int, optional): Speaker index for multi-speaker models
            language_idx (int, optional): Language index for multi-language models
            **kwargs: Additional parameters
        """
        self.model_name = model_name
        self.device = device
        self.use_cuda = use_cuda and torch.cuda.is_available()
        self.download_dir = download_dir
        self.speaker_idx = speaker_idx
        self.language_idx = language_idx

        logger.info(f"Initializing CoquiTTS with model: {model_name} on {device}")

        # Initialize TTS model
        try:
            # Check if CUDA is available when requested
            if self.use_cuda:
                try:
                    if not torch.cuda.is_available():
                        logger.warning("CUDA requested but not available. Falling back to CPU.")
                        self.use_cuda = False
                        device = "cpu"
                    else:
                        # Try to get GPU info to confirm CUDA is working
                        gpu_name = torch.cuda.get_device_name(0)
                        logger.info(f"Using GPU: {gpu_name}")
                        logger.info(f"CUDA version: {torch.version.cuda}")
                except Exception as e:
                    logger.warning(f"Error checking CUDA availability: {e}")
                    logger.warning("Falling back to CPU.")
                    self.use_cuda = False
                    device = "cpu"

            # Log device information
            if not self.use_cuda:
                logger.info("Using CPU for TTS processing")

            # Initialize the TTS model
            logger.info(f"Loading TTS model: {model_name} on {device}")
            self.tts = TTS(model_name=model_name, progress_bar=True)

            # Set device
            if self.use_cuda:
                self.tts.to(device)
                logger.info("Model successfully moved to GPU")

            # Get model information
            model_type = getattr(self.tts, 'model_name', 'Unknown')
            logger.info(f"Model type: {model_type}")

            # Get available speakers and languages
            self.speakers = self.tts.speakers if hasattr(self.tts, "speakers") else None
            self.languages = self.tts.languages if hasattr(self.tts, "languages") else None

            # Check if the model is multi-speaker
            self.is_multi_speaker = hasattr(self.tts, "is_multi_speaker") and self.tts.is_multi_speaker

            # Check if the model is multi-lingual
            self.is_multi_lingual = hasattr(self.tts, "is_multi_lingual") and self.tts.is_multi_lingual

            # Log model properties
            logger.info(f"Model properties: multi_speaker={self.is_multi_speaker}, multi_lingual={self.is_multi_lingual}")

            if self.speakers:
                logger.info(f"Available speakers: {len(self.speakers)}")
                if len(self.speakers) > 0 and len(self.speakers) <= 10:
                    logger.info(f"Speaker list: {', '.join(self.speakers[:10])}")
                elif len(self.speakers) > 10:
                    logger.info(f"First 10 speakers: {', '.join(self.speakers[:10])}...")

            if self.languages:
                logger.info(f"Available languages: {len(self.languages)}")
                if len(self.languages) > 0 and len(self.languages) <= 10:
                    logger.info(f"Language list: {', '.join(self.languages[:10])}")
                elif len(self.languages) > 10:
                    logger.info(f"First 10 languages: {', '.join(self.languages[:10])}...")

        except Exception as e:
            logger.error(f"Error initializing TTS model: {e}")
            # Create a fallback model
            self.tts = None
            self.speakers = None
            self.languages = None
            self.is_multi_speaker = False
            self.is_multi_lingual = False

        if self.speakers:
            logger.info(f"Available speakers: {self.speakers}")
        if self.languages:
            logger.info(f"Available languages: {self.languages}")

        logger.info("CoquiTTS initialized successfully")

    def synthesize(
        self,
        text: str,
        output_path: Optional[str] = None,
        speaker: Optional[str] = None,
        language: Optional[str] = None,
        speed: float = 1.0,
        **kwargs
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
            **kwargs: Additional parameters

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
            if self.tts is None:
                # If TTS model failed to initialize, generate a fallback tone
                logger.warning("TTS model not initialized, using fallback tone")
                self._generate_fallback_tone(output_path)
            else:
                try:
                    # Try with the standard API
                    # Prepare arguments based on model capabilities
                    tts_args = {"text": text, "file_path": output_path, "speed": speed}

                    # Log the text we're trying to synthesize
                    logger.info(f"Attempting to synthesize text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
                    logger.info(f"Output path: {output_path}")

                    # Add speaker only if the model supports it
                    if self.is_multi_speaker:
                        # If speaker is provided, use it
                        if speaker is not None:
                            tts_args["speaker"] = speaker
                            logger.info(f"Using provided speaker: {speaker}")
                        # Otherwise, use the first speaker for VITS model (which requires a speaker)
                        elif "vits" in self.tts.model_name.lower() and self.speakers and len(self.speakers) > 0:
                            selected_speaker = self.speakers[0]
                            logger.info(f"Using default speaker: {selected_speaker}")
                            tts_args["speaker"] = selected_speaker

                    # Add language only if the model supports it and a language is provided
                    if self.is_multi_lingual:
                        # If language is provided, use it
                        if language is not None:
                            tts_args["language"] = language
                            logger.info(f"Using provided language: {language}")
                        # Otherwise, use English for multi-lingual models
                        elif self.languages and "en" in self.languages:
                            logger.info("Using default language: English")
                            tts_args["language"] = "en"

                    # Log all arguments being passed to the TTS function
                    logger.info(f"TTS arguments: {tts_args}")

                    # Split text into smaller chunks if it's too long
                    if len(text) > 100:
                        logger.info("Text is long, splitting into sentences")
                        # Simple sentence splitting
                        sentences = [s.strip() + "." for s in text.replace(".", ".<split>").split("<split>") if s.strip()]

                        # Create a temporary file for each sentence
                        temp_files = []
                        audio_arrays = []

                        for i, sentence in enumerate(sentences):
                            if not sentence.strip():
                                continue

                            # Create a temporary file for this sentence
                            sent_temp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                            temp_files.append(sent_temp.name)
                            sent_temp.close()

                            # Update the text in the arguments
                            sent_args = tts_args.copy()
                            sent_args["text"] = sentence
                            sent_args["file_path"] = sent_temp.name

                            try:
                                # Call the TTS API for this sentence
                                self.tts.tts_to_file(**sent_args)
                                logger.info(f"Synthesized sentence {i+1}/{len(sentences)}: {sentence[:30]}{'...' if len(sentence) > 30 else ''}")
                            except Exception as e:
                                logger.warning(f"Failed to synthesize sentence {i+1}: {e}")

                        # Combine all the audio files
                        if temp_files:
                            try:
                                import numpy as np
                                import soundfile as sf

                                # Read all audio files
                                for temp_file in temp_files:
                                    data, samplerate = sf.read(temp_file)
                                    audio_arrays.append(data)

                                # Concatenate audio arrays
                                if audio_arrays:
                                    try:
                                        # Check if we have valid audio arrays
                                        if len(audio_arrays) == 1:
                                            # Just use the single array
                                            combined_audio = audio_arrays[0]
                                        else:
                                            # Try to concatenate arrays
                                            combined_audio = np.concatenate(audio_arrays)

                                        # Write combined audio to output file
                                        sf.write(output_path, combined_audio, samplerate)
                                        logger.info(f"Combined {len(audio_arrays)} audio segments")
                                    except Exception as e:
                                        logger.error(f"Error concatenating audio arrays: {e}")

                                        # If we have at least one valid audio segment, use the first one
                                        if audio_arrays:
                                            try:
                                                sf.write(output_path, audio_arrays[0], samplerate)
                                                logger.info(f"Used first audio segment as fallback")
                                            except Exception as e2:
                                                logger.error(f"Error writing first audio segment: {e2}")
                                                self._generate_fallback_tone(output_path)
                                        else:
                                            self._generate_fallback_tone(output_path)
                                else:
                                    logger.warning("No audio segments were successfully synthesized")
                                    self._generate_fallback_tone(output_path)

                            except Exception as e:
                                logger.error(f"Error combining audio files: {e}")
                                raise
                            finally:
                                # Clean up temporary files
                                for temp_file in temp_files:
                                    try:
                                        if os.path.exists(temp_file):
                                            os.unlink(temp_file)
                                    except Exception as e:
                                        logger.warning(f"Error removing temp file {temp_file}: {e}")
                    else:
                        # For short text, just call the TTS API directly
                        self.tts.tts_to_file(**tts_args)

                except Exception as e:
                    logger.warning(f"Standard TTS method failed: {e}")
                    logger.warning("Using fallback tone")
                    self._generate_fallback_tone(output_path)

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

    def play_audio(self, audio: Union[str, np.ndarray]) -> None:
        """
        Play audio from file or numpy array.

        Args:
            audio (str or np.ndarray): Path to audio file or audio array
        """
        try:
            if isinstance(audio, str):
                logger.info(f"Playing audio from: {audio}")
                data, samplerate = sf.read(audio)
            else:
                logger.info("Playing audio from array")
                data = audio
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

    def get_available_voices(self) -> List[str]:
        """
        Get list of available voices (speakers).

        Returns:
            List[str]: List of available voice names
        """
        return self.speakers if self.speakers else []

    def get_available_languages(self) -> List[str]:
        """
        Get list of available languages.

        Returns:
            List[str]: List of available language codes
        """
        return self.languages if self.languages else []

    # Legacy methods for backward compatibility

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

    def _generate_fallback_tone(self, output_path: str) -> None:
        """
        Generate a simple sine wave as a fallback when TTS fails.

        Args:
            output_path: Path to save the audio file
        """
        try:
            import numpy as np
            import scipy.io.wavfile as wav_file

            # Generate a 1-second sine wave at 440 Hz
            sample_rate = 22050
            t = np.linspace(0, 1, sample_rate, False)
            audio = 0.5 * np.sin(2 * np.pi * 440 * t)

            # Save the audio to file
            wav_file.write(output_path, sample_rate, audio.astype(np.float32))

            logger.warning(f"Generated fallback audio tone at {output_path}")
        except Exception as e:
            logger.error(f"Error generating fallback tone: {e}")
            # If we can't even generate a fallback tone, we're in trouble
