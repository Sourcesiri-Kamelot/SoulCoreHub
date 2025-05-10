/**
 * MCP Bridge - Model Context Protocol Integration for SoulCoreHub
 * 
 * This module provides a bridge between SoulCoreHub and MCP servers, enabling:
 * - Seamless integration with Model Context Protocol
 * - Dynamic tool discovery and registration
 * - Cross-server communication and coordination
 * - Enhanced AI capabilities through specialized MCP servers
 * - Unified interface for accessing MCP tools
 */

import { EventEmitter } from 'events';
import axios from 'axios';
import WebSocket from 'ws';
import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

// Promisify exec
const execAsync = promisify(exec);

/**
 * MCP Server structure
 */
export interface MCPServer {
  id: string;
  name: string;
  description: string;
  url: string;
  status: 'online' | 'offline' | 'error';
  capabilities: string[];
  tools: MCPTool[];
  lastConnected?: string;
  error?: string;
}

/**
 * MCP Tool structure
 */
export interface MCPTool {
  name: string;
  description: string;
  server: string;
  parameters: MCPToolParameter[];
  returnSchema?: any;
}

/**
 * MCP Tool Parameter structure
 */
export interface MCPToolParameter {
  name: string;
  description: string;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  required: boolean;
  default?: any;
}

/**
 * MCP Tool Result structure
 */
export interface MCPToolResult {
  success: boolean;
  data?: any;
  error?: string;
}

/**
 * MCP Bridge class
 */
export class MCPBridge {
  private servers: Map<string, MCPServer> = new Map();
  private connections: Map<string, WebSocket> = new Map();
  private eventBus: EventEmitter;
  private discoveryInterval: NodeJS.Timeout;
  private heartbeatInterval: NodeJS.Timeout;
  private configPath: string;
  
  /**
   * Initialize MCP Bridge
   * @param configPath Path to MCP configuration file
   */
  constructor(configPath: string = path.join(process.cwd(), 'config', 'mcp_servers.json')) {
    this.configPath = configPath;
    this.eventBus = new EventEmitter();
    
    // Load server configuration
    this.loadServerConfig();
    
    // Start discovery interval (every 5 minutes)
    this.discoveryInterval = setInterval(this.discoverServers.bind(this), 5 * 60 * 1000);
    
    // Start heartbeat interval (every 30 seconds)
    this.heartbeatInterval = setInterval(this.sendHeartbeats.bind(this), 30 * 1000);
    
    console.log('MCP Bridge initialized');
  }
  
  /**
   * Load server configuration
   */
  private loadServerConfig(): void {
    try {
      // Check if config file exists
      if (fs.existsSync(this.configPath)) {
        const config = JSON.parse(fs.readFileSync(this.configPath, 'utf-8'));
        
        // Load servers from config
        if (config.servers && Array.isArray(config.servers)) {
          for (const server of config.servers) {
            this.servers.set(server.id, {
              ...server,
              status: 'offline',
              tools: []
            });
          }
        }
      } else {
        // Create default config
        const defaultConfig = {
          servers: [
            {
              id: 'core-mcp',
              name: 'Core MCP Server',
              description: 'Core Model Context Protocol server',
              url: 'http://localhost:8080',
              capabilities: ['core', 'tools', 'memory']
            }
          ]
        };
        
        // Ensure directory exists
        const dir = path.dirname(this.configPath);
        if (!fs.existsSync(dir)) {
          fs.mkdirSync(dir, { recursive: true });
        }
        
        // Write default config
        fs.writeFileSync(this.configPath, JSON.stringify(defaultConfig, null, 2));
        
        // Load default server
        this.servers.set('core-mcp', {
          id: 'core-mcp',
          name: 'Core MCP Server',
          description: 'Core Model Context Protocol server',
          url: 'http://localhost:8080',
          status: 'offline',
          capabilities: ['core', 'tools', 'memory'],
          tools: []
        });
      }
      
      console.log(`Loaded ${this.servers.size} MCP servers from config`);
    } catch (error) {
      console.error('Error loading MCP server config:', error);
    }
  }
  
