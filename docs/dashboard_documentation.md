# Coda Dashboard Documentation

## Overview

The Coda Dashboard is a Tauri-based application that provides a visual interface for monitoring and controlling Coda Lite. It connects to Coda's WebSocket server to receive real-time events and send commands, allowing users to visualize system events, monitor performance, inspect memory, and control Coda through a graphical interface.

## Features

- **Real-time Visualization**: Display of system events as they happen
- **Performance Monitoring**: Visualization of latency metrics and system performance
- **Memory Inspection**: View and search through Coda's memory items
- **Tool Usage Tracking**: Display of tool calls and their results
- **Conversation View**: Real-time display of the conversation between user and Coda
- **Voice Controls**: Push-to-talk and demo functionality
- **Theme Support**: Light and dark mode with smooth transitions
- **System Information**: Display of version, uptime, and memory usage

## Architecture

The dashboard is built with the following technologies:

- **Tauri**: Cross-platform framework for building desktop applications
- **React**: JavaScript library for building user interfaces
- **WebSockets**: Protocol for real-time bidirectional communication
- **CSS**: Styling with custom variables for theming

The dashboard connects to Coda's WebSocket server running at `ws://localhost:8765` by default. It receives events from the server and displays them in real-time, and can send commands to control Coda's behavior.

## Components

### Avatar

The Avatar component displays Coda's avatar with a speaking animation when Coda is talking. It provides visual feedback to the user about Coda's current state.

### ConversationView

The ConversationView component displays the conversation between the user and Coda in a chat-like interface. It shows both user inputs and Coda's responses with timestamps.

### Dashboard

The main Dashboard component provides an overview of the system's status, including connection status, performance metrics, and system information.

### EventLog

The EventLog component displays all events received from the WebSocket server in chronological order, with timestamps and event types.

### MemoryViewer

The MemoryViewer component allows users to browse and search through Coda's memory items, including facts, preferences, and conversation history.

### PerformanceMonitor

The PerformanceMonitor component displays performance metrics such as latency, memory usage, and CPU usage in real-time charts.

### SystemInfo

The SystemInfo component displays system information such as version, uptime, and memory usage in the footer.

### ThemeToggle

The ThemeToggle component allows users to switch between light and dark modes.

### ToolDisplay

The ToolDisplay component shows tool usage cards with information about tool calls, parameters, and results.

### VoiceControls

The VoiceControls component provides push-to-talk functionality and a demo button for testing the complete voice interaction flow.

## WebSocket Events

The dashboard listens for the following event types:

- `stt_start`, `stt_result`: Speech-to-text events
- `llm_start`, `llm_progress`, `llm_result`: Language model events
- `tts_start`, `tts_progress`, `tts_result`: Text-to-speech events
- `memory_store`, `memory_recall`: Memory events
- `tool_call`, `tool_result`, `tool_error`: Tool usage events
- `latency_trace`: Performance metrics
- `system_info`: System information

## WebSocket Commands

The dashboard can send the following commands to the WebSocket server:

- `stt_start`: Start speech-to-text processing
- `stt_stop`: Stop speech-to-text processing
- `demo_flow`: Run a demo of the complete voice interaction flow

## Installation

### Prerequisites

- Node.js (v16+)
- npm
- Rust (for Tauri)
- Tauri CLI

### Setup

1. Install dependencies:

   ```bash
   cd dashboard
   npm install
   ```

2. Run the development server:

   With Tauri (requires Rust):
   ```bash
   npm run tauri dev
   ```

   Or without Tauri (React-only):
   ```bash
   npm run dev
   ```

   The React-only version will run in your browser at `http://localhost:5173/`

### Building

To build the application:

```bash
npm run tauri build
```

This will create a distributable package in the `src-tauri/target/release` directory.

## Troubleshooting

- **Connection Issues**: Ensure Coda's WebSocket server is running at ws://localhost:8765
- **Missing UI Elements**: Check browser console for errors and ensure all dependencies are installed
- **Tauri Build Errors**: Verify that Rust and Cargo are properly installed

## Related Documentation

- [Dashboard README](../dashboard/README.md) - Quick start guide for the dashboard
- [WebSocket Server Documentation](websocket_server.md) - Documentation for Coda's WebSocket server
- [Architecture Transformation Roadmap](ARCHITECTURE_ROADMAP.md) - Detailed plan for the WebSocket-based architecture

---

*This document will be updated as the dashboard evolves.*
