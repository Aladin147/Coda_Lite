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
    if (this.socket || this.isConnecting) return;
    
    this.isConnecting = true;
    
    try {
      this.socket = new WebSocket(this.url);
      
      this.socket.onopen = () => {
        this.reconnectAttempts = 0;
        this.isConnecting = false;
        this.isReconnecting = false;
        this.notifyObservers('onConnect');
      };
      
      this.socket.onclose = () => {
        this.socket = null;
        this.isConnecting = false;
        this.notifyObservers('onDisconnect');
        this.attemptReconnect();
      };
      
      this.socket.onerror = (error) => {
        this.notifyObservers('onError', new Error('WebSocket error'));
      };
      
      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.notifyObservers('onEvent', data);
        } catch (error) {
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
   */
  public send(message: any): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      this.notifyObservers('onError', new Error('WebSocket is not connected'));
      return;
    }
    
    try {
      this.socket.send(JSON.stringify(message));
    } catch (error) {
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
