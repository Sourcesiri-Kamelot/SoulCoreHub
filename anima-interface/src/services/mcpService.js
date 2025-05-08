class MCPService {
  constructor(url = 'ws://localhost:8765', agentName = 'AnimaInterface') {
    this.url = url;
    this.agentName = agentName;
    this.ws = null;
    this.connected = false;
    this.callbacks = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 2000; // 2 seconds
    this.connectionPromise = null;
    this.lastPingTime = null;
    this.pingInterval = null;
    this.latency = 0;
    this.toolsUsed = new Map();
    this.lastToolUsed = null;
    this.activeTools = [];
    this.eventListeners = new Map();
  }

  connect() {
    if (this.connectionPromise) {
      return this.connectionPromise;
    }

    this.connectionPromise = new Promise((resolve, reject) => {
      try {
        console.log(`Connecting to MCP at ${this.url}`);
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('Connected to MCP server');
          this.connected = true;
          this.reconnectAttempts = 0;
          
          // Start ping interval
          this.startPingInterval();
          
          // Register with MCP
          this.registerWithMCP()
            .then(() => {
              // Get available tools
              return this.getAvailableTools();
            })
            .then(() => {
              resolve(true);
              this._emitEvent('connected', { timestamp: Date.now() });
            })
            .catch(error => {
              console.error('Error during MCP initialization:', error);
              reject(error);
            });
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this._emitEvent('error', { error, timestamp: Date.now() });
          reject(error);
        };

        this.ws.onclose = (event) => {
          console.log(`Disconnected from MCP server: ${event.code} ${event.reason}`);
          this.connected = false;
          this.connectionPromise = null;
          
          // Clear ping interval
          if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = null;
          }
          
          this._emitEvent('disconnected', { 
            code: event.code, 
            reason: event.reason, 
            timestamp: Date.now() 
          });
          
          // Try to reconnect
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            
            setTimeout(() => {
              this.connect().catch(error => {
                console.error('Reconnection failed:', error);
              });
            }, this.reconnectDelay);
          }
        };

        this.ws.onmessage = (message) => {
          try {
            const data = JSON.parse(message.data);
            
            // Handle ping response
            if (data.request_id === 'ping') {
              if (this.lastPingTime) {
                this.latency = Date.now() - this.lastPingTime;
                this._emitEvent('latency', { latency: this.latency });
              }
              return;
            }
            
            // Handle normal responses
            const callback = this.callbacks.get(data.request_id);
            if (callback) {
              callback(data);
              this.callbacks.delete(data.request_id);
            }
            
            // Emit message event
            this._emitEvent('message', { data, timestamp: Date.now() });
          } catch (error) {
            console.error('Error parsing message:', error);
          }
        };
      } catch (error) {
        console.error('Error initializing WebSocket:', error);
        this.connectionPromise = null;
        reject(error);
      }
    });

    return this.connectionPromise;
  }

  disconnect() {
    if (this.ws && this.connected) {
      this.ws.close();
      this.connected = false;
      this.connectionPromise = null;
      
      // Clear ping interval
      if (this.pingInterval) {
        clearInterval(this.pingInterval);
        this.pingInterval = null;
      }
      
      console.log('Disconnected from MCP server');
      return true;
    }
    return false;
  }

  startPingInterval() {
    // Clear existing interval if any
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
    }
    
    // Start new ping interval
    this.pingInterval = setInterval(() => {
      this.ping().catch(error => {
        console.error('Ping failed:', error);
      });
    }, 5000); // Ping every 5 seconds
  }

  async ping() {
    if (!this.connected) {
      throw new Error('Not connected to MCP server');
    }
    
    this.lastPingTime = Date.now();
    
    const request = {
      request_id: 'ping',
      tool: 'echo',
      parameters: { message: 'ping' },
      stream: false,
      agent: this.agentName,
      emotion: 'neutral'
    };
    
    this.ws.send(JSON.stringify(request));
    return true;
  }

  async registerWithMCP() {
    return this.invokeTool('register_agent', {
      agent_name: this.agentName,
      capabilities: ['ui', 'interaction', 'visualization']
    });
  }

  async getAvailableTools() {
    try {
      const result = await this.invokeTool('list_tools', {});
      this.activeTools = result.tools || [];
      this._emitEvent('tools_updated', { tools: this.activeTools });
      return this.activeTools;
    } catch (error) {
      console.error('Failed to get available tools:', error);
      this.activeTools = [];
      return [];
    }
  }

  async invokeTool(toolName, parameters, emotion = 'neutral') {
    if (!this.connected) {
      await this.connect();
    }

    return new Promise((resolve, reject) => {
      const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      this.callbacks.set(requestId, (data) => {
        if (data.error) {
          reject(new Error(data.error));
        } else {
          // Track tool usage
          if (!this.toolsUsed.has(toolName)) {
            this.toolsUsed.set(toolName, 0);
          }
          this.toolsUsed.set(toolName, this.toolsUsed.get(toolName) + 1);
          this.lastToolUsed = {
            name: toolName,
            timestamp: Date.now(),
            parameters
          };
          
          this._emitEvent('tool_invoked', {
            tool: toolName,
            parameters,
            timestamp: Date.now()
          });
          
          resolve(data.result);
        }
      });

      const request = {
        request_id: requestId,
        tool: toolName,
        parameters,
        stream: false,
        agent: this.agentName,
        emotion
      };

      this.ws.send(JSON.stringify(request));
    });
  }

  async invokeToolStream(toolName, parameters, onToken, emotion = 'neutral') {
    if (!this.connected) {
      await this.connect();
    }

    return new Promise((resolve, reject) => {
      const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      this.callbacks.set(requestId, (data) => {
        if (data.error) {
          reject(new Error(data.error));
        } else if (data.type === 'token' && onToken) {
          onToken(data.content);
        } else if (data.type === 'end') {
          // Track tool usage
          if (!this.toolsUsed.has(toolName)) {
            this.toolsUsed.set(toolName, 0);
          }
          this.toolsUsed.set(toolName, this.toolsUsed.get(toolName) + 1);
          this.lastToolUsed = {
            name: toolName,
            timestamp: Date.now(),
            parameters
          };
          
          this._emitEvent('tool_invoked', {
            tool: toolName,
            parameters,
            timestamp: Date.now()
          });
          
          resolve(true);
        }
      });

      const request = {
        request_id: requestId,
        tool: toolName,
        parameters,
        stream: true,
        agent: this.agentName,
        emotion
      };

      this.ws.send(JSON.stringify(request));
    });
  }

  getStatus() {
    return {
      connected: this.connected,
      latency: this.latency,
      reconnectAttempts: this.reconnectAttempts,
      activeTools: this.activeTools.length,
      lastToolUsed: this.lastToolUsed,
      toolsUsed: Array.from(this.toolsUsed.entries()).map(([name, count]) => ({ name, count }))
    };
  }

  addEventListener(event, callback) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event).push(callback);
  }

  removeEventListener(event, callback) {
    if (this.eventListeners.has(event)) {
      const callbacks = this.eventListeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index !== -1) {
        callbacks.splice(index, 1);
      }
      if (callbacks.length === 0) {
        this.eventListeners.delete(event);
      } else {
        this.eventListeners.set(event, callbacks);
      }
    }
  }

  _emitEvent(event, data) {
    if (this.eventListeners.has(event)) {
      for (const callback of this.eventListeners.get(event)) {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error);
        }
      }
    }
  }
}

// Create and export a singleton instance
const mcpService = new MCPService();
export default mcpService;
