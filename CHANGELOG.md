# Changelog

All notable changes to the Coda Lite project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Wake word detection (planned)
- Additional language support (planned)
- Voice quality improvements (planned)

## [0.0.2] - 2025-04-22

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
