#!/usr/bin/env python3
"""
Anima VS Code Bridge - Connects Anima to VS Code for natural language development
"""

import json
import logging
import os
import subprocess
import threading
import time
import websocket
from typing import Dict, Any, Callable, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/anima_vscode.log'
)
logger = logging.getLogger("AnimaVSCodeBridge")

class AnimaVSCodeBridge:
    """Bridge between Anima and VS Code for natural language development"""
    
    def __init__(self, mcp_url: str = "ws://localhost:8765"):
        """
        Initialize the VS Code bridge
        
        Args:
            mcp_url: URL of the MCP server
        """
        self.mcp_url = mcp_url
        self.ws = None
        self.connected = False
        self.command_handlers = {}
        self.running = False
        self.vscode_extension_installed = self._check_vscode_extension()
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        logger.info("AnimaVSCodeBridge initialized")
    
    def _check_vscode_extension(self) -> bool:
        """Check if the VS Code extension is installed"""
        try:
            result = subprocess.run(
                ["code", "--list-extensions"], 
                capture_output=True, 
                text=True
            )
            return "anima-vscode" in result.stdout.lower()
        except Exception as e:
            logger.error(f"Error checking VS Code extension: {e}")
            return False
    
    def connect(self) -> bool:
        """Connect to the MCP server"""
        try:
            self.ws = websocket.WebSocketApp(
                self.mcp_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # Start the WebSocket connection in a separate thread
            self.ws_thread = threading.Thread(target=self.ws.run_forever)
            self.ws_thread.daemon = True
            self.ws_thread.start()
            
            # Wait for connection to establish
            timeout = 10
            start_time = time.time()
            while not self.connected and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            return self.connected
        except Exception as e:
            logger.error(f"Error connecting to MCP server: {e}")
            return False
    
    def _on_open(self, ws):
        """Handle WebSocket open event"""
        self.connected = True
        logger.info("Connected to MCP server")
        
        # Register with the MCP server
        self._send_message({
            "type": "register",
            "name": "AnimaVSCodeBridge",
            "capabilities": ["vscode", "terminal", "builder"]
        })
    
    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            
            if data.get("type") == "command":
                command = data.get("command", "")
                parameters = data.get("parameters", {})
                
                if command in self.command_handlers:
                    # Execute the command handler
                    result = self.command_handlers[command](parameters)
                    
                    # Send the result back
                    self._send_message({
                        "type": "command_result",
                        "command": command,
                        "result": result,
                        "request_id": data.get("request_id")
                    })
                else:
                    logger.warning(f"Unknown command: {command}")
                    self._send_message({
                        "type": "error",
                        "message": f"Unknown command: {command}",
                        "request_id": data.get("request_id")
                    })
        except json.JSONDecodeError:
            logger.error("Invalid JSON message received")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    def _on_error(self, ws, error):
        """Handle WebSocket error"""
        logger.error(f"WebSocket error: {error}")
        self.connected = False
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close event"""
        logger.info(f"WebSocket closed: {close_status_code} - {close_msg}")
        self.connected = False
    
    def _send_message(self, message: Dict[str, Any]):
        """Send a message to the MCP server"""
        if self.connected and self.ws:
            try:
                self.ws.send(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message: {e}")
    
    def register_command(self, command: str, handler: Callable):
        """
        Register a command handler
        
        Args:
            command: Command name
            handler: Function to handle the command
        """
        self.command_handlers[command] = handler
        logger.info(f"Registered command handler for: {command}")
    
    def execute_vscode_command(self, command: str, args: list = None) -> Dict[str, Any]:
        """
        Execute a VS Code command
        
        Args:
            command: VS Code command ID
            args: Command arguments
            
        Returns:
            Command execution result
        """
        if not self.vscode_extension_installed:
            return {"error": "VS Code extension not installed"}
        
        try:
            # Use the VS Code CLI to execute the command
            cmd = ["code", "--remote", "anima", "--execute-command", command]
            
            if args:
                cmd.extend(["--args", json.dumps(args)])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {"success": True, "output": result.stdout}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            logger.error(f"Error executing VS Code command: {e}")
            return {"success": False, "error": str(e)}
    
    def create_file(self, path: str, content: str) -> Dict[str, Any]:
        """
        Create a file in VS Code
        
        Args:
            path: File path
            content: File content
            
        Returns:
            File creation result
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            
            # Write the file
            with open(path, 'w') as f:
                f.write(content)
            
            # Open the file in VS Code
            self.execute_vscode_command("vscode.open", [path])
            
            return {"success": True, "path": path}
        except Exception as e:
            logger.error(f"Error creating file: {e}")
            return {"success": False, "error": str(e)}
    
    def execute_terminal_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a command in the terminal
        
        Args:
            command: Terminal command
            
        Returns:
            Command execution result
        """
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except Exception as e:
            logger.error(f"Error executing terminal command: {e}")
            return {"success": False, "error": str(e)}
    
    def start(self):
        """Start the VS Code bridge"""
        if self.running:
            return
        
        self.running = True
        
        # Connect to the MCP server
        if not self.connect():
            logger.error("Failed to connect to MCP server")
            self.running = False
            return
        
        # Register command handlers
        self.register_command("create_file", lambda params: self.create_file(
            params.get("path", ""), 
            params.get("content", "")
        ))
        
        self.register_command("execute_terminal", lambda params: self.execute_terminal_command(
            params.get("command", "")
        ))
        
        self.register_command("execute_vscode", lambda params: self.execute_vscode_command(
            params.get("command", ""),
            params.get("args", [])
        ))
        
        logger.info("AnimaVSCodeBridge started")
    
    def stop(self):
        """Stop the VS Code bridge"""
        if not self.running:
            return
        
        self.running = False
        
        if self.ws:
            self.ws.close()
        
        if self.ws_thread and self.ws_thread.is_alive():
            self.ws_thread.join(timeout=1)
        
        logger.info("AnimaVSCodeBridge stopped")

# Example usage
if __name__ == "__main__":
    bridge = AnimaVSCodeBridge()
    bridge.start()
    
    try:
        # Keep the main thread running
        while bridge.running:
            time.sleep(1)
    except KeyboardInterrupt:
        bridge.stop()
