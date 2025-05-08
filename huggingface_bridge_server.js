#!/usr/bin/env node
/**
 * SoulCoreHub - Hugging Face Bridge Server
 * 
 * This server provides a REST API interface to the Hugging Face integration,
 * allowing other components of SoulCoreHub to access Hugging Face models
 * through HTTP requests.
 * 
 * @author SoulCoreHub
 * @version 1.0.0
 */

const express = require('express');
const fs = require('fs');
const path = require('path');
const { huggingFaceService, hfEvents } = require('./huggingface_integration');

// Create Express app
const app = express();
app.use(express.json());

// Set port from environment or default
const PORT = process.env.HF_BRIDGE_PORT || 3456;

// Configure CORS for local development
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  
  if (req.method === 'OPTIONS') {
    return res.sendStatus(200);
  }
  
  next();
});

// Middleware to log requests
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Text generation endpoint
app.post('/api/generate-text', async (req, res) => {
  try {
    const { prompt, model } = req.body;
    
    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }
    
    const result = await huggingFaceService.generateText(prompt, model);
    res.json({ result });
  } catch (error) {
    console.error('Error generating text:', error);
    res.status(500).json({ error: error.message });
  }
});

// Image generation endpoint
app.post('/api/generate-image', async (req, res) => {
  try {
    const { prompt, model } = req.body;
    
    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }
    
    const result = await huggingFaceService.generateImage(prompt, model);
    
    // Save the image to a file
    const timestamp = Date.now();
    const imagePath = path.join(__dirname, 'public', 'generated_images', `image_${timestamp}.png`);
    
    // Ensure directory exists
    const dir = path.dirname(imagePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    
    // Write image data to file
    fs.writeFileSync(imagePath, result);
    
    // Return the relative path to the image
    const relativePath = `/generated_images/image_${timestamp}.png`;
    res.json({ imagePath: relativePath });
  } catch (error) {
    console.error('Error generating image:', error);
    res.status(500).json({ error: error.message });
  }
});

// Sentiment analysis endpoint
app.post('/api/analyze-sentiment', async (req, res) => {
  try {
    const { text } = req.body;
    
    if (!text) {
      return res.status(400).json({ error: 'Text is required' });
    }
    
    const result = await huggingFaceService.analyzeSentiment(text);
    res.json(result);
  } catch (error) {
    console.error('Error analyzing sentiment:', error);
    res.status(500).json({ error: error.message });
  }
});

// Text summarization endpoint
app.post('/api/summarize-text', async (req, res) => {
  try {
    const { text } = req.body;
    
    if (!text) {
      return res.status(400).json({ error: 'Text is required' });
    }
    
    const result = await huggingFaceService.summarizeText(text);
    res.json({ summary: result });
  } catch (error) {
    console.error('Error summarizing text:', error);
    res.status(500).json({ error: error.message });
  }
});

// Agent task execution endpoint
app.post('/api/execute-task', async (req, res) => {
  try {
    const { task } = req.body;
    
    if (!task) {
      return res.status(400).json({ error: 'Task description is required' });
    }
    
    const result = await huggingFaceService.executeTask(task);
    res.json({ result });
  } catch (error) {
    console.error('Error executing task:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get usage statistics endpoint
app.get('/api/stats', (req, res) => {
  const stats = huggingFaceService.getUsageStatistics();
  res.json(stats);
});

// Get event logs endpoint
app.get('/api/logs', (req, res) => {
  const logs = huggingFaceService.getEventLogs();
  res.json(logs);
});

// Start the server
const server = app.listen(PORT, () => {
  console.log(`Hugging Face Bridge Server running on port ${PORT}`);
});

// Handle graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});

// Export for testing
module.exports = { app, server };
