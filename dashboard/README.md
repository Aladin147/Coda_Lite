# Coda Dashboard

A Tauri-based dashboard for monitoring and controlling Coda Lite.

## Features

- Real-time visualization of Coda's state
- Performance monitoring
- Memory inspection
- Tool usage tracking
- Conversation view
- Push-to-talk controls
- Dark/light theme support

## Development

### Prerequisites

- Node.js (v16+)
- npm
- Rust (for Tauri)
- Tauri CLI

### Setup

1. Install dependencies:

```bash
npm install
```

2. Run the development server:

```bash
npm run tauri dev
```

### Building

To build the application:

```bash
npm run tauri build
```

This will create a distributable package in the `src-tauri/target/release` directory.

## Architecture

The dashboard connects to Coda's WebSocket server to receive real-time events and send commands. It uses React for the UI and Tauri for the native application wrapper.

### Components

- **Avatar**: Displays Coda's avatar with speaking animation
- **ConversationView**: Shows the conversation between user and Coda
- **Dashboard**: Main dashboard view with system metrics
- **EventLog**: Displays all events from the WebSocket server
- **Header**: Navigation and connection status
- **MemoryViewer**: Displays Coda's memory items
- **PerformanceMonitor**: Shows performance metrics with charts
- **SystemInfo**: Displays system information in the footer
- **ThemeToggle**: Allows switching between light and dark modes
- **ToolDisplay**: Shows tool usage cards
- **VoiceControls**: Provides push-to-talk and demo functionality

## WebSocket Events

The dashboard listens for the following event types:

- `stt_start`, `stt_result`: Speech-to-text events
- `llm_start`, `llm_progress`, `llm_result`: Language model events
- `tts_start`, `tts_progress`, `tts_result`: Text-to-speech events
- `memory_store`, `memory_recall`: Memory events
- `tool_call`, `tool_result`, `tool_error`: Tool usage events
- `latency_trace`: Performance metrics
- `system_info`: System information

## License

MIT
