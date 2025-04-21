"""Tests for the WhisperSTT class."""

import pytest
from unittest.mock import patch, MagicMock

from stt.whisper_stt import WhisperSTT

def test_whisper_stt_init():
    """Test WhisperSTT initialization."""
    # This is a placeholder test that will need to be updated
    # once the actual implementation is complete
    stt = WhisperSTT(model_size="tiny")
    assert stt.model_size == "tiny"

@pytest.mark.skip(reason="Implementation not complete")
def test_transcribe_audio():
    """Test transcribing audio file."""
    # This test will be implemented once the actual functionality is complete
    pass

@pytest.mark.skip(reason="Implementation not complete")
def test_listen():
    """Test listening for speech."""
    # This test will be implemented once the actual functionality is complete
    pass
