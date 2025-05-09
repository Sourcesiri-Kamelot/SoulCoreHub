/**
 * SoulCoreHub WebSocket Handler
 * 
 * This module provides WebSocket functionality for real-time updates:
 * - Market data streaming
 * - Trading signals
 * - Agent status updates
 * - Subscription-based messaging
 */

const WebSocket = require('ws');
const jwt = require('jsonwebtoken');
const { getSecrets } = require('../aws/secrets_manager');

// Store for active connections and their subscriptions
const connections = new Map();

// Topic handlers for different subscription types
const topicHandlers = {
  'market': handleMarketData,
  'trading': handleTradingSignals,
  'agent': handleAgentUpdates,
  'system': handleSystemEvents
};

/**
 * Initialize WebSocket server
 * @param {http.Server} server - HTTP server to attach WebSocket server to
 * @returns {WebSocket.Server} - WebSocket server instance
 */
function initWebSocketServer(server) {
  const wss = new WebSocket.Server({ server });
  
  wss.on('connection', handleConnection);
  
  console.log('WebSocket server initialized');
  return wss;
}

/**
 * Handle new WebSocket connection
 * @param {WebSocket} ws - WebSocket connection
 * @param {http.IncomingMessage} req - HTTP request
 */
function handleConnection(ws, req) {
  console.log('New WebSocket connection');
  
  // Initialize connection data
  const connectionId = generateConnectionId();
  const connectionData = {
    id: connectionId,
    ws,
    subscriptions: new Set(),
    authenticated: false,
    userId: null,
    connectedAt: new Date()
  };
  
  // Store connection
  connections.set(connectionId, connectionData);
  
  // Send welcome message
  sendMessage(ws, {
    type: 'connection',
    connectionId,
    message: 'Connected to SoulCoreHub WebSocket server'
  });
  
  // Set up message handler
  ws.on('message', (message) => handleMessage(connectionData, message));
  
  // Set up close handler
  ws.on('close', () => handleClose(connectionData));
  
  // Set up error handler
  ws.on('error', (error) => handleError(connectionData, error));
}

/**
 * Handle WebSocket message
 * @param {Object} connection - Connection data
 * @param {string} message - Raw message data
 */
function handleMessage(connection, message) {
  try {
    const data = JSON.parse(message);
    
    // Handle different message types
    switch (data.type) {
      case 'authenticate':
        handleAuthentication(connection, data);
        break;
        
      case 'subscribe':
        handleSubscription(connection, data);
        break;
        
      case 'unsubscribe':
        handleUnsubscription(connection, data);
        break;
        
      case 'ping':
        handlePing(connection);
        break;
        
      default:
        sendMessage(connection.ws, {
          type: 'error',
          message: `Unknown message type: ${data.type}`
        });
    }
  } catch (error) {
    console.error('WebSocket message error:', error);
    sendMessage(connection.ws, {
      type: 'error',
      message: 'Invalid message format'
    });
  }
}

/**
 * Handle WebSocket authentication
 * @param {Object} connection - Connection data
 * @param {Object} data - Message data
 */
async function handleAuthentication(connection, data) {
  const { token } = data;
  
  if (!token) {
    return sendMessage(connection.ws, {
      type: 'error',
      message: 'Authentication token is required'
    });
  }
  
  try {
    // Get JWT secret
    const secrets = await getSecrets('SoulCoreSecrets');
    const jwtSecret = secrets.JWT_SECRET || process.env.JWT_SECRET;
    
    if (!jwtSecret) {
      throw new Error('JWT secret not found');
    }
    
    // Verify token
    const decoded = jwt.verify(token, jwtSecret);
    
    // Update connection data
    connection.authenticated = true;
    connection.userId = decoded.id;
    connection.userRole = decoded.role;
    connection.userTier = decoded.tier;
    
    // Send success message
    sendMessage(connection.ws, {
      type: 'authenticated',
      message: 'Authentication successful'
    });
  } catch (error) {
    console.error('Authentication error:', error);
    sendMessage(connection.ws, {
      type: 'error',
      message: 'Authentication failed: ' + error.message
    });
  }
}

/**
 * Handle subscription request
 * @param {Object} connection - Connection data
 * @param {Object} data - Message data
 */
