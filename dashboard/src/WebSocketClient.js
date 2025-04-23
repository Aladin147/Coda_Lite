/**
 * WebSocket client for connecting to the Coda WebSocket server.
 */
class WebSocketClient {
  /**
   * Create a new WebSocket client.
   * 
   * @param {string} url - The WebSocket server URL
   */
  constructor(url) {
    this.url = url;
    this.socket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    
    // Event handlers
    this.onConnect = () => {};
    this.onDisconnect = () => {};
    this.onEvent = (event) => {};
    this.onError = (error) => {};
  }
  
  /**
   * Connect to the WebSocket server.
   */
  connect() {
    try {
      this.socket = new WebSocket(this.url);
      
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
        console.error(`WebSocket error: ${error}`);
        this.onError(error);
      };
      
      this.socket.onmessage = (message) => {
        try {
          const event = JSON.parse(message.data);
          
          // Handle replay events
          if (event.type === 'replay' && Array.isArray(event.events)) {
            console.log(`Received replay with ${event.events.length} events`);
            event.events.forEach(replayEvent => {
              this.onEvent(replayEvent);
            });
          } else {
            this.onEvent(event);
          }
        } catch (error) {
          console.error(`Error parsing message: ${error}`);
        }
      };
    } catch (error) {
      console.error(`Error connecting to ${this.url}: ${error}`);
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
   * @returns {boolean} True if connected, false otherwise
   */
  isConnected() {
    return this.socket && this.socket.readyState === WebSocket.OPEN;
  }
}

export default WebSocketClient;
