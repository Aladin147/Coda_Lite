/**
 * WebSocket client for connecting to the Coda WebSocket server.
 *
 * This is a legacy class that now uses the new WebSocket service.
 * New code should use the WebSocket service directly.
 */
import websocketService, { ConnectionState, EventType } from './services/websocket';

class WebSocketClient {
  /**
   * Create a new WebSocket client.
   *
   * @param {string} url - The WebSocket server URL
   */
  constructor(url) {
    // Ensure we're always connecting to port 8765 regardless of what port the dashboard is running on
    this.url = 'ws://localhost:8765';
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;

    // Event handlers
    this.onConnect = () => {};
    this.onDisconnect = () => {};
    this.onEvent = (event) => {};
    this.onError = (error) => {};

    // Set up connection state listener
    websocketService.addConnectionStateListener(this._handleConnectionStateChange.bind(this));

    // Set up event listeners for all event types
    Object.values(EventType).forEach(eventType => {
      websocketService.addEventListener(eventType, this._handleEvent.bind(this));
    });
  }

  /**
   * Handle connection state changes.
   *
   * @param {string} state - The new connection state
   */
  _handleConnectionStateChange(state) {
    if (state === ConnectionState.CONNECTED) {
      this.onConnect();
    } else if (state === ConnectionState.DISCONNECTED || state === ConnectionState.ERROR) {
      this.onDisconnect();
    }
  }

  /**
   * Handle WebSocket events.
   *
   * @param {Object} event - The WebSocket event
   */
  _handleEvent(event) {
    this.onEvent(event);
  }

  /**
   * Connect to the WebSocket server.
   */
  connect() {
    // Store the client in the window object for global access
    window.wsClient = this;

    // Connect using the WebSocket service
    websocketService.connect(this.url).catch(error => {
      console.error(`Error connecting to ${this.url}:`, error);
      this.onError(error);
    });
  }

  /**
   * Disconnect from the WebSocket server.
   */
  disconnect() {
    // Disconnect using the WebSocket service
    websocketService.disconnect();

    // Remove the client from the window object
    if (window.wsClient === this) {
      window.wsClient = null;
    }
  }

  /**
   * Check if the client is connected.
   *
   * @returns {boolean} True if connected, false otherwise
   */
  isConnected() {
    return websocketService.connectionState === ConnectionState.CONNECTED;
  }

  /**
   * Send a client message to the server.
   *
   * @param {string} messageType - The client message type
   * @param {Object} messageData - The client message data
   */
  sendClientMessage(messageType, messageData = {}) {
    websocketService.sendClientMessage(messageType, messageData);
  }

  /**
   * Send a push-to-talk request.
   *
   * @param {number} duration - The recording duration in seconds
   * @param {boolean} continuous - Whether to continue listening after the duration
   */
  sendPushToTalk(duration = 5, continuous = false) {
    websocketService.sendPushToTalk(duration, continuous);
  }

  /**
   * Send a stop listening request.
   */
  sendStopListening() {
    websocketService.sendStopListening();
  }

  /**
   * Send a stop speaking request.
   */
  sendStopSpeaking() {
    websocketService.sendStopSpeaking();
  }

  /**
   * Send a text input.
   *
   * @param {string} text - The text input
   */
  sendTextInput(text) {
    websocketService.sendTextInput(text);
  }
}

export default WebSocketClient;
