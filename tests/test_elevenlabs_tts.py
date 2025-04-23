"""
Unit tests for the ElevenLabs TTS module.
"""

import unittest
from unittest.mock import MagicMock, patch

from tts.elevenlabs_tts import ElevenLabsTTS
from tts.websocket_elevenlabs_tts import WebSocketElevenLabsTTS
from websocket.integration import CodaWebSocketIntegration


class TestElevenLabsTTS(unittest.TestCase):
    """Test cases for the ElevenLabsTTS class."""

    def setUp(self):
        """Set up the test environment."""
        # Create a mock ElevenLabs client
        self.mock_client = MagicMock()
        
        # Create a patch for the ElevenLabs client
        patcher = patch('elevenlabs.client.ElevenLabs', return_value=self.mock_client)
        patcher.start()
        self.addCleanup(patcher.stop)
        
        # Create an ElevenLabsTTS instance
        self.tts = ElevenLabsTTS(
            api_key="test_api_key",
            voice_id="test_voice_id",
            model_id="eleven_multilingual_v2"
        )
        
        # Replace the client with our mock
        self.tts.client = self.mock_client

    def test_speak(self):
        """Test the speak method."""
        # Mock the synthesize method
        self.tts.synthesize = MagicMock(return_value=MagicMock())
        self.tts.play_audio = MagicMock()
        
        # Call the speak method
        result = self.tts.speak("This is a test.")
        
        # Verify the synthesize method was called
        self.tts.synthesize.assert_called_once_with("This is a test.")
        
        # Verify the play_audio method was called
        self.tts.play_audio.assert_called_once()
        
        # Verify the result
        self.assertTrue(result)


class TestWebSocketElevenLabsTTS(unittest.TestCase):
    """Test cases for the WebSocketElevenLabsTTS class."""

    def setUp(self):
        """Set up the test environment."""
        # Create a mock WebSocket integration
        self.mock_ws = MagicMock(spec=CodaWebSocketIntegration)
        
        # Create a mock ElevenLabs client
        self.mock_client = MagicMock()
        
        # Create a patch for the ElevenLabs client
        patcher = patch('elevenlabs.client.ElevenLabs', return_value=self.mock_client)
        patcher.start()
        self.addCleanup(patcher.stop)
        
        # Create a WebSocketElevenLabsTTS instance
        self.tts = WebSocketElevenLabsTTS(
            websocket_integration=self.mock_ws,
            api_key="test_api_key",
            voice_id="test_voice_id",
            model_id="eleven_multilingual_v2"
        )
        
        # Replace the client with our mock
        self.tts.client = self.mock_client

    def test_speak_with_websocket_events(self):
        """Test the speak method with WebSocket events."""
        # Mock the synthesize method
        self.tts.synthesize = MagicMock(return_value=MagicMock())
        self.tts.play_audio = MagicMock()
        
        # Call the speak method
        result = self.tts.speak("This is a test.")
        
        # Verify the synthesize method was called
        self.tts.synthesize.assert_called_once_with("This is a test.")
        
        # Verify the play_audio method was called
        self.tts.play_audio.assert_called_once()
        
        # Verify the result
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
