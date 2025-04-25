/**
 * WebSocket client for connecting to the Coda WebSocket server.
 */
class WebSocketClient {
  url: string;
  socket: WebSocket | null;
  reconnectAttempts: number;
  maxReconnectAttempts: number;
  reconnectDelay: number;
  
  // Event handlers
  onConnect: () => void;
  onDisconnect: () => void;
  onEvent: (event: any) => void;
  onError: (error: any) => void;

  /**
   * Create a new WebSocket client.
   *
   * @param url - The WebSocket server URL
   */
  constructor(url: string) {
    // Ensure we're always connecting to port 8765 regardless of what port the dashboard is running on
    this.url = 'ws://localhost:8765';
    this.socket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;

    // Initialize event handlers with empty functions
    this.onConnect = () => {};
    this.onDisconnect = () => {};
    this.onEvent = () => {};
    this.onError = () => {};
  }

  /**
   * Connect to the WebSocket server.
   */
  connect() {
    try {
      console.log(`Connecting to WebSocket server at ${this.url}`);
      this.socket = new WebSocket(this.url);

      // Store the client in the window object for global access
      (window as any).wsClient = this;

      this.socket.onopen = () => {
        console.log(`Connected to ${this.url}`);
        this.reconnectAttempts = 0;
        this.onConnect();
      };

      this.socket.onclose = (event) => {
        console.log(`Disconnected from ${this.url}: ${event.code} ${event.reason}`);
        this.onDisconnect();
        this.reconnect();
      };

      this.socket.onerror = (error) => {
        console.error(`WebSocket error:`, error);
        this.onError(error);
      };

      this.socket.onmessage = (message) => {
        try {
          const event = JSON.parse(message.data);

          // Handle replay events
          if (event.type === 'replay' && Array.isArray(event.events)) {
            console.log(`Received replay with ${event.events.length} events`);
            event.events.forEach((replayEvent: any) => {
              this.onEvent(replayEvent);
            });
          } else {
            this.onEvent(event);
          }
        } catch (error) {
          console.error(`Error parsing message:`, error);
        }
      };
    } catch (error) {
      console.error(`Error connecting to ${this.url}:`, error);
      this.onError(error);
      this.reconnect();
    }
  }

  /**
   * Disconnect from the WebSocket server.
   */
  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;

      // Remove the client from the window object
      if ((window as any).wsClient === this) {
        (window as any).wsClient = null;
      }
    }
  }

  /**
   * Reconnect to the WebSocket server.
   */
  reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log(`Maximum reconnect attempts (${this.maxReconnectAttempts}) reached`);
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      console.log(`Attempting to reconnect to ${this.url}`);
      this.connect();
    }, delay);
  }

  /**
   * Check if the client is connected.
   *
   * @returns True if connected, false otherwise
   */
  isConnected() {
    return this.socket && this.socket.readyState === WebSocket.OPEN;
  }
}

export default WebSocketClient;
