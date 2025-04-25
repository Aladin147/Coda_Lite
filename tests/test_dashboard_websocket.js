/**
 * Test script for the dashboard WebSocket client.
 *
 * This script tests the WebSocket client implementation in the dashboard.
 *
 * To run this test:
 * 1. Start the Coda WebSocket server
 * 2. Run this test with Node.js
 * 3. Make sure to install the ws package first: npm install ws
 */

// Import the WebSocket client
// Note: This requires the ws package to be installed
// If running this test directly, first run: npm install ws
let WebSocket;
try {
    WebSocket = require('ws');
} catch (error) {
    console.error('WebSocket module not found. Please install it with: npm install ws');
    console.log('For testing purposes, we will use a mock WebSocket implementation.');

    // Mock WebSocket implementation for testing
    WebSocket = class MockWebSocket {
        constructor(url) {
            this.url = url;
            this.readyState = 1; // OPEN
            console.log(`Mock WebSocket connected to ${url}`);

            // Simulate the connection opening
            setTimeout(() => {
                if (this.onopen) {
                    this.onopen();
                }

                // Simulate receiving an authentication challenge
                setTimeout(() => {
                    if (this.onmessage) {
                        this.onmessage({
                            data: JSON.stringify({
                                type: 'auth_challenge',
                                data: {
                                    token: 'mock_token_123',
                                    message: 'Please authenticate with this token'
                                }
                            })
                        });
                    }
                }, 100);
            }, 100);
        }

        send(data) {
            console.log(`Mock WebSocket sending: ${data}`);

            // Parse the message
            const message = JSON.parse(data);

            // If this is an authentication response, simulate a successful authentication
            if (message.type === 'auth_response') {
                setTimeout(() => {
                    if (this.onmessage) {
                        this.onmessage({
                            data: JSON.stringify({
                                type: 'auth_result',
                                data: {
                                    success: true,
                                    client_id: 'mock_client_123'
                                }
                            })
                        });
                    }
                }, 100);
            }
        }

        close() {
            console.log('Mock WebSocket closed');

            // Simulate the connection closing
            setTimeout(() => {
                if (this.onclose) {
                    this.onclose({
                        code: 1000,
                        reason: 'Normal closure',
                        wasClean: true
                    });
                }
            }, 100);
        }
    };

    // Define the WebSocket states
    WebSocket.OPEN = 1;
}

// Configure logging
const log = (message) => {
  console.log(`[${new Date().toISOString()}] ${message}`);
};

// Mock localStorage for testing
const localStorage = {
  _data: {},
  getItem: function(key) {
    return this._data[key] || null;
  },
  setItem: function(key, value) {
    this._data[key] = value;
  },
  removeItem: function(key) {
    delete this._data[key];
  },
  clear: function() {
    this._data = {};
  }
};

// Mock the auth module
const auth = {
  storeToken: (token) => {
    localStorage.setItem('coda_auth_token', token);
    log(`Stored token: ${token}`);
  },
  getToken: () => {
    return localStorage.getItem('coda_auth_token');
  },
  clearToken: () => {
    localStorage.removeItem('coda_auth_token');
    log('Cleared token');
  },
  isAuthenticated: () => {
    return !!localStorage.getItem('coda_auth_token');
  },
  handleAuthChallenge: (challenge, socket) => {
    const token = challenge.data.token;

    // Store the token
    auth.storeToken(token);

    // Send the authentication response
    socket.send(JSON.stringify({
      type: 'auth_response',
      data: {
        token: token
      }
    }));

    log('Sent authentication response');
  },
  handleAuthResult: (result, onSuccess, onFailure) => {
    const success = result.data.success;

    if (success) {
      // Authentication succeeded
      const clientId = result.data.client_id;
      log(`Authentication succeeded, client ID: ${clientId}`);

      if (onSuccess) {
        onSuccess(clientId);
      }
    } else {
      // Authentication failed
      const message = result.data.message || 'Authentication failed';
      log(`Authentication failed: ${message}`);

      // Clear the token
      auth.clearToken();

      if (onFailure) {
        onFailure(message);
      }
    }
  }
};

// Mock the WebSocket service
class WebSocketService {
  constructor() {
    this.socket = null;
    this.url = 'ws://localhost:8765';
    this.connectionState = 'disconnected';
    this.eventHandlers = {};
    this.connectionStateHandlers = [];
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.clientId = null;
    this.authenticated = false;
    this.messageQueue = [];
  }

  connect(url = 'ws://localhost:8765') {
    return new Promise((resolve, reject) => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        log('WebSocket already connected');
        resolve();
        return;
      }

      this.url = url;
      this.setConnectionState('connecting');

      try {
        this.socket = new WebSocket(url);

        this.socket.onopen = () => {
          log('WebSocket connection established');
          this.onOpen();

          // Wait for authentication before resolving
          const authHandler = (event) => {
            if (event.type === 'auth_result') {
              if (event.data.success) {
                this.removeEventListener('auth_result', authHandler);
                resolve();
              } else {
                this.removeEventListener('auth_result', authHandler);
                reject(new Error(event.data.message || 'Authentication failed'));
              }
            }
          };

          this.addEventListener('auth_result', authHandler);
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
        this.setConnectionState('error');
        log(`Error connecting to WebSocket: ${error}`);
        reject(error);
      }
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.setConnectionState('disconnected');
      log('WebSocket disconnected');
    }
  }

