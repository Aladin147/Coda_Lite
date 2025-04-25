# Coda Dashboard v3

A modern dashboard for interacting with Coda, built with React, TypeScript, and Tailwind CSS.

## Overview

This dashboard provides a user interface for interacting with Coda, a conversational AI assistant. It communicates with the Coda backend using WebSockets and provides various features for monitoring and controlling Coda.

## Features

- Real-time communication with Coda via WebSockets
- Voice controls for starting and stopping speech recognition
- Text input for sending messages directly
- Conversation view for displaying the chat history
- Performance monitoring for tracking latency and resource usage
- Memory viewer for exploring Coda's memory
- Avatar component that reflects Coda's current state and emotion
- WebSocket debugger for monitoring communication

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn
- Coda backend running on localhost:8765

### Installation

1. Clone the repository
2. Navigate to the dashboard-v3 directory
3. Install dependencies:

```bash
npm install
```

### Running the Dashboard

1. Start the Coda backend:

```bash
cd /path/to/coda
python main_websocket.py
```

2. Start the dashboard:

```bash
npm run dev
```

3. Open your browser and navigate to [http://localhost:5173](http://localhost:5173)

## Architecture

The dashboard is built with the following technologies:

- **React**: UI library
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Vite**: Build tool and development server

### Key Components

- **WebSocketClient**: Handles communication with the Coda backend
- **Avatar**: Displays Coda's current state and emotion
- **ConversationView**: Shows the chat history
- **PerformanceMonitor**: Displays latency and resource usage metrics
- **MemoryViewer**: Shows Coda's memory contents
- **VoiceControls**: Provides buttons for controlling speech recognition
- **TextInput**: Allows sending text messages directly
- **WebSocketDebugger**: Monitors WebSocket communication

## Documentation

- [WebSocket Implementation](./docs/WEBSOCKET_IMPLEMENTATION.md): Details on the WebSocket communication
- [Changelog](./docs/CHANGELOG.md): History of changes to the dashboard

## Troubleshooting

### Common Issues

1. **Dashboard can't connect to Coda**
   - Ensure the Coda backend is running
   - Verify the WebSocket server is running on port 8765
   - Check for network issues or firewall restrictions

2. **Voice controls not working**
   - Ensure your browser has permission to access the microphone
   - Check that the Coda backend has STT capabilities enabled

3. **Performance metrics not updating**
   - Verify that the Coda backend is sending system_metrics events
   - Check the WebSocket connection is established
