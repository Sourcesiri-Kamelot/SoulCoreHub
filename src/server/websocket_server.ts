/**
 * WebSocket Server for SoulCoreHub
 * 
 * This module sets up the WebSocket server for SoulCoreHub, enabling real-time
 * communication between the system and clients.
 */

import WebSocket from 'ws';
import http from 'http';
import { animaCore } from '../agents/anima';

/**
 * Set up the WebSocket server
 * @param server HTTP server
 * @returns WebSocket server
 */
export function setupWebSocketServer(server: http.Server) {
  const wss = new WebSocket.Server({ server });
  
  wss.on('connection', (ws) => {
    console.log('Client connected to WebSocket');
    
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
      console.log('Client disconnected from WebSocket');
    });
    
    ws.on('error', (error) => {
      console.error('WebSocket error:', error);
    });
  });
  
  console.log('WebSocket server initialized');
  return wss;
}
