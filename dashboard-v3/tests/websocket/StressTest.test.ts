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
  sendDelay: number = 0;
  shouldFail: boolean = false;

  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  constructor(url: string) {
    this.url = url;
  }

  send(data: string) {
    if (this.shouldFail) {
      throw new Error('Simulated send failure');
    }
    
    if (this.sendDelay > 0) {
      setTimeout(() => {
        this.sentMessages.push(JSON.parse(data));
      }, this.sendDelay);
    } else {
      this.sentMessages.push(JSON.parse(data));
    }
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

describe('WebSocket Stress Test', () => {
  let originalWebSocket: any;
  let mockWs: MockWebSocket;

  beforeEach(() => {
    // Save original WebSocket
    originalWebSocket = global.WebSocket;

    // Mock WebSocket
    mockWs = new MockWebSocket('ws://localhost:8765');
    (global as any).WebSocket = vi.fn(() => mockWs);

    // Mock window
    (global as any).window = {
      wsClient: null
    };

    // Mock console methods
    vi.spyOn(console, 'log').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});

    // Mock setTimeout
    vi.useFakeTimers();
  });

  afterEach(() => {
    // Restore original WebSocket
    global.WebSocket = originalWebSocket;

    // Clear mocks
    vi.clearAllMocks();
    vi.restoreAllMocks();
  });

  it('should handle rapid message sending without errors', async () => {
    const client = new WebSocketClient('ws://localhost:8765');
    client.connect();

    // Simulate connection
    mockWs.simulateConnection();

    // Send 100 messages rapidly
    for (let i = 0; i < 100; i++) {
      const message = {
        type: 'test_message',
        data: { index: i },
        timestamp: new Date().toISOString()
      };
      
      (window as any).wsClient.socket.send(JSON.stringify(message));
    }

    // Check that all messages were sent
    expect(mockWs.sentMessages.length).toBe(100);
    
    // Check that messages were sent in order
    for (let i = 0; i < 100; i++) {
      expect(mockWs.sentMessages[i].data.index).toBe(i);
    }
  });

  it('should handle concurrent message sending with delayed responses', async () => {
    // Set a send delay to simulate network latency
    mockWs.sendDelay = 10;

    const client = new WebSocketClient('ws://localhost:8765');
    client.connect();

    // Simulate connection
    mockWs.simulateConnection();

    // Send 50 messages concurrently
    const sendPromises = [];
    for (let i = 0; i < 50; i++) {
      const message = {
        type: 'test_message',
        data: { index: i },
        timestamp: new Date().toISOString()
      };
      
      const sendPromise = new Promise<void>((resolve) => {
        (window as any).wsClient.socket.send(JSON.stringify(message));
        setTimeout(resolve, 5); // Small delay between sends
      });
      
      sendPromises.push(sendPromise);
    }

    // Wait for all sends to complete
    await Promise.all(sendPromises);
    
    // Advance timers to process all delayed sends
    vi.advanceTimersByTime(1000);

    // Check that all messages were sent
    expect(mockWs.sentMessages.length).toBe(50);
    
    // Check that all messages were received (may not be in order due to delays)
    const receivedIndices = mockWs.sentMessages.map(msg => msg.data.index);
    for (let i = 0; i < 50; i++) {
      expect(receivedIndices).toContain(i);
    }
  });

  it('should handle message sending during reconnection', async () => {
    const client = new WebSocketClient('ws://localhost:8765');
    client.connect();

    // Simulate connection
    mockWs.simulateConnection();

    // Send 10 messages
    for (let i = 0; i < 10; i++) {
      const message = {
        type: 'test_message',
        data: { index: i },
        timestamp: new Date().toISOString()
      };
      
      (window as any).wsClient.socket.send(JSON.stringify(message));
    }

    // Simulate disconnection
    mockWs.close();

    // Try to send 10 more messages while disconnected
    for (let i = 10; i < 20; i++) {
      const message = {
        type: 'test_message',
        data: { index: i },
        timestamp: new Date().toISOString()
      };
      
      // This should not throw an error, but the messages won't be sent
      try {
        (window as any).wsClient.socket.send(JSON.stringify(message));
      } catch (error) {
        // Ignore errors
      }
    }

    // Create a new mock WebSocket for reconnection
    const newMockWs = new MockWebSocket('ws://localhost:8765');
    (global as any).WebSocket = vi.fn(() => newMockWs);

    // Advance timers to trigger reconnection
    vi.advanceTimersByTime(1000);

    // Simulate connection on the new WebSocket
    newMockWs.simulateConnection();

    // Send 10 more messages after reconnection
    for (let i = 20; i < 30; i++) {
      const message = {
        type: 'test_message',
        data: { index: i },
        timestamp: new Date().toISOString()
      };
      
      (window as any).wsClient.socket.send(JSON.stringify(message));
    }

    // Check that the first 10 messages were sent
    expect(mockWs.sentMessages.length).toBe(10);
    
    // Check that the last 10 messages were sent to the new WebSocket
    expect(newMockWs.sentMessages.length).toBe(10);
    
    // Check message indices
    for (let i = 0; i < 10; i++) {
      expect(mockWs.sentMessages[i].data.index).toBe(i);
    }
    
    for (let i = 0; i < 10; i++) {
      expect(newMockWs.sentMessages[i].data.index).toBe(i + 20);
    }
  });

  it('should handle send failures gracefully', async () => {
    const client = new WebSocketClient('ws://localhost:8765');
    client.connect();

    // Simulate connection
    mockWs.simulateConnection();

    // Make sends fail
    mockWs.shouldFail = true;

    // Send 10 messages that will fail
    for (let i = 0; i < 10; i++) {
      const message = {
        type: 'test_message',
        data: { index: i },
        timestamp: new Date().toISOString()
      };
      
      try {
        (window as any).wsClient.socket.send(JSON.stringify(message));
      } catch (error) {
        // Errors should be caught and logged, but not crash the application
      }
    }

    // Make sends succeed again
    mockWs.shouldFail = false;

    // Send 10 more messages that should succeed
    for (let i = 10; i < 20; i++) {
      const message = {
        type: 'test_message',
        data: { index: i },
        timestamp: new Date().toISOString()
      };
      
      (window as any).wsClient.socket.send(JSON.stringify(message));
    }

    // Check that the successful messages were sent
    expect(mockWs.sentMessages.length).toBe(10);
    
    // Check message indices
    for (let i = 0; i < 10; i++) {
      expect(mockWs.sentMessages[i].data.index).toBe(i + 10);
    }
  });
});
