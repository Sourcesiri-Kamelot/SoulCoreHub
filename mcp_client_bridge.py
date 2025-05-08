#!/usr/bin/env python3
"""
MCP Client Bridge for SoulCoreHub
Handles socket communication with MCP servers and logs interactions
"""

import socket
import json
import time
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("mcp_client.log"), logging.StreamHandler()]
)
logger = logging.getLogger("mcp_client_bridge")

class MCPClientBridge:
    """Client for communicating with MCP servers and logging interactions"""
    
    def __init__(self, memory_file="mcp_memory.json"):
        """Initialize the MCP client bridge"""
        self.memory_file = memory_file
        self._ensure_memory_file_exists()
        logger.info("MCP Client Bridge initialized")
    
    def _ensure_memory_file_exists(self):
        """Create memory file if it doesn't exist"""
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, 'w') as f:
                json.dump([], f)
            logger.info(f"Created new memory file: {self.memory_file}")
    
    def _load_memory(self):
        """Load the memory from file"""
        try:
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Error decoding {self.memory_file}, creating new memory")
            return []
    
    def _save_memory(self, memory):
        """Save the memory to file"""
        with open(self.memory_file, 'w') as f:
            json.dump(memory, f, indent=2)
    
    def _log_interaction(self, query, port, result):
        """Log the interaction to memory file"""
        memory = self._load_memory()
        
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "port": port,
            "result": result
        }
        
        memory.append(interaction)
        self._save_memory(memory)
        logger.info(f"Logged interaction with MCP server on port {port}")
    
    def query_mcp_server(self, query, port):
        """
        Send a query to an MCP server and return the result
        
        Args:
            query (str): The query to send to the MCP server
            port (int): The port number of the MCP server
            
        Returns:
            dict: The JSON result from the MCP server
        """
        logger.info(f"Querying MCP server on port {port}")
        
        try:
            # Create a socket connection to the MCP server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)  # Set timeout to 10 seconds
                s.connect(('localhost', port))
                
                # Prepare the query as JSON
                query_json = json.dumps({"query": query}).encode('utf-8')
                
                # Send the query
                s.sendall(query_json)
                
                # Receive the response
                data = b''
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                
                # Parse the response
                result = json.loads(data.decode('utf-8'))
                
                # Log the interaction
                self._log_interaction(query, port, result)
                
                return result
                
        except socket.timeout:
            error_msg = f"Connection to MCP server on port {port} timed out"
            logger.error(error_msg)
            result = {"error": error_msg, "success": False}
            self._log_interaction(query, port, result)
            return result
            
        except ConnectionRefusedError:
            error_msg = f"Connection to MCP server on port {port} refused"
            logger.error(error_msg)
            result = {"error": error_msg, "success": False}
            self._log_interaction(query, port, result)
            return result
            
        except json.JSONDecodeError:
            error_msg = f"Failed to decode JSON response from MCP server on port {port}"
            logger.error(error_msg)
            result = {"error": error_msg, "success": False, "raw_response": data.decode('utf-8', errors='replace')}
            self._log_interaction(query, port, result)
            return result
            
        except Exception as e:
            error_msg = f"Error querying MCP server on port {port}: {str(e)}"
            logger.error(error_msg)
            result = {"error": error_msg, "success": False}
            self._log_interaction(query, port, result)
            return result

# Command line interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Client Bridge")
    parser.add_argument("--query", required=True, help="Query to send to the MCP server")
    parser.add_argument("--port", required=True, type=int, help="Port number of the MCP server")
    
    args = parser.parse_args()
    
    client = MCPClientBridge()
    result = client.query_mcp_server(args.query, args.port)
    
    print(json.dumps(result, indent=2))
