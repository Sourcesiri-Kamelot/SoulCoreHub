/**
 * SoulCoreHub API Gateway
 * 
 * This module sets up an Express server with API routes and middleware:
 * - Authentication
 * - Payment processing
 * - WebSocket support
 * - CORS and security headers
 */

const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const { authMiddleware } = require('../auth/auth_middleware');
const authRoutes = require('../auth/auth_routes');
const paymentRoutes = require('../payments/stripe_routes');

// Create Express app
const app = express();

// Create HTTP server
const server = http.createServer(app);

// Create WebSocket server
const wss = new WebSocket.Server({ server });

// Set up rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    success: false,
    error: 'Too many requests',
    message: 'Too many requests from this IP, please try again later'
  }
});

// Apply middleware
app.use(helmet()); // Security headers
app.use(cors()); // CORS
app.use(limiter); // Rate limiting
app.use(express.json()); // Parse JSON bodies
app.use(express.urlencoded({ extended: true })); // Parse URL-encoded bodies

// Apply authentication middleware to all routes except /public and /auth
app.use((req, res, next) => {
  if (req.path.startsWith('/public') || req.path.startsWith('/auth') || req.path === '/health' || req.path === '/payments/webhook') {
    return next();
  }
  authMiddleware(req, res, next);
});

// Set up routes
app.use('/auth', authRoutes);
app.use('/payments', paymentRoutes);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString()
  });
});

// API routes
app.get('/api/user/profile', (req, res) => {
  // User is added to req by auth middleware
  res.json({
    success: true,
    user: req.user
  });
});

// Handle WebSocket connections
wss.on('connection', (ws) => {
  console.log('Client connected');
  
  // Send welcome message
  ws.send(JSON.stringify({
    type: 'connection',
    message: 'Connected to SoulCoreHub WebSocket server'
  }));
  
  // Handle messages
  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      
      // Handle different message types
      switch (data.type) {
        case 'ping':
          ws.send(JSON.stringify({
            type: 'pong',
            timestamp: new Date().toISOString()
          }));
          break;
          
        case 'subscribe':
          // Handle subscription to a topic
          handleSubscription(ws, data);
          break;
          
        case 'unsubscribe':
          // Handle unsubscription from a topic
          handleUnsubscription(ws, data);
          break;
          
        default:
          ws.send(JSON.stringify({
            type: 'error',
            message: `Unknown message type: ${data.type}`
          }));
      }
    } catch (error) {
      console.error('WebSocket message error:', error);
      ws.send(JSON.stringify({
        type: 'error',
        message: 'Invalid message format'
      }));
    }
  });
  
  // Handle disconnection
  ws.on('close', () => {
    console.log('Client disconnected');
  });
});

// Handle WebSocket subscriptions
function handleSubscription(ws, data) {
  const { topic } = data;
  
  if (!topic) {
    return ws.send(JSON.stringify({
      type: 'error',
      message: 'Topic is required for subscription'
    }));
  }
  
  // Store subscription info on the WebSocket connection
  if (!ws.subscriptions) {
    ws.subscriptions = new Set();
  }
  
  ws.subscriptions.add(topic);
  
  ws.send(JSON.stringify({
    type: 'subscribed',
    topic,
    message: `Subscribed to ${topic}`
  }));
}

// Handle WebSocket unsubscriptions
function handleUnsubscription(ws, data) {
  const { topic } = data;
  
  if (!topic) {
    return ws.send(JSON.stringify({
      type: 'error',
      message: 'Topic is required for unsubscription'
    }));
  }
  
  // Remove subscription
  if (ws.subscriptions) {
    ws.subscriptions.delete(topic);
  }
  
  ws.send(JSON.stringify({
    type: 'unsubscribed',
    topic,
    message: `Unsubscribed from ${topic}`
  }));
}

// Broadcast message to all clients subscribed to a topic
function broadcastToTopic(topic, data) {
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN && 
        client.subscriptions && 
        client.subscriptions.has(topic)) {
      client.send(JSON.stringify({
        type: 'message',
        topic,
        data
      }));
    }
  });
}

// Start server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

// Export for testing
module.exports = {
  app,
  server,
  wss,
  broadcastToTopic
};
