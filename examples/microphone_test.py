#!/usr/bin/env python3
"""
Test script for microphone input with WhisperSTT.
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("microphone_test")

from stt import WhisperSTT
import pyaudio
import torch

def list_audio_devices():
    """List all available audio devices."""
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    
    print("\nAudio Devices:")
    print("-------------")
    
    input_devices = []
    output_devices = []
    
    for i in range(num_devices):
        device_info = p.get_device_info_by_index(i)
        device_name = device_info.get('name')
        max_input_channels = device_info.get('maxInputChannels')
        max_output_channels = device_info.get('maxOutputChannels')
        
        if max_input_channels > 0:
            input_devices.append((i, device_name))
            print(f"Input Device {i}: {device_name}")
        
        if max_output_channels > 0:
            output_devices.append((i, device_name))
    
    p.terminate()
    
    return input_devices, output_devices

def test_microphone(device_index=None, duration=5):
    """Test microphone recording."""
    p = pyaudio.PyAudio()
    
    if device_index is None:
        device_index = p.get_default_input_device_info()['index']
        print(f"Using default input device: {p.get_device_info_by_index(device_index)['name']}")
    else:
        print(f"Using selected input device: {p.get_device_info_by_index(device_index)['name']}")
    
    # Set up audio parameters
    format = pyaudio.paInt16
    channels = 1
    rate = 16000
    chunk = 1024
    
    # Open audio stream
    stream = p.open(
        format=format,
        channels=channels,
        rate=rate,
        input=True,
        input_device_index=device_index,
        frames_per_buffer=chunk
    )
    
    print(f"\nRecording for {duration} seconds...")
    
    # Record audio
    frames = []
    for i in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
    
    print("Recording finished")
    
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Save the recording to a temporary file
    temp_file = "temp_recording.wav"
    import wave
    wf = wave.open(temp_file, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    print(f"Recording saved to {temp_file}")
    
    return temp_file

def main():
    """Test microphone input with WhisperSTT."""
    try:
        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        if device == "cuda":
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"CUDA version: {torch.version.cuda}")
        
        # List audio devices
        input_devices, _ = list_audio_devices()
        
        # Ask user to select a device
        device_index = None
        if input_devices:
            try:
                selection = input("\nEnter the device number to use (or press Enter for default): ")
                if selection.strip():
                    device_index = int(selection)
            except ValueError:
                print("Invalid selection, using default device")
        
        # Test microphone recording
        audio_file = test_microphone(device_index)
        
        # Initialize the WhisperSTT module
        print("\nInitializing WhisperSTT...")
        stt = WhisperSTT(
            model_size="base",
            device=device,
            compute_type="float16" if device == "cuda" else "float32",
            language="en",
            vad_filter=True
        )
        
        # Transcribe the recording
        print("\nTranscribing recording...")
        start_time = time.time()
        transcription = stt.transcribe_audio(audio_file)
        end_time = time.time()
        
        print(f"\nTranscription completed in {end_time - start_time:.2f} seconds")
        print(f"Transcription: {transcription}")
        
        # Test continuous listening
        print("\nTesting continuous listening (30 seconds)...")
        print("Speak naturally, pausing between phrases.")
        print("Press Ctrl+C to stop earlier.")
        
        # Set up a callback to handle transcriptions
        def handle_transcription(text):
            print(f"Transcription: {text}")
        
        # Set up a stop callback to limit the duration
        start_time = time.time()
        def should_stop():
            return time.time() - start_time > 30
        
        try:
            # Start continuous listening
            stt.listen_continuous(
                callback=handle_transcription,
                stop_callback=should_stop,
                silence_threshold=0.1,
                silence_duration=1.0,
            )
        except KeyboardInterrupt:
            print("\nStopped by user")
        
        # Clean up
        stt.close()
        
        # Clean up temporary file
        if os.path.exists(audio_file):
            os.remove(audio_file)
        
        print("\nTest completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
