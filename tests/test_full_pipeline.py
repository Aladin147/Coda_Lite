"""
Comprehensive tests for the full STT-LLM-TTS pipeline.

This module provides tests for the complete processing pipeline:
1. Speech-to-Text (STT)
2. Language Model (LLM)
3. Text-to-Speech (TTS)

It includes both unit tests for individual components and integration tests
for the full pipeline.
"""

import os
import time
import unittest
import logging
import tempfile
from unittest.mock import MagicMock, patch

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("coda.tests.full_pipeline")

# Import the components to test
from stt.whisper_stt import WhisperSTT
from llm.ollama_llm import OllamaLLM
# Import ElevenLabsTTS directly to avoid importing CSM TTS which has MeCab dependency
import sys
import os

# Add the tts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "tts"))

# Import directly from the module
from elevenlabs_tts import ElevenLabsTTS

# Mock the factory functions
def get_tts_instance(tts_type, websocket_integration=None, config=None, **kwargs):
    """Mock get_tts_instance function."""
    if websocket_integration:
        from websocket_elevenlabs_tts import WebSocketElevenLabsTTS
        return WebSocketElevenLabsTTS(
            websocket_integration=websocket_integration,
            api_key=kwargs.get("api_key", "test_key"),
            voice_id=kwargs.get("voice_id", "test_voice"),
            **kwargs
        )
    else:
        return ElevenLabsTTS(
            api_key=kwargs.get("api_key", "test_key"),
            voice_id=kwargs.get("voice_id", "test_voice"),
            **kwargs
        )

def unload_current_tts():
    """Mock unload_current_tts function."""
    pass
from utils.perf_tracker import PerfTracker
from websocket.integration import CodaWebSocketIntegration


class TestFullPipeline(unittest.TestCase):
    """Test cases for the full STT-LLM-TTS pipeline."""

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

        # Create the STT, LLM, and TTS instances
        self.stt = WhisperSTT(model_size="tiny", device="cpu")
        self.llm = OllamaLLM(model_name="llama3", host="http://localhost:11434")
        self.tts = ElevenLabsTTS(api_key="test_key", voice_id="test_voice")

        # Create a test audio file path
        self.test_audio_path = os.path.join(os.path.dirname(__file__), "data", "test_audio.wav")

        # Create a directory for test data if it doesn't exist
        os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)

        # Create a test audio file if it doesn't exist
        if not os.path.exists(self.test_audio_path):
            with open(self.test_audio_path, "wb") as f:
                f.write(b"test_audio_data")

    def test_stt_component(self):
        """Test the STT component in isolation."""
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

        # Verify the model was called with the correct parameters
        self.mock_stt_model.transcribe.assert_called_once()

    def test_llm_component(self):
        """Test the LLM component in isolation."""
        # Call the generate_response method
        result = self.llm.generate_response(
            prompt="What is the weather today?",
            system_prompt="You are a helpful assistant."
        )

        # Check the result
        self.assertEqual(result, "This is a test response from the LLM.")

    def test_tts_component(self):
        """Test the TTS component in isolation."""
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

            # Check that the file exists
            self.assertTrue(os.path.exists(output_path))
        finally:
            # Clean up
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_tts_factory(self):
        """Test the TTS factory with lazy loading."""
        # Get a TTS instance
        tts = get_tts_instance(
            tts_type="elevenlabs",
            websocket_integration=self.ws,
            config={"tts.elevenlabs_api_key": "test_key", "tts.elevenlabs_voice_id": "test_voice"}
        )

        # Check that the instance is of the correct type
        self.assertIsNotNone(tts)
        self.assertEqual(tts.__class__.__name__, "WebSocketElevenLabsTTS")

        # Unload the TTS instance
        unload_current_tts()

    @patch('stt.whisper_stt.WhisperModel')
    @patch('llm.ollama_llm.requests')
    @patch('tts.elevenlabs_tts.requests')
    def test_full_pipeline(self, mock_tts_requests, mock_llm_requests, mock_whisper_model):
        """Test the full STT-LLM-TTS pipeline."""
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

        # Create the components
        stt = WhisperSTT(model_size="tiny", device="cpu")
        llm = OllamaLLM(model_name="llama3", host="http://localhost:11434")
        tts = ElevenLabsTTS(api_key="test_key", voice_id="test_voice")

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

            # Check that the file exists
            self.assertTrue(os.path.exists(output_path))

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

            logger.info(f"Pipeline duration: {pipeline_duration:.3f}s")
            logger.info(f"STT duration: {trace['stt_seconds']:.3f}s")
            logger.info(f"LLM duration: {trace['llm_seconds']:.3f}s")
            logger.info(f"TTS duration: {trace['tts_seconds']:.3f}s")
            logger.info(f"Total processing duration: {trace['total_processing_seconds']:.3f}s")

        finally:
            # Clean up
            if os.path.exists(output_path):
                os.unlink(output_path)

    def tearDown(self):
        """Clean up after the tests."""
        # Clean up the test audio file
        if os.path.exists(self.test_audio_path):
            os.unlink(self.test_audio_path)


if __name__ == "__main__":
    unittest.main()
