# Coda Lite - Development Journal

This journal tracks the development progress, decisions, challenges, and insights gained during the development of Coda Lite.

## April 23, 2023 - TTS Module Implementation

**Activities:**
- Implemented the Text-to-Speech (TTS) module using Coqui TTS
- Added audio playback functionality
- Created comprehensive unit tests for the TTS module
- Added example script to demonstrate TTS usage

**Decisions:**
- Switched from CSM-1B to Coqui TTS for easier integration and broader model support
- Implemented both file-based and direct audio playback
- Added support for multiple speakers and languages
- Used sounddevice for audio playback due to its simplicity and reliability

**Challenges:**
- Finding the right TTS library that balances quality and ease of integration
- Managing model downloads and caching
- Handling different output formats (file vs. direct playback)

**Next Steps:**
- Establish LLM connection with Ollama
- Create the main conversation loop
- Integrate STT and TTS modules in the main loop

**Notes:**
- Coqui TTS provides a wide range of models with different quality/speed tradeoffs
- The default model works well for testing, but we may want to explore other models for production

## April 22, 2023 - STT Module Implementation

**Activities:**
- Implemented the Speech-to-Text (STT) module using faster-whisper
- Added real-time audio capture functionality
- Created comprehensive unit tests for the STT module
- Added example script to demonstrate STT usage

**Decisions:**
- Implemented both file-based and real-time transcription
- Added continuous listening mode with silence detection
- Used PyAudio for audio capture due to its flexibility and reliability
- Included Voice Activity Detection (VAD) to improve transcription quality

**Challenges:**
- Ensuring proper resource management for audio streams
- Balancing between transcription accuracy and latency
- Handling different audio input formats (file vs. real-time)

**Next Steps:**
- Implement the TTS module with CSM-1B
- Establish LLM connection with Ollama
- Create the main conversation loop

**Notes:**
- The tiny model works well for testing but larger models will be needed for production
- VAD significantly improves transcription quality by filtering out silence

## April 21, 2023 - Project Initialization

**Activities:**
- Created GitHub repository with README and LICENSE
- Established initial project structure
- Set up basic module placeholders
- Created documentation framework
- Set up development environment with pre-commit hooks

**Decisions:**
- Chose faster-whisper for STT due to its efficiency and accuracy
- Selected Ollama as the LLM interface for local model management
- Opted for CSM-1B for TTS based on quality and performance
- Implemented a modular design to allow easy component swapping

**Challenges:**
- Balancing between comprehensive functionality and maintaining low latency
- Determining the optimal project structure for future extensibility

**Next Steps:**
- Implement basic STT functionality
- Establish LLM connection
- Create TTS integration

**Notes:**
- Initial focus will be on creating a functional voice loop before adding tools
- Need to research optimal model sizes for balancing quality and performance

---

*New entries will be added in reverse chronological order (newest at the top).*
