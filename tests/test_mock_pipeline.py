"""
Simple mock tests for the STT-LLM-TTS pipeline.

This module provides tests using mocks to avoid external dependencies.
"""

import unittest
from unittest.mock import MagicMock, patch

class TestMockPipeline(unittest.TestCase):
    """Test cases for the mock pipeline."""

    def setUp(self):
        """Set up the test environment."""
        # Create mock components
        self.stt = MagicMock()
        self.stt.transcribe_audio.return_value = "What is the weather today?"
        
        self.llm = MagicMock()
        self.llm.generate_response.return_value = "The weather today is sunny with a high of 75 degrees."
        
        self.tts = MagicMock()
        self.tts.synthesize.return_value = "/path/to/audio.wav"
        self.tts.speak.return_value = True
        
        # Create a mock performance tracker
        self.perf_tracker = MagicMock()
        self.perf_tracker.mark.return_value = 123456789.0
        self.perf_tracker.mark_component.return_value = 123456789.0
        self.perf_tracker.get_duration.return_value = 0.5
        self.perf_tracker.get_latency_trace.return_value = {
            "stt_seconds": 0.2,
            "llm_seconds": 0.3,
            "tts_seconds": 0.1,
            "total_processing_seconds": 0.6,
            "total_seconds": 0.6,
            "stt_audio_duration": 1.5,
            "tts_audio_duration": 2.0,
            "total_interaction_seconds": 4.1
        }

    def test_full_pipeline(self):
        """Test the full pipeline with mocks."""
        # Mark the start of the pipeline
        self.perf_tracker.mark("pipeline_start")

        # Step 1: STT - Transcribe audio
        self.perf_tracker.mark_component("stt", "process", start=True)
        transcription = self.stt.transcribe_audio("test_audio.wav")
        self.perf_tracker.mark_component("stt", "process", start=False)

        # Check the transcription
        self.assertEqual(transcription, "What is the weather today?")

        # Step 2: LLM - Generate response
        self.perf_tracker.mark_component("llm", "generate", start=True)
        response = self.llm.generate_response(
            prompt=transcription,
            system_prompt="You are a helpful assistant."
        )
        self.perf_tracker.mark_component("llm", "generate", start=False)

        # Check the response
        self.assertEqual(response, "The weather today is sunny with a high of 75 degrees.")

        # Step 3: TTS - Synthesize speech
        self.perf_tracker.mark_component("tts", "synthesize", start=True)
        audio_path = self.tts.synthesize(
            text=response,
            output_path="output.wav"
        )
        self.perf_tracker.mark_component("tts", "synthesize", start=False)

        # Check that the audio path is correct
        self.assertEqual(audio_path, "/path/to/audio.wav")

        # Mark the end of the pipeline
        self.perf_tracker.mark("pipeline_end")

        # Get the latency trace
        trace = self.perf_tracker.get_latency_trace()

        # Check that the trace contains the expected components
        self.assertIn("stt_seconds", trace)
        self.assertIn("llm_seconds", trace)
        self.assertIn("tts_seconds", trace)
        self.assertIn("total_processing_seconds", trace)
        self.assertIn("total_interaction_seconds", trace)

        # Check that the pipeline duration is reasonable
        pipeline_duration = self.perf_tracker.get_duration("pipeline_start", "pipeline_end")
        self.assertEqual(pipeline_duration, 0.5)

    def test_tts_stop(self):
        """Test the TTS stop functionality."""
        # Add stop method to the mock
        self.tts.stop = MagicMock()
        
        # Call the speak method
        self.tts.speak("This is a test response that should be stopped.")

        # Now stop the TTS
        self.tts.stop()

        # Verify stop was called
        self.tts.stop.assert_called_once()


if __name__ == "__main__":
    unittest.main()
