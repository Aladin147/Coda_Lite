"""
Unit tests for the Speech-to-Text (STT) module.
"""

import os
import unittest
import numpy as np
from unittest.mock import MagicMock, patch

from stt.whisper_stt import WhisperSTT
from stt.websocket_stt import WebSocketWhisperSTT
from websocket.integration import CodaWebSocketIntegration


class TestWhisperSTT(unittest.TestCase):
    """Test cases for the WhisperSTT class."""

    @patch('stt.whisper_stt.WhisperModel')
    @patch('stt.whisper_stt.pyaudio.PyAudio')
    def setUp(self, mock_pyaudio, mock_whisper_model):
        """Set up the test environment."""
        # Mock the WhisperModel
        self.mock_model = MagicMock()
        mock_whisper_model.return_value = self.mock_model

        # Create a WhisperSTT instance
        self.stt = WhisperSTT(model_size="tiny", device="cpu")

        # Create a test audio file path
        self.test_audio_path = os.path.join(os.path.dirname(__file__), "data", "test_audio.wav")

        # Create a directory for test data if it doesn't exist
        os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)

    def test_transcribe_audio_file(self):
        """Test transcribing an audio file."""
        # Mock the transcribe method
        self.mock_model.transcribe.return_value = (
            [MagicMock(text="This is a test.")],
            MagicMock(language="en", avg_logprob=-0.5)
        )

        # Create a dummy audio file if it doesn't exist
        if not os.path.exists(self.test_audio_path):
            with open(self.test_audio_path, "wb") as f:
                f.write(b"dummy audio data")

        # Call the transcribe_audio method
        result = self.stt.transcribe_audio(self.test_audio_path)

        # Check the result
        self.assertEqual(result, "This is a test.")

        # Verify the model was called with the correct parameters
        self.mock_model.transcribe.assert_called_once_with(
            self.test_audio_path,
            language=self.stt.language,
            beam_size=self.stt.beam_size,
            vad_filter=self.stt.vad_filter,
            vad_parameters=self.stt.vad_parameters
        )

    def test_transcribe_audio_array(self):
        """Test transcribing an audio array."""
        # Mock the transcribe method
        self.mock_model.transcribe.return_value = (
            [MagicMock(text="This is a test.")],
            MagicMock(language="en", avg_logprob=-0.5)
        )

        # Create a dummy audio array
        audio_array = np.zeros(16000, dtype=np.float32)

        # Call the transcribe_audio method
        result = self.stt.transcribe_audio(audio_array)

        # Check the result
        self.assertEqual(result, "This is a test.")

        # Verify the model was called with the correct parameters
        self.mock_model.transcribe.assert_called_once_with(
            audio_array,
            language=self.stt.language,
            beam_size=self.stt.beam_size,
            vad_filter=self.stt.vad_filter,
            vad_parameters=self.stt.vad_parameters
        )


class TestWebSocketWhisperSTT(unittest.TestCase):
    """Test cases for the WebSocketWhisperSTT class."""

    @patch('stt.whisper_stt.WhisperModel')
    @patch('stt.whisper_stt.pyaudio.PyAudio')
    def setUp(self, mock_pyaudio, mock_whisper_model):
        """Set up the test environment."""
        # Mock the WhisperModel
        self.mock_model = MagicMock()
        mock_whisper_model.return_value = self.mock_model

        # Mock the WebSocket integration
        self.mock_ws = MagicMock(spec=CodaWebSocketIntegration)

        # Create a WebSocketWhisperSTT instance
        self.stt = WebSocketWhisperSTT(
            websocket_integration=self.mock_ws,
            model_size="tiny",
            device="cpu"
        )

        # Create a test audio file path
        self.test_audio_path = os.path.join(os.path.dirname(__file__), "data", "test_audio.wav")

        # Create a directory for test data if it doesn't exist
        os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)

    def test_transcribe_audio_with_websocket_events(self):
        """Test transcribing an audio file with WebSocket events."""
        # Mock the transcribe method
        self.mock_model.transcribe.return_value = (
            [MagicMock(text="This is a test.", avg_logprob=-0.5)],
            MagicMock(language="en", avg_logprob=-0.5)
        )

        # Create a dummy audio file if it doesn't exist
        if not os.path.exists(self.test_audio_path):
            with open(self.test_audio_path, "wb") as f:
                f.write(b"dummy audio data")

        # Call the transcribe_audio method
        result = self.stt.transcribe_audio(self.test_audio_path)

        # Check the result
        self.assertEqual(result, "This is a test.")

        # Verify WebSocket events were emitted
        self.mock_ws.stt_start.assert_called_once_with(mode="file")
        self.mock_ws.stt_interim_result.assert_called_once()
        self.mock_ws.stt_result.assert_called_once()

        # Verify the model was called with the correct parameters
        self.mock_model.transcribe.assert_called_once_with(
            self.test_audio_path,
            language=self.stt.language,
            beam_size=self.stt.beam_size,
            vad_filter=self.stt.vad_filter,
            vad_parameters=self.stt.vad_parameters
        )

    def test_transcribe_audio_with_error(self):
        """Test transcribing an audio file with an error."""
        # Mock the transcribe method to raise an exception
        self.mock_model.transcribe.side_effect = Exception("Test error")

        # Call the transcribe_audio method
        result = self.stt.transcribe_audio(self.test_audio_path)

        # Check the result
        self.assertEqual(result, "")

        # Verify WebSocket events were emitted
        self.mock_ws.stt_start.assert_called_once_with(mode="file")
        self.mock_ws.stt_error.assert_called_once_with("Test error")


if __name__ == "__main__":
    unittest.main()
