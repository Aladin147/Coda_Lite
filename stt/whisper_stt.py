"""
Whisper-based speech recognition implementation for Coda Lite.
Uses faster-whisper for efficient local transcription.
"""

import os
import tempfile
import time
import wave
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pyaudio
from faster_whisper import WhisperModel

import logging
logger = logging.getLogger("coda.stt")

class WhisperSTT:
    """Speech-to-text implementation using faster-whisper."""

    def __init__(
        self,
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
        Initialize the WhisperSTT module.

        Args:
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
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.language = language
        self.beam_size = beam_size
        self.vad_filter = vad_filter
        self.vad_parameters = vad_parameters or {}

        logger.info(f"Initializing WhisperSTT with model size: {model_size} on {device}")

        # Initialize faster-whisper model
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
            download_root=download_root,
            local_files_only=local_files_only,
        )

        # Audio recording parameters
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000  # Whisper expects 16kHz audio
        self.chunk = 1024
        self.record_seconds = 5  # Default recording duration
        self.audio = pyaudio.PyAudio()

        logger.info("WhisperSTT initialized successfully")

    def transcribe_audio(self, audio_path: Union[str, np.ndarray]) -> str:
        """
        Transcribe audio file to text.

        Args:
            audio_path (str or np.ndarray): Path to the audio file to transcribe or audio array

        Returns:
            str: Transcribed text
        """
        logger.info(f"Transcribing audio: {audio_path if isinstance(audio_path, str) else 'numpy array'}")

        try:
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

            logger.info(f"Transcription completed: {result[:50]}{'...' if len(result) > 50 else ''}")
            return result.strip()

        except Exception as e:
            logger.error(f"Error transcribing audio: {e}", exc_info=True)
            return ""

    def listen(self, duration: int = 5) -> str:
        """
        Listen for speech and transcribe in real-time.

        Args:
            duration (int): Duration to listen in seconds

        Returns:
            str: Transcribed text
        """
        logger.info(f"Listening for speech for {duration} seconds...")

        try:
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
            for i in range(0, int(self.rate / self.chunk * duration)):
                data = stream.read(self.chunk)
                frames.append(data)

            logger.info("Recording finished")

            # Stop and close the stream
            stream.stop_stream()
            stream.close()

            # Convert frames to numpy array
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0

            # Transcribe the audio
            return self.transcribe_audio(audio_data)

        except Exception as e:
            logger.error(f"Error during listening: {e}", exc_info=True)
            return ""

    def listen_continuous(self, callback=None, stop_callback=None, silence_threshold=0.1, silence_duration=2.0):
        """
        Listen continuously for speech and transcribe when speech is detected.

        Args:
            callback (callable): Function to call with transcription results
            stop_callback (callable): Function that returns True when listening should stop
            silence_threshold (float): Threshold for silence detection
            silence_duration (float): Duration of silence to consider speech ended

        Returns:
            None
        """
        logger.info("Starting continuous listening")

        try:
            # Open audio stream
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )

            frames = []
            silent_chunks = 0
            is_speaking = False
            max_silent_chunks = int(silence_duration * self.rate / self.chunk)

            logger.info("Continuous listening started")

            while True:
                if stop_callback and stop_callback():
                    logger.info("Stop callback triggered, ending continuous listening")
                    break

                # Read audio chunk
                data = stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)

                # Check if this chunk is silent
                audio_chunk = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                if np.abs(audio_chunk).mean() < silence_threshold:
                    silent_chunks += 1
                else:
                    silent_chunks = 0
                    is_speaking = True

                # If we've collected enough silent chunks after speech, process the audio
                if is_speaking and silent_chunks > max_silent_chunks:
                    logger.info("Speech detected, transcribing")

                    # Convert frames to numpy array
                    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0

                    # Transcribe the audio
                    transcription = self.transcribe_audio(audio_data)

                    # Call the callback with the transcription
                    if callback and transcription:
                        callback(transcription)

                    # Reset for next utterance
                    frames = []
                    is_speaking = False
                    silent_chunks = 0

            # Stop and close the stream
            stream.stop_stream()
            stream.close()

        except Exception as e:
            logger.error(f"Error during continuous listening: {e}", exc_info=True)
            if stream:
                stream.stop_stream()
                stream.close()

    def save_audio_to_file(self, frames, filename):
        """
        Save recorded audio frames to a WAV file.

        Args:
            frames (list): List of audio frames
            filename (str): Output filename

        Returns:
            str: Path to the saved file
        """
        try:
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            return filename
        except Exception as e:
            logger.error(f"Error saving audio to file: {e}", exc_info=True)
            return None

    def close(self):
        """
        Clean up resources.
        """
        self.audio.terminate()
        logger.info("WhisperSTT resources released")
