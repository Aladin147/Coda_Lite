# Mini-Command Language

Coda Lite supports a mini-command language that allows users to control various aspects of the system using simple commands. These commands are prefixed with a `#` symbol and can be used in conversation to trigger specific actions.

## Available Commands

### Personality Commands

| Command | Description |
|---------|-------------|
| `#reset_tone [casual\|formal\|technical\|concise]` | Reset personality tone to a specific style |
| `#mood_reset` | Reset personality to default state |
| `#personality_insight` | Show current personality settings |
| `#apply_feedback` | Apply feedback patterns to personality |

### Memory Commands

| Command | Description |
|---------|-------------|
| `#show_memory` | Show memory statistics |
| `#summarize_session` | Generate a summary of the current session |
| `#summarize_day` | Generate a summary of today's interactions |
| `#view_feedback [type]` | View feedback history or specific type |
| `#view_feedback_memories [type]` | View feedback memories from long-term memory |

### Feedback Commands

| Command | Description |
|---------|-------------|
| `#feedback [type]` | Request specific feedback (helpfulness, memory, tone, verbosity, accuracy, general) |

### System Commands

| Command | Description |
|---------|-------------|
| `#debug_on` | Enable debug mode |
| `#debug_off` | Disable debug mode |
| `#help` | Show available commands |

## Examples

Here are some examples of how to use the mini-commands:

```
#reset_tone casual
```
Resets the personality tone to a casual, conversational style.

```
#personality_insight
```
Shows the current personality settings, including learned preferences.

```
#summarize_session
```
Generates a summary of the current conversation session.

```
#feedback tone
```
Requests feedback about the tone of Coda's responses.

```
#help
```
Shows a list of all available commands.

## Implementation Details

The mini-command language is implemented in the `intent` module, specifically in the `IntentRouter` and `IntentHandlers` classes. When a user input starts with a `#` symbol, it is detected as a system command and routed to the appropriate handler.

The system commands are processed before any other intent detection, allowing them to override normal conversation flow when needed.

## Adding New Commands

To add a new command to the mini-command language:

1. Update the `IntentRouter` class to detect the new command
2. Add a handler for the new command in the `IntentHandlers` class
3. Update the `#help` command to include the new command in its output
4. Update this documentation file with the new command

## Memory-Based Personality Conditioning

The `#apply_feedback` command is part of the memory-based personality conditioning system, which allows Coda to learn from user feedback and adjust its personality parameters accordingly. This creates a more adaptive and personalized experience.

The system analyzes feedback patterns from memory, identifies consistent preferences, and adjusts personality parameters based on feedback history. It also provides insights into user preferences through the `#personality_insight` command.

## Feedback System

The feedback system allows users to provide feedback on various aspects of Coda's performance, such as helpfulness, memory, tone, verbosity, and accuracy. This feedback is stored in long-term memory and used to improve Coda's responses over time.

The `#feedback` command allows users to manually request feedback on a specific aspect, while the `#view_feedback` and `#view_feedback_memories` commands allow users to view feedback history and statistics.
