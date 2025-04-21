"""
Example script to test CSM-1B TTS directly using MeloTTS.
"""

import os
import sys
import logging
import tempfile

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("csm_direct")

def main():
    """Test CSM-1B TTS directly."""
    try:
        import torch
        import torchaudio
        from melotts.models.csm import CSM
        from melotts.configs.csm_config import CSMConfig
        
        print("Initializing CSM-1B TTS...")
        
        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        # Initialize the CSM model
        config = CSMConfig()
        model = CSM.init_from_config(config)
        model.load_checkpoint(config, checkpoint_path=None)
        model.to(device)
        
        # Test text
        text = "Hello, I am Coda. I'm now speaking with CSM-1B, a high-quality text-to-speech model."
        
        print(f"Synthesizing: {text}")
        
        # Generate speech
        wav = model.inference(text, language="en")
        
        # Save to temporary file
        temp_file = os.path.join(tempfile.gettempdir(), "coda_csm_test.wav")
        torchaudio.save(temp_file, torch.tensor(wav).unsqueeze(0), 22050)
        
        print(f"Audio saved to: {temp_file}")
        
        # Play the audio
        try:
            import simpleaudio as sa
            wave_obj = sa.WaveObject.from_wave_file(temp_file)
            play_obj = wave_obj.play()
            play_obj.wait_done()
            print("Audio playback completed")
        except Exception as e:
            print(f"Error playing audio: {e}")
        
        print("Done!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
