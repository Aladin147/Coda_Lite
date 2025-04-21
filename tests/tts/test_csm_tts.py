"""Tests for the CSMTTS class."""

import os
import tempfile

import numpy as np
import pytest
from unittest.mock import patch, MagicMock

from tts.csm_tts import CSMTTS


def test_csm_tts_init():
    """Test CSMTTS initialization."""
    with patch('TTS.api.TTS') as mock_tts_class:
        # Configure the mock TTS class
        mock_tts = mock_tts_class.return_value
        mock_tts.speakers = ["speaker1", "speaker2"]
        mock_tts.languages = ["en", "fr"]

        # Create the CSMTTS instance
        tts = CSMTTS(model_name="test_model", device="cpu")

        # Verify the initialization
        assert tts.model_name == "test_model"
        assert tts.device == "cpu"
        assert tts.speakers == ["speaker1", "speaker2"]
        assert tts.languages == ["en", "fr"]

        # Verify TTS was initialized correctly
        mock_tts_class.assert_called_once_with(model_name="test_model", progress_bar=False)


def test_synthesize():
    """Test synthesizing speech with output path."""
    with patch('TTS.api.TTS') as mock_tts_class, \
         patch('os.unlink') as mock_unlink:

        # Configure the mock TTS class
        mock_tts = mock_tts_class.return_value

        # Create the CSMTTS instance
        tts = CSMTTS(model_name="test_model")

        # Test synthesizing with output path
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            output_path = temp_file.name

        result = tts.synthesize("Hello world", output_path=output_path)

        # Verify the synthesis
        mock_tts.tts_to_file.assert_called_once_with(
            text="Hello world",
            file_path=output_path,
            speaker=None,
            language=None,
            speed=1.0
        )

        assert result == output_path

        # Clean up
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_synthesize_with_playback():
    """Test synthesizing speech with direct playback."""
    with patch('TTS.api.TTS') as mock_tts_class, \
         patch('tempfile.NamedTemporaryFile') as mock_temp_file, \
         patch.object(CSMTTS, 'play_audio') as mock_play_audio, \
         patch('os.unlink') as mock_unlink:

        # Configure the mock TTS class
        mock_tts = mock_tts_class.return_value

        # Configure the mock temporary file
        mock_temp = MagicMock()
        mock_temp.name = "/tmp/test.wav"
        mock_temp_file.return_value = mock_temp

        # Create the CSMTTS instance
        tts = CSMTTS(model_name="test_model")

        # Test synthesizing with direct playback
        result = tts.synthesize("Hello world")

        # Verify the synthesis
        mock_tts.tts_to_file.assert_called_once_with(
            text="Hello world",
            file_path="/tmp/test.wav",
            speaker=None,
            language=None,
            speed=1.0
        )

        # Verify audio was played
        mock_play_audio.assert_called_once_with("/tmp/test.wav")

        # Verify temporary file was cleaned up
        mock_unlink.assert_called_once_with("/tmp/test.wav")

        assert result is None


def test_play_audio_file():
    """Test playing audio from file."""
    with patch('soundfile.read') as mock_read, \
         patch('sounddevice.play') as mock_play, \
         patch('sounddevice.wait') as mock_wait:

        # Configure the mock soundfile.read
        mock_read.return_value = (np.zeros(1000), 22050)

        # Create the CSMTTS instance
        tts = CSMTTS(model_name="test_model")

        # Test playing audio from file
        tts.play_audio("/tmp/test.wav")

        # Verify the audio playback
        mock_read.assert_called_once_with("/tmp/test.wav")
        mock_play.assert_called_once()
        mock_wait.assert_called_once()


def test_play_audio_array():
    """Test playing audio from array."""
    with patch('sounddevice.play') as mock_play, \
         patch('sounddevice.wait') as mock_wait:

        # Create the CSMTTS instance
        tts = CSMTTS(model_name="test_model")

        # Test playing audio from array
        audio_array = np.zeros(1000)
        tts.play_audio(audio_array)

        # Verify the audio playback
        mock_play.assert_called_once()
        mock_wait.assert_called_once()


def test_list_available_models():
    """Test listing available models."""
    with patch('TTS.api.TTS') as mock_tts_class:
        # Configure the mock TTS class
        mock_tts = mock_tts_class.return_value
        mock_tts.list_models.return_value = ["model1", "model2"]

        # Create the CSMTTS instance
        tts = CSMTTS(model_name="test_model")

        # Test listing available models
        models = tts.list_available_models()

        # Verify the result
        assert models == ["model1", "model2"]


def test_list_speakers():
    """Test listing available speakers."""
    with patch('TTS.api.TTS') as mock_tts_class:
        # Configure the mock TTS class
        mock_tts = mock_tts_class.return_value
        mock_tts.speakers = ["speaker1", "speaker2"]

        # Create the CSMTTS instance
        tts = CSMTTS(model_name="test_model")

        # Test listing available speakers
        speakers = tts.list_speakers()

        # Verify the result
        assert speakers == ["speaker1", "speaker2"]


def test_list_languages():
    """Test listing available languages."""
    with patch('TTS.api.TTS') as mock_tts_class:
        # Configure the mock TTS class
        mock_tts = mock_tts_class.return_value
        mock_tts.languages = ["en", "fr"]

        # Create the CSMTTS instance
        tts = CSMTTS(model_name="test_model")

        # Test listing available languages
        languages = tts.list_languages()

        # Verify the result
        assert languages == ["en", "fr"]
