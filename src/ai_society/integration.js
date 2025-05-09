/**
 * Integration Script for AI Society
 * 
 * This script provides a way to integrate the AI Society with the existing SoulCoreHub server.
 * It should be required in the main server.js file.
 */

// This will be populated once TypeScript is compiled
let societyApi;
let setupSocietyWebsocket;

try {
  // Try to import from compiled TypeScript
  const aiSocietyApi = require('../dist/ai_society/api');
  societyApi = aiSocietyApi.societyApi;
  setupSocietyWebsocket = aiSocietyApi.setupSocietyWebsocket;
  console.log('AI Society loaded from compiled TypeScript');
} catch (error) {
  console.error('Failed to load AI Society from compiled TypeScript:', error.message);
  console.log('Please compile the TypeScript files first with: npx tsc');
  
  // Provide dummy implementations
  societyApi = require('express').Router();
  setupSocietyWebsocket = () => console.log('AI Society WebSocket setup skipped');
}

/**
 * Integrate AI Society with Express app
 * @param {Express} app - Express application
 */
function integrateWithExpress(app) {
  // Add API routes
  app.use('/api/society', societyApi);
  console.log('AI Society API routes registered at /api/society');
}

/**
 * Integrate AI Society with WebSocket server
 * @param {WebSocket.Server} wss - WebSocket server
 */
function integrateWithWebSocket(wss) {
  // Set up WebSocket handler
  setupSocietyWebsocket(wss);
  console.log('AI Society WebSocket handler registered');
}

module.exports = {
  integrateWithExpress,
  integrateWithWebSocket
};
