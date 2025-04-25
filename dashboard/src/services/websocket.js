/**
 * WebSocket service for the Coda dashboard.
 * 
 * This module provides a WebSocket client for communicating with the Coda WebSocket server.
 */

import { getToken, handleAuthChallenge, handleAuthResult, clearToken } from './auth';

// Default WebSocket URL
const DEFAULT_WS_URL = 'ws://localhost:8765';

// WebSocket connection states
export const ConnectionState = {
  DISCONNECTED: 'disconnected',
  CONNECTING: 'connecting',
  AUTHENTICATING: 'authenticating',
  CONNECTED: 'connected',
  ERROR: 'error'
};

// Event types
export const EventType = {
  CONVERSATION_TURN: 'conversation_turn',
  STT_START: 'stt_start',
  STT_INTERIM: 'stt_interim',
  STT_FINAL: 'stt_final',
  STT_END: 'stt_end',
  LLM_START: 'llm_start',
  LLM_TOKEN: 'llm_token',
  LLM_END: 'llm_end',
  TTS_START: 'tts_start',
  TTS_AUDIO: 'tts_audio',
  TTS_END: 'tts_end',
  MEMORY_WRITE: 'memory_write',
  MEMORY_READ: 'memory_read',
  SYSTEM_METRICS: 'system_metrics',
  TOOL_START: 'tool_start',
  TOOL_END: 'tool_end',
  DUPLICATE_MESSAGE: 'duplicate_message',
  AUTH_CHALLENGE: 'auth_challenge',
  AUTH_RESULT: 'auth_result'
};

class WebSocketService {
  constructor() {
    this.socket = null;
    this.url = DEFAULT_WS_URL;
    this.connectionState = ConnectionState.DISCONNECTED;
    this.eventHandlers = {};
    this.connectionStateHandlers = [];
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000; // Start with 1 second delay
    this.clientId = null;
    this.authenticated = false;
    this.messageQueue = []; // Queue for messages to send after authentication
    
    // Bind methods to this instance
    this.connect = this.connect.bind(this);
    this.disconnect = this.disconnect.bind(this);
    this.send = this.send.bind(this);
    this.onMessage = this.onMessage.bind(this);
    this.onOpen = this.onOpen.bind(this);
    this.onClose = this.onClose.bind(this);
    this.onError = this.onError.bind(this);
    this.reconnect = this.reconnect.bind(this);
    this.setConnectionState = this.setConnectionState.bind(this);
  }
  
