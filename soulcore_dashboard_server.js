const express = require('express');
const path = require('path');
const fs = require('fs');
const { handleCommand } = require('./scripts/dashboard_command_handler');

const app = express();
const port = 3000;

// Create logs directory
const logDir = path.join(__dirname, 'logs', 'dashboard');
if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
}

// Configure logging
const logFile = path.join(logDir, 'server.log');
const log = (message) => {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] ${message}\n`;
    fs.appendFileSync(logFile, logEntry);
    console.log(message);
};

// Middleware to parse JSON bodies
app.use(express.json());
app.use(express.static(path.join(__dirname, '.')));

// Log all requests
app.use((req, res, next) => {
    log(`${req.method} ${req.url}`);
    next();
});

// Endpoint to execute commands
app.post('/execute-command', async (req, res) => {
    const command = req.body.command;
    
    // Log the command
    log(`Received command: ${command}`);
    
    // Fix python command to use python3 instead of python
    let fixedCommand = command;
    if (command.startsWith('python ')) {
        fixedCommand = 'python3 ' + command.substring(7);
    }
    
    try {
        // Execute the command using the handler
        const result = await handleCommand(fixedCommand);
        log(`Command result: ${result.success ? 'SUCCESS' : 'FAILURE'}`);
        res.json({ output: result.output });
    } catch (error) {
        log(`Error executing command: ${error.message}`);
        res.status(500).json({ 
            output: `Server error: ${error.message}`,
            error: true
        });
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Serve the dashboard
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'soulcore_dashboard.html'));
});

// Start the server
app.listen(port, () => {
    log(`SoulCore Dashboard server running at http://localhost:${port}`);
    log(`Open your browser and navigate to http://localhost:${port}`);
});
