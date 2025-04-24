# Changelog

All notable changes to the Coda Lite project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Wake word detection (planned)
- Additional language support (planned)
- Voice quality improvements (planned)

## [0.1.1-dashboard-transformation] - 2025-04-24

### Added

- Comprehensive dashboard audit and transformation plan
- Enhanced memory tracking for TTS modules
- Improved performance metrics separating processing from speaking time
- TTS cut-off when PTT button is pressed (1-second delay)
- Continuous recording while PTT button is held
- Comprehensive testing for the full pipeline
- Mock tests for WebSocket pipeline
- Detailed dashboard transformation plan document

### Changed

- Updated TTS factory with memory usage tracking
- Improved performance metrics to show real data
- Optimized module initialization with lazy loading
- Enhanced WebSocket event handling for better performance
- Updated README with dashboard transformation plan

### Fixed

- Performance bottlenecks in event processing
- Initialization of unused TTS modules
- Memory leaks in TTS module unloading

## [0.1.1-personality-update] - 2025-04-29

### Added

- Comprehensive personality update with playful, energetic, smart, loyal, and rebellious traits
- Enhanced contextual traits with adaptive humor, supportive empathy, and friendly sarcasm
- Updated backstory focused on breaking stereotypes of typical digital assistants
- New preferences for humor, late-night coding, and espresso (metaphorical)
- New dislikes for bureaucracy, monotony, and excessive formality
- Personality quirks including Late Night Coder, Bureaucracy Critic, and Prototype Pride
- Identity anchors for introductions, mistake recovery, and task completion
- Formative memories about prototype mishaps and playful nature
- Detailed documentation of the personality update

### Changed

- Updated basic personality traits in coda_personality.json
- Enhanced personality with weighted traits and context-specific strengths
- Updated personal lore with new backstory, preferences, and quirks
- Adjusted personality parameters for higher humor, energy, and playfulness
- Added new parameters for sarcasm, empathy, and playfulness

## [0.1.1-dashboard-consolidation] - 2025-04-28

### Added

- Consolidated dashboard with single-page view
- Advanced memory debug panel with statistics and operations log
- Event inspector with filtering and detailed view
- Performance visualizer with trends and statistics
- Toggle controls for different view modes
- Consistent section headers across all components
- Button groups for related actions
- Time formatting with appropriate units (ms/s)

### Changed

- Improved performance metrics calculation
- Enhanced memory visualization with operation types
- Updated event log with better categorization
- Improved tool display with visual indicators
- Enhanced conversation view with automatic scrolling
- Updated documentation to reflect new features

### Fixed

- Fixed conversation panel not updating with new messages
- Fixed performance metrics to properly separate processing time from audio duration
- Fixed memory panel to show memory events correctly
- Fixed tool display to show more tool events
- Added proper error handling and null checks

## [0.1.1-memory-fixes] - 2025-04-26

### Added

- Comprehensive memory system diagnostic tools
- Enhanced topic extraction for better memory organization
- Improved importance scoring for personal information
- Memory persistence verification tools
- Memory system documentation with detailed fixes

### Changed

- Reduced memory persistence interval for more frequent saving
- Enhanced memory retrieval with lower similarity threshold
- Improved memory formatting with topic-based grouping
- Updated memory integration in the LLM context
- Enhanced vector database persistence with better error handling

### Fixed

- Fixed memory persistence issues causing memory loss
- Fixed memory retrieval with more relevant results
- Fixed memory encoding for better topic extraction
- Fixed vector database issues with inconsistent persistence
- Fixed memory integration for better context generation

## [0.1.1-dashboard-update] - 2025-04-25

### Added

- Event queue system for non-blocking event handling
- Component-specific timing for accurate performance metrics
- Separation of processing time from audio duration metrics
- Text input option alongside voice input
- Fixed position push-to-talk button to prevent scrolling issues
- Dark mode as default theme
- Comprehensive WebSocket dashboard documentation

### Changed

- Improved performance metrics display with separate processing and audio duration sections
- Enhanced latency trace calculation for more accurate measurements
- Updated dashboard layout for better usability
- Improved WebSocket event handling with queue-based approach
- Updated README with new dashboard features

### Fixed

