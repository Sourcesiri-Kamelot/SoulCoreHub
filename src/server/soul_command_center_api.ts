/**
 * Soul Command Center API - Unified Control Interface for SoulCoreHub
 * 
 * This module provides a comprehensive API for the Soul Command Center, enabling:
 * - Centralized control of all SoulCoreHub components
 * - Real-time monitoring of system status
 * - Agent management and communication
 * - System configuration and customization
 * - Advanced diagnostics and troubleshooting
 */

import express from 'express';
import { animaCore } from '../agents/anima';
import { evoVeCore } from '../agents/evove/evove_core';
import { evoVeRepairSystem } from '../agents/evove/evove_repair_system';
import { mcpBridge } from '../mcp/mcp_bridge';
import { llmConnector } from '../llm/llm_connector';
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';
import WebSocket from 'ws';

// Promisify exec
const execAsync = promisify(exec);

const router = express.Router();

/**
 * @route GET /api/command-center/status
 * @desc Get overall system status
 * @access Public
 */
router.get('/status', async (req, res) => {
  try {
    // Get system components status
    const components = evoVeCore.getComponents();
    const issues = evoVeCore.getIssues();
    const metrics = evoVeCore.getMetrics(1)[0] || {};
    
    // Get agent statuses
    const anima = {
      status: 'online',
      emotionalState: animaCore.getEmotionalState()
    };
    
    // Get MCP servers status
    const mcpServers = mcpBridge.getServers();
    
    // Get LLM status
    let llmStatus = 'unknown';
    try {
      const ollamaAvailable = await llmConnector.isAvailable('ollama');
      const huggingfaceAvailable = await llmConnector.isAvailable('huggingface');
      
      if (ollamaAvailable) {
        llmStatus = 'ollama';
      } else if (huggingfaceAvailable) {
        llmStatus = 'huggingface';
      } else {
        llmStatus = 'offline';
      }
    } catch (error) {
      llmStatus = 'error';
    }
    
    res.json({
      success: true,
      status: {
        system: {
          components: components.length,
          healthyComponents: components.filter(c => c.status === 'healthy').length,
          issues: issues.length,
          metrics
        },
        agents: {
          anima
        },
        mcp: {
          servers: mcpServers.length,
          onlineServers: mcpServers.filter(s => s.status === 'online').length,
          tools: mcpServers.reduce((count, server) => count + server.tools.length, 0)
        },
        llm: {
          provider: llmStatus
        }
      }
    });
  } catch (error) {
    console.error('Error getting system status:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route GET /api/command-center/components
 * @desc Get system components
 * @access Public
 */
router.get('/components', (req, res) => {
  try {
    const components = evoVeCore.getComponents();
    res.json({ success: true, components });
  } catch (error) {
    console.error('Error getting system components:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route GET /api/command-center/issues
 * @desc Get system issues
 * @access Public
 */
router.get('/issues', (req, res) => {
  try {
    const includeResolved = req.query.includeResolved === 'true';
    const issues = evoVeCore.getIssues(includeResolved);
    res.json({ success: true, issues });
  } catch (error) {
    console.error('Error getting system issues:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route POST /api/command-center/repair/:issueId
 * @desc Repair a system issue
 * @access Public
 */
router.post('/repair/:issueId', async (req, res) => {
  try {
    const { issueId } = req.params;
    const success = await evoVeCore.repairIssue(issueId);
    
    if (success) {
      res.json({ success: true, message: `Issue ${issueId} repaired successfully` });
    } else {
      res.status(500).json({ success: false, error: `Failed to repair issue ${issueId}` });
    }
  } catch (error) {
    console.error('Error repairing issue:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route GET /api/command-center/diagnostics
 * @desc Get system diagnostics
 * @access Public
 */
router.get('/diagnostics', (req, res) => {
  try {
    const diagnostics = evoVeRepairSystem.getDiagnostics();
    res.json({ success: true, diagnostics });
  } catch (error) {
    console.error('Error getting system diagnostics:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route GET /api/command-center/code-quality
 * @desc Get code quality issues
 * @access Public
 */
router.get('/code-quality', (req, res) => {
  try {
    const codeQualityIssues = evoVeRepairSystem.getCodeQualityIssues();
    res.json({ success: true, issues: codeQualityIssues });
  } catch (error) {
    console.error('Error getting code quality issues:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route GET /api/command-center/optimizations
 * @desc Get system optimizations
 * @access Public
 */
router.get('/optimizations', (req, res) => {
  try {
    const optimizations = evoVeRepairSystem.getOptimizations();
    res.json({ success: true, optimizations });
  } catch (error) {
    console.error('Error getting system optimizations:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route POST /api/command-center/optimize/:optimizationId
 * @desc Implement a system optimization
 * @access Public
 */
router.post('/optimize/:optimizationId', async (req, res) => {
  try {
    const { optimizationId } = req.params;
    const success = await evoVeRepairSystem.implementOptimization(optimizationId);
    
    if (success) {
      res.json({ success: true, message: `Optimization ${optimizationId} implemented successfully` });
    } else {
      res.status(500).json({ success: false, error: `Failed to implement optimization ${optimizationId}` });
    }
  } catch (error) {
    console.error('Error implementing optimization:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route GET /api/command-center/anima/state
 * @desc Get Anima's emotional state
 * @access Public
 */
router.get('/anima/state', (req, res) => {
  try {
    const state = animaCore.getEmotionalState();
    res.json({ success: true, state });
  } catch (error) {
    console.error('Error getting Anima state:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route POST /api/command-center/anima/event
 * @desc Process an emotional event for Anima
 * @access Public
 */
router.post('/anima/event', async (req, res) => {
  try {
    const { event, context } = req.body;
    
    if (!event) {
      return res.status(400).json({ success: false, error: 'Event is required' });
    }
    
    const result = await animaCore.processEmotionalEvent(event, context);
    res.json({ success: true, result });
  } catch (error) {
    console.error('Error processing emotional event:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route GET /api/command-center/mcp/servers
 * @desc Get MCP servers
 * @access Public
 */
router.get('/mcp/servers', (req, res) => {
  try {
    const servers = mcpBridge.getServers();
    res.json({ success: true, servers });
  } catch (error) {
    console.error('Error getting MCP servers:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route GET /api/command-center/mcp/tools
 * @desc Get MCP tools
 * @access Public
 */
router.get('/mcp/tools', (req, res) => {
  try {
    const tools = mcpBridge.getAllTools();
    res.json({ success: true, tools });
  } catch (error) {
    console.error('Error getting MCP tools:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route POST /api/command-center/mcp/execute
 * @desc Execute an MCP tool
 * @access Public
 */
router.post('/mcp/execute', async (req, res) => {
  try {
    const { server, tool, parameters } = req.body;
    
    if (!server || !tool) {
      return res.status(400).json({ success: false, error: 'Server and tool are required' });
    }
    
    const result = await mcpBridge.executeTool(server, tool, parameters || {});
    
    if (result.success) {
      res.json({ success: true, data: result.data });
    } else {
      res.status(500).json({ success: false, error: result.error });
    }
  } catch (error) {
    console.error('Error executing MCP tool:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route POST /api/command-center/mcp/start/:serverId
 * @desc Start an MCP server
 * @access Public
 */
router.post('/mcp/start/:serverId', async (req, res) => {
  try {
    const { serverId } = req.params;
    const success = await mcpBridge.startServer(serverId);
    
    if (success) {
      res.json({ success: true, message: `MCP server ${serverId} started successfully` });
    } else {
      res.status(500).json({ success: false, error: `Failed to start MCP server ${serverId}` });
    }
  } catch (error) {
    console.error('Error starting MCP server:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route POST /api/command-center/mcp/stop/:serverId
 * @desc Stop an MCP server
 * @access Public
 */
router.post('/mcp/stop/:serverId', async (req, res) => {
  try {
    const { serverId } = req.params;
    const success = await mcpBridge.stopServer(serverId);
    
    if (success) {
      res.json({ success: true, message: `MCP server ${serverId} stopped successfully` });
    } else {
      res.status(500).json({ success: false, error: `Failed to stop MCP server ${serverId}` });
    }
  } catch (error) {
    console.error('Error stopping MCP server:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route GET /api/command-center/llm/status
 * @desc Get LLM status
 * @access Public
 */
router.get('/llm/status', async (req, res) => {
  try {
    const ollamaAvailable = await llmConnector.isAvailable('ollama');
    const huggingfaceAvailable = await llmConnector.isAvailable('huggingface');
    
    let provider = 'none';
    if (ollamaAvailable) {
      provider = 'ollama';
    } else if (huggingfaceAvailable) {
      provider = 'huggingface';
    }
    
    res.json({
      success: true,
      status: {
        available: ollamaAvailable || huggingfaceAvailable,
        provider,
        ollama: ollamaAvailable,
        huggingface: huggingfaceAvailable
      }
    });
  } catch (error) {
    console.error('Error getting LLM status:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route GET /api/command-center/llm/models
 * @desc Get available LLM models
 * @access Public
 */
router.get('/llm/models', async (req, res) => {
  try {
    const provider = req.query.provider as string || undefined;
    const models = await llmConnector.getAvailableModels(provider as any);
    
    res.json({ success: true, models });
  } catch (error) {
    console.error('Error getting LLM models:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route POST /api/command-center/llm/generate
 * @desc Generate text with LLM
 * @access Public
 */
router.post('/llm/generate', async (req, res) => {
  try {
    const { prompt, options } = req.body;
    
    if (!prompt) {
      return res.status(400).json({ success: false, error: 'Prompt is required' });
    }
    
    const response = await llmConnector.generateText(prompt, options);
    res.json({ success: true, response });
  } catch (error) {
    console.error('Error generating text with LLM:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route GET /api/command-center/system/processes
 * @desc Get system processes
 * @access Public
 */
router.get('/system/processes', async (req, res) => {
  try {
    const { stdout } = await execAsync('ps -eo pid,ppid,cmd,%cpu,%mem | grep -i "python\\|node\\|anima\\|evove\\|gptsoul\\|azur" | grep -v grep');
    
    const processes = stdout.trim().split('\n').map(line => {
      const parts = line.trim().split(/\s+/);
      const pid = parseInt(parts[0]);
      const ppid = parseInt(parts[1]);
      const cpu = parseFloat(parts[parts.length - 2]);
      const mem = parseFloat(parts[parts.length - 1]);
      const cmd = parts.slice(2, parts.length - 2).join(' ');
      
      return { pid, ppid, cmd, cpu, mem };
    });
    
    res.json({ success: true, processes });
  } catch (error) {
    console.error('Error getting system processes:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route POST /api/command-center/system/kill/:pid
 * @desc Kill a system process
 * @access Public
 */
router.post('/system/kill/:pid', async (req, res) => {
  try {
    const { pid } = req.params;
    
    // Validate PID
    if (!pid || isNaN(parseInt(pid))) {
      return res.status(400).json({ success: false, error: 'Invalid PID' });
    }
    
    await execAsync(`kill ${pid}`);
    res.json({ success: true, message: `Process ${pid} killed successfully` });
  } catch (error) {
    console.error('Error killing process:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route GET /api/command-center/system/logs
 * @desc Get system logs
 * @access Public
 */
router.get('/system/logs', async (req, res) => {
  try {
    const { service } = req.query;
    const logsDir = path.join(process.cwd(), 'logs');
    
    if (!fs.existsSync(logsDir)) {
      return res.status(404).json({ success: false, error: 'Logs directory not found' });
    }
    
    let logFiles = fs.readdirSync(logsDir);
    
    // Filter by service if provided
    if (service) {
      logFiles = logFiles.filter(file => file.includes(service as string));
    }
    
    // Get log file stats
    const logs = logFiles.map(file => {
      const filePath = path.join(logsDir, file);
      const stats = fs.statSync(filePath);
      
      return {
        name: file,
        size: stats.size,
        modified: stats.mtime
      };
    });
    
    res.json({ success: true, logs });
  } catch (error) {
    console.error('Error getting system logs:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route GET /api/command-center/system/logs/:filename
 * @desc Get log file content
 * @access Public
 */
router.get('/system/logs/:filename', async (req, res) => {
  try {
    const { filename } = req.params;
    const { lines } = req.query;
    const logPath = path.join(process.cwd(), 'logs', filename);
    
    if (!fs.existsSync(logPath)) {
      return res.status(404).json({ success: false, error: 'Log file not found' });
    }
    
    let content;
    
    if (lines) {
      // Get last N lines
      const { stdout } = await execAsync(`tail -n ${lines} ${logPath}`);
      content = stdout;
    } else {
      // Get entire file
      content = fs.readFileSync(logPath, 'utf-8');
    }
    
    res.json({ success: true, content });
  } catch (error) {
    console.error('Error getting log content:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @route POST /api/command-center/system/restart
 * @desc Restart a system service
 * @access Public
 */
router.post('/system/restart', async (req, res) => {
  try {
    const { service } = req.body;
    
    if (!service) {
      return res.status(400).json({ success: false, error: 'Service name is required' });
    }
    
    // Map service name to script
    const serviceScripts: Record<string, string> = {
      'anima': 'scripts/start_anima_cli.sh',
      'evove': 'scripts/start_evove.sh',
      'server': 'scripts/start.sh',
      'mcp': 'scripts/start_mcp_servers.sh'
    };
    
    const script = serviceScripts[service];
    
    if (!script) {
      return res.status(400).json({ success: false, error: `Unknown service: ${service}` });
    }
    
    // Kill existing processes
    await execAsync(`pkill -f "${service}"`);
    
    // Start service
    const scriptPath = path.join(process.cwd(), script);
    await execAsync(`bash ${scriptPath} &`);
    
    res.json({ success: true, message: `Service ${service} restarted successfully` });
  } catch (error) {
    console.error('Error restarting service:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * Set up WebSocket handlers for the Soul Command Center
 * @param wss WebSocket server
 */
export function setupCommandCenterWebSocket(wss: WebSocket.Server): void {
  // Track connected clients
  const clients = new Set<WebSocket>();
  
  // Handle new connections
  wss.on('connection', (ws) => {
    // Add client to set
    clients.add(ws);
    
    console.log('Client connected to Command Center WebSocket');
    
    // Send initial state
    ws.send(JSON.stringify({
      type: 'system:state',
      data: {
        components: evoVeCore.getComponents().length,
        issues: evoVeCore.getIssues().length,
        anima: animaCore.getEmotionalState()
      }
    }));
    
    // Handle messages
    ws.on('message', async (message) => {
      try {
        const data = JSON.parse(message.toString());
        
        // Handle message based on type
        switch (data.type) {
          case 'ping':
            ws.send(JSON.stringify({
              type: 'pong',
              timestamp: new Date().toISOString()
            }));
            break;
            
          case 'subscribe':
            // Handle subscription requests
            // This would set up event listeners for the requested events
            break;
            
          default:
            console.log(`Unknown message type: ${data.type}`);
        }
      } catch (error) {
        console.error('Error handling WebSocket message:', error);
        ws.send(JSON.stringify({
          type: 'error',
          message: 'Error processing message'
        }));
      }
    });
    
    // Handle disconnection
    ws.on('close', () => {
      // Remove client from set
      clients.delete(ws);
      console.log('Client disconnected from Command Center WebSocket');
    });
    
    // Handle errors
    ws.on('error', (error) => {
      console.error('WebSocket error:', error);
    });
  });
  
  // Set up event listeners
  
  // EvoVe events
  evoVeCore.onEvent('issue:detected', (issue) => {
    broadcastToClients({
      type: 'issue:detected',
      data: issue
    });
  });
  
  evoVeCore.onEvent('issue:resolved', (data) => {
    broadcastToClients({
      type: 'issue:resolved',
      data
    });
  });
  
  // Anima events
  animaCore.onEvent('emotional:state:updated', (state) => {
    broadcastToClients({
      type: 'anima:state',
      data: state
    });
  });
  
  // MCP events
  mcpBridge.onEvent('server:online', (server) => {
    broadcastToClients({
      type: 'mcp:server:online',
      data: server
    });
  });
  
  mcpBridge.onEvent('server:offline', (server) => {
    broadcastToClients({
      type: 'mcp:server:offline',
      data: server
    });
  });
  
  mcpBridge.onEvent('tools:discovered', (data) => {
    broadcastToClients({
      type: 'mcp:tools:discovered',
      data
    });
  });
  
  // Broadcast message to all connected clients
  function broadcastToClients(message: any): void {
    const messageStr = JSON.stringify(message);
    
    for (const client of clients) {
      if (client.readyState === WebSocket.OPEN) {
        client.send(messageStr);
      }
    }
  }
}

export default router;