  /**
   * Save server configuration
   */
  private saveServerConfig(): void {
    try {
      const config = {
        servers: Array.from(this.servers.values()).map(server => ({
          id: server.id,
          name: server.name,
          description: server.description,
          url: server.url,
          capabilities: server.capabilities
        }))
      };
      
      // Ensure directory exists
      const dir = path.dirname(this.configPath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      
      // Write config
      fs.writeFileSync(this.configPath, JSON.stringify(config, null, 2));
      
      console.log('Saved MCP server config');
    } catch (error) {
      console.error('Error saving MCP server config:', error);
    }
  }
  
  /**
   * Discover MCP servers
   */
  async discoverServers(): Promise<void> {
    console.log('Discovering MCP servers...');
    
    // Check each server
    for (const [id, server] of this.servers.entries()) {
      try {
        // Check if server is online
        const response = await axios.get(`${server.url}/mcp/info`, { timeout: 5000 });
        
        if (response.status === 200 && response.data) {
          // Update server info
          const updatedServer: MCPServer = {
            ...server,
            name: response.data.name || server.name,
            description: response.data.description || server.description,
            capabilities: response.data.capabilities || server.capabilities,
            status: 'online',
            lastConnected: new Date().toISOString()
          };
          
          this.servers.set(id, updatedServer);
          
          // Discover tools
          await this.discoverServerTools(updatedServer);
          
          // Connect to server WebSocket
          this.connectToServer(updatedServer);
          
          // Emit server online event
          this.eventBus.emit('server:online', updatedServer);
        } else {
          throw new Error('Invalid server response');
        }
      } catch (error) {
        // Mark server as offline
        const updatedServer: MCPServer = {
          ...server,
          status: 'error',
          error: error.message
        };
        
        this.servers.set(id, updatedServer);
        
        // Close WebSocket connection if exists
        this.closeServerConnection(id);
        
        // Emit server offline event
        this.eventBus.emit('server:offline', updatedServer);
        
        console.error(`Error connecting to MCP server ${id}:`, error);
      }
    }
    
    // Save updated config
    this.saveServerConfig();
    
    console.log(`Discovered ${Array.from(this.servers.values()).filter(s => s.status === 'online').length} online MCP servers`);
  }
  
  /**
   * Discover tools provided by an MCP server
   * @param server MCP server
   */
  private async discoverServerTools(server: MCPServer): Promise<void> {
    try {
      // Get tools from server
      const response = await axios.get(`${server.url}/mcp/tools`, { timeout: 5000 });
      
      if (response.status === 200 && response.data && Array.isArray(response.data.tools)) {
        // Update server tools
        server.tools = response.data.tools.map((tool: any) => ({
          name: tool.name,
          description: tool.description,
          server: server.id,
          parameters: tool.parameters || [],
          returnSchema: tool.returnSchema
        }));
        
        console.log(`Discovered ${server.tools.length} tools from server ${server.id}`);
        
        // Emit tools discovered event
        this.eventBus.emit('tools:discovered', {
          server,
          tools: server.tools
        });
      }
    } catch (error) {
      console.error(`Error discovering tools from server ${server.id}:`, error);
    }
  }
  
  /**
   * Connect to an MCP server WebSocket
   * @param server MCP server
   */
  private connectToServer(server: MCPServer): void {
    try {
      // Close existing connection if any
      this.closeServerConnection(server.id);
      
      // Extract WebSocket URL from server URL
      const wsUrl = server.url.replace(/^http/, 'ws') + '/mcp/ws';
      
      // Connect to WebSocket
      const ws = new WebSocket(wsUrl);
      
      ws.on('open', () => {
        console.log(`Connected to MCP server ${server.id} WebSocket`);
        
        // Send hello message
        ws.send(JSON.stringify({
          type: 'hello',
          client: 'SoulCoreHub',
          version: '1.0.0'
        }));
        
        // Store connection
        this.connections.set(server.id, ws);
        
        // Emit connection event
        this.eventBus.emit('server:connected', server);
      });
      
      ws.on('message', (data: WebSocket.Data) => {
        try {
          const message = JSON.parse(data.toString());
          
          // Handle message
          this.handleServerMessage(server.id, message);
        } catch (error) {
          console.error(`Error parsing message from server ${server.id}:`, error);
        }
      });
      
      ws.on('error', (error) => {
        console.error(`WebSocket error for server ${server.id}:`, error);
        
        // Emit error event
        this.eventBus.emit('server:error', {
          server,
          error: error.message
        });
      });
      
      ws.on('close', () => {
        console.log(`Disconnected from MCP server ${server.id} WebSocket`);
        
        // Remove connection
        this.connections.delete(server.id);
        
        // Emit disconnection event
        this.eventBus.emit('server:disconnected', server);
      });
    } catch (error) {
      console.error(`Error connecting to MCP server ${server.id} WebSocket:`, error);
    }
  }
  
  /**
   * Close WebSocket connection to an MCP server
   * @param serverId Server ID
   */
  private closeServerConnection(serverId: string): void {
    const connection = this.connections.get(serverId);
    
    if (connection) {
      // Close connection
      connection.close();
      
      // Remove connection
      this.connections.delete(serverId);
      
      console.log(`Closed connection to MCP server ${serverId}`);
    }
  }
  
  /**
   * Handle message from an MCP server
   * @param serverId Server ID
   * @param message Message
   */
  private handleServerMessage(serverId: string, message: any): void {
    // Get server
    const server = this.servers.get(serverId);
    
    if (!server) {
      console.error(`Received message from unknown server ${serverId}`);
      return;
    }
    
    // Handle message based on type
    switch (message.type) {
      case 'hello':
        // Server hello message
        console.log(`Received hello from MCP server ${serverId}: ${message.server} ${message.version}`);
        break;
        
      case 'tool_result':
        // Tool execution result
        this.eventBus.emit('tool:result', {
          server,
          requestId: message.requestId,
          result: message.result
        });
        break;
        
      case 'event':
        // Server event
        this.eventBus.emit('server:event', {
          server,
          event: message.event,
          data: message.data
        });
        break;
        
      case 'error':
        // Server error
        console.error(`Error from MCP server ${serverId}:`, message.error);
        
        // Emit error event
        this.eventBus.emit('server:error', {
          server,
          error: message.error
        });
        break;
        
      default:
        // Unknown message type
        console.log(`Received unknown message type from MCP server ${serverId}:`, message.type);
    }
  }
  
  /**
   * Send heartbeats to connected servers
   */
  private sendHeartbeats(): void {
    for (const [serverId, connection] of this.connections.entries()) {
      try {
        // Send heartbeat message
        connection.send(JSON.stringify({
          type: 'heartbeat',
          timestamp: Date.now()
        }));
      } catch (error) {
        console.error(`Error sending heartbeat to MCP server ${serverId}:`, error);
      }
    }
  }
  
  /**
   * Register a new MCP server
   * @param server Server to register
   * @returns Registered server
   */
  async registerServer(server: Omit<MCPServer, 'status' | 'tools'>): Promise<MCPServer> {
    // Generate ID if not provided
    const id = server.id || `mcp-${Date.now()}`;
    
    // Create server object
    const newServer: MCPServer = {
      ...server,
      id,
      status: 'offline',
      tools: []
    };
    
    // Add server
    this.servers.set(id, newServer);
    
    // Save config
    this.saveServerConfig();
    
    // Discover server
    await this.discoverServers();
    
    // Return updated server
    return this.servers.get(id) || newServer;
  }
  
  /**
   * Unregister an MCP server
   * @param serverId Server ID
   * @returns Success status
   */
  unregisterServer(serverId: string): boolean {
    // Close connection if exists
    this.closeServerConnection(serverId);
    
    // Remove server
    const removed = this.servers.delete(serverId);
    
    // Save config
    this.saveServerConfig();
    
    return removed;
  }
  
  /**
   * Execute a tool on an MCP server
   * @param serverName Server name
   * @param toolName Tool name
   * @param parameters Tool parameters
   * @returns Tool result
   */
  async executeTool(serverName: string, toolName: string, parameters: any): Promise<MCPToolResult> {
    // Find server
    const server = Array.from(this.servers.values()).find(s => s.name === serverName || s.id === serverName);
    
    if (!server) {
      throw new Error(`MCP server ${serverName} not found`);
    }
    
    // Check if server is online
    if (server.status !== 'online') {
      throw new Error(`MCP server ${serverName} is offline`);
    }
    
    // Find tool
    const tool = server.tools.find(t => t.name === toolName);
    
    if (!tool) {
      throw new Error(`Tool ${toolName} not found on server ${serverName}`);
    }
    
    try {
      // Execute tool
      const response = await axios.post(`${server.url}/mcp/execute`, {
        tool: toolName,
        parameters
      }, { timeout: 30000 });
      
      if (response.status === 200) {
        return {
          success: true,
          data: response.data
        };
      } else {
        throw new Error(`Tool execution failed with status ${response.status}`);
      }
    } catch (error) {
      console.error(`Error executing tool ${toolName} on server ${serverName}:`, error);
      
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  /**
   * Execute a tool asynchronously on an MCP server
   * @param serverName Server name
   * @param toolName Tool name
   * @param parameters Tool parameters
   * @returns Request ID
   */
  async executeToolAsync(serverName: string, toolName: string, parameters: any): Promise<string> {
    // Find server
    const server = Array.from(this.servers.values()).find(s => s.name === serverName || s.id === serverName);
    
    if (!server) {
      throw new Error(`MCP server ${serverName} not found`);
    }
    
    // Check if server is online
    if (server.status !== 'online') {
      throw new Error(`MCP server ${serverName} is offline`);
    }
    
    // Find tool
    const tool = server.tools.find(t => t.name === toolName);
    
    if (!tool) {
      throw new Error(`Tool ${toolName} not found on server ${serverName}`);
    }
    
    // Check if WebSocket connection exists
    const connection = this.connections.get(server.id);
    
    if (!connection) {
      throw new Error(`No WebSocket connection to server ${serverName}`);
    }
    
    // Generate request ID
    const requestId = `req-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`;
    
    // Send execution request
    connection.send(JSON.stringify({
      type: 'execute_tool',
      requestId,
      tool: toolName,
      parameters
    }));
    
    return requestId;
  }
  
  /**
   * Get all registered MCP servers
   * @returns Array of servers
   */
  getServers(): MCPServer[] {
    return Array.from(this.servers.values());
  }
  
  /**
   * Get a specific MCP server
   * @param serverId Server ID
   * @returns Server or undefined
   */
  getServer(serverId: string): MCPServer | undefined {
    return this.servers.get(serverId);
  }
  
  /**
   * Get all tools from all servers
   * @returns Array of tools
   */
  getAllTools(): MCPTool[] {
    const tools: MCPTool[] = [];
    
    for (const server of this.servers.values()) {
      tools.push(...server.tools);
    }
    
    return tools;
  }
  
  /**
   * Get tools from a specific server
   * @param serverId Server ID
   * @returns Array of tools
   */
  getServerTools(serverId: string): MCPTool[] {
    const server = this.servers.get(serverId);
    return server ? server.tools : [];
  }
  
  /**
   * Find a tool by name
   * @param toolName Tool name
   * @returns Tool or undefined
   */
  findTool(toolName: string): { tool: MCPTool; server: MCPServer } | undefined {
    for (const server of this.servers.values()) {
      const tool = server.tools.find(t => t.name === toolName);
      
      if (tool) {
        return { tool, server };
      }
    }
    
    return undefined;
  }
  
  /**
   * Start an MCP server
   * @param serverId Server ID
   * @returns Success status
   */
  async startServer(serverId: string): Promise<boolean> {
    // Get server
    const server = this.servers.get(serverId);
    
    if (!server) {
      throw new Error(`MCP server ${serverId} not found`);
    }
    
    try {
      // Check if server is already running
      try {
        const response = await axios.get(`${server.url}/mcp/info`, { timeout: 2000 });
        
        if (response.status === 200) {
          console.log(`MCP server ${serverId} is already running`);
          return true;
        }
      } catch (error) {
        // Server is not running, continue
      }
      
      // Start server process
      const serverScript = path.join(process.cwd(), 'mcp_servers', `${serverId}.py`);
      
      if (!fs.existsSync(serverScript)) {
        throw new Error(`Server script ${serverScript} not found`);
      }
      
      // Start server in background
      const { stdout, stderr } = await execAsync(`python ${serverScript} &`);
      
      console.log(`Started MCP server ${serverId}`);
      console.log(`stdout: ${stdout}`);
      console.log(`stderr: ${stderr}`);
      
      // Wait for server to start
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Check if server is running
      try {
        const response = await axios.get(`${server.url}/mcp/info`, { timeout: 5000 });
        
        if (response.status === 200) {
          // Update server status
          server.status = 'online';
          server.lastConnected = new Date().toISOString();
          
          // Discover tools
          await this.discoverServerTools(server);
          
          // Connect to server WebSocket
          this.connectToServer(server);
          
          return true;
        }
      } catch (error) {
        throw new Error(`Server started but not responding: ${error.message}`);
      }
      
      return false;
    } catch (error) {
      console.error(`Error starting MCP server ${serverId}:`, error);
      return false;
    }
  }
  
  /**
   * Stop an MCP server
   * @param serverId Server ID
   * @returns Success status
   */
  async stopServer(serverId: string): Promise<boolean> {
    // Get server
    const server = this.servers.get(serverId);
    
    if (!server) {
      throw new Error(`MCP server ${serverId} not found`);
    }
    
    try {
      // Send shutdown request
      await axios.post(`${server.url}/mcp/shutdown`, {}, { timeout: 5000 });
      
      // Close connection
      this.closeServerConnection(serverId);
      
      // Update server status
      server.status = 'offline';
      
      console.log(`Stopped MCP server ${serverId}`);
      
      return true;
    } catch (error) {
      console.error(`Error stopping MCP server ${serverId}:`, error);
      
      // Force kill process
      try {
        await execAsync(`pkill -f "${serverId}.py"`);
        
        // Close connection
        this.closeServerConnection(serverId);
        
        // Update server status
        server.status = 'offline';
        
        console.log(`Force killed MCP server ${serverId}`);
        
        return true;
      } catch (killError) {
        console.error(`Error force killing MCP server ${serverId}:`, killError);
        return false;
      }
    }
  }
  
  /**
   * Register an event listener
   * @param event Event name
   * @param callback Callback function
   */
  onEvent(event: string, callback: (...args: any[]) => void): void {
    this.eventBus.on(event, callback);
  }
}

// Create singleton instance
export const mcpBridge = new MCPBridge();
