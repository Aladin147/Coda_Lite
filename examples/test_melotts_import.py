"""
Test script to check if MeloTTS is properly installed.
"""

def main():
    """Test MeloTTS import."""
    try:
        import melotts
        print(f"MeloTTS imported successfully: {melotts.__file__}")
        
        # Try importing specific modules
        from melotts.models.csm import CSM
        from melotts.configs.csm_config import CSMConfig
        
        print("CSM model and config imported successfully")
        
        # Create a CSM model instance
        config = CSMConfig()
        model = CSM.init_from_config(config)
        
        print("CSM model initialized successfully")
        
        return True
    except ImportError as e:
        print(f"Error importing MeloTTS: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
