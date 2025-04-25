"""
WebSocket-integrated ElevenLabs TTS implementation for Coda Lite.
Extends ElevenLabsTTS to emit events via WebSocket.
"""

import os
import time
import logging
import tempfile
from typing import Optional, Union, List, Dict, Any, Generator
import numpy as np

# Import only what's available in the elevenlabs package
from elevenlabs import stream
from elevenlabs.client import ElevenLabs

from tts.elevenlabs_tts import ElevenLabsTTS
from websocket.integration import CodaWebSocketIntegration

# Set up logging
logger = logging.getLogger("coda.tts.websocket")

class WebSocketElevenLabsTTS(ElevenLabsTTS):
    """
    ElevenLabs TTS implementation with WebSocket integration.
    """

    def __init__(
        self,
        websocket_integration: CodaWebSocketIntegration,
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
        Initialize the WebSocketElevenLabsTTS engine.

        Args:
            websocket_integration: The WebSocket integration instance
            api_key: ElevenLabs API key. If not provided, will try to use ELEVENLABS_API_KEY env var.
            voice_id: ID of the voice to use.
            model_id: ID of the model to use.
            stability: Stability factor (0.0 to 1.0).
            similarity_boost: Similarity boost factor (0.0 to 1.0).
            style: Style factor (0.0 to 1.0).
            use_speaker_boost: Whether to use speaker boost.
            output_format: Output format for the audio.
        """
        super().__init__(
            api_key=api_key,
            voice_id=voice_id,
            model_id=model_id,
            stability=stability,
            similarity_boost=similarity_boost,
            style=style,
            use_speaker_boost=use_speaker_boost,
            output_format=output_format,
            **kwargs
        )

        self.ws = websocket_integration
        logger.info("WebSocketElevenLabsTTS initialized with WebSocket integration")

    def synthesize(self, text: str, output_path: Optional[str] = None) -> np.ndarray:
        """
        Synthesize speech from text with WebSocket events.

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

        # Signal start of TTS
        self.ws.tts_start(
            text=text,
            voice=self._get_voice_name(),
            provider="elevenlabs"
        )

        # Start timing for the entire process
        start_time = time.time()

        try:
            # Prepare voice settings
            voice_settings = {
                "stability": self.stability,
                "similarity_boost": self.similarity_boost,
                "style": self.style,
                "use_speaker_boost": self.use_speaker_boost
            }

            # Track progress
            progress = 0
            self.ws.tts_progress(progress)

            # Mark the start of actual synthesis (API call)
            if hasattr(self.ws, 'perf'):
                self.ws.perf.mark_component("tts", "synthesize", start=True)
            synthesis_start_time = time.time()

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
            chunk_count = 0
            for chunk in audio_stream:
                if isinstance(chunk, bytes):
                    audio_chunks.append(chunk)
                    chunk_count += 1

                    # Update progress (approximate)
                    if chunk_count % 5 == 0:  # Update every 5 chunks
                        progress = min(progress + 10, 90)  # Cap at 90% until complete
                        self.ws.tts_progress(progress)

            # Mark the end of actual synthesis (API call)
            synthesis_end_time = time.time()
            if hasattr(self.ws, 'perf'):
                self.ws.perf.mark_component("tts", "synthesize", start=False)
                # Store the synthesis time for accurate metrics
                synthesis_duration = synthesis_end_time - synthesis_start_time
                self.ws.perf.mark("tts_synthesis_duration")
                self.ws.perf.markers["tts_synthesis_duration"] = synthesis_duration

            # Create a temporary file to save the audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_path = temp_file.name

                # Write all chunks to the file
                for chunk in audio_chunks:
                    temp_file.write(chunk)

            # Final progress update
            self.ws.tts_progress(100)

            # Load the audio file with librosa
            import librosa
            audio_array, _ = librosa.load(temp_path, sr=44100, mono=True)

            # Clean up the temporary file
            os.unlink(temp_path)

            # Calculate durations
            end_time = time.time()
            processing_duration = end_time - start_time
            audio_duration = len(audio_array) / 44100  # in seconds

            # Store the audio duration for metrics
            if hasattr(self.ws, 'perf'):
                self.ws.perf.markers["tts_audio_duration"] = audio_duration

            # Signal TTS completion
            self.ws.tts_result(
                audio_duration_seconds=audio_duration,
                char_count=len(text)
            )

            return audio_array

        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")

            # Signal TTS error
            self.ws.tts_error(str(e))

            raise

    def stream_synthesize(self, text: str) -> Generator[bytes, None, None]:
        """
        Stream synthesize speech from text with WebSocket events.

        Args:
            text: Text to synthesize.

        Returns:
            Audio stream generator that yields audio chunks.
        """
        if not text:
            logger.warning("Empty text provided for synthesis, returning empty audio.")
            return np.array([], dtype=np.float32)

        logger.info(f"Streaming speech synthesis: {text[:50]}...")

        # Signal start of TTS
        self.ws.tts_start(
            text=text,
            voice=self._get_voice_name(),
            provider="elevenlabs"
        )

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

            # Track progress
            progress = 0
            self.ws.tts_progress(progress)

            # Generate speech as a stream
            audio_stream = self.client.text_to_speech.convert_as_stream(
                text=text,
                voice_id=self.voice_id,
                model_id=self.model_id,
                voice_settings=voice_settings,
                output_format=self.output_format
            )

            # Return a generator that yields audio chunks with progress updates
            chunk_count = 0
            total_bytes = 0

            for chunk in audio_stream:
                if isinstance(chunk, bytes):
                    chunk_count += 1
                    total_bytes += len(chunk)

                    # Update progress (approximate)
                    if chunk_count % 5 == 0:  # Update every 5 chunks
                        progress = min(progress + 10, 90)  # Cap at 90% until complete
                        self.ws.tts_progress(progress)

                    yield chunk

            # Final progress update
            self.ws.tts_progress(100)

            # Estimate audio duration (rough approximation)
            # MP3 at 128kbps is about 16KB per second of audio
            audio_duration = total_bytes / (16 * 1024)

            # Signal TTS completion
            end_time = time.time()
            self.ws.tts_result(
                audio_duration_seconds=audio_duration,
                char_count=len(text)
            )

        except Exception as e:
            logger.error(f"Error streaming speech synthesis: {e}")

            # Signal TTS error
            self.ws.tts_error(str(e))

            raise

    def speak(self, text: str) -> bool:
        """
        Synthesize speech from text and play it with WebSocket events.

        Args:
            text: Text to synthesize and play.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Signal start of TTS
            self.ws.tts_start(
                text=text,
                voice=self._get_voice_name(),
                provider="elevenlabs"
            )

            # Start timing
            start_time = time.time()

            # Synthesize speech
            logger.info(f"Synthesizing and playing speech: {text[:50]}...")
            audio = self.synthesize(text)

            # Play the audio
            self.play_audio(audio)

            # Calculate duration
            end_time = time.time()
            processing_duration = end_time - start_time
            audio_duration = len(audio) / 44100  # in seconds

            # Signal TTS completion
            self.ws.tts_result(
                audio_duration_seconds=audio_duration,
                char_count=len(text)
            )

            return True
        except Exception as e:
            logger.error(f"Error speaking text: {e}")

            # Signal TTS error
            self.ws.tts_error(str(e))

            return False

    def _get_voice_name(self) -> str:
        """
        Get the name of the current voice.

        Returns:
            str: Voice name or ID if name cannot be determined
        """
        try:
            voices = self.client.voices.get_all()
            for voice in voices.voices:
                if voice.voice_id == self.voice_id:
                    return voice.name
        except Exception as e:
            logger.warning(f"Could not get voice name: {e}")

        return self.voice_id

    def stop(self) -> None:
        """
        Stop any ongoing speech playback and send a WebSocket event.
        """
        logger.info("Stopping WebSocketElevenLabsTTS playback")

        # Send a WebSocket event to notify clients
        try:
            if hasattr(self, 'ws'):
                self.ws.tts_stop(reason="user_interrupt")
        except Exception as e:
            logger.warning(f"Error sending TTS stop event: {e}")

        # Call the parent class's stop method
        super().stop()

        logger.info("WebSocketElevenLabsTTS playback stopped")

    def unload(self) -> None:
        """
        Unload the TTS engine and free resources.
        Also sends a WebSocket event to notify clients.
        """
        logger.info("Unloading WebSocketElevenLabsTTS resources")

        # Send a WebSocket event to notify clients
        try:
            if hasattr(self, 'ws'):
                self.ws.tts_status("unloaded")
        except Exception as e:
            logger.warning(f"Error sending TTS unload event: {e}")

        # Call the parent class's unload method
        super().unload()

        logger.info("WebSocketElevenLabsTTS resources unloaded")
