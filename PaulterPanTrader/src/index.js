/**
 * Paulter Pan Trader - Main Application Entry Point
 * 
 * This file serves as the main entry point for the Paulter Pan Trader application,
 * initializing all necessary components and starting the web server.
 */

const express = require('express');
const path = require('path');
const marketDataService = require('./services/marketDataService');
const tradingStrategiesService = require('./services/tradingStrategiesService');
const projectionService = require('./services/projectionService');

// Initialize express app
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, '../public')));

// API Routes
app.use('/api/market-data', require('../api/marketDataRoutes'));
app.use('/api/strategies', require('../api/strategyRoutes'));
app.use('/api/projections', require('../api/projectionRoutes'));
app.use('/api/platforms', require('../api/platformRoutes'));

// Initialize services
async function initializeServices() {
  try {
    await marketDataService.initialize();
    await tradingStrategiesService.initialize();
    await projectionService.initialize();
    
    console.log('All services initialized successfully');
  } catch (error) {
    console.error('Failed to initialize services:', error);
    process.exit(1);
  }
}

// Start server
app.listen(PORT, async () => {
  console.log(`Paulter Pan Trader server running on port ${PORT}`);
  await initializeServices();
});
