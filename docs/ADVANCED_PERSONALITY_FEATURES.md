# Advanced Personality Features

This document describes the Advanced Personality Features in Coda Lite v0.1.5.

## Overview

The Advanced Personality Features build upon the Enhanced Personality Engine to provide a more sophisticated, adaptive, and human-like personality for Coda. These features include behavioral conditioning, topic awareness, session management, and configurable personality parameters.

## Architecture

The Advanced Personality Features are implemented using a layered architecture:

1. **Personality Parameters Layer**: Foundation layer for configurable personality parameters
2. **Behavioral Conditioning Layer**: Tracks and adapts to user behavior patterns
3. **Topic Awareness Layer**: Detects and responds to conversation topics
4. **Session Management Layer**: Manages session state and closure
5. **Advanced Personality Manager**: Integrates all layers into a unified system

## Features

### 1. Configurable Personality Parameters

Coda's personality is now defined by a set of configurable parameters:

```json
{
  "verbosity": {
    "value": 0.5,
    "range": [0.0, 1.0],
    "description": "Controls length and detail of responses",
    "context_adjustments": {
      "technical_topic": 0.2,
      "casual_conversation": -0.1,
      "formal_context": 0.1
    }
  }
}
```

These parameters can be adjusted based on:
- User preferences
- Conversation context
- Topic category
- Session state

### 2. Behavioral Conditioning

Coda now tracks and adapts to user behavior patterns:

```python
def process_user_input(self, user_input):
    """Process user input for behavioral patterns."""
    # Detect explicit preferences
    preferences = self._detect_explicit_preferences(user_input)
    
    # Apply detected preferences
    if preferences:
        self._apply_preferences(preferences, confidence=0.8)
    
    return preferences
```

Key features:
- Detection of explicit preferences in user input
- Analysis of interaction patterns over time
- Gradual adaptation to user communication style
- Confidence-weighted preference application

### 3. Topic Awareness

Coda now detects and responds to conversation topics:

```python
def detect_topic(self, text):
    """Detect the topic of a text."""
    # Tokenize and normalize text
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Count category matches
    category_counts = Counter()
    
    for word in words:
        if word in self.topic_keywords:
            for category in self.topic_keywords[word]:
                category_counts[category] += 1
    
    # Determine primary category
    if not category_counts:
        return {
            "topic": None,
            "category": None,
            "confidence": 0.0,
            "keywords": []
        }
    
    # ... determine topic and confidence ...
    
    return result
```

Key features:
- Topic detection based on keyword matching
- Categorization into domains (technical, creative, business, etc.)
- Topic-specific personality adjustments
- Tracking of topic shifts during conversations

### 4. Session Management

Coda now manages session state and provides appropriate closure:

```python
def should_enter_closure_mode(self):
    """Determine if we should enter session closure mode."""
    self.update()
    
    # Enter closure mode if session is long or idle time is significant
    if self.session_duration > self.long_session_threshold:
        return True
    
    if self.idle_time > self.idle_threshold:
        return True
        
    return False
```

Key features:
- Tracking of session duration and idle time
- Detection of when a session should enter closure mode
- Generation of session summaries
- Personality adjustments for session closure

### 5. Advanced Personality Manager

The Advanced Personality Manager integrates all these features:

```python
def process_user_input(self, user_input):
    """Process user input through all personality components."""
    results = {}
    
    # Process through behavioral conditioner
    behavior_results = self.behavioral_conditioner.process_user_input(user_input)
    results["behavior"] = behavior_results
    
    # Process through topic awareness
    topic_results = self.topic_awareness.process_user_input(user_input)
    results["topic"] = topic_results
    
    # Update session manager
    self.session_manager.process_interaction("user", user_input)
    session_state = self.session_manager.get_session_state()
    results["session"] = session_state
    
    # Update current context
    self._update_current_context(topic_results, session_state)
    
    return results
```

Key features:
- Unified interface for personality management
- Context-aware prompt generation
- Response formatting based on personality parameters
- Integration with memory system

## Implementation Details

### PersonalityParameters Class

The `PersonalityParameters` class manages configurable personality parameters:

```python
def adjust_for_context(self, context_type):
    """Adjust parameters for a specific context."""
    adjustments = {}
    
    for name, param in self.parameters.items():
        context_adjustments = param.get("context_adjustments", {})
        adjustment = context_adjustments.get(context_type, 0.0)
        
        if adjustment != 0.0:
            current_value = param.get("value", 0.5)
            param_range = param.get("range", [0.0, 1.0])
            
            # Apply adjustment with clamping
            new_value = max(param_range[0], min(current_value + adjustment, param_range[1]))
            
            # Record the adjustment
            self.adjustment_history.append({
                "parameter": name,
                "old_value": current_value,
                "new_value": new_value,
                "reason": f"context:{context_type}",
                "adjustment": adjustment,
                "timestamp": import_time()
            })
            
            # Update the parameter
            param["value"] = new_value
            adjustments[name] = new_value
    
    return adjustments
```

### BehavioralConditioner Class

