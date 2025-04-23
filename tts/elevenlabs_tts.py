#!/usr/bin/env python3
"""
ElevenLabs TTS implementation for Coda.
"""

import os
import time
import logging
import tempfile
from typing import Optional, Union, List, Dict, Any
import numpy as np

# Import only what's available in the elevenlabs package
from elevenlabs import stream
from elevenlabs.client import ElevenLabs

from tts.speak import BaseTTS

# Set up logging
logger = logging.getLogger("coda.tts")

class ElevenLabsTTS(BaseTTS):
    """
    ElevenLabs TTS implementation.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: str = "JBFqnCBsd6RMkjVDRZzb",  # Default voice: Josh (male)
        model_id: str = "eleven_multilingual_v2",  # Default model: Multilingual v2
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True,
        output_format: str = "mp3_44100_128",
        **kwargs
    ):
        """
        Initialize the ElevenLabs TTS engine.

        Args:
            api_key: ElevenLabs API key. If not provided, will try to use ELEVENLABS_API_KEY env var.
            voice_id: ID of the voice to use.
            model_id: ID of the model to use.
            stability: Stability factor (0.0 to 1.0).
            similarity_boost: Similarity boost factor (0.0 to 1.0).
            style: Style factor (0.0 to 1.0).
            use_speaker_boost: Whether to use speaker boost.
            output_format: Output format for the audio.
        """
        super().__init__()

        # Store parameters
        self.api_key = api_key or os.environ.get("ELEVENLABS_API_KEY")
        if not self.api_key:
            logger.warning("No ElevenLabs API key provided. Please set ELEVENLABS_API_KEY environment variable or pass api_key parameter.")

        self.voice_id = voice_id
        self.model_id = model_id
        self.stability = stability
        self.similarity_boost = similarity_boost
        self.style = style
        self.use_speaker_boost = use_speaker_boost
        self.output_format = output_format

        # Initialize ElevenLabs client
        try:
            self.client = ElevenLabs(api_key=self.api_key)
            logger.info(f"ElevenLabs TTS initialized with model: {self.model_id}")

            # Test if API key is valid by fetching available voices
            try:
                voices = self.client.voices.get_all()
                logger.info(f"ElevenLabs API connection successful. {len(voices.voices)} voices available.")
            except Exception as e:
                logger.warning(f"Could not fetch voices from ElevenLabs API: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize ElevenLabs TTS: {e}")
            raise

    def synthesize(self, text: str, output_path: Optional[str] = None) -> np.ndarray:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize.
            output_path: Path to save the audio file. If None, a temporary file will be used.

        Returns:
            Audio data as a numpy array.
        """
        if not text:
            logger.warning("Empty text provided for synthesis, returning empty audio.")
            return np.array([], dtype=np.float32)

        logger.info(f"Synthesizing speech: {text[:50]}...")

        # Start timing
        start_time = time.time()

        try:
            # Prepare voice settings
            voice_settings = {
                "stability": self.stability,
                "similarity_boost": self.similarity_boost,
                "style": self.style,
                "use_speaker_boost": self.use_speaker_boost
            }

            # Generate speech
            audio_stream = self.client.text_to_speech.convert_as_stream(
                text=text,
                voice_id=self.voice_id,
                model_id=self.model_id,
                voice_settings=voice_settings,
                output_format=self.output_format
            )

            # Collect all chunks from the stream
            audio_chunks = []
            for chunk in audio_stream:
                if isinstance(chunk, bytes):
                    audio_chunks.append(chunk)

            # Combine all chunks into a single bytes object
            audio = b''.join(audio_chunks)

            # End timing
            end_time = time.time()
            generation_time = end_time - start_time
            logger.info(f"Speech generation completed in {generation_time:.3f} seconds")

            # Save to file if output_path is provided
            if output_path:
                with open(output_path, "wb") as f:
                    f.write(audio)
                logger.info(f"Speech synthesized successfully to {output_path}")

            # Convert audio bytes to numpy array
            # We need to save to a temporary file and then load it with librosa
            # because ElevenLabs returns compressed audio (mp3/wav)
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_path = temp_file.name
                temp_file.write(audio)

            # Load the audio file with librosa
            import librosa
            audio_array, _ = librosa.load(temp_path, sr=44100, mono=True)

            # Clean up the temporary file
            os.unlink(temp_path)

            return audio_array

        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            raise

    def stream_synthesize(self, text: str) -> Any:
        """
        Stream synthesize speech from text.

        Args:
            text: Text to synthesize.

        Returns:
            Audio stream generator that yields audio chunks.
        """
        if not text:
            logger.warning("Empty text provided for synthesis, returning empty audio.")
            return np.array([], dtype=np.float32)

        logger.info(f"Streaming speech synthesis: {text[:50]}...")

        try:
            # Prepare voice settings
            voice_settings = {
                "stability": self.stability,
                "similarity_boost": self.similarity_boost,
                "style": self.style,
                "use_speaker_boost": self.use_speaker_boost
            }

            # Generate speech as a stream
            audio_stream = self.client.text_to_speech.convert_as_stream(
                text=text,
                voice_id=self.voice_id,
                model_id=self.model_id,
                voice_settings=voice_settings,
                output_format=self.output_format
            )

            # Return a generator that yields audio chunks
            def audio_chunk_generator():
                for chunk in audio_stream:
                    if isinstance(chunk, bytes):
                        yield chunk

            return audio_chunk_generator()

        except Exception as e:
            logger.error(f"Error streaming speech synthesis: {e}")
            raise

    def play_audio(self, audio: Union[str, np.ndarray]) -> None:
        """
        Play audio from file or numpy array.

        Args:
            audio (str or np.ndarray): Path to audio file or audio array
        """
        try:
            import sounddevice as sd
            import soundfile as sf

            if isinstance(audio, str):
                # Load audio file
                data, samplerate = sf.read(audio)
                sd.play(data, samplerate)
                sd.wait()  # Wait until audio is finished playing
            elif isinstance(audio, np.ndarray):
                # Play audio array
                sd.play(audio, 44100)  # Assuming 44.1kHz sample rate
                sd.wait()  # Wait until audio is finished playing
            else:
                logger.error(f"Unsupported audio type: {type(audio)}")
        except Exception as e:
            logger.error(f"Error playing audio: {e}")

    def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get a list of available voices.

        Returns:
            List of available voices.
        """
        try:
            voices_response = self.client.voices.get_all()
            return [
                {
                    "id": voice.voice_id,
                    "name": voice.name,
                    "category": "elevenlabs",
                    "description": voice.description or "",
                    "preview_url": voice.preview_url or "",
                    "gender": "unknown",  # ElevenLabs doesn't provide gender info
                    "language": "multilingual" if "multilingual" in self.model_id else "english"
                }
                for voice in voices_response.voices
            ]
        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
            return []

    def speak(self, text: str) -> bool:
        """
        Synthesize speech from text and play it.

        Args:
            text: Text to synthesize and play.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Synthesize speech
            logger.info(f"Synthesizing and playing speech: {text[:50]}...")
            audio = self.synthesize(text)

            # Play the audio
            self.play_audio(audio)
            return True
        except Exception as e:
            logger.error(f"Error speaking text: {e}")
            return False

    def get_available_languages(self) -> List[str]:
        """
        Get list of available languages.

        Returns:
            List[str]: List of available language codes
        """
        if "multilingual" in self.model_id:
            # Multilingual v2 supports 29 languages
            return [
                "en", "de", "fr", "es", "it", "pt", "pl", "nl", "ro", "cs",
                "hu", "sv", "da", "fi", "no", "tr", "ru", "ar", "zh", "ja",
                "ko", "hi", "id", "bn", "ta", "te", "ur", "fil", "ms"
            ]
        elif "turbo" in self.model_id:
            # Turbo v2.5 supports 32 languages
            return [
                "en", "de", "fr", "es", "it", "pt", "pl", "nl", "ro", "cs",
                "hu", "sv", "da", "fi", "no", "tr", "ru", "ar", "zh", "ja",
                "ko", "hi", "id", "bn", "ta", "te", "ur", "fil", "ms", "vi", "uk", "el"
            ]
        else:
            # Monolingual v1 supports only English
            return ["en"]
