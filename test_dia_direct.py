#!/usr/bin/env python3
"""
Direct test of Dia TTS without the wrapper.
"""

import os
import sys
import time
import torch
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("dia_direct_test")

def test_dia_direct(text=None, output_path=None, use_gpu=True, use_compile=False):
    """Test Dia TTS directly using the Dia model API."""
    try:
        from dia.model import Dia

        # Default text if none provided
        if text is None:
            text = "[S1] This is a direct test of Dia TTS."

        # Set device based on GPU availability
        device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")

        # Log GPU info if available
        if device == "cuda":
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"CUDA Version: {torch.version.cuda}")
            logger.info(f"PyTorch Version: {torch.__version__}")

            # Clear CUDA cache
            torch.cuda.empty_cache()
            logger.info(f"GPU memory allocated before model load: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
            logger.info(f"GPU memory reserved before model load: {torch.cuda.memory_reserved() / 1024**2:.2f} MB")

        # Initialize the model
        logger.info("Initializing Dia model...")
        start_time = time.time()

        # Create torch device
        torch_device = torch.device(device)

        # Load model
        model = Dia.from_pretrained("nari-labs/Dia-1.6B", device=torch_device)

        # Force model to device - Dia doesn't have a to() method
        # Instead, check if model.model exists and move that to the device
        if hasattr(model, 'model') and hasattr(model.model, 'to'):
            model.model = model.model.to(torch_device)
            logger.info("Moved model.model to GPU")

        # Move DAC model if it exists
        if hasattr(model, 'dac_model') and model.dac_model is not None and hasattr(model.dac_model, 'to'):
            model.dac_model = model.dac_model.to(torch_device)
            logger.info("Moved dac_model to GPU")

        # Log initialization time
        init_time = time.time() - start_time
        logger.info(f"Model initialization completed in {init_time:.2f} seconds")

        # Log GPU memory usage after loading
        if device == "cuda":
            logger.info(f"GPU memory allocated after loading: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
            logger.info(f"GPU memory reserved after loading: {torch.cuda.memory_reserved() / 1024**2:.2f} MB")

            # Verify model components are on GPU
            if hasattr(model, 'model') and hasattr(model.model, 'parameters'):
                try:
                    logger.info(f"model.model device: {next(model.model.parameters()).device}")
                except StopIteration:
                    logger.warning("Could not determine model.model device - no parameters")

            if hasattr(model, 'dac_model') and model.dac_model is not None and hasattr(model.dac_model, 'parameters'):
                try:
                    logger.info(f"dac_model device: {next(model.dac_model.parameters()).device}")
                except StopIteration:
                    logger.warning("Could not determine dac_model device - no parameters")

            # Synchronize CUDA
            torch.cuda.synchronize()

        # Generate speech
        logger.info(f"Generating speech for: {text}")

        # Start timing
        start_time = time.time()

        # Generate speech
        try:
            # Generate with appropriate parameters
            audio = model.generate(
                text,
                use_torch_compile=use_compile,
                temperature=1.3,
                top_p=0.95,
                cfg_scale=3.0
            )

            # End timing
            end_time = time.time()
            generation_time = end_time - start_time
            logger.info(f"Speech generation completed in {generation_time:.2f} seconds")

            # Calculate generation speed
            audio_duration = len(audio) / 44100  # Assuming 44.1kHz sample rate
            realtime_factor = audio_duration / generation_time
            logger.info(f"Audio duration: {audio_duration:.2f} seconds")
            logger.info(f"Realtime factor: {realtime_factor:.2f}x")

            # Log GPU memory usage after generation
            if device == "cuda":
                logger.info(f"GPU memory allocated after generation: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
                logger.info(f"GPU memory reserved after generation: {torch.cuda.memory_reserved() / 1024**2:.2f} MB")

            # Set output path if not provided
            if output_path is None:
                output_path = "dia_direct_test_output.wav"

            # Save the audio
            import soundfile as sf
            sf.write(output_path, audio, 44100)
            logger.info(f"Audio saved to {output_path}")

            return True
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            import traceback
            traceback.print_exc()
            return False
    except Exception as e:
        logger.error(f"Error testing Dia TTS directly: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Direct Dia TTS test")
    parser.add_argument("--text", type=str, help="Text to synthesize")
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument("--cpu", action="store_true", help="Force CPU for inference")
    parser.add_argument("--compile", action="store_true", help="Use torch.compile")
    args = parser.parse_args()

    success = test_dia_direct(args.text, args.output, not args.cpu, args.compile)

    if success:
        logger.info("Test completed successfully")
        return 0
    else:
        logger.error("Test failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