- Fixed push-to-talk button scrolling issues
- Fixed performance metrics calculation to exclude audio playback/recording time
- Fixed dark mode persistence
- Fixed feedback manager to work without intent results

## [0.1.1-dashboard] - 2025-04-23

### Added

- React-based dashboard implementation
- Real-time visualization of system events
- Performance monitoring and metrics display
- Memory inspection and visualization
- Tool usage tracking and display
- Conversation view with real-time updates
- Push-to-talk and demo functionality
- Dark/light theme support
- Responsive design for different screen sizes
- Avatar component with speaking animation
- System information display in footer
- WebSocket server compatibility with websockets 15.0.1+

### Changed

- Updated WebSocket server to be compatible with latest websockets library
- Improved event handling in WebSocket server
- Enhanced WebSocket client with global accessibility
- Updated main README with dashboard information

### Fixed

- Fixed WebSocket server handler to work with websockets 15.0.1+

## [0.1.0-dia-tts] - 2025-04-22

### Added

- Dia TTS integration for high-quality speech synthesis
- GPU acceleration for both Dia TTS and Ollama
- Comprehensive GPU configuration documentation
- Automatic fallback to CPU when GPU is not available
- Performance monitoring for speech synthesis

### Changed

- Updated configuration to support Dia TTS
- Improved TTS module to handle multiple TTS engines
- Enhanced logging with GPU memory usage information
- Updated README with GPU acceleration information

## [0.0.9] - 2025-05-03

### Added

- Centralized version management system
- Version information in logs and startup
- Version history tracking

### Changed

- Updated documentation to reflect current version
- Reorganized version naming to follow semantic versioning
- Improved version display with descriptive names

## [0.2.0] - 2025-05-02

### Added

- Memory-based personality conditioning system
- Feedback pattern analysis and application
- User preference insights based on feedback history
- #apply_feedback command for manually applying feedback patterns
- #view_feedback_memories command for viewing feedback memories
- Enhanced personality insights with learned preferences
- Automatic feedback pattern application every 10 turns
- Feedback storage in long-term memory

### Changed

- Updated advanced personality manager to use memory conditioner
- Enhanced memory manager to store and retrieve feedback
- Improved intent handlers to support new commands
- Extended personality insight command to show learned preferences

## [0.1.9] - 2025-05-01

### Added

- Expanded mini-command language with new commands
- #feedback command for requesting specific feedback types
- #mood_reset command for resetting personality to default state
- #personality_insight command for showing current personality settings
- #summarize_day command for generating a summary of the day's interactions
- #view_feedback command for viewing feedback history or specific types
- Day summary generation in memory manager
- Integration between feedback manager and personality manager

### Changed

- Updated intent router to support new commands
- Enhanced system command handling with specialized responses
- Improved help command with categorized command listing
- Updated advanced personality manager to support feedback manager

## [0.1.8] - 2025-04-30

### Added

- User feedback hooks for collecting and processing user feedback
- Feedback-based personality adjustments
- Sentiment analysis for feedback responses
- Feedback storage in long-term memory
- Feedback statistics tracking
- Configurable feedback frequency and cooldown
- Integration with intent and personality systems

### Changed

- Updated main application to request feedback after responses
- Extended memory system to store and retrieve feedback
- Enhanced configuration with feedback settings
- Improved personality adjustments based on user feedback

## [0.1.7] - 2025-04-29

### Added

- Lightweight intent routing system with pattern-based detection
- Intent-specific handlers for different types of requests
- Entity extraction from user input
- System command processing with #command syntax
- Memory-specific intent handling for recall and storage
- Personality adjustment through intent detection
- Debug mode for intent routing diagnostics
- Intent history tracking and distribution analysis

### Changed

- Updated main application to use intent routing
- Extended configuration with intent routing settings
- Improved memory recall with intent-based formatting
- Enhanced system command handling with specialized responses

## [0.1.6] - 2025-04-28

### Added

- Personal lore system with backstory, preferences, and traits
- Context-aware personality anchors for consistent voice
- Personality quirks with trigger-based expressions
- Formative memories for character depth
- Lore-based response formatting
- Usage tracking for balanced lore references

### Changed

- Enhanced advanced personality manager with personal lore integration
- Improved prompt generation with lore injection
- Extended context tracking with trigger words
- Updated personality module documentation