  /**
   * Connect to the WebSocket server.
   * 
   * @param {string} url - The WebSocket URL (default: ws://localhost:8765)
   * @returns {Promise} A promise that resolves when connected and authenticated
   */
  connect(url = DEFAULT_WS_URL) {
    return new Promise((resolve, reject) => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        console.log('WebSocket already connected');
        resolve();
        return;
      }
      
      this.url = url;
      this.setConnectionState(ConnectionState.CONNECTING);
      
      try {
        this.socket = new WebSocket(url);
        
        this.socket.onopen = () => {
          console.log('WebSocket connection established');
          this.onOpen();
          
          // Wait for authentication before resolving
          const authHandler = (event) => {
            if (event.type === EventType.AUTH_RESULT) {
              if (event.data.success) {
                this.removeEventListener(EventType.AUTH_RESULT, authHandler);
                resolve();
              } else {
                this.removeEventListener(EventType.AUTH_RESULT, authHandler);
                reject(new Error(event.data.message || 'Authentication failed'));
              }
            }
          };
          
          this.addEventListener(EventType.AUTH_RESULT, authHandler);
        };
        
        this.socket.onmessage = (event) => {
          this.onMessage(event);
        };
        
        this.socket.onclose = (event) => {
          this.onClose(event);
          reject(new Error('WebSocket connection closed'));
        };
        
        this.socket.onerror = (error) => {
          this.onError(error);
          reject(error);
        };
      } catch (error) {
        this.setConnectionState(ConnectionState.ERROR);
        console.error('Error connecting to WebSocket:', error);
        reject(error);
      }
    });
  }
  
  /**
   * Disconnect from the WebSocket server.
   */
  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.setConnectionState(ConnectionState.DISCONNECTED);
      console.log('WebSocket disconnected');
    }
  }
  
  /**
   * Send a message to the WebSocket server.
   * 
   * @param {string} type - The message type
   * @param {Object} data - The message data
   */
  send(type, data = {}) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected, queueing message:', type);
      this.messageQueue.push({ type, data });
      return;
    }
    
    if (!this.authenticated && type !== 'auth_response') {
      console.warn('Not authenticated, queueing message:', type);
      this.messageQueue.push({ type, data });
      return;
    }
    
    const message = {
      type,
      data
    };
    
    try {
      this.socket.send(JSON.stringify(message));
    } catch (error) {
      console.error('Error sending WebSocket message:', error);
    }
  }
  
  /**
   * Handle a WebSocket message.
   * 
   * @param {MessageEvent} event - The WebSocket message event
   */
  onMessage(event) {
    try {
      const message = JSON.parse(event.data);
      const { type, data } = message;
      
      // Handle authentication messages
      if (type === EventType.AUTH_CHALLENGE) {
        console.log('Received authentication challenge');
        this.setConnectionState(ConnectionState.AUTHENTICATING);
        handleAuthChallenge(message, this.socket);
        return;
      }
      
      if (type === EventType.AUTH_RESULT) {
        console.log('Received authentication result');
        handleAuthResult(message, 
          // Success callback
          (clientId) => {
            this.clientId = clientId;
            this.authenticated = true;
            this.setConnectionState(ConnectionState.CONNECTED);
            this.reconnectAttempts = 0;
            
            // Send any queued messages
            while (this.messageQueue.length > 0) {
              const { type, data } = this.messageQueue.shift();
              this.send(type, data);
            }
          },
          // Failure callback
          (message) => {
            this.setConnectionState(ConnectionState.ERROR);
            this.disconnect();
          }
        );
      }
      
      // Handle duplicate message notifications
      if (type === EventType.DUPLICATE_MESSAGE) {
        console.warn('Duplicate message detected:', data.original_type, 'count:', data.count);
      }
      
      // Notify event handlers
      this.notifyEventHandlers(type, data);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }
  
  /**
   * Handle WebSocket connection open.
   */
  onOpen() {
    console.log('WebSocket connection opened');
    // Authentication will be handled by the server sending an auth_challenge
  }
  
  /**
   * Handle WebSocket connection close.
   * 
   * @param {CloseEvent} event - The WebSocket close event
   */
  onClose(event) {
    this.authenticated = false;
    
    if (event.wasClean) {
      console.log(`WebSocket connection closed cleanly, code=${event.code}, reason=${event.reason}`);
      this.setConnectionState(ConnectionState.DISCONNECTED);
    } else {
      console.error('WebSocket connection died');
      this.setConnectionState(ConnectionState.ERROR);
      this.reconnect();
    }
  }
  
  /**
   * Handle WebSocket connection error.
   * 
   * @param {Event} error - The WebSocket error event
   */
  onError(error) {
    console.error('WebSocket error:', error);
    this.setConnectionState(ConnectionState.ERROR);
  }
  
  /**
   * Attempt to reconnect to the WebSocket server.
   */
  reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error(`Maximum reconnect attempts (${this.maxReconnectAttempts}) reached`);
      return;
    }
    
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      this.connect(this.url).catch((error) => {
        console.error('Reconnect failed:', error);
      });
    }, delay);
  }
  
  /**
   * Set the connection state and notify handlers.
   * 
   * @param {string} state - The new connection state
   */
  setConnectionState(state) {
    if (this.connectionState !== state) {
      this.connectionState = state;
      this.notifyConnectionStateHandlers(state);
    }
  }
  
  /**
   * Add an event listener.
   * 
   * @param {string} type - The event type
   * @param {Function} handler - The event handler
   */
  addEventListener(type, handler) {
    if (!this.eventHandlers[type]) {
      this.eventHandlers[type] = [];
    }
    
    this.eventHandlers[type].push(handler);
  }
  
  /**
   * Remove an event listener.
   * 
   * @param {string} type - The event type
   * @param {Function} handler - The event handler
   */
  removeEventListener(type, handler) {
    if (!this.eventHandlers[type]) {
      return;
    }
    
    this.eventHandlers[type] = this.eventHandlers[type].filter(h => h !== handler);
  }
  
  /**
   * Add a connection state listener.
   * 
   * @param {Function} handler - The connection state handler
   */
  addConnectionStateListener(handler) {
    this.connectionStateHandlers.push(handler);
    
    // Immediately notify the handler of the current state
    handler(this.connectionState);
  }
  
  /**
   * Remove a connection state listener.
   * 
   * @param {Function} handler - The connection state handler
   */
  removeConnectionStateListener(handler) {
    this.connectionStateHandlers = this.connectionStateHandlers.filter(h => h !== handler);
  }
  
  /**
   * Notify all event handlers for a specific event type.
   * 
   * @param {string} type - The event type
   * @param {Object} data - The event data
   */
  notifyEventHandlers(type, data) {
    if (!this.eventHandlers[type]) {
      return;
    }
    
    for (const handler of this.eventHandlers[type]) {
      try {
        handler({ type, data });
      } catch (error) {
        console.error(`Error in event handler for ${type}:`, error);
      }
    }
  }
  
  /**
   * Notify all connection state handlers.
   * 
   * @param {string} state - The connection state
   */
  notifyConnectionStateHandlers(state) {
    for (const handler of this.connectionStateHandlers) {
      try {
        handler(state);
      } catch (error) {
        console.error('Error in connection state handler:', error);
      }
    }
  }
  
  /**
   * Send a client message to the server.
   * 
   * @param {string} messageType - The client message type
   * @param {Object} messageData - The client message data
   */
  sendClientMessage(messageType, messageData = {}) {
    this.send('client_message', {
      message_type: messageType,
      message_data: messageData
    });
  }
  
  /**
   * Send a push-to-talk request.
   * 
   * @param {number} duration - The recording duration in seconds
   * @param {boolean} continuous - Whether to continue listening after the duration
   */
  sendPushToTalk(duration = 5, continuous = false) {
    this.sendClientMessage('push_to_talk', {
      duration,
      continuous
    });
  }
  
  /**
   * Send a stop listening request.
   */
  sendStopListening() {
    this.sendClientMessage('stop_listening');
  }
  
  /**
   * Send a stop speaking request.
   */
  sendStopSpeaking() {
    this.sendClientMessage('stop_speaking');
  }
  
  /**
   * Send a text input.
   * 
   * @param {string} text - The text input
   */
  sendTextInput(text) {
    this.sendClientMessage('text_input', {
      text
    });
  }
}

// Create a singleton instance
const websocketService = new WebSocketService();

export default websocketService;
