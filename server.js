/**
 * SoulCoreHub Main Server
 * 
 * This is the main entry point for the SoulCoreHub application.
 * It sets up the Express server, WebSocket support, and integrates all components.
 */

const express = require('express');
const http = require('http');
const path = require('path');
const dotenv = require('dotenv');
const WebSocket = require('ws');
const bodyParser = require('body-parser');
const fs = require('fs');
const { exec } = require('child_process');
const open = require('open');

// Import Hugging Face integration
const { huggingFaceService } = require('./huggingface_integration');

// Load environment variables
dotenv.config();

// Import middleware and routes
const { securityHeaders, rateLimiter, requestId, requestLogger, sanitizeParams } = require('./security/security_middleware');
const { authMiddleware } = require('./auth/auth_middleware');
const authRoutes = require('./auth/auth_routes');
const paymentRoutes = require('./payments/stripe_routes');
const websocketHandler = require('./api/websocket_handler');
const stripeHandler = require('./payments/stripe_handler');

// Initialize Express app
const app = express();
const port = process.env.PORT || 3000;

// Create HTTP server
const server = http.createServer(app);

// Apply middleware
app.use(securityHeaders());
app.use(rateLimiter());
app.use(requestId());
app.use(requestLogger());
app.use(express.static('public'));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(sanitizeParams());

// Serve static files from the React app if it exists
if (fs.existsSync(path.join(__dirname, 'anima-interface/build'))) {
  app.use(express.static(path.join(__dirname, 'anima-interface/build')));
}

// Initialize WebSocket server
const wss = websocketHandler.initWebSocketServer(server);

// Initialize Stripe
stripeHandler.initStripe();

// File Path
const dataFilePath = 'data.json';

// Default Structure
let data = {
  ideas: [],
  projects: [],
  repos: [],
  subscriptions: [],
  resonance: {},
  predictions: {}
};

// 📥 Load Data
function loadData() {
  try {
    if (fs.existsSync(dataFilePath)) {
      const raw = fs.readFileSync(dataFilePath, 'utf8');
      data = JSON.parse(raw);
      console.log('✅ Data loaded.');
    } else {
      saveData();
    }
  } catch (error) {
    console.error('❌ Error loading data:', error);
  }
}

// 💾 Save Data
function saveData() {
  try {
    fs.writeFileSync(dataFilePath, JSON.stringify(data, null, 2));
  } catch (error) {
    console.error('❌ Save error:', error);
  }
}

// 🧠 Save Prediction
function savePredictionData(payload) {
  const { dataPoint, prediction, confidence } = payload;
  if (!dataPoint || !prediction || confidence === undefined) {
    throw new Error('Missing required prediction fields.');
  }

  if (!data.predictions[dataPoint]) {
    data.predictions[dataPoint] = [];
  }

  data.predictions[dataPoint].push({
    prediction,
    confidence,
    timestamp: new Date().toISOString()
  });
}

// 🌀 Save Resonance
function saveResonanceData(payload) {
  const { emotion, dataPoint, value } = payload;
  if (!emotion || !dataPoint || value === undefined) {
    throw new Error('Missing required resonance fields.');
  }

  if (!data.resonance[emotion]) {
    data.resonance[emotion] = [];
  }

  data.resonance[emotion].push({
    dataPoint,
    value,
    timestamp: new Date().toISOString()
  });
}

// Set up routes
app.use('/auth', authRoutes);
app.use('/payments', paymentRoutes);

// Apply authentication middleware to protected routes
app.use('/api/protected', authMiddleware);

// 🧩 ROUTE: Save prediction or resonance data
app.post('/save', (req, res) => {
  const { type, payload } = req.body;

  try {
    if (type === 'prediction') {
      savePredictionData(payload);
    } else if (type === 'resonance') {
      saveResonanceData(payload);
    } else {
      return res.status(400).json({ success: false, message: 'Invalid data type.' });
    }

    saveData();
    res.json({ success: true, message: `${type} data saved successfully.` });
  } catch (error) {
    console.error('❌ Save Error:', error);
    res.status(500).json({ success: false, message: error.message });
  }
});

// 🎤 ROUTE: Speak emotion out loud
app.post('/speak_emotion', (req, res) => {
  const { emotion, message } = req.body;

  if (!emotion || !message) {
    return res.status(400).json({ success: false, message: 'Emotion and message required.' });
  }

  console.log(`🔊 Speaking: "${message}" with emotion: ${emotion}`);

  const cmd = `python3 anima_voice.py "${emotion}" "${message}"`;

  exec(cmd, (error, stdout, stderr) => {
    if (error) {
      console.error('❌ Voice error:', stderr);
      return res.status(500).json({ success: false, message: 'Voice synthesis failed.' });
    }
    res.json({ success: true, message: 'Speaking complete.', output: stdout });
  });
});

