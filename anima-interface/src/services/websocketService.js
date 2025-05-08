import { io } from 'socket.io-client';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 2000; // 2 seconds
    this.url = process.env.REACT_APP_WEBSOCKET_URL || 'ws://localhost:3001/ws';
    this.connectionPromise = null;
  }

  connect() {
    if (this.connectionPromise) {
      return this.connectionPromise;
    }

    this.connectionPromise = new Promise((resolve, reject) => {
      try {
        console.log(`Connecting to WebSocket at ${this.url}`);
        
        this.socket = io(this.url, {
          reconnection: true,
          reconnectionAttempts: this.maxReconnectAttempts,
          reconnectionDelay: this.reconnectDelay,
          transports: ['websocket'],
          auth: {
            token: localStorage.getItem('auth_token')
          }
        });

        // Connection event handlers
        this.socket.on('connect', () => {
          console.log('WebSocket connected');
          this.isConnected = true;
          this.reconnectAttempts = 0;
          resolve(true);
        });

        this.socket.on('disconnect', (reason) => {
          console.log(`WebSocket disconnected: ${reason}`);
          this.isConnected = false;
          
          // If the disconnection was initiated by the server, try to reconnect
          if (reason === 'io server disconnect') {
            this.socket.connect();
          }
          
          // Reset connection promise on disconnect
          this.connectionPromise = null;
        });

        this.socket.on('connect_error', (error) => {
          console.error('WebSocket connection error:', error);
          this.reconnectAttempts++;
          
          if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            reject(error);
            this.connectionPromise = null;
          }
        });

        // Set up default event listeners
        this.setupDefaultListeners();

      } catch (error) {
        console.error('Error initializing WebSocket:', error);
        this.connectionPromise = null;
        reject(error);
      }
    });

    return this.connectionPromise;
  }

  setupDefaultListeners() {
    // Listen for status updates
    this.on('status_update', (data) => {
      console.log('Status update received:', data);
    });

    // Listen for agent updates
    this.on('agent_update', (data) => {
      console.log('Agent update received:', data);
    });

    // Listen for memory updates
    this.on('memory_update', (data) => {
      console.log('Memory update received:', data);
    });

    // Listen for emotional state changes
    this.on('emotional_state_change', (data) => {
      console.log('Emotional state change received:', data);
    });

    // Listen for notifications
    this.on('notification', (data) => {
      console.log('Notification received:', data);
    });

    // Listen for file updates
    this.on('file_update', (data) => {
      console.log('File update received:', data);
    });

    // Listen for MCP updates
    this.on('mcp_update', (data) => {
      console.log('MCP update received:', data);
    });

    // Listen for command responses
    this.on('command_response', (data) => {
      console.log('Command response received:', data);
    });
  }

  disconnect() {
    if (this.socket && this.isConnected) {
      this.socket.disconnect();
      this.isConnected = false;
      this.connectionPromise = null;
      console.log('WebSocket disconnected');
    }
  }

  on(event, callback) {
    if (!this.socket) {
      console.warn('WebSocket not initialized. Connect first before adding listeners.');
      return false;
    }

    // Store the callback in our listeners map
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);

    // Add the listener to the socket
    this.socket.on(event, callback);
    return true;
  }

  off(event, callback) {
    if (!this.socket) {
      console.warn('WebSocket not initialized.');
      return false;
    }

    if (callback) {
      // Remove specific callback
      this.socket.off(event, callback);
      
      // Update our listeners map
      if (this.listeners.has(event)) {
        const callbacks = this.listeners.get(event);
        const index = callbacks.indexOf(callback);
        if (index !== -1) {
          callbacks.splice(index, 1);
        }
        if (callbacks.length === 0) {
          this.listeners.delete(event);
        } else {
          this.listeners.set(event, callbacks);
        }
      }
    } else {
      // Remove all callbacks for this event
      this.socket.off(event);
      this.listeners.delete(event);
    }
    
    return true;
  }

  emit(event, data) {
    if (!this.socket || !this.isConnected) {
      console.warn('WebSocket not connected. Cannot emit event.');
      return false;
    }

    this.socket.emit(event, data);
    return true;
  }

  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      reconnectAttempts: this.reconnectAttempts,
      url: this.url
    };
  }
}

// Create and export a singleton instance
const websocketService = new WebSocketService();
export default websocketService;
