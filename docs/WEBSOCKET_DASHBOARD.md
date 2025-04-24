# WebSocket Dashboard Documentation

## Overview

The WebSocket Dashboard provides a real-time visual interface for monitoring and interacting with Coda. It connects to Coda's WebSocket server and displays various metrics, events, and conversation data.

## Features

### Real-time Event Monitoring
- Displays all events from Coda's WebSocket server in real-time
- Categorizes events by type (STT, LLM, TTS, etc.)
- Shows timestamps and detailed event data

### Performance Metrics
- **Processing Time**: Accurate measurements of processing time for each component
  - STT Processing: Time spent converting speech to text (excluding recording time)
  - LLM Generation: Time spent generating responses
  - TTS Synthesis: Time spent synthesizing speech (excluding playback time)
  - Total Processing: Combined processing time of all components
  
- **Audio Duration**: Measurements of actual audio durations
  - User Speaking: Duration of user's speech input
  - Coda Speaking: Duration of Coda's speech output
  - Total Conversation: Combined duration of processing and audio playback/recording

### Voice Controls
- Push-to-Talk button for voice input
- Text input option for typing messages
- Demo flow button for testing the complete conversation flow

### System Monitoring
- Memory usage tracking
- CPU usage monitoring
- GPU VRAM usage (when available)
- Uptime tracking

### Memory Viewer
- Displays Coda's long-term memories
- Shows memory importance scores
- Provides timestamps for memory creation

### Tool Usage Tracking
- Displays tool calls and their parameters
- Shows tool execution results
- Tracks tool execution time

### Conversation View
- Real-time display of the conversation
- Shows both user and Coda messages
- Updates as the conversation progresses

### UI Features
- Dark mode by default (with light mode option)
- Responsive design for different screen sizes
- Avatar with speaking animation
- Tab-based navigation between different views

## Technical Implementation

### Architecture
- React-based frontend
- WebSocket client for real-time communication
- Event-driven updates
- Component-based design

### Performance Tracking
- Component-specific timing markers for accurate measurements
- Separation of processing time from audio duration
- Real-time latency trace events

### Event Queue System
- Thread-safe event queue for non-blocking event handling
- Priority-based event processing
- Asynchronous event dispatch

## Usage

1. Start Coda with the WebSocket server:
   ```
   python main_websocket.py
   ```

2. Start the dashboard:
   ```
   cd dashboard
   npm run dev
   ```

3. Open the dashboard in your browser:
   ```
   http://localhost:5173/
   ```

4. Use the Push-to-Talk button or text input to interact with Coda.

## Future Improvements

- Enhanced visualization of performance metrics
- More detailed memory visualization
- Tool usage statistics and analytics
- User preference settings
- Voice selection interface
- System configuration options
