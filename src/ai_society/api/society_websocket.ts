/**
 * WebSocket Handler for AI Society
 * 
 * This module provides WebSocket functionality for real-time updates from the AI Society.
 */

import WebSocket from 'ws';
import { aiSociety } from '../index';

/**
 * Set up WebSocket server for AI Society
 * @param wss WebSocket server
 */
export function setupSocietyWebsocket(wss: WebSocket.Server): void {
  // Track connected clients
  const clients = new Set<WebSocket>();
  
  // Handle new connections
  wss.on('connection', (ws) => {
    clients.add(ws);
    console.log('New client connected to AI Society WebSocket');
    
    // Send initial stats
    aiSociety.getSimulationStats().then(stats => {
      ws.send(JSON.stringify({
        type: 'stats',
        data: stats
      }));
    });
    
    // Handle client disconnect
    ws.on('close', () => {
      clients.delete(ws);
      console.log('Client disconnected from AI Society WebSocket');
    });
    
    // Handle client messages
    ws.on('message', async (message) => {
      try {
        const data = JSON.parse(message.toString());
        
        switch (data.type) {
          case 'subscribe':
            // Handle subscription requests
            console.log(`Client subscribed to ${data.topic}`);
            break;
            
          case 'command':
            // Handle commands
            console.log(`Received command: ${data.command}`);
            break;
            
          default:
            console.warn(`Unknown message type: ${data.type}`);
        }
      } catch (error) {
        console.error('Error handling WebSocket message', error);
      }
    });
  });
  
  // Set up event listeners for AI Society events
  
  // Listen for simulation tick events
  aiSociety['simulationClock'].onEvent('simulation:tick', (data) => {
    broadcast({
      type: 'tick',
      data
    });
  });
  
  // Listen for simulation stats events
  aiSociety['simulationClock'].onEvent('simulation:stats', (data) => {
    broadcast({
      type: 'stats',
      data
    });
  });
  
  // Listen for agent speech events
  aiSociety['behaviorCore'].onEvent('agent:speak', (data) => {
    broadcast({
      type: 'speech',
      data
    });
  });
  
  // Listen for agent interaction events
  aiSociety['behaviorCore'].onEvent('agent:interact', (data) => {
    broadcast({
      type: 'interaction',
      data
    });
  });
  
  /**
   * Broadcast message to all connected clients
   * @param data Data to broadcast
   */
  function broadcast(data: any): void {
    const message = JSON.stringify(data);
    
    clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    });
  }
}
