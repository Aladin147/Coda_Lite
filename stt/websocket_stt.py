"""
WebSocket-integrated speech recognition implementation for Coda Lite.
Extends WhisperSTT to emit events via WebSocket.
"""

import logging
from typing import Dict, List, Optional, Tuple, Union, Callable, Any

import numpy as np

from stt.whisper_stt import WhisperSTT
from websocket.integration import CodaWebSocketIntegration

logger = logging.getLogger("coda.stt.websocket")

class WebSocketWhisperSTT(WhisperSTT):
    """Speech-to-text implementation using faster-whisper with WebSocket integration."""

    def __init__(
        self,
        websocket_integration: CodaWebSocketIntegration,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "float32",
        download_root: Optional[str] = None,
        local_files_only: bool = False,
        language: Optional[str] = None,
        beam_size: int = 5,
        vad_filter: bool = True,
        vad_parameters: Optional[Dict] = None,
    ):
        """
        Initialize the WebSocketWhisperSTT module.

        Args:
            websocket_integration: The WebSocket integration instance
            model_size (str): Size of the Whisper model to use.
                Options: "tiny", "base", "small", "medium", "large-v3"
            device (str): Device to use for computation ("cpu", "cuda", "auto")
            compute_type (str): Type to use for computation ("float32", "float16", "int8")
            download_root (str, optional): Directory where the models should be saved
            local_files_only (bool): If True, avoid downloading the model
            language (str, optional): Language code for transcription (e.g., "en", "fr")
            beam_size (int): Beam size to use for decoding
            vad_filter (bool): Whether to use voice activity detection
            vad_parameters (dict, optional): Parameters for VAD
        """
        super().__init__(
            model_size=model_size,
            device=device,
            compute_type=compute_type,
            download_root=download_root,
            local_files_only=local_files_only,
            language=language,
            beam_size=beam_size,
            vad_filter=vad_filter,
            vad_parameters=vad_parameters,
        )

        self.ws = websocket_integration
        logger.info("WebSocketWhisperSTT initialized with WebSocket integration")

    def transcribe_audio(self, audio_path: Union[str, np.ndarray]) -> str:
        """
        Transcribe audio file to text with WebSocket events.

        Args:
            audio_path (str or np.ndarray): Path to the audio file to transcribe or audio array

        Returns:
            str: Transcribed text
        """
        logger.info(f"Transcribing audio: {audio_path if isinstance(audio_path, str) else 'numpy array'}")

        try:
            # Signal start of transcription
            self.ws.stt_start(mode="file")

            # Transcribe the audio
            segments, info = self.model.transcribe(
                audio_path,
                language=self.language,
                beam_size=self.beam_size,
                vad_filter=self.vad_filter,
                vad_parameters=self.vad_parameters,
            )

            # Collect all segments
            result = ""
            for segment in segments:
                result += segment.text + " "

                # Send interim result for each segment
                self.ws.stt_interim_result(segment.text, segment.avg_logprob)

            result = result.strip()

            # Send final result
            self.ws.stt_result(result, info.avg_logprob if hasattr(info, 'avg_logprob') else 0.0, info.language)

            logger.info(f"Transcription completed: {result[:50]}{'...' if len(result) > 50 else ''}")
            return result

        except Exception as e:
            logger.error(f"Error during transcription: {e}", exc_info=True)

            # Send error event
            self.ws.stt_error(str(e))

            return ""

    def listen(self, duration: int = 5) -> str:
        """
        Listen for speech and transcribe with WebSocket events.

        Args:
            duration (int): Duration to listen in seconds

        Returns:
            str: Transcribed text
        """
        logger.info(f"Listening for speech for {duration} seconds...")

        try:
            # Reset the stop listening flag
            self._stop_listening = False

            # Signal start of listening
            self.ws.stt_start(mode="push_to_talk")

            # Open audio stream
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )

            logger.info("Recording started")

            # Record audio
            frames = []
            max_frames = int(self.rate / self.chunk * duration)

            for i in range(0, max_frames):
                # Check if we should stop listening
                if self._stop_listening:
                    logger.info("Stop listening flag set, stopping recording")
                    break

                data = stream.read(self.chunk)
                frames.append(data)

            logger.info("Recording finished")

            # Stop and close the stream
            stream.stop_stream()
            stream.close()

            # Reset the stop listening flag
            self._stop_listening = False

            # If we have no frames, return empty string
            if not frames:
                logger.info("No audio recorded, returning empty string")
                return ""

            # Convert frames to numpy array
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0

            # Transcribe the audio
            return self.transcribe_audio(audio_data)

        except Exception as e:
            logger.error(f"Error during listening: {e}", exc_info=True)

            # Send error event
            self.ws.stt_error(str(e))

            return ""

    # Flag to control push-to-talk listening
    _stop_listening = False

    def stop_listening(self):
        """
        Stop the current listening session.
        This is used to stop push-to-talk listening when the button is released.
        """
        logger.info("Stopping listening session")
        self._stop_listening = True

    def listen_continuous(self, callback=None, stop_callback=None, silence_threshold=0.1, silence_duration=2.0):
        """
        Listen continuously for speech and transcribe when speech is detected with WebSocket events.

        Args:
            callback (callable): Function to call with transcription results
            stop_callback (callable): Function that returns True when listening should stop
            silence_threshold (float): Threshold for silence detection
            silence_duration (float): Duration of silence to consider speech ended

        Returns:
            None
        """
        logger.info("Starting continuous listening")

        # Signal start of continuous listening
        self.ws.stt_start(mode="continuous")

        try:
            # Open audio stream
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )

            logger.info("Continuous recording started")

            # Initialize variables for continuous listening
            frames = []
            silent_frames = 0
            speaking = False
            silent_threshold = silence_threshold
            silent_frames_threshold = int(silence_duration * self.rate / self.chunk)

            # Reset the stop listening flag
            self._stop_listening = False

            # Listen continuously
            while True:
                # Check if we should stop
                if (stop_callback and stop_callback()) or self._stop_listening:
                    logger.info("Stop condition met, stopping continuous listening")
                    # Reset the flag
                    self._stop_listening = False
                    break

                # Read audio data
                data = stream.read(self.chunk)
                audio_chunk = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0

                # Check if this chunk is silent
                is_silent = np.abs(audio_chunk).mean() < silent_threshold

                if speaking:
                    # Add the chunk to the frames
                    frames.append(data)

                    # If silent, increment the silent frame counter
                    if is_silent:
                        silent_frames += 1
                        if silent_frames >= silent_frames_threshold:
                            # Enough silence, process the speech
                            speaking = False
                            silent_frames = 0

                            # Convert frames to numpy array
                            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0
                            frames = []

                            # Transcribe the audio
                            result = self.transcribe_audio(audio_data)

                            # Call the callback with the result
                            if callback and result:
                                callback(result)
                    else:
                        # Reset silent frame counter if not silent
                        silent_frames = 0
                else:
                    # Not speaking, check if we should start
                    if not is_silent:
                        logger.info("Speech detected, starting to record")
                        speaking = True
                        frames.append(data)

            # Stop and close the stream
            stream.stop_stream()
            stream.close()

            logger.info("Continuous recording stopped")

        except Exception as e:
            logger.error(f"Error during continuous listening: {e}", exc_info=True)

            # Send error event
            self.ws.stt_error(str(e))

            # Close the stream if it's open
            try:
                if 'stream' in locals() and stream.is_active():
                    stream.stop_stream()
                    stream.close()
            except Exception:
                pass
