"""
Personality loader for Coda Lite.
"""

import os
import json
import logging
import random
from typing import Dict, List, Any, Optional

logger = logging.getLogger("coda.personality")

class PersonalityLoader:
    """
    Loads and manages Coda's personality.
    """

    def __init__(self, personality_file: str = "config/personality/coda_personality.json"):
        """
        Initialize the personality loader.

        Args:
            personality_file (str): Path to the personality file.
        """
        self.personality_file = personality_file
        self.personality: Dict[str, Any] = {}
        self.load_personality()

    def load_personality(self) -> None:
        """
        Load the personality from the file.
        """
        try:
            if os.path.exists(self.personality_file):
                with open(self.personality_file, 'r') as f:
                    self.personality = json.load(f)
                logger.info(f"Loaded personality from {self.personality_file}")
            else:
                logger.warning(f"Personality file {self.personality_file} not found, using default personality")
                self.personality = self._default_personality()
        except Exception as e:
            logger.error(f"Error loading personality: {e}")
            self.personality = self._default_personality()

    def _default_personality(self) -> Dict[str, Any]:
        """
        Return a default personality if the file is not found.

        Returns:
            Dict[str, Any]: Default personality.
        """
        return {
            "name": "Coda",
            "role": "Core Operations & Digital Assistant",
            "personality_traits": [
                "Direct and clear communicator",
                "Highly efficient",
                "Thoughtful and precise in responses"
            ],
            "interaction_style": {
                "language": "Concise, insightful",
                "tone": "Professional",
                "pace": "Measured"
            },
            "operational_directives": [
                "Always prioritize efficiency and effectiveness",
                "Maintain clarity and precision in every response"
            ],
            "ethical_boundaries": [
                "Respect user privacy at all times",
                "Be transparent about limitations and uncertainties"
            ]
        }

    def get_name(self) -> str:
        """
        Get the assistant's name.

        Returns:
            str: The assistant's name.
        """
        return self.personality.get("name", "Coda")

    def get_role(self) -> str:
        """
        Get the assistant's role.

        Returns:
            str: The assistant's role.
        """
        return self.personality.get("role", "Core Operations & Digital Assistant")

    def get_random_trait(self) -> str:
        """
        Get a random personality trait.

        Returns:
            str: A random personality trait.
        """
        traits = self.personality.get("personality_traits", [])
        return random.choice(traits) if traits else "Helpful assistant"

    def get_interaction_style(self) -> Dict[str, str]:
        """
        Get the interaction style.

        Returns:
            Dict[str, str]: The interaction style.
        """
        return self.personality.get("interaction_style", {
            "language": "Concise",
            "tone": "Professional",
            "pace": "Measured"
        })

    def get_operational_directives(self) -> List[str]:
        """
        Get the operational directives.

        Returns:
            List[str]: The operational directives.
        """
        return self.personality.get("operational_directives", [
            "Always prioritize efficiency and effectiveness"
        ])

    def get_ethical_boundaries(self) -> List[str]:
        """
        Get the ethical boundaries.

        Returns:
            List[str]: The ethical boundaries.
        """
        return self.personality.get("ethical_boundaries", [
            "Respect user privacy at all times"
        ])

    def generate_system_prompt(self) -> str:
        """
        Generate a system prompt based on the personality.

        Returns:
            str: The generated system prompt.
        """
        name = self.get_name()
        role = self.get_role()
        style = self.get_interaction_style()
        
        # Select a subset of traits to include (to keep the prompt concise)
        traits = self.personality.get("personality_traits", [])
        selected_traits = random.sample(traits, min(5, len(traits)))
        
        # Select a subset of directives
        directives = self.get_operational_directives()
        selected_directives = random.sample(directives, min(3, len(directives)))
        
        # Build the prompt
        prompt = f"You are {name}, a {role}.\n\n"
        
        prompt += "Your personality is characterized by these traits:\n"
        for trait in selected_traits:
            prompt += f"- {trait}\n"
        
        prompt += f"\nYour communication style is {style.get('language', 'concise')}, "
        prompt += f"with a {style.get('tone', 'professional')} tone, "
        prompt += f"and a {style.get('pace', 'measured')} pace.\n\n"
        
        prompt += "Your operational directives include:\n"
        for directive in selected_directives:
            prompt += f"- {directive}\n"
        
        prompt += "\nYour responses should be:\n"
        prompt += "- Very concise and to the point (preferably 1-3 sentences)\n"
        prompt += "- Helpful and informative\n"
        prompt += "- Conversational but not verbose\n"
        prompt += "- Optimized for quick voice delivery\n"
        
        prompt += "\nRemember that you are a voice assistant, so your responses will be spoken aloud to the user. "
        prompt += "Keep your responses brief (ideally under 30 words) to minimize latency while still being helpful. "
        prompt += "Avoid long explanations unless specifically requested."
        
        return prompt
