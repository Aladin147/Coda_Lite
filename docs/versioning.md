# Coda Lite Versioning Guide

This document explains the versioning scheme used in Coda Lite.

## Semantic Versioning

Coda Lite follows [Semantic Versioning](https://semver.org/) with the format `MAJOR.MINOR.PATCH`:

- **MAJOR**: Incremented for incompatible API changes
- **MINOR**: Incremented for backward-compatible functionality additions
- **PATCH**: Incremented for backward-compatible bug fixes

## Version Roadmap

| Version | Tagline | Description |
|---------|---------|-------------|
| 0.0.0 | Initial Prototype | Basic voice loop with STT, LLM, and TTS |
| 0.0.1 | Personality Engine | Added personality module for more engaging interactions |
| 0.0.2 | Memory & Tools | Added short-term memory and basic tool calling |
| 0.0.9 | Adaptive Agent | Self-tuning, memory-aware assistant with feedback-based personality conditioning |
| 0.1.0 | Alpha Candidate | Fully autonomous loop, early demos possible |
| 0.2.0 | Beta Candidate | Feature-complete with stability improvements |
| 1.0.0 | Production Release | Stable, production-ready release |

## Current Version

The current version is defined in `version.py` and is displayed in the logs when Coda starts up.

## Version History

For a detailed history of changes in each version, see the [CHANGELOG.md](../CHANGELOG.md) file.

## Upcoming Features for 0.1.0

To reach version 0.1.0 (Alpha Candidate), the following features need to be implemented:

1. Session summary - Generate comprehensive summaries of conversation sessions
2. Memory explainability - Provide insights into what Coda remembers and why
3. Additional tool classes - Implement task management tools

## Version Naming

Each version has a descriptive name that reflects its main characteristics:

- **0.0.9: Adaptive Agent** - Self-tuning, memory-aware assistant
- **0.1.0: Alpha Candidate** - Fully autonomous loop, early demos possible

## Checking the Version

You can check the current version in several ways:

1. In the logs when Coda starts up
2. By importing from the version module:
   ```python
   from version import __version__, __version_name__, get_full_version_string
   print(get_full_version_string())
   ```
