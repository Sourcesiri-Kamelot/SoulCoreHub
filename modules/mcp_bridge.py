#!/usr/bin/env python3
"""
MCP Bridge Module - Connects EvoVe to the Model Context Protocol
Enables EvoVe to communicate with other components through MCP
"""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent))

# Try to import MCP client
try:
    from mcp.mcp_client_soul import SoulCoreMCPClient
except ImportError:
    # Fallback to direct import
    try:
        sys.path.append(str(Path(__file__).parent.parent / "mcp"))
        from mcp_client_soul import SoulCoreMCPClient
    except ImportError:
        logging.error("Failed to import SoulCoreMCPClient")
        SoulCoreMCPClient = None

class MCPBridge:
    """Bridge between EvoVe and the Model Context Protocol"""
    
    def __init__(self, agent_name="EvoVe"):
        """
        Initialize the MCP Bridge
        
        Args:
            agent_name (str): Name of the agent using this bridge
        """
        self.agent_name = agent_name
        self.client = None
        self.connected = False
        self.initialize_client()
        
    def initialize_client(self):
        """Initialize the MCP client"""
        if SoulCoreMCPClient is None:
            logging.error("MCP client module not available")
            return False
            
        try:
            self.client = SoulCoreMCPClient(agent_name=self.agent_name)
            self.connected = True
            logging.info(f"MCP Bridge initialized for {self.agent_name}")
            return True
        except Exception as e:
            logging.error(f"Error initializing MCP client: {str(e)}")
            self.connected = False
            return False
    
    def invoke_tool(self, tool_name, params=None, emotion="determined"):
        """
        Invoke a tool through MCP
        
        Args:
            tool_name (str): Name of the tool to invoke
            params (dict): Parameters for the tool
            emotion (str): Emotional state for the invocation
            
        Returns:
            dict: Response from the tool or error
        """
        if not self.connected or self.client is None:
            if not self.initialize_client():
                return {"error": "MCP client not available"}
        
        try:
            response = self.client.sync_invoke(tool_name, params, emotion)
            return response
        except Exception as e:
            logging.error(f"Error invoking tool {tool_name}: {str(e)}")
            return {"error": f"Tool invocation failed: {str(e)}"}
    
    def read_file(self, path, start_line=None, end_line=None):
        """
        Read a file through MCP
        
        Args:
            path (str): Path to the file
            start_line (int): Starting line number (optional)
            end_line (int): Ending line number (optional)
            
        Returns:
            dict: Result with content or error
        """
        params = {"path": path}
        if start_line is not None:
            params["start_line"] = start_line
        if end_line is not None:
            params["end_line"] = end_line
            
        return self.invoke_tool("read_file", params, "curious")
    
    def write_file(self, path, content, mode="create"):
        """
        Write to a file through MCP
        
        Args:
            path (str): Path to the file
            content (str): Content to write
            mode (str): 'create' to create/overwrite, 'append' to append
            
        Returns:
            dict: Result with status or error
        """
        params = {
            "path": path,
            "content": content,
            "mode": mode
        }
        
        return self.invoke_tool("write_file", params, "careful")
    
    def execute_command(self, command, cwd=None):
        """
        Execute a shell command through MCP
        
        Args:
            command (str): Command to execute
            cwd (str): Working directory
            
        Returns:
            dict: Result with output or error
        """
        params = {"command": command}
        if cwd:
            params["cwd"] = cwd
            
        return self.invoke_tool("execute_command", params, "cautious")
    
    def list_directory(self, path, pattern="*", recursive=False, depth=1):
        """
        List directory contents through MCP
        
        Args:
            path (str): Path to the directory
            pattern (str): File pattern to match
            recursive (bool): Whether to list recursively
            depth (int): Maximum depth for recursive listing
            
        Returns:
            dict: Result with directory contents or error
        """
        params = {
            "path": path,
            "pattern": pattern,
            "recursive": recursive,
            "depth": depth
        }
        
        return self.invoke_tool("list_directory", params, "curious")

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    bridge = MCPBridge()
    result = bridge.read_file(__file__)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Successfully read {result.get('lines', 0)} lines")
