/**
 * WebSocket Server for SoulCoreHub
 * 
 * This module sets up the WebSocket server for SoulCoreHub, enabling real-time
 * communication between the system and clients.
 */

import WebSocket from 'ws';
import http from 'http';
import { animaCore } from '../agents/anima';
import { setupCommandCenterWebSocket } from './soul_command_center_api';

/**
 * Set up the WebSocket server
 * @param server HTTP server
 * @returns WebSocket server
 */
export function setupWebSocketServer(server: http.Server) {
  const wss = new WebSocket.Server({ server });
  
  // Set up WebSocket routes
  const animaWss = new WebSocket.Server({ noServer: true });
  const commandCenterWss = new WebSocket.Server({ noServer: true });
  
  // Handle upgrade requests to route to the correct WebSocket server
  server.on('upgrade', (request, socket, head) => {
    const pathname = new URL(request.url || '', `http://${request.headers.host}`).pathname;
    
    if (pathname === '/anima') {
      animaWss.handleUpgrade(request, socket, head, (ws) => {
        animaWss.emit('connection', ws, request);
      });
    } else if (pathname === '/command-center') {
      commandCenterWss.handleUpgrade(request, socket, head, (ws) => {
        commandCenterWss.emit('connection', ws, request);
      });
    } else {
      // Default WebSocket server
      wss.handleUpgrade(request, socket, head, (ws) => {
        wss.emit('connection', ws, request);
      });
    }
  });
  
  // Set up Anima WebSocket handlers
  setupAnimaWebSocket(animaWss);
  
  // Set up Command Center WebSocket handlers
  setupCommandCenterWebSocket(commandCenterWss);
  
  // Set up default WebSocket handlers
  wss.on('connection', (ws) => {
    console.log('Client connected to default WebSocket');
    
    // Send welcome message
    ws.send(JSON.stringify({
      type: 'welcome',
      message: 'Welcome to SoulCoreHub WebSocket Server',
      timestamp: new Date().toISOString()
    }));
    
    // Handle messages
    ws.on('message', (message) => {
      try {
        const data = JSON.parse(message.toString());
        
        if (data.type === 'ping') {
          ws.send(JSON.stringify({
            type: 'pong',
            timestamp: new Date().toISOString()
          }));
        }
      } catch (error) {
        console.error('Error handling WebSocket message:', error);
        ws.send(JSON.stringify({
          type: 'error',
          message: 'Error processing message'
        }));
      }
    });
    
    ws.on('close', () => {
      console.log('Client disconnected from default WebSocket');
    });
    
    ws.on('error', (error) => {
      console.error('WebSocket error:', error);
    });
  });
  
  console.log('WebSocket server initialized');
  return wss;
}

/**
 * Set up Anima WebSocket handlers
 * @param wss WebSocket server
 */
function setupAnimaWebSocket(wss: WebSocket.Server): void {
  wss.on('connection', (ws) => {
    console.log('Client connected to Anima WebSocket');
    
    // Send initial state
    ws.send(JSON.stringify({
      type: 'anima:state',
      data: animaCore.getEmotionalState()
    }));
    
    // Listen for Anima events
    animaCore.onEvent('emotional:state:updated', (state) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          type: 'anima:state',
          data: state
        }));
      }
    });
    
    // Handle messages
    ws.on('message', async (message) => {
      try {
        const data = JSON.parse(message.toString());
        
        if (data.type === 'anima:analyze') {
          const emotion = await animaCore.analyzeEmotion(data.text);
          ws.send(JSON.stringify({
            type: 'anima:analysis',
            data: emotion
          }));
        } else if (data.type === 'anima:respond') {
          const response = await animaCore.generateEmotionalResponse(data.input);
          ws.send(JSON.stringify({
            type: 'anima:response',
            data: response
          }));
        } else if (data.type === 'anima:process-event') {
          const result = await animaCore.processEmotionalEvent(data.event, data.context);
          ws.send(JSON.stringify({
            type: 'anima:event-result',
            data: result
          }));
        } else if (data.type === 'anima:reflect') {
          const reflection = await animaCore.generateEmotionalReflection(data.topic);
          ws.send(JSON.stringify({
            type: 'anima:reflection',
            data: reflection
          }));
        } else if (data.type === 'ping') {
          ws.send(JSON.stringify({
            type: 'pong',
            timestamp: new Date().toISOString()
          }));
        }
      } catch (error) {
        console.error('Error handling WebSocket message:', error);
        ws.send(JSON.stringify({
          type: 'error',
          message: 'Error processing message'
        }));
      }
    });
    
    ws.on('close', () => {
      console.log('Client disconnected from Anima WebSocket');
    });
    
    ws.on('error', (error) => {
      console.error('WebSocket error:', error);
    });
  });
}
