/**
 * dashboard_command_handler.js - Command handler for SoulCore dashboard
 * 
 * This script provides a more robust command execution system for the SoulCore dashboard,
 * with proper error handling, logging, and support for asynchronous operations.
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Base directory for SoulCore
const BASE_DIR = path.resolve(__dirname, '..');

// Log directory
const LOG_DIR = path.join(BASE_DIR, 'logs', 'dashboard');
if (!fs.existsSync(LOG_DIR)) {
    fs.mkdirSync(LOG_DIR, { recursive: true });
}

// Log file for command execution
const COMMAND_LOG = path.join(LOG_DIR, 'commands.log');

/**
 * Log a message to the command log file
 * @param {string} message - Message to log
 */
function logMessage(message) {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] ${message}\n`;
    
    fs.appendFileSync(COMMAND_LOG, logEntry);
    console.log(message);
}

/**
 * Execute a command and return the result
 * @param {string} command - Command to execute
 * @param {Object} options - Command options
 * @returns {Promise<Object>} - Command result
 */
function executeCommand(command, options = {}) {
    return new Promise((resolve, reject) => {
        // Log the command
        logMessage(`Executing command: ${command}`);
        
        // Split the command into parts
        const parts = command.split(' ');
        const cmd = parts[0];
        const args = parts.slice(1);
        
        // Set default options
        const cmdOptions = {
            cwd: BASE_DIR,
            shell: true,
            ...options
        };
        
        // Spawn the command
        const process = spawn(cmd, args, cmdOptions);
        
        let stdout = '';
        let stderr = '';
        
        // Collect stdout
        process.stdout.on('data', (data) => {
            stdout += data.toString();
        });
        
        // Collect stderr
        process.stderr.on('data', (data) => {
            stderr += data.toString();
        });
        
        // Handle process completion
        process.on('close', (code) => {
            const result = {
                command,
                stdout,
                stderr,
                code
            };
            
            if (code === 0) {
                logMessage(`Command completed successfully: ${command}`);
                resolve(result);
            } else {
                logMessage(`Command failed with code ${code}: ${command}`);
                logMessage(`Error: ${stderr}`);
                resolve(result); // Still resolve, but with error info
            }
        });
        
        // Handle process errors
        process.on('error', (error) => {
            logMessage(`Command error: ${error.message}`);
            reject(error);
        });
    });
}

/**
 * Handle a command from the dashboard
 * @param {string} command - Command to execute
 * @returns {Promise<Object>} - Command result
 */
async function handleCommand(command) {
    try {
        // Execute the command
        const result = await executeCommand(command);
        
        // Return the result
        return {
            output: result.stdout || result.stderr,
            success: result.code === 0
        };
    } catch (error) {
        logMessage(`Error handling command: ${error.message}`);
        return {
            output: `Error: ${error.message}`,
            success: false
        };
    }
}

module.exports = {
    handleCommand,
    executeCommand,
    logMessage
};