## [0.1.5] - 2025-04-27

### Added

- Advanced personality features with behavioral conditioning
- Configurable personality parameters system
- Topic awareness with category-based personality adjustments
- Session management with closure detection and summaries
- Integrated advanced personality manager
- Behavioral pattern detection and adaptation
- User preference tracking and application

### Changed

- Enhanced personality module with layered architecture
- Improved context detection with topic categorization
- Extended personality system with parameter-based adjustments
- Added comprehensive test suite for advanced personality features

## [0.1.4] - 2025-04-26

### Added

- Long-term memory system with vector embeddings
- Semantic search for retrieving relevant memories
- Memory importance scoring and time decay
- Memory encoder for chunking conversations
- User preference and fact storage
- Memory-related tools for adding facts and preferences
- Enhanced context generation with relevant memories
- Memory statistics and search capabilities

### Changed

- Updated main application to use enhanced memory manager
- Extended configuration with long-term memory settings
- Improved tool system with memory-specific tools
- Enhanced cleanup process for proper memory persistence

## [0.1.2] - 2025-04-24

### Added

- Enhanced Personality Engine with weighted traits and context awareness
- Adaptive tone switching based on conversation context
- Separation of personality and functional prompts
- Personality quirks and signature behaviors
- Session metadata injection into prompts
- Live reloading capability for personality configuration
- Comprehensive test suite for personality features

## [0.1.3] - 2025-04-25

### Added

- Refined output styling for consistent voice across responses
- Dynamic memory hint injection based on conversation history
- Emotional responsiveness with configurable intensity levels
- Session-level personality drift based on conversation context
- Response templates for greetings, confirmations, refusals, etc.
- Emotion detection from user input
- Enhanced prompt templates with styling guidelines

### Changed

- Refactored personality loader to support enhanced features
- Reorganized prompt templates into separate files
- Improved system prompt generation with context-specific traits

## [0.1.1] - 2025-04-23

### Added

- Tools Manifest and Help Command feature
- `list_tools` tool for displaying available tools
- `show_capabilities` tool for explaining what Coda can do
- Enhanced tool metadata with categories, examples, and parameter descriptions
- Auto-discovery of tool parameters from function signatures
- Updated system prompt to inform users about the help command

### Changed

- Reorganized tools into categories (Time & Date, Entertainment, Memory, Help)
- Improved tool registration with more detailed metadata
- Enhanced tool router to store and retrieve tool metadata

## [0.1.0] - 2025-04-22

### Added

- Enhanced tool calling system with two-pass approach
- Aggressive JSON cleaning to reduce JSON leakage
- Enhanced error handling and logging for tool execution
- Direct fallbacks for common tools when execution fails
- Test script for verifying tool calling functionality

### Fixed

- Fixed duplicate __init__ method in CodaAssistant class
- Fixed OllamaLLM.chat method to properly handle function messages
- Fixed streaming issues with OllamaLLM
- Improved context handling for the second pass

### Known Issues

- JSON from tool calls sometimes leaks into the final response
- Second pass occasionally fails to completely remove JSON formatting

## [0.0.2] - 2025-04-21

### Added

- Short-term memory module for conversation context
- Token-aware context management for LLM
- Memory export/import functionality
- Automatic session memory saving
- Basic tool calling implementation
- Tool router for handling structured LLM output
- Simple tools like `get_time()`, `tell_joke()`

### Changed

- Updated main application to use the memory manager
- Improved conversation context handling
- Enhanced cleanup process with memory export
- Updated system prompt for tool calling

## [0.0.1] - 2025-04-21

### Added

- Personality module for more engaging interactions
- JSON-based personality definition
- Dynamic system prompt generation based on personality
- Randomized welcome messages
- Performance optimization with concurrent processing
- Benchmark script for measuring performance improvements

### Changed

- Updated main application to use the personality module
- Improved system prompt with personality traits
- Updated system prompt to encourage more concise responses
- Implemented threading for pipeline optimization
- Added TTS worker thread for non-blocking audio playback

### Fixed

- Improved cleanup process for graceful shutdown

## [0.0.0] - 2025-04-15

### Added

- Initial project structure
- Basic STT implementation with Whisper
- LLM integration with Ollama
- Initial TTS implementation
- Configuration system
