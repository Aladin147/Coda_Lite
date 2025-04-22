# Enhanced Personality Engine

This document describes the Enhanced Personality Engine in Coda Lite v0.1.2.

## Overview

The Enhanced Personality Engine provides a more sophisticated and flexible personality system for Coda, with features like context-aware traits, adaptive tone switching, personality quirks, and session metadata injection.

## Features

### 1. Weighted Personality Traits with Context Awareness

Traits are now defined with weights and context tags, allowing Coda to adapt her personality based on the conversation context:

```json
{
  "trait": "Direct and clear communicator",
  "strength": 0.9,
  "contexts": ["default", "tool_call", "information"],
  "examples": ["Here's what you need to know, without the fluff."]
}
```

- **Trait**: The personality trait description
- **Strength**: A value between 0.0 and 1.0 indicating how strongly this trait should be expressed
- **Contexts**: A list of contexts where this trait is appropriate
- **Examples**: Example phrases that demonstrate this trait

### 2. Adaptive Tone Switching

Coda can now adapt her tone based on the conversation context:

```json
"tones": {
  "default": "professional yet conversational",
  "tool_call": "concise and direct",
  "information": "clear and informative",
  "casual": "relaxed and friendly",
  "entertainment": "playful and engaging",
  "error": "calm and constructive",
  "formal": "polished and professional",
  "emergency": "calm and authoritative"
}
```

The system automatically detects the appropriate context from user input and selects the corresponding tone.

### 3. Separation of Personality and Functional Prompts

Prompt templates are now stored separately from the personality definition, making it easier to maintain and update them:

```
config/prompts/templates/
├── default.txt
├── tool_detection.txt
├── summarization.txt
```

This separation allows for more focused and efficient prompts, reducing token usage and improving response quality.

### 4. Personality Quirks and Signature Behaviors

Coda now has quirks that give her a more memorable and distinctive personality:

```json
{
  "quirk": "Poetic about time",
  "trigger": "time",
  "frequency": 0.3,
  "examples": [
    "It's 3:04 — or as I call it, digital tea time.",
    "The clock says {{time}}, but time is just an illusion... a very precise illusion."
  ]
}
```

- **Quirk**: The quirk description
- **Trigger**: The word or phrase that triggers this quirk
- **Frequency**: How often this quirk should be expressed (0.0 to 1.0)
- **Examples**: Example phrases that demonstrate this quirk

### 5. Session Metadata Injection

Coda is now aware of session context, which is injected into the system prompt:

```
Current session information:
- User: aladin
- Device: Windows 10
- Session started: 2025-04-24 09:15:23
- Session duration: 45 minutes
- Current time: 10:00
```

This makes Coda more aware of her operational context and allows for more personalized interactions.

### 6. Live Reloading Capability

The personality configuration can now be reloaded without restarting the application, making it easier to iterate on personality tuning:

```python
personality.reload()
```

## Context Types

The Enhanced Personality Engine supports the following context types:

- **default**: The default context for general conversation
- **tool_call**: When Coda needs to use a tool
- **information**: When providing factual information
- **casual**: For casual, friendly conversation
- **entertainment**: For jokes, stories, and other entertainment
- **error**: When handling errors or problems
- **formal**: For more formal or professional interactions
- **emergency**: For urgent or critical situations

## Implementation Details

### EnhancedPersonalityLoader Class

The `EnhancedPersonalityLoader` class provides the following methods:

- **get_traits_for_context(context_type)**: Get traits appropriate for the given context
- **get_tone(context_type)**: Get the appropriate tone for the given context
- **get_quirk_for_trigger(trigger)**: Get a quirk that matches the given trigger
- **apply_quirk(response)**: Apply appropriate quirks to the response
- **detect_context(user_input)**: Detect the context type based on user input
- **generate_system_prompt(context_type)**: Generate a system prompt based on the personality and context
- **reload()**: Reload the personality and templates

### Personality Configuration

The personality configuration is stored in a JSON file:

```
config/personality/coda_personality_enhanced.json
```

This file contains the personality traits, tones, quirks, interaction style, operational directives, and ethical boundaries.

## Usage Examples

### Generating a System Prompt

```python
from personality import EnhancedPersonalityLoader

# Create an instance of the enhanced personality loader
personality = EnhancedPersonalityLoader()

# Generate a system prompt for the default context
prompt = personality.generate_system_prompt("default")
```

### Detecting Context from User Input

```python
# Detect the context from user input
user_input = "What time is it?"
context = personality.detect_context(user_input)  # Returns "tool_call"
```

### Applying Quirks to Responses

```python
# Apply quirks to a response
response = "It's 3:45 PM."
quirky_response = personality.apply_quirk(response)  # Might return "It's 3:45 PM — or as I call it, digital tea time."
```

## Testing

A test script is provided to verify the Enhanced Personality Engine functionality:

```
python tests/test_enhanced_personality.py
```

This script tests basic functionality, tone switching, quirks, prompt generation, context detection, and live reloading.
