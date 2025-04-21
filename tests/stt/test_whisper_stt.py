"""Tests for the WhisperSTT class."""

import os
import tempfile
from pathlib import Path

import numpy as np
import pytest
from unittest.mock import patch, MagicMock

from stt.whisper_stt import WhisperSTT


def test_whisper_stt_init():
    """Test WhisperSTT initialization."""
    with patch('faster_whisper.WhisperModel') as mock_model:
        stt = WhisperSTT(model_size="tiny", device="cpu", compute_type="float32")
        assert stt.model_size == "tiny"
        assert stt.device == "cpu"
        assert stt.compute_type == "float32"
        mock_model.assert_called_once_with(
            "tiny",
            device="cpu",
            compute_type="float32",
            download_root=None,
            local_files_only=False
        )


def test_transcribe_audio():
    """Test transcribing audio file."""
    # Create a mock model and segments
    mock_segment = MagicMock()
    mock_segment.text = "This is a test transcription."

    mock_segments = [mock_segment]
    mock_info = MagicMock()

    with patch('faster_whisper.WhisperModel') as mock_model_class:
        # Configure the mock model to return our mock segments
        mock_model = mock_model_class.return_value
        mock_model.transcribe.return_value = (mock_segments, mock_info)

        # Create the WhisperSTT instance with the mocked model
        stt = WhisperSTT(model_size="tiny")

        # Test with a file path
        result = stt.transcribe_audio("test_audio.wav")
        assert result == "This is a test transcription."

        # Test with numpy array
        audio_array = np.zeros(16000, dtype=np.float32)  # 1 second of silence
        result = stt.transcribe_audio(audio_array)
        assert result == "This is a test transcription."


def test_listen():
    """Test listening for speech."""
    # Create mock audio data
    mock_audio_data = np.zeros(16000, dtype=np.float32)  # 1 second of silence

    # Create a mock PyAudio instance and stream
    mock_stream = MagicMock()
    mock_stream.read.return_value = b'\x00' * 2048  # Mock audio data

    mock_pyaudio = MagicMock()
    mock_pyaudio.open.return_value = mock_stream

    with patch('pyaudio.PyAudio', return_value=mock_pyaudio), \
         patch('numpy.frombuffer', return_value=mock_audio_data), \
         patch.object(WhisperSTT, 'transcribe_audio', return_value="Test transcription"):

        # Create the WhisperSTT instance
        stt = WhisperSTT(model_size="tiny")

        # Test the listen method
        result = stt.listen(duration=1)
        assert result == "Test transcription"

        # Verify the stream was properly closed
        mock_stream.stop_stream.assert_called_once()
        mock_stream.close.assert_called_once()


def test_listen_continuous():
    """Test continuous listening."""
    # Create mock audio data
    mock_audio_data = np.zeros(16000, dtype=np.float32)  # 1 second of silence

    # Create a mock PyAudio instance and stream
    mock_stream = MagicMock()
    # First return silent data, then speech data, then silent data again
    mock_stream.read.side_effect = [
        b'\x00' * 2048,  # Silent
        b'\x01' * 2048,  # Speech
        b'\x01' * 2048,  # Speech
        b'\x00' * 2048,  # Silent
        b'\x00' * 2048,  # Silent
        b'\x00' * 2048,  # Silent
    ]

    mock_pyaudio = MagicMock()
    mock_pyaudio.open.return_value = mock_stream

    # Create a mock callback and stop_callback
    mock_callback = MagicMock()
    stop_after_one = MagicMock()
    stop_after_one.side_effect = [False, False, False, False, False, True]

    with patch('pyaudio.PyAudio', return_value=mock_pyaudio), \
         patch('numpy.frombuffer', return_value=mock_audio_data), \
         patch('numpy.abs') as mock_abs, \
         patch.object(WhisperSTT, 'transcribe_audio', return_value="Test continuous transcription"):

        # Configure mock_abs to simulate silence detection
        mock_mean = MagicMock()
        mock_mean.side_effect = [0.05, 0.2, 0.2, 0.05, 0.05, 0.05]  # Below, above, above, below threshold
        mock_abs.return_value.mean = mock_mean

        # Create the WhisperSTT instance
        stt = WhisperSTT(model_size="tiny")

        # Test the listen_continuous method
        stt.listen_continuous(
            callback=mock_callback,
            stop_callback=stop_after_one,
            silence_threshold=0.1,
            silence_duration=0.1  # Short duration for testing
        )

        # Verify the callback was called with the transcription
        mock_callback.assert_called_with("Test continuous transcription")

        # Verify the stream was properly closed
        mock_stream.stop_stream.assert_called_once()
        mock_stream.close.assert_called_once()


def test_save_audio_to_file():
    """Test saving audio to file."""
    # Create mock frames
    frames = [b'\x00' * 1024, b'\x01' * 1024]

    # Create a mock wave file
    mock_wave_file = MagicMock()

    with patch('wave.open', return_value=mock_wave_file), \
         patch('pyaudio.PyAudio') as mock_pyaudio_class:

        # Configure the mock PyAudio
        mock_pyaudio = mock_pyaudio_class.return_value
        mock_pyaudio.get_sample_size.return_value = 2

        # Create the WhisperSTT instance
        stt = WhisperSTT(model_size="tiny")

        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Test saving audio to file
            result = stt.save_audio_to_file(frames, temp_path)
            assert result == temp_path

            # Verify wave file operations
            mock_wave_file.setnchannels.assert_called_once_with(1)
            mock_wave_file.setsampwidth.assert_called_once_with(2)
            mock_wave_file.setframerate.assert_called_once_with(16000)
            mock_wave_file.writeframes.assert_called_once_with(b'\x00' * 1024 + b'\x01' * 1024)
            mock_wave_file.close.assert_called_once()
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
