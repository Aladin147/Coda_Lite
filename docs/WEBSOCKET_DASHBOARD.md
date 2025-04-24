# WebSocket Dashboard Documentation

## Overview

The WebSocket Dashboard provides a real-time visual interface for monitoring and interacting with Coda. It connects to Coda's WebSocket server and displays various metrics, events, and conversation data in a consolidated, single-page view.

## Features

### Consolidated Dashboard

- **Single-Page View**: All critical metrics visible on a single screen
- **Grid Layout**: Organized sections for different components
- **Responsive Design**: Adapts to different screen sizes
- **Toggle Controls**: Show/hide sections as needed
- **TTS-End Event-Driven Updates**: Dashboard updates synchronize with conversation flow

### Real-time Event Monitoring

- **Event Log**: Displays recent events in chronological order
- **Event Inspector**: Advanced tool for filtering and examining events
  - Filter by event type, search text, and time range
  - Detailed view of event data
  - Event timeline visualization
- **Event Categorization**: Events grouped by type (STT, LLM, TTS, etc.)
- **Timestamps**: Precise timing information for all events

### Performance Metrics

- **Processing Time**: Accurate measurements of processing time for each component
  - STT Processing: Time spent converting speech to text (excluding recording time)
  - LLM Generation: Time spent generating responses
  - TTS Synthesis: Time spent synthesizing speech (excluding playback time)
  - Tool Execution: Time spent executing tools (when applicable)
  - Memory Operations: Time spent on memory retrieval and storage
  - Total Processing: Combined processing time of all components

- **Audio Duration**: Measurements of actual audio durations
  - User Speaking: Duration of user's speech input
  - Coda Speaking: Duration of Coda's speech output
  - Total Conversation: Combined duration of processing and audio playback/recording

- **Performance Visualizer**: Trends and statistics for performance metrics
  - Historical performance data visualization
  - Metric selection (STT, LLM, TTS, etc.)
  - Time range selection
  - Performance statistics (average, min, max)

### Voice Controls

- Push-to-Talk button for voice input
- Text input option for typing messages
- Demo flow button for testing the complete conversation flow
- Fixed position controls for better accessibility

### System Monitoring

- Memory usage tracking
- CPU usage monitoring
- GPU VRAM usage (when available)
- Uptime tracking

### Memory System

- **Basic Memory Viewer**: Displays Coda's long-term memories
  - Shows memory importance scores
  - Provides timestamps for memory creation
  - Visual indicators for new memories

- **Memory Debug Panel**: Advanced tools for memory system debugging
  - Memory statistics display (short-term, long-term, retrieval)
  - Memory operations log
  - Memory search functionality
  - Topic visualization

### Tool Usage Tracking

- Displays tool calls and their parameters
- Shows tool execution results
- Tracks tool execution time
- Visual indicators for new tool calls

### Conversation View

- Real-time display of the conversation
- Shows both user and Coda messages
- Updates as the conversation progresses
- Automatic scrolling to latest messages

### UI Features

- Dark mode by default (with light mode option)
- Responsive design for different screen sizes
- Avatar with speaking animation
- Consistent section headers with toggle controls

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

   ```bash
   python main_websocket.py
   ```

2. Start the dashboard:

   ```bash
   cd dashboard
   npm run dev
   ```

3. Open the dashboard in your browser:

   ```bash
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