  send(type, data = {}) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      log(`WebSocket not connected, queueing message: ${type}`);
      this.messageQueue.push({ type, data });
      return;
    }

    if (!this.authenticated && type !== 'auth_response') {
      log(`Not authenticated, queueing message: ${type}`);
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
      log(`Error sending WebSocket message: ${error}`);
    }
  }

  onMessage(event) {
    try {
      const message = JSON.parse(event.data);
      const { type, data } = message;

      // Handle authentication messages
      if (type === 'auth_challenge') {
        log('Received authentication challenge');
        this.setConnectionState('authenticating');
        auth.handleAuthChallenge(message, this.socket);
        return;
      }

      if (type === 'auth_result') {
        log('Received authentication result');
        auth.handleAuthResult(message,
          // Success callback
          (clientId) => {
            this.clientId = clientId;
            this.authenticated = true;
            this.setConnectionState('connected');
            this.reconnectAttempts = 0;

            // Send any queued messages
            while (this.messageQueue.length > 0) {
              const { type, data } = this.messageQueue.shift();
              this.send(type, data);
            }
          },
          // Failure callback
          (message) => {
            this.setConnectionState('error');
            this.disconnect();
          }
        );
      }

      // Handle duplicate message notifications
      if (type === 'duplicate_message') {
        log(`Duplicate message detected: ${data.original_type}, count: ${data.count}`);
      }

      // Notify event handlers
      this.notifyEventHandlers(type, data);
    } catch (error) {
      log(`Error parsing WebSocket message: ${error}`);
    }
  }

  onOpen() {
    log('WebSocket connection opened');
    // Authentication will be handled by the server sending an auth_challenge
  }

  onClose(event) {
    this.authenticated = false;

    if (event.wasClean) {
      log(`WebSocket connection closed cleanly, code=${event.code}, reason=${event.reason}`);
      this.setConnectionState('disconnected');
    } else {
      log('WebSocket connection died');
      this.setConnectionState('error');
      this.reconnect();
    }
  }

  onError(error) {
    log(`WebSocket error: ${error}`);
    this.setConnectionState('error');
  }

  reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      log(`Maximum reconnect attempts (${this.maxReconnectAttempts}) reached`);
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      this.connect(this.url).catch((error) => {
        log(`Reconnect failed: ${error}`);
      });
    }, delay);
  }

  setConnectionState(state) {
    if (this.connectionState !== state) {
      this.connectionState = state;
      this.notifyConnectionStateHandlers(state);
    }
  }

  addEventListener(type, handler) {
    if (!this.eventHandlers[type]) {
      this.eventHandlers[type] = [];
    }

    this.eventHandlers[type].push(handler);
  }

  removeEventListener(type, handler) {
    if (!this.eventHandlers[type]) {
      return;
    }

    this.eventHandlers[type] = this.eventHandlers[type].filter(h => h !== handler);
  }

  addConnectionStateListener(handler) {
    this.connectionStateHandlers.push(handler);

    // Immediately notify the handler of the current state
    handler(this.connectionState);
  }

  removeConnectionStateListener(handler) {
    this.connectionStateHandlers = this.connectionStateHandlers.filter(h => h !== handler);
  }

  notifyEventHandlers(type, data) {
    if (!this.eventHandlers[type]) {
      return;
    }

    for (const handler of this.eventHandlers[type]) {
      try {
        handler({ type, data });
      } catch (error) {
        log(`Error in event handler for ${type}: ${error}`);
      }
    }
  }

  notifyConnectionStateHandlers(state) {
    for (const handler of this.connectionStateHandlers) {
      try {
        handler(state);
      } catch (error) {
        log(`Error in connection state handler: ${error}`);
      }
    }
  }

  sendClientMessage(messageType, messageData = {}) {
    this.send('client_message', {
      message_type: messageType,
      message_data: messageData
    });
  }

  sendPushToTalk(duration = 5, continuous = false) {
    this.sendClientMessage('push_to_talk', {
      duration,
      continuous
    });
  }

  sendStopListening() {
    this.sendClientMessage('stop_listening');
  }

  sendStopSpeaking() {
    this.sendClientMessage('stop_speaking');
  }

  sendTextInput(text) {
    this.sendClientMessage('text_input', {
      text
    });
  }
}

// Create a WebSocket service instance
const websocketService = new WebSocketService();

// Test the WebSocket service
async function testWebSocketService() {
  log('Testing WebSocket service...');

  try {
    // Connect to the server
    log('Connecting to WebSocket server...');
    await websocketService.connect();
    log('Connected to WebSocket server');

    // Add event listeners
    websocketService.addEventListener('conversation_turn', (event) => {
      log(`Received conversation turn: ${event.data.role} - ${event.data.content}`);
    });

    websocketService.addEventListener('llm_token', (event) => {
      process.stdout.write(event.data.token);
    });

    // Send a text input
    log('Sending text input...');
    websocketService.sendTextInput('Hello, world!');

    // Wait for 10 seconds to receive events
    log('Waiting for events...');
    await new Promise(resolve => setTimeout(resolve, 10000));

    // Disconnect
    log('Disconnecting...');
    websocketService.disconnect();
    log('Disconnected');

    log('Test completed successfully');
  } catch (error) {
    log(`Test failed: ${error}`);
  }
}

// Run the test
testWebSocketService();
