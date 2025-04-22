# Enhanced Personality Features

This document describes the Enhanced Personality Features in Coda Lite v0.1.3.

## Overview

The Enhanced Personality Features build upon the Enhanced Personality Engine to provide a more sophisticated, dynamic, and human-like personality for Coda. These features include refined output styling, dynamic memory hint injection, emotional responsiveness, and session-level personality drift.

## Features

### 1. Refined Output Styling

Coda now has consistent output styling across all responses, ensuring a coherent voice and personality:

```python
def format_response(self, response, response_type=None, user_emotion="neutral", context_type="default"):
    # Apply response templates if specified
    if response_type and response_type in self.personality.get("response_templates", {}):
        templates = self.personality.get("response_templates", {}).get(response_type, [])
        if templates:
            template = random.choice(templates)
            # Apply template...
    
    # Apply emotional responses if enabled
    # Apply quirks
    # Apply general styling rules
    
    return response
```

Response templates are defined in the personality configuration:

```json
"response_templates": {
  "greeting": ["Hello!", "Hi there!", "Hey!", "Greetings!"],
  "confirmation": ["Got it.", "I understand.", "Noted.", "All set.", "Done."],
  "refusal": ["I'm afraid I can't do that.", "That's not something I can help with."],
  "farewell": ["Let me know if you need anything else.", "Happy to help anytime."]
}
```

### 2. Dynamic Memory Hint Injection

Coda now uses memory hints from previous conversations to provide more context-aware responses:

```python
def extract_memory_hint(self, memory_manager, max_hints=1):
    hints = []
    
    # Get recent topics from memory
    if hasattr(memory_manager, 'get_recent_topics'):
        recent_topics = memory_manager.get_recent_topics(limit=3)
        if recent_topics:
            hints.append(f"The user recently asked about {', '.join(recent_topics)}.")
    
    # Get last used tool
    if hasattr(memory_manager, 'get_last_tool_used'):
        last_tool = memory_manager.get_last_tool_used()
        if last_tool:
            hints.append(f"You recently used the {last_tool} tool to help the user.")
    
    # More memory hints...
    
    return hints[:max_hints]
```

These hints are injected into the system prompt:

```
Recent context:
- The user recently asked about weather, time, jokes.
- You recently used the get_time tool to help the user.
```

### 3. Emotional Responsiveness

Coda can now detect and respond to the user's emotional state:

```python
def detect_emotion(self, text):
    # Simple keyword-based approach
    emotions = {
        "positive": ["happy", "great", "excellent", "good", "love", "like", "thanks"],
        "negative": ["sad", "bad", "terrible", "hate", "dislike", "frustrated", "angry"],
        "surprise": ["wow", "whoa", "oh", "really", "seriously", "unexpected"],
        "neutral": []
    }
    
    text_lower = text.lower()
    
    for emotion, keywords in emotions.items():
        if any(keyword in text_lower for keyword in keywords):
            return emotion
    
    return "neutral"
```

Emotional responses are defined in the personality configuration:

```json
"emotional_responses": {
  "positive": ["That's great!", "Excellent!", "Nice!", "Wonderful!", "Perfect!"],
  "negative": ["I understand that's frustrating.", "Sorry to hear that.", "That sounds challenging."],
  "surprise": ["Oh!", "Interesting!", "Wow!", "I didn't expect that!", "That's surprising!"],
  "neutral": ["I see.", "Understood.", "Noted.", "Alright.", "Fair enough."]
}
```

The intensity of emotional responses can be configured:

```python
def set_emotion_mode(self, mode="lite"):
    if mode in ["off", "lite", "full"]:
        self.emotion_mode = mode
        logger.info(f"Emotion mode set to: {mode}")
    else:
        logger.warning(f"Invalid emotion mode: {mode}. Using default: lite")
        self.emotion_mode = "lite"
```

### 4. Session-Level Personality Drift

Coda's personality can now evolve during a session based on the nature of the conversation:

