#!/usr/bin/env python3
"""
Test script for the personality module.
"""

import os
import sys
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

logger = logging.getLogger("personality_test")

from personality import PersonalityLoader

def main():
    """Test the personality module."""
    try:
        print("=" * 50)
        print("Coda Lite Personality Test")
        print("=" * 50)
        
        # Initialize the personality loader
        print("\nInitializing personality loader...")
        personality = PersonalityLoader()
        
        # Get basic information
        name = personality.get_name()
        role = personality.get_role()
        
        print(f"\nName: {name}")
        print(f"Role: {role}")
        
        # Get personality traits
        print("\nPersonality Traits:")
        traits = personality.personality.get("personality_traits", [])
        for i, trait in enumerate(traits, 1):
            print(f"  {i}. {trait}")
        
        # Get interaction style
        print("\nInteraction Style:")
        style = personality.get_interaction_style()
        for key, value in style.items():
            print(f"  {key.capitalize()}: {value}")
        
        # Get operational directives
        print("\nOperational Directives:")
        directives = personality.get_operational_directives()
        for i, directive in enumerate(directives, 1):
            print(f"  {i}. {directive}")
        
        # Get ethical boundaries
        print("\nEthical Boundaries:")
        boundaries = personality.get_ethical_boundaries()
        for i, boundary in enumerate(boundaries, 1):
            print(f"  {i}. {boundary}")
        
        # Generate system prompt
        print("\nGenerated System Prompt:")
        print("-" * 50)
        system_prompt = personality.generate_system_prompt()
        print(system_prompt)
        print("-" * 50)
        
        # Generate multiple system prompts to show variety
        print("\nMultiple System Prompts (showing variety):")
        for i in range(3):
            print(f"\nSystem Prompt {i+1}:")
            print("-" * 30)
            system_prompt = personality.generate_system_prompt()
            # Print just the first few lines to show the difference
            print("\n".join(system_prompt.split("\n")[:10]) + "\n...")
            print("-" * 30)
        
        print("\nTest completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
