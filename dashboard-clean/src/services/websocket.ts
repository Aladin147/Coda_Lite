// WebSocket service for communication with the Coda backend

// Types for WebSocket messages
export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: number;
}

// WebSocket service class
class WebSocketService {
  private socket: WebSocket | null = null;
  private url: string;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private reconnectTimeout: number = 2000; // Start with 2 seconds
  private reconnectTimer: number | null = null;
  private messageListeners: ((message: WebSocketMessage) => void)[] = [];
  private statusListeners: ((connected: boolean) => void)[] = [];

  constructor(url: string = 'ws://localhost:8765') {
    this.url = url;
  }

  // Connect to the WebSocket server
  connect(): void {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      console.log('WebSocket is already connected or connecting');
      return;
    }

    console.log(`Connecting to WebSocket at ${this.url}`);

    try {
      this.socket = new WebSocket(this.url);

      this.socket.onopen = this.handleOpen.bind(this);
      this.socket.onmessage = this.handleMessage.bind(this);
      this.socket.onclose = this.handleClose.bind(this);
      this.socket.onerror = this.handleError.bind(this);
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      this.notifyStatusListeners(false);
      this.scheduleReconnect();
    }
  }

  // Disconnect from the WebSocket server
  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }

    if (this.reconnectTimer !== null) {
      window.clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    this.reconnectAttempts = 0;
    this.notifyStatusListeners(false);
  }

  // Send a message to the WebSocket server
  send(message: WebSocketMessage): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    } else {
      console.warn('Cannot send message, WebSocket is not connected');
    }
  }

  // Add a listener for incoming messages
  addMessageListener(listener: (message: WebSocketMessage) => void): void {
    this.messageListeners.push(listener);
  }

  // Remove a message listener
  removeMessageListener(listener: (message: WebSocketMessage) => void): void {
    this.messageListeners = this.messageListeners.filter(l => l !== listener);
  }

  // Add a listener for connection status changes
  addStatusListener(listener: (connected: boolean) => void): void {
    this.statusListeners.push(listener);
    // Immediately notify the listener of the current status
    if (this.socket) {
      listener(this.socket.readyState === WebSocket.OPEN);
    } else {
      listener(false);
    }
  }

  // Remove a status listener
  removeStatusListener(listener: (connected: boolean) => void): void {
    this.statusListeners = this.statusListeners.filter(l => l !== listener);
  }

  // Check if the WebSocket is connected
  isConnected(): boolean {
    return this.socket !== null && this.socket.readyState === WebSocket.OPEN;
  }

  // Handle WebSocket open event
  private handleOpen(event: Event): void {
    console.log('WebSocket connected');
    this.reconnectAttempts = 0;
    this.notifyStatusListeners(true);
  }

  // Handle WebSocket message event
  private handleMessage(event: MessageEvent): void {
    try {
      const message = JSON.parse(event.data) as WebSocketMessage;
      this.notifyMessageListeners(message);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  // Handle WebSocket close event
  private handleClose(event: CloseEvent): void {
    console.log(`WebSocket disconnected: ${event.code} ${event.reason}`);
    this.socket = null;
    this.notifyStatusListeners(false);
    this.scheduleReconnect();
  }

  // Handle WebSocket error event
  private handleError(event: Event): void {
    console.error('WebSocket error:', event);
    this.notifyStatusListeners(false);
  }

  // Notify all message listeners of a new message
  private notifyMessageListeners(message: WebSocketMessage): void {
    this.messageListeners.forEach(listener => {
      try {
        listener(message);
      } catch (error) {
        console.error('Error in message listener:', error);
      }
    });
  }

  // Notify all status listeners of a connection status change
  private notifyStatusListeners(connected: boolean): void {
    this.statusListeners.forEach(listener => {
      try {
        listener(connected);
      } catch (error) {
        console.error('Error in status listener:', error);
      }
    });
  }

  // Schedule a reconnect attempt
  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Maximum reconnect attempts reached');
      return;
    }

    if (this.reconnectTimer !== null) {
      window.clearTimeout(this.reconnectTimer);
    }

    const timeout = this.reconnectTimeout * Math.pow(1.5, this.reconnectAttempts);
    console.log(`Scheduling reconnect in ${timeout}ms`);

    this.reconnectTimer = window.setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, timeout);
  }
}

// Create a singleton instance
const websocketService = new WebSocketService();

export default websocketService;
