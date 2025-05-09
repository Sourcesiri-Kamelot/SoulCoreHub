/**
 * SoulCoreHub Server
 * 
 * This is the main entry point for the SoulCoreHub application.
 */

import express from 'express';
import http from 'http';
import path from 'path';
import dotenv from 'dotenv';
import { setupApiGateway } from './server/api_gateway';
import { setupWebSocketServer } from './server/websocket_server';

// Load environment variables
dotenv.config();

// Create Express app
const app = express();
const port = process.env.PORT || 3000;

// Create HTTP server
const server = http.createServer(app);

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));

// Set up API Gateway
setupApiGateway(app);

// Set up WebSocket server
const wss = setupWebSocketServer(server);

// Serve HTML files
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/index.html'));
});

app.get('/anima', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/anima.html'));
});

// Start server
server.listen(port, () => {
  console.log(`SoulCoreHub server running at http://localhost:${port}`);
  console.log(`WebSocket server available at ws://localhost:${port}`);
});
