import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Simple message queue implementation for testing
class MessageQueue {
  private queue: any[] = [];
  private isSending: boolean = false;
  private socket: any;
  
  constructor(socket: any) {
    this.socket = socket;
  }
  
  enqueue(type: string, data: any = {}) {
    const message = {
      type,
      data,
      timestamp: new Date().toISOString()
    };
    
    this.queue.push(message);
    this.processQueue();
    
    return message;
  }
  
  processQueue() {
    if (this.isSending || this.queue.length === 0) {
      return;
    }
    
    this.isSending = true;
    const message = this.queue.shift();
    
    try {
      this.socket.send(JSON.stringify(message));
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      this.isSending = false;
      
      // Process next message after a small delay
      setTimeout(() => this.processQueue(), 50);
    }
  }
  
  getQueueLength() {
    return this.queue.length;
  }
  
  clear() {
    this.queue = [];
  }
}

describe('MessageQueue', () => {
  let mockSocket: any;
  let messageQueue: MessageQueue;
  let sentMessages: any[] = [];
  
  beforeEach(() => {
    // Reset sent messages
    sentMessages = [];
    
    // Create mock socket
    mockSocket = {
      send: vi.fn((data) => {
        sentMessages.push(JSON.parse(data));
      })
    };
    
    // Create message queue
    messageQueue = new MessageQueue(mockSocket);
    
    // Mock setTimeout
    vi.useFakeTimers();
  });
  
  afterEach(() => {
    vi.restoreAllMocks();
  });
  
  it('should enqueue and send a message', () => {
    messageQueue.enqueue('test_message', { foo: 'bar' });
    
    expect(mockSocket.send).toHaveBeenCalled();
    expect(sentMessages.length).toBe(1);
    expect(sentMessages[0].type).toBe('test_message');
    expect(sentMessages[0].data.foo).toBe('bar');
  });
  
  it('should process messages in order', () => {
    messageQueue.enqueue('message1', { index: 1 });
    messageQueue.enqueue('message2', { index: 2 });
    messageQueue.enqueue('message3', { index: 3 });
    
    // First message should be sent immediately
    expect(mockSocket.send).toHaveBeenCalledTimes(1);
    expect(sentMessages.length).toBe(1);
    expect(sentMessages[0].type).toBe('message1');
    
    // Advance timers to process next message
    vi.advanceTimersByTime(50);
    
    expect(mockSocket.send).toHaveBeenCalledTimes(2);
    expect(sentMessages.length).toBe(2);
    expect(sentMessages[1].type).toBe('message2');
    
    // Advance timers to process last message
    vi.advanceTimersByTime(50);
    
    expect(mockSocket.send).toHaveBeenCalledTimes(3);
    expect(sentMessages.length).toBe(3);
    expect(sentMessages[2].type).toBe('message3');
  });
  
  it('should handle rapid message enqueueing', () => {
    // Enqueue 10 messages rapidly
    for (let i = 0; i < 10; i++) {
      messageQueue.enqueue('test_message', { index: i });
    }
    
    // First message should be sent immediately
    expect(mockSocket.send).toHaveBeenCalledTimes(1);
    expect(sentMessages.length).toBe(1);
    expect(sentMessages[0].data.index).toBe(0);
    
    // Queue should have 9 messages left
    expect(messageQueue.getQueueLength()).toBe(9);
    
    // Process all remaining messages
    for (let i = 0; i < 9; i++) {
      vi.advanceTimersByTime(50);
    }
    
    // All messages should be sent
    expect(mockSocket.send).toHaveBeenCalledTimes(10);
    expect(sentMessages.length).toBe(10);
    
    // Messages should be sent in order
    for (let i = 0; i < 10; i++) {
      expect(sentMessages[i].data.index).toBe(i);
    }
    
    // Queue should be empty
    expect(messageQueue.getQueueLength()).toBe(0);
  });
  
  it('should handle socket errors', () => {
    // Mock console.error
    const consoleErrorMock = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    // Make socket.send throw an error
    mockSocket.send = vi.fn(() => {
      throw new Error('Socket error');
    });
    
    // Enqueue a message
    messageQueue.enqueue('test_message', { foo: 'bar' });
    
    // Error should be logged
    expect(consoleErrorMock).toHaveBeenCalled();
    
    // Queue should continue processing
    messageQueue.enqueue('another_message', { baz: 'qux' });
    
    // Advance timers to process next message
    vi.advanceTimersByTime(50);
    
    // Another error should be logged
    expect(consoleErrorMock).toHaveBeenCalledTimes(2);
  });
  
  it('should clear the queue', () => {
    // Enqueue several messages
    for (let i = 0; i < 5; i++) {
      messageQueue.enqueue('test_message', { index: i });
    }
    
    // First message should be sent immediately
    expect(mockSocket.send).toHaveBeenCalledTimes(1);
    
    // Queue should have 4 messages left
    expect(messageQueue.getQueueLength()).toBe(4);
    
    // Clear the queue
    messageQueue.clear();
    
    // Queue should be empty
    expect(messageQueue.getQueueLength()).toBe(0);
    
    // Advance timers
    vi.advanceTimersByTime(50);
    
    // No more messages should be sent
    expect(mockSocket.send).toHaveBeenCalledTimes(1);
  });
});
