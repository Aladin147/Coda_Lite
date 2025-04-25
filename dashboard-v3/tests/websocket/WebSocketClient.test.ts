import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import WebSocketClient from '../../src/WebSocketClient';

// Mock WebSocket
class MockWebSocket {
  url: string;
  readyState: number = 0; // CONNECTING
  onopen: (() => void) | null = null;
  onclose: ((event: any) => void) | null = null;
  onerror: ((error: any) => void) | null = null;
  onmessage: ((event: any) => void) | null = null;
  sentMessages: any[] = [];

  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  constructor(url: string) {
    this.url = url;
  }

  send(data: string) {
    this.sentMessages.push(JSON.parse(data));
  }

  close() {
    this.readyState = MockWebSocket.CLOSED;
    if (this.onclose) {
      this.onclose({ code: 1000, reason: 'Normal closure' });
    }
  }

  // Helper to simulate connection
  simulateConnection() {
    this.readyState = MockWebSocket.OPEN;
    if (this.onopen) {
      this.onopen();
    }
  }

  // Helper to simulate message
  simulateMessage(data: any) {
    if (this.onmessage) {
      this.onmessage({ data: JSON.stringify(data) });
    }
  }

  // Helper to simulate error
  simulateError(error: any) {
    if (this.onerror) {
      this.onerror(error);
    }
  }
}

// Mock window
const mockWindow = {
  wsClient: null as any
};

describe('WebSocketClient', () => {
  let originalWebSocket: any;
  let originalWindow: any;
  let mockWs: MockWebSocket;

  beforeEach(() => {
    // Save original WebSocket and window
    originalWebSocket = global.WebSocket;
    originalWindow = global.window;

    // Mock WebSocket
    mockWs = new MockWebSocket('ws://localhost:8765');
    (global as any).WebSocket = vi.fn(() => mockWs);

    // Mock window
    (global as any).window = mockWindow;
  });

  afterEach(() => {
    // Restore original WebSocket and window
    global.WebSocket = originalWebSocket;
    global.window = originalWindow;

    // Clear mocks
    vi.clearAllMocks();
  });

  it('should create a WebSocketClient with the correct URL', () => {
    const client = new WebSocketClient('ws://example.com');
    expect(client.url).toBe('ws://localhost:8765'); // Should always use this URL
  });

  it('should connect to the WebSocket server', () => {
    const client = new WebSocketClient('ws://localhost:8765');
    client.connect();

    expect(global.WebSocket).toHaveBeenCalledWith('ws://localhost:8765');
    expect(mockWs.onopen).not.toBeNull();
    expect(mockWs.onclose).not.toBeNull();
    expect(mockWs.onerror).not.toBeNull();
    expect(mockWs.onmessage).not.toBeNull();
  });

  it('should store itself in window.wsClient on connection', () => {
    const client = new WebSocketClient('ws://localhost:8765');
    client.connect();

    // Simulate connection
    mockWs.simulateConnection();

    expect(mockWindow.wsClient).toBe(client);
  });

  it('should call onConnect when connected', () => {
    const client = new WebSocketClient('ws://localhost:8765');
    const onConnectMock = vi.fn();
    client.onConnect = onConnectMock;
    client.connect();

    // Simulate connection
    mockWs.simulateConnection();

    expect(onConnectMock).toHaveBeenCalled();
  });

  it('should call onDisconnect when disconnected', () => {
    const client = new WebSocketClient('ws://localhost:8765');
    const onDisconnectMock = vi.fn();
    client.onDisconnect = onDisconnectMock;
    client.connect();

    // Simulate connection and then disconnection
    mockWs.simulateConnection();
    client.disconnect();

    expect(onDisconnectMock).toHaveBeenCalled();
  });

  it('should call onEvent when a message is received', () => {
    const client = new WebSocketClient('ws://localhost:8765');
    const onEventMock = vi.fn();
    client.onEvent = onEventMock;
    client.connect();

    // Simulate connection
    mockWs.simulateConnection();

    // Simulate message
    const testEvent = { type: 'test', data: { foo: 'bar' }, timestamp: '2023-06-01T12:34:56.789Z' };
    mockWs.simulateMessage(testEvent);

    expect(onEventMock).toHaveBeenCalledWith(testEvent);
  });

  it('should call onError when an error occurs', () => {
    const client = new WebSocketClient('ws://localhost:8765');
    const onErrorMock = vi.fn();
    client.onError = onErrorMock;
    client.connect();

    // Simulate error
    const testError = new Error('Test error');
    mockWs.simulateError(testError);

    expect(onErrorMock).toHaveBeenCalled();
  });

  it('should return correct connection status', () => {
    const client = new WebSocketClient('ws://localhost:8765');
    client.connect();

    // Not connected yet
    expect(client.isConnected()).toBe(false);

    // Simulate connection
    mockWs.simulateConnection();
    expect(client.isConnected()).toBe(true);

    // Disconnect
    client.disconnect();
    expect(client.isConnected()).toBe(false);
  });

  it('should handle replay events correctly', () => {
    const client = new WebSocketClient('ws://localhost:8765');
    const onEventMock = vi.fn();
    client.onEvent = onEventMock;
    client.connect();

    // Simulate connection
    mockWs.simulateConnection();

    // Simulate replay message
    const replayEvents = [
      { type: 'event1', data: { foo: 'bar' }, timestamp: '2023-06-01T12:34:56.789Z' },
      { type: 'event2', data: { baz: 'qux' }, timestamp: '2023-06-01T12:34:57.789Z' }
    ];
    mockWs.simulateMessage({
      type: 'replay',
      events: replayEvents,
      timestamp: '2023-06-01T12:35:00.000Z'
    });

    expect(onEventMock).toHaveBeenCalledTimes(2);
    expect(onEventMock).toHaveBeenCalledWith(replayEvents[0]);
    expect(onEventMock).toHaveBeenCalledWith(replayEvents[1]);
  });

  // Test for concurrent message sending
  it('should handle multiple messages sent in quick succession', async () => {
    const client = new WebSocketClient('ws://localhost:8765');
    client.connect();

    // Simulate connection
    mockWs.simulateConnection();

    // Send multiple messages in quick succession
    for (let i = 0; i < 10; i++) {
      const message = {
        type: 'test_message',
        data: { index: i },
        timestamp: new Date().toISOString()
      };
      mockWs.socket.send(JSON.stringify(message));
    }

    // Wait for all messages to be processed
    await new Promise(resolve => setTimeout(resolve, 100));

    // Check that all messages were sent
    expect(mockWs.sentMessages.length).toBe(10);
    
    // Check that messages were sent in order
    for (let i = 0; i < 10; i++) {
      expect(mockWs.sentMessages[i].data.index).toBe(i);
    }
  });
});