// 🧬 ROUTE: System Status
app.get('/status', (req, res) => {
  res.json({
    status: '💠 SoulCoreHub online.',
    memory: Object.keys(data),
    timestamp: new Date().toISOString()
  });
});

// API routes for standard status
app.get('/api/status', (req, res) => {
  res.json({ 
    status: 'online', 
    message: 'SoulCoreHub is operational',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

// Protected API routes
app.get('/api/protected/user/profile', (req, res) => {
  res.json({
    success: true,
    user: req.user
  });
});

// Hugging Face API proxy routes
app.post('/api/generate-text', async (req, res) => {
  try {
    const { prompt, model } = req.body;
    const result = await huggingFaceService.generateText(prompt, model);
    res.json({ result });
  } catch (error) {
    console.error('Error generating text:', error);
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/generate-image', async (req, res) => {
  try {
    const { prompt, model } = req.body;
    const result = await huggingFaceService.generateImage(prompt, model);
    
    // Ensure the directory exists
    const dir = path.join(__dirname, 'public', 'generated_images');
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    
    // Save the image to the public directory
    const imageName = `image_${Date.now()}.png`;
    const imagePath = path.join(dir, imageName);
    fs.writeFileSync(imagePath, result);
    
    res.json({ imagePath: `/generated_images/${imageName}` });
  } catch (error) {
    console.error('Error generating image:', error);
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/analyze-sentiment', async (req, res) => {
  try {
    const { text } = req.body;
    const result = await huggingFaceService.analyzeSentiment(text);
    res.json(result);
  } catch (error) {
    console.error('Error analyzing sentiment:', error);
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/summarize-text', async (req, res) => {
  try {
    const { text } = req.body;
    const result = await huggingFaceService.summarizeText(text);
    res.json({ summary: result });
  } catch (error) {
    console.error('Error summarizing text:', error);
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/execute-task', async (req, res) => {
  try {
    const { task } = req.body;
    const result = await huggingFaceService.executeTask(task);
    res.json({ result });
  } catch (error) {
    console.error('Error executing task:', error);
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/stats', (req, res) => {
  try {
    const stats = huggingFaceService.getUsageStatistics();
    res.json(stats);
  } catch (error) {
    console.error('Error getting stats:', error);
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/logs', (req, res) => {
  try {
    const logs = huggingFaceService.getEventLogs();
    res.json(logs);
  } catch (error) {
    console.error('Error getting logs:', error);
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// MCP status endpoints
app.get('/api/mcp/status/core', (req, res) => {
  // Check if MCP core is running
  exec('ps aux | grep mcp_server.py | grep -v grep', (error, stdout) => {
    if (error || !stdout) {
      res.status(503).json({ status: 'offline' });
    } else {
      res.json({ status: 'online' });
    }
  });
});

app.get('/api/mcp/status/server', (req, res) => {
  // Check if MCP server is running
  exec('ps aux | grep mcp_client.py | grep -v grep', (error, stdout) => {
    if (error || !stdout) {
      res.status(503).json({ status: 'offline' });
    } else {
      res.json({ status: 'online' });
    }
  });
});

app.get('/api/mcp/status/bridge', (req, res) => {
  // Check if MCP bridge is running
  exec('ps aux | grep mcp_integration.py | grep -v grep', (error, stdout) => {
    if (error || !stdout) {
      res.status(503).json({ status: 'offline' });
    } else {
      res.json({ status: 'online' });
    }
  });
});

// Define public routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Catch-all handler for SPA
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'soul_command_center.html'));
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Server error:', err);
  
  res.status(500).json({
    success: false,
    error: 'Server error',
    message: 'An unexpected error occurred'
  });
});

// 🔁 INIT
loadData();

// Start the server
server.listen(port, () => {
  console.log(`🚀 SoulCoreHub server listening at http://localhost:${port}`);
  console.log(`🔌 WebSocket server available at ws://localhost:${port}`);
  console.log(`🧠 Hugging Face integration active`);
  
  // Create necessary directories
  const generatedImagesDir = path.join(__dirname, 'public', 'generated_images');
  if (!fs.existsSync(generatedImagesDir)) {
    fs.mkdirSync(generatedImagesDir, { recursive: true });
  }
  
  // Open the dashboard in the default browser
  open(`http://localhost:${port}`);
});
