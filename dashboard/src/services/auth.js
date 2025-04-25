/**
 * Authentication service for the Coda dashboard.
 * 
 * This module provides functions for authenticating with the Coda WebSocket server.
 */

/**
 * Store the authentication token in local storage.
 * 
 * @param {string} token - The authentication token
 */
export const storeToken = (token) => {
  localStorage.setItem('coda_auth_token', token);
};

/**
 * Get the authentication token from local storage.
 * 
 * @returns {string|null} The authentication token, or null if not found
 */
export const getToken = () => {
  return localStorage.getItem('coda_auth_token');
};

/**
 * Clear the authentication token from local storage.
 */
export const clearToken = () => {
  localStorage.removeItem('coda_auth_token');
};

/**
 * Check if the user is authenticated.
 * 
 * @returns {boolean} True if the user is authenticated, false otherwise
 */
export const isAuthenticated = () => {
  return !!getToken();
};

/**
 * Handle an authentication challenge from the server.
 * 
 * @param {Object} challenge - The authentication challenge
 * @param {WebSocket} socket - The WebSocket connection
 */
export const handleAuthChallenge = (challenge, socket) => {
  const token = challenge.data.token;
  
  // Store the token
  storeToken(token);
  
  // Send the authentication response
  socket.send(JSON.stringify({
    type: 'auth_response',
    data: {
      token: token
    }
  }));
  
  console.log('Sent authentication response');
};

/**
 * Handle an authentication result from the server.
 * 
 * @param {Object} result - The authentication result
 * @param {Function} onSuccess - Callback for successful authentication
 * @param {Function} onFailure - Callback for failed authentication
 */
export const handleAuthResult = (result, onSuccess, onFailure) => {
  const success = result.data.success;
  
  if (success) {
    // Authentication succeeded
    const clientId = result.data.client_id;
    console.log(`Authentication succeeded, client ID: ${clientId}`);
    
    if (onSuccess) {
      onSuccess(clientId);
    }
  } else {
    // Authentication failed
    const message = result.data.message || 'Authentication failed';
    console.error(`Authentication failed: ${message}`);
    
    // Clear the token
    clearToken();
    
    if (onFailure) {
      onFailure(message);
    }
  }
};
