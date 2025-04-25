"""
Tests for the WebSocket implementation of the STT-LLM-TTS pipeline.

This module provides tests for the WebSocket-enabled components:
1. WebSocketWhisperSTT
2. WebSocketOllamaLLM
3. WebSocketElevenLabsTTS

It includes both unit tests for individual components and integration tests
for the full WebSocket pipeline.
"""

import os
import time
import asyncio
import unittest
import logging
import tempfile
from unittest.mock import MagicMock, patch

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("coda.tests.websocket_pipeline")

# Import the components to test
from stt.websocket_stt import WebSocketWhisperSTT
from llm.websocket_llm import WebSocketOllamaLLM
# Import WebSocketElevenLabsTTS directly to avoid importing CSM TTS which has MeCab dependency
import sys
import os

# Add the tts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "tts"))

# Import directly from the module
from websocket_elevenlabs_tts import WebSocketElevenLabsTTS
from websocket.integration import CodaWebSocketIntegration
from utils.perf_tracker import PerfTracker


class TestWebSocketPipeline(unittest.TestCase):
    """Test cases for the WebSocket-enabled pipeline."""

    @patch('stt.whisper_stt.WhisperModel')
    @patch('llm.ollama_llm.requests')
    @patch('tts.elevenlabs_tts.requests')
    def setUp(self, mock_tts_requests, mock_llm_requests, mock_whisper_model):
        """Set up the test environment."""
        # Mock the WhisperModel
        self.mock_stt_model = MagicMock()
        mock_whisper_model.return_value = self.mock_stt_model

        # Mock the LLM requests
        self.mock_llm_response = MagicMock()
        self.mock_llm_response.json.return_value = {
            "response": "This is a test response from the LLM."
        }
        self.mock_llm_response.status_code = 200
        mock_llm_requests.post.return_value = self.mock_llm_response

        # Mock the TTS requests
        self.mock_tts_response = MagicMock()
        self.mock_tts_response.content = b"audio_data"
        self.mock_tts_response.status_code = 200
        mock_tts_requests.post.return_value = self.mock_tts_response

        # Create a performance tracker
        self.perf_tracker = PerfTracker()

        # Create a WebSocket integration
        self.ws = MagicMock(spec=CodaWebSocketIntegration)
        self.ws.perf_tracker = self.perf_tracker

        # Create the WebSocket-enabled components
        self.stt = WebSocketWhisperSTT(
            websocket_integration=self.ws,
            model_size="tiny",
            device="cpu"
        )
        self.llm = WebSocketOllamaLLM(
            websocket_integration=self.ws,
            model_name="llama3",
            host="http://localhost:11434"
        )
        self.tts = WebSocketElevenLabsTTS(
            websocket_integration=self.ws,
            api_key="test_key",
            voice_id="test_voice"
        )

        # Create a test audio file path
        self.test_audio_path = os.path.join(os.path.dirname(__file__), "data", "test_audio.wav")

        # Create a directory for test data if it doesn't exist
        os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)

        # Create a test audio file if it doesn't exist
        if not os.path.exists(self.test_audio_path):
            with open(self.test_audio_path, "wb") as f:
                f.write(b"test_audio_data")

    def test_websocket_stt(self):
        """Test the WebSocket-enabled STT component."""
        # Configure the mock model to return a test transcription
        self.mock_stt_model.transcribe.return_value = {
            "text": "What is the weather today?",
            "language": "en",
            "segments": []
        }

        # Call the transcribe_audio method
        result = self.stt.transcribe_audio(self.test_audio_path)

        # Check the result
        self.assertEqual(result, "What is the weather today?")

        # Verify WebSocket events were emitted
        self.ws.stt_start.assert_called_once()
        self.ws.stt_result.assert_called_once()

    def test_websocket_llm(self):
        """Test the WebSocket-enabled LLM component."""
        # Call the generate_response method
        result = self.llm.generate_response(
            prompt="What is the weather today?",
            system_prompt="You are a helpful assistant."
        )

        # Check the result
        self.assertEqual(result, "This is a test response from the LLM.")

        # Verify WebSocket events were emitted
        self.ws.llm_start.assert_called_once()
        self.ws.llm_result.assert_called_once()

    def test_websocket_tts(self):
        """Test the WebSocket-enabled TTS component."""
        # Call the synthesize method with a temporary output path
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            output_path = temp_file.name

        try:
            result = self.tts.synthesize(
                text="This is a test response from the LLM.",
                output_path=output_path
            )

            # Check that the result is the output path
            self.assertEqual(result, output_path)

            # Verify WebSocket events were emitted
            self.ws.tts_start.assert_called_once()
            self.ws.tts_result.assert_called_once()
        finally:
            # Clean up
            if os.path.exists(output_path):
                os.unlink(output_path)

    @patch('stt.whisper_stt.WhisperModel')
    @patch('llm.ollama_llm.requests')
    @patch('tts.elevenlabs_tts.requests')
    def test_full_websocket_pipeline(self, mock_tts_requests, mock_llm_requests, mock_whisper_model):
        """Test the full WebSocket-enabled pipeline."""
        # Configure the mock STT model to return a test transcription
        mock_stt_model = MagicMock()
        mock_stt_model.transcribe.return_value = {
            "text": "What is the weather today?",
            "language": "en",
            "segments": []
        }
        mock_whisper_model.return_value = mock_stt_model

        # Configure the mock LLM response
        mock_llm_response = MagicMock()
        mock_llm_response.json.return_value = {
            "response": "The weather today is sunny with a high of 75 degrees."
        }
        mock_llm_response.status_code = 200
        mock_llm_requests.post.return_value = mock_llm_response

        # Configure the mock TTS response
        mock_tts_response = MagicMock()
        mock_tts_response.content = b"audio_data"
        mock_tts_response.status_code = 200
        mock_tts_requests.post.return_value = mock_tts_response

        # Create a WebSocket integration with event tracking
        ws = MagicMock(spec=CodaWebSocketIntegration)
        ws.perf_tracker = self.perf_tracker

        # Track emitted events
        emitted_events = []

        def track_event(event_type, data):
            emitted_events.append((event_type, data))

        # Mock the event methods to track calls
        ws.stt_start.side_effect = lambda **kwargs: track_event("stt_start", kwargs)
        ws.stt_result.side_effect = lambda **kwargs: track_event("stt_result", kwargs)
        ws.llm_start.side_effect = lambda **kwargs: track_event("llm_start", kwargs)
        ws.llm_token.side_effect = lambda **kwargs: track_event("llm_token", kwargs)
        ws.llm_result.side_effect = lambda **kwargs: track_event("llm_result", kwargs)
        ws.tts_start.side_effect = lambda **kwargs: track_event("tts_start", kwargs)
        ws.tts_result.side_effect = lambda **kwargs: track_event("tts_result", kwargs)

        # Create the WebSocket-enabled components
        stt = WebSocketWhisperSTT(
            websocket_integration=ws,
            model_size="tiny",
            device="cpu"
        )
        llm = WebSocketOllamaLLM(
            websocket_integration=ws,
            model_name="llama3",
            host="http://localhost:11434"
        )
        tts = WebSocketElevenLabsTTS(
            websocket_integration=ws,
            api_key="test_key",
            voice_id="test_voice"
        )

        # Mark the start of the pipeline
        self.perf_tracker.mark("pipeline_start")

        # Step 1: STT - Transcribe audio
        self.perf_tracker.mark_component("stt", "process", start=True)
        transcription = stt.transcribe_audio(self.test_audio_path)
        self.perf_tracker.mark_component("stt", "process", start=False)

        # Check the transcription
        self.assertEqual(transcription, "What is the weather today?")

        # Step 2: LLM - Generate response
        self.perf_tracker.mark_component("llm", "generate", start=True)
        response = llm.generate_response(
            prompt=transcription,
            system_prompt="You are a helpful assistant."
        )
        self.perf_tracker.mark_component("llm", "generate", start=False)

        # Check the response
        self.assertEqual(response, "The weather today is sunny with a high of 75 degrees.")

        # Step 3: TTS - Synthesize speech
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            output_path = temp_file.name

        try:
            self.perf_tracker.mark_component("tts", "synthesize", start=True)
            audio_path = tts.synthesize(
                text=response,
                output_path=output_path
            )
            self.perf_tracker.mark_component("tts", "synthesize", start=False)

            # Check that the audio path is correct
            self.assertEqual(audio_path, output_path)

            # Mark the end of the pipeline
            self.perf_tracker.mark("pipeline_end")

            # Get the latency trace
            trace = self.perf_tracker.get_latency_trace()

            # Check that the trace contains the expected components
            self.assertIn("stt_seconds", trace)
            self.assertIn("llm_seconds", trace)
            self.assertIn("tts_seconds", trace)
            self.assertIn("total_processing_seconds", trace)

            # Check that the pipeline duration is reasonable
            pipeline_duration = self.perf_tracker.get_duration("pipeline_start", "pipeline_end")
            self.assertGreater(pipeline_duration, 0)

            # Check that all expected WebSocket events were emitted
            event_types = [event[0] for event in emitted_events]
            self.assertIn("stt_start", event_types)
            self.assertIn("stt_result", event_types)
            self.assertIn("llm_start", event_types)
            self.assertIn("llm_result", event_types)
            self.assertIn("tts_start", event_types)
            self.assertIn("tts_result", event_types)

            logger.info(f"Pipeline duration: {pipeline_duration:.3f}s")
            logger.info(f"STT duration: {trace['stt_seconds']:.3f}s")
            logger.info(f"LLM duration: {trace['llm_seconds']:.3f}s")
            logger.info(f"TTS duration: {trace['tts_seconds']:.3f}s")
            logger.info(f"Total processing duration: {trace['total_processing_seconds']:.3f}s")
            logger.info(f"WebSocket events emitted: {len(emitted_events)}")

        finally:
            # Clean up
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_tts_stop(self):
        """Test the TTS stop functionality."""
        # Call the speak method
        self.tts.speak("This is a test response that should be stopped.")

        # Verify TTS start event was emitted
        self.ws.tts_start.assert_called_once()

        # Now stop the TTS
        self.tts.stop()

        # Verify TTS stop event was emitted
        self.ws.tts_stop.assert_called_once()

    def tearDown(self):
        """Clean up after the tests."""
        # Clean up the test audio file
        if os.path.exists(self.test_audio_path):
            os.unlink(self.test_audio_path)


if __name__ == "__main__":
    unittest.main()
