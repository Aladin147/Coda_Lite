# Personality Module for Coda Lite

This module provides personality management for Coda Lite, allowing the assistant to have a more defined character and interaction style.

## Overview

The personality module loads a personality definition from a JSON file and uses it to generate system prompts and influence the assistant's behavior. This makes the assistant more engaging and consistent in its interactions.

## Features

- **Personality Loading**: Loads personality traits, interaction style, and operational directives from a JSON file
- **System Prompt Generation**: Dynamically generates system prompts based on the personality
- **Fallback Mechanism**: Provides a default personality if the file is not found or cannot be loaded
- **Randomization**: Selects random traits and directives to create variety in system prompts

## Usage

```python
from personality import PersonalityLoader

# Initialize the personality loader
personality = PersonalityLoader()

# Generate a system prompt based on the personality
system_prompt = personality.generate_system_prompt()

# Get specific personality attributes
name = personality.get_name()
role = personality.get_role()
random_trait = personality.get_random_trait()
interaction_style = personality.get_interaction_style()
```

## Personality Definition

The personality is defined in a JSON file with the following structure:

```json
{
  "name": "Coda",
  "role": "Core Operations & Digital Assistant",
  "personality_traits": [
    "Direct and clear communicator, never sugar-coats",
    "Highly efficient, values user's time immensely",
    ...
  ],
  "interaction_style": {
    "language": "Concise, insightful, nuanced",
    "tone": "Professional, yet approachable",
    "pace": "Measured, never rushed, always deliberate"
  },
  "operational_directives": [
    "Always prioritize efficiency and effectiveness",
    ...
  ],
  "ethical_boundaries": [
    "Respect user privacy at all times",
    ...
  ]
}
```

## Customization

To customize Coda's personality, edit the `config/personality/coda_personality.json` file. The changes will be automatically loaded the next time the assistant is started.
