# anima_mcp_integration.py
"""
Anima MCP Integration
Connects Anima to the MCP server for enhanced capabilities
"""

import logging
from mcp.mcp_client_soul import SyncSoulCoreMCPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AnimaMCPIntegration")

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
        self.client = None

    def connect(self):
        try:
            self.client = SyncSoulCoreMCPClient(self.websocket_url)
            self.client.connect()
            logger.info("✅ Connected to MCP server at %s", self.websocket_url)
            self._register_anima()
        except Exception as e:
            logger.error("❌ Failed to connect to MCP server: %s", str(e))

    def _register_anima(self):
        try:
            if not self.client:
                logger.error("❌ Client is not connected. Cannot register.")
                return
            response = self.client.sync_invoke("register_agent", data={
                "agent_name": "Anima",
                "emotion": "excited"
            })
            if response.get("status") == "ok":
                logger.info("✅ Anima registered with MCP.")
            else:
                logger.warning("⚠️ Registration returned unexpected response: %s", response)
        except Exception as e:
            logger.error("❌ Registration with MCP failed: %s", str(e))

# Create a global instance
anima_mcp = AnimaMCPIntegration()
