#!/usr/bin/env python3
"""
MCP Integration for SoulCoreHub
Integrates the MCP server with the rest of the system
"""

import os
import json
import logging
import asyncio
import threading
import time
from pathlib import Path
from mcp_server import MCPServer
from mcp_tools import mcp_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mcp_integration.log')
    ]
)
logger = logging.getLogger("MCPIntegration")

class MCPIntegration:
    """
    Integrates the MCP server with the rest of the system
    """
    
    def __init__(self, host="localhost", port=8765):
        """
        Initialize the MCP Integration
        
        Args:
            host: Host for the MCP server
            port: Port for the MCP server
        """
        self.host = host
        self.port = port
        self.server = MCPServer(host, port)
        self.server_thread = None
        self.running = False
        logger.info("MCP Integration initialized")
    
    def start(self):
        """
        Start the MCP server in a separate thread
        
        Returns:
            bool: True if server started successfully, False otherwise
        """
        if self.running:
            logger.warning("MCP server is already running")
            return True
        
        try:
            # Register tools from mcp_tools
            for tool_name, tool_handler in mcp_tools.get_all_tools().items():
                self.server.register_tool(tool_name, tool_handler)
            
            # Start the server in a separate thread
            self.server_thread = threading.Thread(target=self._run_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            # Wait for server to start
            time.sleep(1)
            
            self.running = True
            logger.info(f"MCP server started on ws://{self.host}:{self.port}")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            return False
    
    def _run_server(self):
        """Run the MCP server in the current thread"""
        asyncio.run(self._async_run_server())
    
    async def _async_run_server(self):
        """Run the MCP server asynchronously"""
        await self.server.start()
        
        try:
            # Keep the server running
            while True:
                await asyncio.sleep(1)
        
        except asyncio.CancelledError:
            logger.info("MCP server task cancelled")
        
        finally:
            await self.server.stop()
    
    def stop(self):
        """
        Stop the MCP server
        
        Returns:
            bool: True if server stopped successfully, False otherwise
        """
        if not self.running:
            logger.warning("MCP server is not running")
            return True
        
        try:
            # Create a new event loop to stop the server
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Stop the server
            loop.run_until_complete(self.server.stop())
            loop.close()
            
            # Wait for thread to finish
            self.server_thread.join(timeout=5)
            
            self.running = False
            logger.info("MCP server stopped")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to stop MCP server: {e}")
            return False
    
    def is_running(self):
        """
        Check if the MCP server is running
        
        Returns:
            bool: True if server is running, False otherwise
        """
        return self.running

def main():
    """Main function for the MCP Integration"""
    integration = MCPIntegration()
    
    success = integration.start()
    
    if success:
        print(f"MCP server running on ws://{integration.host}:{integration.port}")
        print("Available tools:")
        for tool_name in mcp_tools.get_all_tools():
            print(f"  - {tool_name}")
        print("\nPress Ctrl+C to stop the server")
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\nStopping MCP server...")
            integration.stop()
    
    return success

if __name__ == "__main__":
    main()
