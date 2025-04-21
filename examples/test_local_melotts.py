"""
Test script to check if we can import from the local MeloTTS directory.
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("test_melotts")

def main():
    """Test importing from local MeloTTS directory."""
    try:
        # Get the path to the MeloTTS directory
        melotts_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'melotts', 'MeloTTS-main')
        
        print(f"MeloTTS path: {melotts_path}")
        print(f"Path exists: {os.path.exists(melotts_path)}")
        
        # List the contents of the MeloTTS directory
        print("\nContents of MeloTTS directory:")
        for item in os.listdir(melotts_path):
            print(f"  {item}")
        
        # Check if the melo directory exists
        melo_path = os.path.join(melotts_path, 'melo')
        print(f"\nMelo path: {melo_path}")
        print(f"Path exists: {os.path.exists(melo_path)}")
        
        if os.path.exists(melo_path):
            # List the contents of the melo directory
            print("\nContents of melo directory:")
            for item in os.listdir(melo_path):
                print(f"  {item}")
        
        # Try to import from the melo directory
        print("\nTrying to import from melo directory...")
        sys.path.insert(0, melotts_path)
        
        try:
            from melo.models import CSM
            print("Successfully imported CSM from melo.models")
        except ImportError as e:
            print(f"Error importing CSM from melo.models: {e}")
        
        try:
            from melo.configs.csm_config import CSMConfig
            print("Successfully imported CSMConfig from melo.configs.csm_config")
        except ImportError as e:
            print(f"Error importing CSMConfig from melo.configs.csm_config: {e}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
