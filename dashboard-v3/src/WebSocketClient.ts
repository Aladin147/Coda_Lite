/**
 * WebSocket client for connecting to the Coda WebSocket server.
 * This is a direct port of the original working implementation with added
 * instrumentation for debugging and analysis.
 */
class WebSocketClient {
  url: string;
  socket: WebSocket | null;
  reconnectAttempts: number;
  maxReconnectAttempts: number;
  reconnectDelay: number;
  clientId: string;
  messageCounter: number;
  sentMessages: Map<string, any>;

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

    // Generate a unique client ID for tracking
    this.clientId = `client_${Math.random().toString(36).substring(2, 10)}`;
    this.messageCounter = 0;

    // Keep track of sent messages for deduplication and debugging
    this.sentMessages = new Map();

    // Initialize event handlers with empty functions
    this.onConnect = () => {};
    this.onDisconnect = () => {};
    this.onEvent = () => {};
    this.onError = () => {};

    console.log(`[WebSocketClient] Created new client with ID: ${this.clientId}`);
  }

  /**
   * Connect to the WebSocket server.
   */
  connect() {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}][WebSocketClient:${this.clientId}] Connecting to ${this.url}`);

    try {
      // Check if there's an existing socket and close it first
      if (this.socket) {
        console.log(`[${timestamp}][WebSocketClient:${this.clientId}] Closing existing socket before creating a new one`);
        this.socket.close();
        this.socket = null;
      }

      this.socket = new WebSocket(this.url);

      // Store the client in the window object for global access
      if ((window as any).wsClient && (window as any).wsClient !== this) {
        console.warn(`[${timestamp}][WebSocketClient:${this.clientId}] Overwriting existing wsClient in window object`);
      }
      (window as any).wsClient = this;

      this.socket.onopen = () => {
        const openTimestamp = new Date().toISOString();
        console.log(`[${openTimestamp}][WebSocketClient:${this.clientId}] Connected to ${this.url}`);
        this.reconnectAttempts = 0;
        this.onConnect();
      };

      this.socket.onclose = (event) => {
        const closeTimestamp = new Date().toISOString();
        console.log(`[${closeTimestamp}][WebSocketClient:${this.clientId}] Disconnected from ${this.url}: ${event.code} ${event.reason}`);
        this.onDisconnect();
        this.reconnect();
      };

      this.socket.onerror = (error) => {
        const errorTimestamp = new Date().toISOString();
        console.error(`[${errorTimestamp}][WebSocketClient:${this.clientId}] WebSocket error:`, error);
        this.onError(error);
      };

      this.socket.onmessage = (message) => {
        const messageTimestamp = new Date().toISOString();
        try {
          const event = JSON.parse(message.data);
          console.log(`[${messageTimestamp}][WebSocketClient:${this.clientId}] Received message:`, event);

          // Handle replay events
          if (event.type === 'replay' && Array.isArray(event.events)) {
            console.log(`[${messageTimestamp}][WebSocketClient:${this.clientId}] Received replay with ${event.events.length} events`);
            event.events.forEach((replayEvent: any) => {
              this.onEvent(replayEvent);
            });
          } else {
            this.onEvent(event);
          }
        } catch (error) {
          console.error(`[${messageTimestamp}][WebSocketClient:${this.clientId}] Error parsing message:`, error, message.data);
        }
      };
    } catch (error) {
      const errorTimestamp = new Date().toISOString();
      console.error(`[${errorTimestamp}][WebSocketClient:${this.clientId}] Error connecting to ${this.url}:`, error);
      this.onError(error);
      this.reconnect();
    }
  }

  /**
   * Disconnect from the WebSocket server.
   */
  disconnect() {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}][WebSocketClient:${this.clientId}] Disconnecting from ${this.url}`);

    if (this.socket) {
      console.log(`[${timestamp}][WebSocketClient:${this.clientId}] Socket state before closing: ${this.getReadyStateString()}`);
      this.socket.close();
      this.socket = null;

      // Remove the client from the window object
      if ((window as any).wsClient === this) {
        console.log(`[${timestamp}][WebSocketClient:${this.clientId}] Removing client from window.wsClient`);
        (window as any).wsClient = null;
      } else if ((window as any).wsClient) {
        console.warn(`[${timestamp}][WebSocketClient:${this.clientId}] Not removing client from window.wsClient as it contains a different client`);
      }
    } else {
      console.log(`[${timestamp}][WebSocketClient:${this.clientId}] No socket to disconnect`);
    }
  }

  /**
   * Reconnect to the WebSocket server.
   */
  reconnect() {
    const timestamp = new Date().toISOString();

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log(`[${timestamp}][WebSocketClient:${this.clientId}] Maximum reconnect attempts (${this.maxReconnectAttempts}) reached`);
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(`[${timestamp}][WebSocketClient:${this.clientId}] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      const reconnectTimestamp = new Date().toISOString();
      console.log(`[${reconnectTimestamp}][WebSocketClient:${this.clientId}] Attempting to reconnect to ${this.url}`);
      this.connect();
    }, delay);
  }

  /**
   * Get a string representation of the WebSocket ready state
   */
  private getReadyStateString(): string {
    if (!this.socket) return 'null';

    switch (this.socket.readyState) {
      case WebSocket.CONNECTING: return 'CONNECTING';
      case WebSocket.OPEN: return 'OPEN';
      case WebSocket.CLOSING: return 'CLOSING';
      case WebSocket.CLOSED: return 'CLOSED';
      default: return `UNKNOWN (${this.socket.readyState})`;
    }
  }

  /**
   * Check if the client is connected.
   *
   * @returns True if connected, false otherwise
   */
  isConnected() {
    const connected = this.socket && this.socket.readyState === WebSocket.OPEN;
    return connected;
  }

  /**
   * Send a message to the WebSocket server with instrumentation
   *
   * @param type Message type
   * @param data Message data
   * @returns Message ID for tracking
   */
  sendMessage(type: string, data: any = {}) {
    const timestamp = new Date().toISOString();
    this.messageCounter++;

    // Generate a unique message ID
    const messageId = `${this.clientId}_${this.messageCounter}_${Math.random().toString(36).substring(2, 10)}`;

    // Create the message
    const message = {
      type,
      data,
      timestamp,
      _debug: {
        messageId,
        clientId: this.clientId,
        counter: this.messageCounter
      }
    };

    console.log(`[${timestamp}][WebSocketClient:${this.clientId}] Preparing to send message:`, message);

    // Check if connected
    if (!this.isConnected()) {
      console.error(`[${timestamp}][WebSocketClient:${this.clientId}] Cannot send message: WebSocket not connected (state: ${this.getReadyStateString()})`);
      return messageId;
    }

    // Check for duplicate messages (same type and data within the last 500ms)
    const messageFingerprint = `${type}_${JSON.stringify(data)}`;
    const recentMessages = Array.from(this.sentMessages.values())
      .filter(m =>
        m.fingerprint === messageFingerprint &&
        Date.now() - m.sentAt < 500
      );

    if (recentMessages.length > 0) {
      console.warn(`[${timestamp}][WebSocketClient:${this.clientId}] Potential duplicate message detected:`, {
        current: message,
        previous: recentMessages
      });
    }

    // Store message in sent messages map
    this.sentMessages.set(messageId, {
      message,
      fingerprint: messageFingerprint,
      sentAt: Date.now()
    });

    // Limit the size of the sent messages map
    if (this.sentMessages.size > 100) {
      // Remove the oldest messages
      const keys = Array.from(this.sentMessages.keys());
      const oldestKeys = keys.slice(0, keys.length - 100);
      oldestKeys.forEach(key => this.sentMessages.delete(key));
    }

    // Send the message
    try {
      const messageStr = JSON.stringify(message);
      console.log(`[${timestamp}][WebSocketClient:${this.clientId}] Sending message:`, messageStr);
      this.socket!.send(messageStr);
      console.log(`[${timestamp}][WebSocketClient:${this.clientId}] Message sent successfully: ${messageId}`);
    } catch (error) {
      console.error(`[${timestamp}][WebSocketClient:${this.clientId}] Error sending message:`, error);
    }

    return messageId;
  }
}

export default WebSocketClient;
