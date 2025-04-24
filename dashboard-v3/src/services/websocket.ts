import { CodaEvent } from '../types/events';

/**
 * Interface for WebSocket observers
 */
export interface WebSocketObserver {
  onConnect: () => void;
  onDisconnect: () => void;
  onEvent: (event: CodaEvent) => void;
  onError: (error: Error) => void;
  onReconnecting?: (attempt: number) => void;
}

/**
 * WebSocket service for communicating with the Coda backend
 */
export class WebSocketService {
  private socket: WebSocket | null = null;
  private url: string;
  private observers: WebSocketObserver[] = [];
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout: number | null = null;
  private isConnecting = false;
  private isReconnecting = false;

  constructor(url: string) {
    this.url = url;
  }

  /**
   * Connect to the WebSocket server
   */
  public connect(): void {
    if (this.socket || this.isConnecting) {
      console.log('WebSocket already connected or connecting');
      return;
    }

    this.isConnecting = true;
    console.log(`Connecting to WebSocket at ${this.url}`);

    try {
      // Create a new WebSocket connection with proper protocol
      this.socket = new WebSocket(this.url);

      console.log('WebSocket object created, waiting for connection...');

      this.socket.onopen = () => {
        console.log('WebSocket connection established successfully');
        this.reconnectAttempts = 0;
        this.isConnecting = false;
        this.isReconnecting = false;
        this.notifyObservers('onConnect');

        // Send a ping message to test the connection
        this.send('ping', { timestamp: new Date().toISOString() });
      };

      this.socket.onclose = (event) => {
        console.log(`WebSocket connection closed: ${event.code} ${event.reason}`);
        this.socket = null;
        this.isConnecting = false;
        this.notifyObservers('onDisconnect');
        this.attemptReconnect();
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.notifyObservers('onError', new Error('WebSocket connection error'));
      };

      this.socket.onmessage = (event) => {
        try {
          console.log('WebSocket message received:', event.data);
          const data = JSON.parse(event.data);
          console.log('Parsed WebSocket message:', data);
          this.notifyObservers('onEvent', data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
          console.error('Raw message data:', event.data);
          this.notifyObservers('onError', new Error('Failed to parse WebSocket message'));
        }
      };
    } catch (error) {
      this.isConnecting = false;
      this.notifyObservers('onError', error instanceof Error ? error : new Error('Unknown error'));
      this.attemptReconnect();
    }
  }

  /**
   * Disconnect from the WebSocket server
   */
  public disconnect(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  /**
   * Send a message to the WebSocket server
   * @param type The message type or a complete message object
   * @param data Optional data to include in the message
   */
  public send(type: string | any, data?: any): void {
    if (!this.socket) {
      console.error('Cannot send message: WebSocket not initialized', type, data);
      this.notifyObservers('onError', new Error('WebSocket is not initialized'));
      return;
    }

    if (this.socket.readyState !== WebSocket.OPEN) {
      console.error('Cannot send message: WebSocket not connected (state:', this.socket.readyState, ')', type, data);
      this.notifyObservers('onError', new Error(`WebSocket is not connected (state: ${this.socket.readyState})`));
      return;
    }

    try {
      let message: any;

      // Check if the first parameter is a string (type) or a complete message object
      if (typeof type === 'string') {
        // Format the message with type and data
        message = {
          type,
          data: data || {},
          timestamp: new Date().toISOString()
        };
      } else {
        // The first parameter is already a complete message object
        message = type;
      }

      const messageStr = JSON.stringify(message);
      console.log('Sending WebSocket message:', messageStr);
      this.socket.send(messageStr);
      console.log('Message sent successfully');
    } catch (error) {
      console.error('Error sending message:', error);
      this.notifyObservers('onError', error instanceof Error ? error : new Error('Failed to send message'));
    }
  }

  /**
   * Add an observer to the WebSocket service
   */
  public addObserver(observer: WebSocketObserver): void {
    this.observers.push(observer);
  }

  /**
   * Remove an observer from the WebSocket service
   */
  public removeObserver(observer: WebSocketObserver): void {
    this.observers = this.observers.filter(obs => obs !== observer);
  }

  /**
   * Check if the WebSocket is connected
   */
  public isConnected(): boolean {
    return this.socket !== null && this.socket.readyState === WebSocket.OPEN;
  }

  /**
   * Get the connection status
   */
  public getConnectionStatus(): boolean {
    return this.isConnected();
  }

  /**
   * Get detailed connection information for debugging
   */
  public getConnectionInfo(): { connected: boolean; state: number; stateDesc: string } {
    if (!this.socket) {
      return {
        connected: false,
        state: -1,
        stateDesc: 'Not initialized'
      };
    }

    const stateMap = {
      [WebSocket.CONNECTING]: 'Connecting',
      [WebSocket.OPEN]: 'Open',
      [WebSocket.CLOSING]: 'Closing',
      [WebSocket.CLOSED]: 'Closed'
    };

    return {
      connected: this.socket.readyState === WebSocket.OPEN,
      state: this.socket.readyState,
      stateDesc: stateMap[this.socket.readyState] || 'Unknown'
    };
  }

  /**
   * Check if the WebSocket is reconnecting
   */
  public isReconnectingStatus(): boolean {
    return this.isReconnecting;
  }

  /**
   * Get the current reconnect attempt
   */
  public getReconnectAttempt(): number {
    return this.reconnectAttempts;
  }

  /**
   * Attempt to reconnect to the WebSocket server
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.notifyObservers('onError', new Error('Maximum reconnect attempts reached'));
      this.isReconnecting = false;
      return;
    }

    this.reconnectAttempts++;
    this.isReconnecting = true;

    // Notify observers that we're reconnecting
    this.observers.forEach(observer => {
      if (observer.onReconnecting) {
        observer.onReconnecting(this.reconnectAttempts);
      }
    });

    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);

    this.reconnectTimeout = window.setTimeout(() => {
      this.connect();
    }, delay);
  }

  /**
   * Notify all observers of an event
   */
  private notifyObservers(method: keyof WebSocketObserver, data?: any): void {
    this.observers.forEach(observer => {
      try {
        if (method === 'onEvent' && data) {
          observer.onEvent(data);
        } else if (method === 'onError' && data) {
          observer.onError(data);
        } else if (method === 'onConnect') {
          observer.onConnect();
        } else if (method === 'onDisconnect') {
          observer.onDisconnect();
        }
      } catch (error) {
        console.error('Error in WebSocket observer:', error);
      }
    });
  }
}
