# Development Guidelines

This document provides guidelines for developing the Coda Dashboard v3.

## WebSocket Communication

### Using the WebSocketClient

The dashboard uses a global WebSocketClient instance to communicate with the Coda backend. Here's how to use it:

```typescript
// Sending a message
if ((window as any).wsClient && (window as any).wsClient.isConnected()) {
  const message = {
    type: 'message_type',
    data: { /* message data */ },
    timestamp: new Date().toISOString()
  };
  
  (window as any).wsClient.socket.send(JSON.stringify(message));
}
```

### Message Types

When sending messages to Coda, use the following message types:

- `stt_start`: Start speech recognition
- `stt_stop`: Stop speech recognition
- `text_input`: Send text input
- `demo_flow`: Run a demo flow

Example:

```typescript
// Send a text message
const message = {
  type: 'text_input',
  data: { text: 'Hello, Coda!' },
  timestamp: new Date().toISOString()
};

(window as any).wsClient.socket.send(JSON.stringify(message));
```

## Component Development

### State Management

The dashboard uses React's built-in state management (useState, useEffect) for most components. For more complex state, consider using a custom hook.

Example:

```typescript
// Custom hook for managing WebSocket events
function useWebSocketEvents() {
  const [events, setEvents] = useState<any[]>([]);
  
  useEffect(() => {
    if (!(window as any).wsClient) return;
    
    const handleEvent = (event: any) => {
      setEvents(prev => [event, ...prev].slice(0, 100));
    };
    
    (window as any).wsClient.onEvent = handleEvent;
    
    return () => {
      if ((window as any).wsClient) {
        (window as any).wsClient.onEvent = () => {};
      }
    };
  }, []);
  
  return events;
}
```

### Component Structure

Follow these guidelines for component structure:

1. Import statements
2. Interface/type definitions
3. Component function
4. State declarations
5. Effects
6. Event handlers
7. Render function

Example:

```typescript
import React, { useState, useEffect } from 'react';

interface MyComponentProps {
  title: string;
}

const MyComponent: React.FC<MyComponentProps> = ({ title }) => {
  // State
  const [data, setData] = useState<any[]>([]);
  
  // Effects
  useEffect(() => {
    // Effect logic
  }, []);
  
  // Event handlers
  const handleClick = () => {
    // Handler logic
  };
  
  // Render
  return (
    <div>
      <h2>{title}</h2>
      {/* Component content */}
    </div>
  );
};

export default MyComponent;
```

## Styling

The dashboard uses Tailwind CSS for styling. Follow these guidelines:

1. Use Tailwind utility classes for most styling
2. Use the provided color variables for consistency
3. Use the card class for container elements
4. Use responsive classes (sm:, md:, lg:) for responsive design

Example:

```tsx
<div className="card p-4 bg-dark-700 text-white">
  <h2 className="text-xl font-bold mb-4">Component Title</h2>
  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
    {/* Component content */}
  </div>
</div>
```

## Error Handling

Follow these guidelines for error handling:

1. Always check if the WebSocket client exists and is connected before sending messages
2. Use try/catch blocks when sending WebSocket messages
3. Provide user feedback for connection issues
4. Log errors to the console for debugging

Example:

```typescript
const sendMessage = (text: string) => {
  if (!(window as any).wsClient) {
    console.error('WebSocket client not initialized');
    // Show error to user
    return;
  }
  
  if (!(window as any).wsClient.isConnected()) {
    console.error('WebSocket not connected');
    // Show error to user
    return;
  }
  
  try {
    const message = {
      type: 'text_input',
      data: { text },
      timestamp: new Date().toISOString()
    };
    
    (window as any).wsClient.socket.send(JSON.stringify(message));
  } catch (error) {
    console.error('Error sending message:', error);
    // Show error to user
  }
};
```

## Testing

The dashboard uses Vitest for testing. Follow these guidelines:

1. Write tests for all components
2. Mock the WebSocket client for testing
3. Test both success and error cases
4. Use the testing library's render and fireEvent functions

Example:

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import TextInput from './TextInput';

// Mock the WebSocket client
vi.mock('../WebSocketClient', () => ({
  __esModule: true,
  default: vi.fn().mockImplementation(() => ({
    isConnected: () => true,
    socket: {
      send: vi.fn()
    }
  }))
}));

describe('TextInput', () => {
  beforeEach(() => {
    // Set up the global WebSocket client
    (window as any).wsClient = {
      isConnected: () => true,
      socket: {
        send: vi.fn()
      }
    };
  });
  
  it('should send a message when the form is submitted', () => {
    render(<TextInput connected={true} onSendMessage={() => {}} />);
    
    const input = screen.getByPlaceholderText('Type your message here...');
    fireEvent.change(input, { target: { value: 'Hello, Coda!' } });
    
    const form = screen.getByRole('form');
    fireEvent.submit(form);
    
    expect((window as any).wsClient.socket.send).toHaveBeenCalledWith(
      expect.stringContaining('Hello, Coda!')
    );
  });
});
```

## Documentation

Follow these guidelines for documentation:

1. Add JSDoc comments to all components and functions
2. Update the README.md file with new features
3. Update the CHANGELOG.md file with changes
4. Document known issues in KNOWN_ISSUES.md
5. Update this guide as needed

Example:

```typescript
/**
 * TextInput component for sending text messages to Coda
 * 
 * @param connected - Whether the WebSocket is connected
 * @param onSendMessage - Callback function for when a message is sent
 */
const TextInput: React.FC<TextInputProps> = ({ connected, onSendMessage }) => {
  // Component implementation
};
```

## Commit Guidelines

Follow these guidelines for commits:

1. Use descriptive commit messages
2. Prefix commits with the type of change (feat, fix, docs, etc.)
3. Reference issues in commit messages when applicable
4. Keep commits focused on a single change

Example:

```
feat: Add WebSocketDebugger component

- Add WebSocketDebugger component for monitoring WebSocket communication
- Add connection status display
- Add event list with filtering
- Add manual reconnect button

Fixes #123
```
