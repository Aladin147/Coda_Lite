import { CodaEvent, BaseEvent } from '../types/events';

/**
 * Observer interface for WebSocket events
 */
export interface WebSocketObserver {
  onEvent(event: CodaEvent): void;
  onConnect?(): void;
  onDisconnect?(): void;
  onError?(error: Error): void;
}

/**
 * WebSocket service for communicating with the Coda backend
 */
export class WebSocketService {
  private url: string;
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // ms
  private observers: WebSocketObserver[] = [];
  private messageBuffer: CodaEvent[] = [];
  private isConnected = false;
  private reconnectTimer: number | null = null;

  /**
   * Create a new WebSocket service
   * @param url The WebSocket server URL
   */
  constructor(url: string = 'ws://localhost:8765') {
    this.url = url;
  }

  /**
   * Add an observer to receive WebSocket events
   * @param observer The observer to add
   */
  addObserver(observer: WebSocketObserver): void {
    this.observers.push(observer);
    
    // If we're already connected, notify the observer
    if (this.isConnected && observer.onConnect) {
      observer.onConnect();
    }
    
    // Send buffered messages to the new observer
    if (this.messageBuffer.length > 0) {
      this.messageBuffer.forEach(event => observer.onEvent(event));
    }
  }

  /**
   * Remove an observer
   * @param observer The observer to remove
   */
  removeObserver(observer: WebSocketObserver): void {
    const index = this.observers.indexOf(observer);
    if (index !== -1) {
      this.observers.splice(index, 1);
    }
  }

  /**
   * Connect to the WebSocket server
   */
  connect(): void {
    try {
      this.socket = new WebSocket(this.url);

      this.socket.onopen = () => {
        console.log(`Connected to ${this.url}`);
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.notifyObservers('connect');
      };

      this.socket.onclose = (event) => {
        console.log(`Disconnected from ${this.url}: ${event.code} ${event.reason}`);
        this.isConnected = false;
        this.notifyObservers('disconnect');
        this.reconnect();
      };

      this.socket.onerror = (error) => {
        console.error(`WebSocket error:`, error);
        this.notifyObservers('error', error);
      };

      this.socket.onmessage = (message) => {
        try {
          const event = JSON.parse(message.data) as CodaEvent;
          
          // Handle replay events
          if (event.type === 'replay' && Array.isArray(event.data?.events)) {
            console.log(`Received replay with ${event.data.events.length} events`);
            event.data.events.forEach(replayEvent => {
              this.bufferMessage(replayEvent);
              this.notifyObservers('event', replayEvent);
            });
          } else {
            this.bufferMessage(event);
            this.notifyObservers('event', event);
          }
        } catch (error) {
          console.error(`Error parsing message:`, error);
        }
      };
    } catch (error) {
      console.error(`Error connecting to ${this.url}:`, error);
      this.notifyObservers('error', error);
      this.reconnect();
    }
  }

  /**
   * Disconnect from the WebSocket server
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    
    // Clear any pending reconnect timer
    if (this.reconnectTimer !== null) {
      window.clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  /**
   * Send a message to the WebSocket server
   * @param type The message type
   * @param data The message data
   */
  send(type: string, data: any = {}): void {
    if (!this.isConnected || !this.socket) {
      console.error('Cannot send message: WebSocket not connected');
      return;
    }

    const message: BaseEvent = {
      type,
      data,
      timestamp: new Date().toISOString()
    };

    try {
      this.socket.send(JSON.stringify(message));
    } catch (error) {
      console.error('Error sending message:', error);
      this.notifyObservers('error', error);
    }
  }

  /**
   * Check if the WebSocket is connected
   */
  getConnectionStatus(): boolean {
    return this.isConnected;
  }

  /**
   * Get the buffered messages
   */
  getMessageBuffer(): CodaEvent[] {
    return [...this.messageBuffer];
  }

  /**
   * Clear the message buffer
   */
  clearMessageBuffer(): void {
    this.messageBuffer = [];
  }

  /**
   * Attempt to reconnect to the WebSocket server
   */
  private reconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log(`Maximum reconnect attempts (${this.maxReconnectAttempts}) reached`);
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    this.reconnectTimer = window.setTimeout(() => {
      console.log(`Attempting to reconnect to ${this.url}`);
      this.connect();
    }, delay);
  }

  /**
   * Buffer a message for new observers
   * @param event The event to buffer
   */
  private bufferMessage(event: CodaEvent): void {
    // Keep a limited buffer of recent messages (last 100)
    this.messageBuffer.unshift(event);
    if (this.messageBuffer.length > 100) {
      this.messageBuffer.pop();
    }
  }

  /**
   * Notify all observers of an event
   * @param type The event type
   * @param data The event data
   */
  private notifyObservers(type: 'connect' | 'disconnect' | 'error' | 'event', data?: any): void {
    this.observers.forEach(observer => {
      try {
        switch (type) {
          case 'connect':
            if (observer.onConnect) observer.onConnect();
            break;
          case 'disconnect':
            if (observer.onDisconnect) observer.onDisconnect();
            break;
          case 'error':
            if (observer.onError) observer.onError(data);
            break;
          case 'event':
            observer.onEvent(data);
            break;
        }
      } catch (error) {
        console.error(`Error notifying observer:`, error);
      }
    });
  }
}
