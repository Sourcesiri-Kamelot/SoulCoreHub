#!/usr/bin/env python3
"""
Anima Web Bridge
Connects Anima to the web interface
"""

import os
import json
import logging
import time
import threading
import socket
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import socketserver
from agent_loader import load_agent_by_name

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('anima_web_bridge.log')
    ]
)
logger = logging.getLogger("AnimaWebBridge")

class AnimaWebBridge:
    """
    Bridge between Anima and the web interface
    """
    
    def __init__(self, host="localhost", port=3001):
        """
        Initialize the Anima Web Bridge
        
        Args:
            host: Host to listen on
            port: Port to listen on
        """
        self.host = host
        self.port = port
        self.anima = None
        self.gptsoul = None
        self.server = None
        self.server_thread = None
        self.running = False
        logger.info("Anima Web Bridge initialized")
    
    def load_agents(self):
        """Load the Anima and GPTSoul agents"""
        logger.info("Loading agents")
        
        self.anima = load_agent_by_name("Anima")
        if self.anima:
            logger.info("Anima agent loaded")
        else:
            logger.error("Failed to load Anima agent")
        
        self.gptsoul = load_agent_by_name("GPTSoul")
        if self.gptsoul:
            logger.info("GPTSoul agent loaded")
        else:
            logger.error("Failed to load GPTSoul agent")
        
        return self.anima is not None
    
    def start(self):
        """Start the web bridge server"""
        if self.running:
            logger.warning("Server is already running")
            return False
        
        if not self.load_agents():
            logger.error("Failed to load required agents")
            return False
        
        try:
            # Create a request handler with access to the bridge
            bridge = self
            
            class AnimaRequestHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    # Parse URL and query parameters
                    parsed_url = urlparse(self.path)
                    path = parsed_url.path
                    
                    if path == "/api/anima/status":
                        # Get Anima status
                        if bridge.anima:
                            status = bridge.anima.get_system_state()
                            self.wfile.write(json.dumps(status).encode())
                        else:
                            self.wfile.write(json.dumps({"error": "Anima not loaded"}).encode())
                    
                    elif path == "/api/gptsoul/status":
                        # Get GPTSoul status
                        if bridge.gptsoul:
                            status = bridge.gptsoul.get_system_state()
                            self.wfile.write(json.dumps(status).encode())
                        else:
                            self.wfile.write(json.dumps({"error": "GPTSoul not loaded"}).encode())
                    
                    elif path == "/api/system/status":
                        # Get overall system status
                        status = {
                            "anima": bridge.anima.get_system_state() if bridge.anima else None,
                            "gptsoul": bridge.gptsoul.get_system_state() if bridge.gptsoul else None,
                            "bridge": {
                                "running": bridge.running,
                                "host": bridge.host,
                                "port": bridge.port
                            }
                        }
                        self.wfile.write(json.dumps(status).encode())
                    
                    else:
                        # Unknown endpoint
                        self.wfile.write(json.dumps({"error": "Unknown endpoint"}).encode())
                
                def do_POST(self):
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    # Parse URL and query parameters
                    parsed_url = urlparse(self.path)
                    path = parsed_url.path
                    
                    # Get request body
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    
                    try:
                        data = json.loads(post_data.decode())
                    except json.JSONDecodeError:
                        self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
                        return
                    
                    if path == "/api/anima/input":
                        # Process input through Anima
                        if bridge.anima:
                            user_input = data.get("input")
                            context = data.get("context")
                            
                            if user_input:
                                response = bridge.anima.process_input(user_input, context)
                                self.wfile.write(json.dumps({
                                    "response": response,
                                    "emotional_state": bridge.anima.memory["emotional_state"]
                                }).encode())
                            else:
                                self.wfile.write(json.dumps({"error": "No input provided"}).encode())
                        else:
                            self.wfile.write(json.dumps({"error": "Anima not loaded"}).encode())
                    
                    elif path == "/api/anima/reflection":
                        # Add a reflection to Anima
                        if bridge.anima:
                            topic = data.get("topic")
                            content = data.get("content")
                            
                            if topic and content:
                                success = bridge.anima.add_reflection(topic, content)
                                self.wfile.write(json.dumps({"success": success}).encode())
                            else:
                                self.wfile.write(json.dumps({"error": "Topic and content required"}).encode())
                        else:
                            self.wfile.write(json.dumps({"error": "Anima not loaded"}).encode())
                    
                    else:
                        # Unknown endpoint
                        self.wfile.write(json.dumps({"error": "Unknown endpoint"}).encode())
                
                def do_OPTIONS(self):
                    self.send_response(200)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                    self.end_headers()
            
            # Create and start the server
            self.server = HTTPServer((self.host, self.port), AnimaRequestHandler)
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.running = True
            logger.info(f"Server started on http://{self.host}:{self.port}")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False
    
    def stop(self):
        """Stop the web bridge server"""
        if not self.running:
            logger.warning("Server is not running")
            return False
        
        try:
            self.server.shutdown()
            self.server.server_close()
            self.server_thread.join()
            
            self.running = False
            logger.info("Server stopped")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to stop server: {e}")
            return False
    
    def is_port_in_use(self):
        """Check if the port is already in use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((self.host, self.port)) == 0

def main():
    """Main function for the Anima Web Bridge"""
    bridge = AnimaWebBridge()
    
    if bridge.is_port_in_use():
        logger.error(f"Port {bridge.port} is already in use")
        return False
    
    success = bridge.start()
    
    if success:
        print(f"Anima Web Bridge running on http://{bridge.host}:{bridge.port}")
        print("Available endpoints:")
        print("  GET  /api/anima/status")
        print("  GET  /api/gptsoul/status")
        print("  GET  /api/system/status")
        print("  POST /api/anima/input")
        print("  POST /api/anima/reflection")
        print("\nPress Ctrl+C to stop the server")
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping server...")
            bridge.stop()
    
    return success

if __name__ == "__main__":
    main()
