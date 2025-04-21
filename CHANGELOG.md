# Changelog

All notable changes to the Coda Lite project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Wake word detection (planned)
- Additional language support (planned)
- Voice quality improvements (planned)

## [0.0.1] - 2025-04-21

### Added
- Complete voice loop implementation (STT → LLM → TTS)
- GPU acceleration for both STT (Whisper) and TTS (CSM-1B)
- Multiple English voices (US, British, Australian, Indian)
- Debug GUI for testing the conversation loop
- Example scripts for testing individual components
- Configuration system with YAML files

### Changed
- Switched from CPU to CUDA for faster inference
- Optimized TTS for better performance
- Updated PyTorch to CUDA-enabled version

### Fixed
- Audio playback issues in TTS module
- PyTorch CUDA detection
- Main application voice loop

## [0.0.0] - 2025-04-15

### Added
- Initial project structure
- Basic STT implementation with Whisper
- LLM integration with Ollama
- Initial TTS implementation
- Configuration system
