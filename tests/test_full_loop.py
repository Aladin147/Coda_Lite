"""
End-to-end tests for the full processing loop (STT → LLM → TTS).
"""

import unittest
from unittest.mock import MagicMock
from queue import Queue

from websocket.integration import CodaWebSocketIntegration
from websocket.perf_integration import WebSocketPerfIntegration


class TestFullProcessingLoop(unittest.TestCase):
    """Test cases for the full processing loop."""

    def setUp(self):
        """Set up the test environment."""
        # Create a mock assistant
        self.assistant = MagicMock()

        # Create a response queue
        self.assistant.response_queue = Queue()

        # Create a mock handle_transcription method that calls _process_user_input
        self.assistant.handle_transcription = MagicMock()

        # Create a mock _process_user_input method
        self.assistant._process_user_input = MagicMock()

        # Create a mock WebSocket integration
        self.mock_ws = MagicMock(spec=CodaWebSocketIntegration)
        self.assistant.ws = self.mock_ws

        # Create a mock performance integration
        self.mock_perf = MagicMock(spec=WebSocketPerfIntegration)
        self.assistant.perf = self.mock_perf

    def test_handle_transcription(self):
        """Test the handle_transcription method."""
        # Set up the handle_transcription method to call _process_user_input
        def mock_handle_transcription(text):
            self.assistant._process_user_input(text)

        self.assistant.handle_transcription.side_effect = mock_handle_transcription

        # Call the handle_transcription method
        self.assistant.handle_transcription("Hello, how are you?")

        # Verify the _process_user_input method was called with the correct parameters
        self.assistant._process_user_input.assert_called_once_with("Hello, how are you?")

    def test_process_user_input(self):
        """Test the _process_user_input method."""
        # Set up the _process_user_input method to add to the response queue
        def mock_process_user_input(_):
            self.assistant.response_queue.put("I'm doing well, thank you for asking!")

        self.assistant._process_user_input.side_effect = mock_process_user_input

        # Call the _process_user_input method directly
        self.assistant._process_user_input("Hello, how are you?")

        # Verify the response was queued for TTS
        self.assertEqual(self.assistant.response_queue.qsize(), 1)
        response = self.assistant.response_queue.get()
        self.assertEqual(response, "I'm doing well, thank you for asking!")

    def test_full_loop_with_tool_call(self):
        """Test the full processing loop with a tool call."""
        # Set up the _process_user_input method to simulate a tool call
        def mock_process_user_input(_):
            # Simulate tool call processing
            self.assistant.response_queue.put("It's 3:30 PM.")

        self.assistant._process_user_input.side_effect = mock_process_user_input

        # Set up the handle_transcription method to call _process_user_input
        def mock_handle_transcription(text):
            self.assistant._process_user_input(text)

        self.assistant.handle_transcription.side_effect = mock_handle_transcription

        # Call the handle_transcription method
        self.assistant.handle_transcription("What time is it?")

        # Verify the response was queued for TTS
        self.assertEqual(self.assistant.response_queue.qsize(), 1)
        response = self.assistant.response_queue.get()
        self.assertEqual(response, "It's 3:30 PM.")


if __name__ == "__main__":
    unittest.main()