function handleSubscription(connection, data) {
  const { topic, parameters } = data;
  
  if (!topic) {
    return sendMessage(connection.ws, {
      type: 'error',
      message: 'Topic is required for subscription'
    });
  }
  
  // Check if authentication is required for this topic
  if (requiresAuthentication(topic) && !connection.authenticated) {
    return sendMessage(connection.ws, {
      type: 'error',
      message: 'Authentication required for this topic'
    });
  }
  
  // Check if subscription is allowed for user's tier
  if (!isSubscriptionAllowed(topic, connection.userTier)) {
    return sendMessage(connection.ws, {
      type: 'error',
      message: `Your subscription tier (${connection.userTier}) does not allow access to this topic`
    });
  }
  
  // Add subscription
  const subscriptionId = `${topic}:${JSON.stringify(parameters || {})}`;
  connection.subscriptions.add(subscriptionId);
  
  // Send confirmation
  sendMessage(connection.ws, {
    type: 'subscribed',
    topic,
    parameters,
    message: `Subscribed to ${topic}`
  });
  
  // Send initial data if available
  const handler = topicHandlers[topic.split(':')[0]];
  if (handler) {
    handler(connection, 'subscribe', { topic, parameters });
  }
}

/**
 * Handle unsubscription request
 * @param {Object} connection - Connection data
 * @param {Object} data - Message data
 */
function handleUnsubscription(connection, data) {
  const { topic, parameters } = data;
  
  if (!topic) {
    return sendMessage(connection.ws, {
      type: 'error',
      message: 'Topic is required for unsubscription'
    });
  }
  
  // Remove subscription
  const subscriptionId = `${topic}:${JSON.stringify(parameters || {})}`;
  connection.subscriptions.delete(subscriptionId);
  
  // Send confirmation
  sendMessage(connection.ws, {
    type: 'unsubscribed',
    topic,
    parameters,
    message: `Unsubscribed from ${topic}`
  });
  
  // Notify handler
  const handler = topicHandlers[topic.split(':')[0]];
  if (handler) {
    handler(connection, 'unsubscribe', { topic, parameters });
  }
}

/**
 * Handle ping request
 * @param {Object} connection - Connection data
 */
function handlePing(connection) {
  sendMessage(connection.ws, {
    type: 'pong',
    timestamp: new Date().toISOString()
  });
}

/**
 * Handle WebSocket close
 * @param {Object} connection - Connection data
 */
function handleClose(connection) {
  console.log(`WebSocket connection ${connection.id} closed`);
  
  // Clean up subscriptions
  connection.subscriptions.clear();
  
  // Remove connection
  connections.delete(connection.id);
}

/**
 * Handle WebSocket error
 * @param {Object} connection - Connection data
 * @param {Error} error - Error object
 */
function handleError(connection, error) {
  console.error(`WebSocket error for connection ${connection.id}:`, error);
}

/**
 * Send message to WebSocket
 * @param {WebSocket} ws - WebSocket connection
 * @param {Object} data - Message data
 */
function sendMessage(ws, data) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(data));
  }
}

/**
 * Broadcast message to all connections
 * @param {Object} data - Message data
 */
function broadcast(data) {
  connections.forEach((connection) => {
    sendMessage(connection.ws, data);
  });
}

/**
 * Broadcast message to all connections subscribed to a topic
 * @param {string} topic - Topic to broadcast to
 * @param {Object} data - Message data
 * @param {Object} parameters - Topic parameters to match
 */
function broadcastToTopic(topic, data, parameters = {}) {
  const subscriptionId = `${topic}:${JSON.stringify(parameters)}`;
  
  connections.forEach((connection) => {
    if (connection.subscriptions.has(subscriptionId)) {
      sendMessage(connection.ws, {
        type: 'message',
        topic,
        parameters,
        data
      });
    }
  });
}

/**
 * Broadcast message to a specific user
 * @param {string} userId - User ID to broadcast to
 * @param {Object} data - Message data
 */
function broadcastToUser(userId, data) {
  connections.forEach((connection) => {
    if (connection.userId === userId) {
      sendMessage(connection.ws, data);
    }
  });
}

/**
 * Check if a topic requires authentication
 * @param {string} topic - Topic to check
 * @returns {boolean} - Whether authentication is required
 */
function requiresAuthentication(topic) {
  // Public topics that don't require authentication
  const publicTopics = ['system:status', 'system:announcements'];
  
  return !publicTopics.includes(topic);
}