The `BehavioralConditioner` class tracks and adapts to user behavior patterns:

```python
def _detect_explicit_preferences(self, text):
    """Detect explicit preferences in text."""
    preferences = {}
    
    # Check each parameter for preference patterns
    for param_name, patterns in self.preference_patterns.items():
        # Check for increase patterns
        for pattern in patterns["increase"]:
            if re.search(pattern, text, re.IGNORECASE):
                preferences[param_name] = 0.1  # Small increase
                break
        
        # Check for decrease patterns
        for pattern in patterns["decrease"]:
            if re.search(pattern, text, re.IGNORECASE):
                preferences[param_name] = -0.1  # Small decrease
                break
    
    return preferences
```

### TopicAwareness Class

The `TopicAwareness` class detects and responds to conversation topics:

```python
def _apply_topic_adjustments(self, category):
    """Apply personality adjustments based on topic category."""
    if category not in self.topic_categories:
        return {}
    
    adjustments = self.topic_categories[category].get("personality_adjustments", {})
    
    # Apply adjustments to personality parameters
    applied_adjustments = {}
    for param_name, adjustment in adjustments.items():
        if param_name in self.parameters.get_all_parameters():
            current_value = self.parameters.get_parameter_value(param_name)
            
            # Apply adjustment
            self.parameters.set_parameter_value(
                param_name,
                current_value + adjustment,
                reason=f"topic:{category}"
            )
            
            applied_adjustments[param_name] = adjustment
    
    return applied_adjustments
```

### SessionManager Class

The `SessionManager` class manages session state and closure:

```python
def generate_session_summary(self):
    """Generate a summary of the current session."""
    summary = {
        "duration_minutes": int(self.session_duration / 60),
        "turn_count": self.turn_count,
        "start_time": self.session_start_time.isoformat(),
        "topics": [],
        "actions": []
    }
    
    # Extract information from memory if available
    if self.memory_manager:
        # ... extract topics and actions ...
    
    return summary
```

### AdvancedPersonalityManager Class

The `AdvancedPersonalityManager` class integrates all personality features:

```python
def generate_system_prompt(self):
    """Generate a system prompt based on current context and personality."""
    context_type = self.current_context.get("type", "default")
    
    # Generate prompt using enhanced personality loader
    prompt = self.personality_loader.generate_system_prompt(
        context_type=context_type,
        memory_manager=self.memory_manager
    )
    
    # Add session closure message if in closure mode
    if self.current_context.get("in_closure_mode"):
        closure_message = self.session_manager.get_closure_message()
        if closure_message:
            prompt += f"\n\nThe session appears to be winding down. Consider using this message: \"{closure_message}\""
    
    # Add current personality parameters
    param_info = "\n\nCurrent personality parameters:\n"
    for name, param in self.parameters.get_all_parameters().items():
        value = param.get("value", 0.5)
        param_info += f"- {name}: {value:.2f}\n"
    
    prompt += param_info
    
    return prompt
```

## Integration with Long-Term Memory

The Advanced Personality Features integrate with the Long-Term Memory system:

1. **Behavior Profile Storage**: User behavior profiles are stored in long-term memory
2. **Topic History**: Conversation topics are tracked and stored for future reference
3. **Session Summaries**: Session summaries can be stored in long-term memory
4. **Memory-Based Adaptation**: Personality adapts based on memories of past interactions

## Usage Examples

### Processing User Input

```python
# Initialize advanced personality manager
personality_manager = AdvancedPersonalityManager(
    memory_manager=memory_manager,
    config=config
)

# Process user input
user_input = "Can you give me a more concise explanation of how this works?"
results = personality_manager.process_user_input(user_input)

# Generate system prompt
prompt = personality_manager.generate_system_prompt()

# Format response
response = "Here's a detailed explanation of how this works..."
formatted_response = personality_manager.format_response(response)
```

### Adapting to User Preferences

```python
# User expresses preference for more concise responses
user_input = "I prefer shorter, more direct answers."
personality_manager.process_user_input(user_input)

# User expresses preference for more technical language
user_input = "Please use more technical terms in your explanations."
personality_manager.process_user_input(user_input)

# Get current behavior profile
profile = personality_manager.get_behavior_profile()
```

### Topic-Based Personality Adjustment

```python
# User discusses a technical topic
user_input = "Can you explain how neural networks work?"
personality_manager.process_user_input(user_input)

# User switches to a creative topic
user_input = "I'm working on a painting and need some artistic advice."
personality_manager.process_user_input(user_input)

# Get current topic
topic = personality_manager.get_current_topic()
```

### Session Closure

```python
# Check if session is in closure mode
session_state = personality_manager.get_session_state()
if session_state.get("in_closure_mode"):
    # Get closure message
    closure_message = personality_manager.session_manager.get_closure_message()
    print(closure_message)
```

## Testing

A test script is provided to verify the Advanced Personality Features functionality:

```
python examples/test_advanced_personality.py
```

This script tests personality parameters, behavioral conditioning, topic awareness, session management, and the integrated advanced personality manager.
