"""
Anima MCP Integration
Connects Anima to the MCP server for enhanced capabilities
"""

import logging
import threading
import time
from mcp.mcp_client_soul import SyncSoulCoreMCPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Anima MCP Integration")

class AnimaMCPIntegration:
    """
    Integrates Anima with the MCP server
    """
    
    def __init__(self, websocket_url="ws://localhost:8765"):
        """
        Initialize the Anima MCP integration
        
        Args:
            websocket_url: URL of the MCP server
        """
        self.websocket_url = websocket_url
        self.client = SyncSoulCoreMCPClient(websocket_url, "Anima")
        self.connected = False
        self.heartbeat_thread = None
        self.running = False
        logger.info("Anima MCP Integration initialized")
    
    def connect(self):
        """
        Connect to the MCP server and register Anima
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            # Register with the MCP server
            response = self.client.register_with_mcp()
            
            if "error" in response:
                logger.error(f"Failed to register with MCP server: {response['error']}")
                return False
            
            self.connected = True
            logger.info("Successfully connected to MCP server")
            
            # Start heartbeat thread
            self.running = True
            self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
            self.heartbeat_thread.start()
            
            return True
        except Exception as e:
            logger.error(f"Error connecting to MCP server: {e}")
            return False
    
    def _heartbeat_loop(self):
        """
        Send periodic heartbeats to the MCP server
        """
        while self.running:
            try:
                response = self.client.invoke("heartbeat", {
                    "status": "active",
                    "timestamp": time.time()
                }, emotion="calm")
                
                if "error" in response:
                    logger.warning(f"Heartbeat error: {response['error']}")
                    self.connected = False
                else:
                    self.connected = True
                    logger.debug("Heartbeat successful")
            except Exception as e:
                logger.warning(f"Heartbeat exception: {e}")
                self.connected = False
            
            # Sleep for 30 seconds
            time.sleep(30)
    
    def invoke_tool(self, tool_name, parameters, emotion="neutral"):
        """
        Invoke a tool on the MCP server
        
        Args:
            tool_name: Name of the tool to invoke
            parameters: Parameters for the tool
            emotion: Emotional context
            
        Returns:
            Tool response
        """
        if not self.connected:
            try:
                self.connect()
            except Exception as e:
                logger.error(f"Failed to reconnect to MCP server: {e}")
                return {"error": "Not connected to MCP server"}
        
        try:
            return self.client.invoke(tool_name, parameters, emotion)
        except Exception as e:
            logger.error(f"Error invoking tool {tool_name}: {e}")
            return {"error": str(e)}
    
    def disconnect(self):
        """
        Disconnect from the MCP server
        """
        self.running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=1)
        self.connected = False
        logger.info("Disconnected from MCP server")

# Singleton instance for easy access
anima_mcp = AnimaMCPIntegration()

def get_anima_mcp():
    """
    Get the Anima MCP integration singleton
    
    Returns:
        AnimaMCPIntegration: The singleton instance
    """
    return anima_mcp