/**
 * Check if a subscription is allowed for a user's tier
 * @param {string} topic - Topic to check
 * @param {string} tier - User's subscription tier
 * @returns {boolean} - Whether subscription is allowed
 */
function isSubscriptionAllowed(topic, tier) {
  // If no tier is specified, default to free
  tier = tier || 'free';
  
  // Define topic access by tier
  const tierAccess = {
    free: ['system:status', 'system:announcements', 'market:summary'],
    pro: ['system:status', 'system:announcements', 'market:summary', 'market:detail', 'trading:signals'],
    enterprise: ['system:status', 'system:announcements', 'market:summary', 'market:detail', 'trading:signals', 'trading:advanced', 'agent:status'],
    trader: ['system:status', 'system:announcements', 'market:summary', 'market:detail', 'trading:signals'],
    trader_pro: ['system:status', 'system:announcements', 'market:summary', 'market:detail', 'trading:signals', 'trading:advanced']
  };
  
  // Check if topic is allowed for tier
  return tierAccess[tier] && tierAccess[tier].some(allowedTopic => 
    topic === allowedTopic || topic.startsWith(`${allowedTopic}:`)
  );
}

/**
 * Generate a unique connection ID
 * @returns {string} - Unique connection ID
 */
function generateConnectionId() {
  return `conn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Handle market data updates
 * @param {Object} connection - Connection data
 * @param {string} action - Action (subscribe, unsubscribe)
 * @param {Object} data - Message data
 */
function handleMarketData(connection, action, data) {
  const { topic, parameters } = data;
  
  if (action === 'subscribe') {
    // Send initial market data
    sendMessage(connection.ws, {
      type: 'message',
      topic,
      parameters,
      data: {
        timestamp: new Date().toISOString(),
        markets: [
          { symbol: 'BTC-USD', price: 50000, change: 2.5 },
          { symbol: 'ETH-USD', price: 3000, change: 1.8 },
          { symbol: 'SOL-USD', price: 150, change: 3.2 }
        ]
      }
    });
  }
}

/**
 * Handle trading signals updates
 * @param {Object} connection - Connection data
 * @param {string} action - Action (subscribe, unsubscribe)
 * @param {Object} data - Message data
 */
function handleTradingSignals(connection, action, data) {
  const { topic, parameters } = data;
  
  if (action === 'subscribe') {
    // Send initial trading signals
    sendMessage(connection.ws, {
      type: 'message',
      topic,
      parameters,
      data: {
        timestamp: new Date().toISOString(),
        signals: [
          { symbol: 'BTC-USD', action: 'BUY', confidence: 0.85, reason: 'Bullish pattern detected' },
          { symbol: 'ETH-USD', action: 'HOLD', confidence: 0.65, reason: 'Consolidation phase' }
        ]
      }
    });
  }
}

/**
 * Handle agent status updates
 * @param {Object} connection - Connection data
 * @param {string} action - Action (subscribe, unsubscribe)
 * @param {Object} data - Message data
 */
function handleAgentUpdates(connection, action, data) {
  const { topic, parameters } = data;
  
  if (action === 'subscribe') {
    // Send initial agent status
    sendMessage(connection.ws, {
      type: 'message',
      topic,
      parameters,
      data: {
        timestamp: new Date().toISOString(),
        agents: [
          { name: 'GPTSoul', status: 'active', lastUpdate: new Date().toISOString() },
          { name: 'Anima', status: 'active', lastUpdate: new Date().toISOString() },
          { name: 'EvoVe', status: 'developing', lastUpdate: new Date().toISOString() },
          { name: 'Azür', status: 'active', lastUpdate: new Date().toISOString() }
        ]
      }
    });
  }
}

/**
 * Handle system events
 * @param {Object} connection - Connection data
 * @param {string} action - Action (subscribe, unsubscribe)
 * @param {Object} data - Message data
 */
function handleSystemEvents(connection, action, data) {
  const { topic, parameters } = data;
  
  if (action === 'subscribe') {
    // Send initial system status
    sendMessage(connection.ws, {
      type: 'message',
      topic,
      parameters,
      data: {
        timestamp: new Date().toISOString(),
        status: 'operational',
        message: 'All systems operational',
        version: '1.0.0'
      }
    });
  }
}

module.exports = {
  initWebSocketServer,
  broadcast,
  broadcastToTopic,
  broadcastToUser,
  connections
};