```python
def update_mood(self, user_input, context_type):
    # Track the last 10 interactions
    self.mood_history.append({
        "input": user_input,
        "context": context_type
    })
    if len(self.mood_history) > 10:
        self.mood_history.pop(0)
    
    # Adjust weights based on context types
    playful_contexts = ["casual", "entertainment"]
    professional_contexts = ["formal", "information", "tool_call"]
    
    # Count recent contexts
    playful_count = sum(1 for item in self.mood_history if item["context"] in playful_contexts)
    professional_count = sum(1 for item in self.mood_history if item["context"] in professional_contexts)
    
    # Adjust weights (with damping to prevent wild swings)
    total = len(self.mood_history)
    if total > 0:
        self.mood_weights["playful"] = 0.3 + (0.7 * playful_count / total)
        self.mood_weights["professional"] = 0.3 + (0.7 * professional_count / total)
        
        # Normalize to ensure they sum to 1.0
        total_weight = sum(self.mood_weights.values())
        for mood in self.mood_weights:
            self.mood_weights[mood] /= total_weight
```

These mood weights are applied to trait selection:

```python
def get_traits_for_context(self, context_type="default", max_traits=5):
    # Filter traits by context
    matching_traits = [...]
    
    # Apply mood weighting to trait selection
    professional_traits = ["Direct and clear communicator", "Thoughtful and precise", "Professional but approachable"]
    playful_traits = ["Balanced humor", "Relaxed when appropriate", "Dry wit"]
    
    # Create a copy of the traits with adjusted strengths
    weighted_traits = []
    for trait in matching_traits:
        trait_copy = trait.copy()
        trait_name = trait_copy.get("trait", "")
        
        # Apply mood weights to trait strength
        if trait_name in professional_traits:
            adjusted_strength = trait_copy.get("strength", 0.5) * self.mood_weights.get("professional", 0.5)
        elif trait_name in playful_traits:
            adjusted_strength = trait_copy.get("strength", 0.5) * self.mood_weights.get("playful", 0.5)
        else:
            adjusted_strength = trait_copy.get("strength", 0.5)
            
        trait_copy["adjusted_strength"] = adjusted_strength
        weighted_traits.append(trait_copy)
    
    # Sort by adjusted strength (descending)
    sorted_traits = sorted(
        weighted_traits, 
        key=lambda x: x.get("adjusted_strength", x.get("strength", 0.0)), 
        reverse=True
    )
    
    return sorted_traits[:max_traits]
```

## Implementation Details

### EnhancedPersonalityLoader Class

The `EnhancedPersonalityLoader` class has been extended with the following methods:

- **format_response(response, response_type, user_emotion, context_type)**: Format the response according to templates, style guidelines, and emotional context
- **_apply_styling_rules(response)**: Apply general styling rules to the response
- **extract_memory_hint(memory_manager, max_hints)**: Extract relevant hints from memory to inject into prompts
- **set_emotion_mode(mode)**: Set the emotional responsiveness mode
- **update_mood(user_input, context_type)**: Update mood weights based on user interaction
- **detect_emotion(text)**: Detect the emotional tone of text

### Personality Configuration

The personality configuration has been extended with the following sections:

```json
"response_templates": {
  "greeting": [...],
  "confirmation": [...],
  "refusal": [...],
  "farewell": [...],
  "error": [...],
  "thinking": [...],
  "signature": [...]
},
"emotional_responses": {
  "positive": [...],
  "negative": [...],
  "surprise": [...],
  "neutral": [...]
}
```

### Prompt Templates

The prompt templates have been updated to include placeholders for memory hints and output styling:

```
{{memory_hints}}
{{output_styling}}
```

## Usage Examples

### Formatting Responses

```python
from personality import EnhancedPersonalityLoader

# Create an instance of the enhanced personality loader
personality = EnhancedPersonalityLoader()

# Format a response
response = "I've found the information you requested."
formatted = personality.format_response(
    response,
    response_type="confirmation",
    user_emotion="positive",
    context_type="information"
)
```

### Detecting Emotion from User Input

```python
# Detect emotion from user input
user_input = "Thanks for your help, I appreciate it."
emotion = personality.detect_emotion(user_input)  # Returns "positive"
```

### Generating a System Prompt with Memory Hints

```python
# Generate a system prompt with memory hints
prompt = personality.generate_system_prompt("default", memory_manager)
```

### Updating Mood Based on Interactions

```python
# Update mood based on user interaction
personality.update_mood("Tell me a joke", "entertainment")
```

## Testing

A test script is provided to verify the Enhanced Personality Features functionality:

```
python tests/test_enhanced_personality_features.py
```

This script tests response formatting, emotional responses, memory hint extraction, prompt generation with memory hints, emotion detection, and mood tracking.
