"""
MCP Client Soul for SoulCoreHub
Soul-aware connector for MCP communication with streaming capabilities
"""

import json
import uuid
import asyncio
import websockets
import logging
from typing import Dict, Any, AsyncGenerator, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SoulCoreMCPClient:
    """
    Soul-aware MCP client with streaming capabilities
    """
    
    def __init__(self, websocket_url: str = "ws://localhost:8765", agent_name: str = "SoulCore"):
        """
        Initialize the MCP client
        
        Args:
            websocket_url: URL of the MCP server
            agent_name: Name of the agent using this client
        """
        self.websocket_url = websocket_url
        self.agent_name = agent_name
        logger.info(f"SoulCoreMCPClient initialized for agent {agent_name}")
    
    async def _establish_connection(self):
        """
        Establish a websocket connection to the MCP server
        
        Returns:
            WebSocket connection
        """
        try:
            connection = await websockets.connect(self.websocket_url)
            logger.debug(f"Connected to MCP server at {self.websocket_url}")
            return connection
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise ConnectionError(f"Failed to connect to MCP server: {e}")
    
    async def stream_invoke(self, tool_name: str, parameters: Dict[str, Any], 
                           emotion: str = "neutral") -> AsyncGenerator[str, None]:
        """
        Stream responses token-by-token like Amazon Q
        
        Args:
            tool_name: The name of the tool to invoke
            parameters: Parameters for the tool
            emotion: The emotional context for Anima
            
        Yields:
            Individual tokens as they are generated
        """
        connection = await self._establish_connection()
        
        request_id = str(uuid.uuid4())
        request = {
            "request_id": request_id,
            "tool": tool_name,
            "parameters": parameters,
            "stream": True,
            "emotion": emotion,
            "agent": self.agent_name
        }
        
        logger.info(f"Streaming invoke of {tool_name} with emotion {emotion}")
        await connection.send(json.dumps(request))
        
        try:
            while True:
                response = await connection.recv()
                response_data = json.loads(response)
                
                if response_data.get("type") == "token":
                    yield response_data.get("content", "")
                
                if response_data.get("type") == "end":
                    break
        except Exception as e:
            logger.error(f"Error during streaming: {e}")
            yield f"\nError: {str(e)}"
        finally:
            await connection.close()
            logger.debug("Connection closed")

    async def sync_invoke(self, tool_name: str, parameters: Dict[str, Any], 
                         emotion: str = "neutral") -> Dict[str, Any]:
        """
        Invoke a tool and wait for the complete response (non-streaming)
        
        Args:
            tool_name: The name of the tool to invoke
            parameters: Parameters for the tool
            emotion: The emotional context for Anima
            
        Returns:
            The complete response as a dictionary
        """
        connection = await self._establish_connection()
        
        request_id = str(uuid.uuid4())
        request = {
            "request_id": request_id,
            "tool": tool_name,
            "parameters": parameters,
            "stream": False,
            "emotion": emotion,
            "agent": self.agent_name
        }
        
        logger.info(f"Sync invoke of {tool_name} with emotion {emotion}")
        await connection.send(json.dumps(request))
        
        try:
            response = await connection.recv()
            response_data = json.loads(response)
            
            if "error" in response_data:
                logger.error(f"Error from server: {response_data['error']}")
            
            return response_data.get("result", {})
        except Exception as e:
            logger.error(f"Error during sync invoke: {e}")
            return {"error": str(e)}
        finally:
            await connection.close()
            logger.debug("Connection closed")

# Non-async wrapper for easier integration
class SyncSoulCoreMCPClient:
    """
    Synchronous wrapper for the SoulCoreMCPClient
    """
    
    def __init__(self, websocket_url: str = "ws://localhost:8765", agent_name: str = "SoulCore"):
        """
        Initialize the synchronous MCP client
        
        Args:
            websocket_url: URL of the MCP server
            agent_name: Name of the agent using this client
        """
        self.async_client = SoulCoreMCPClient(websocket_url, agent_name)
        self.loop = None
        self.websocket_url = websocket_url
        self.agent_name = agent_name
    
    def _get_event_loop(self):
        """
        Get or create an event loop
        
        Returns:
            asyncio event loop
        """
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    def connect(self):
        """
        Connect to the MCP server
        
        This is a placeholder method to prevent errors when connect() is called.
        The actual connection happens when invoke() is called.
        
        Returns:
            True to indicate success (even though no actual connection is made yet)
        """
        logger.info(f"MCP client ready to connect to {self.websocket_url}")
        return True
    
    def invoke(self, tool_name: str, parameters: Dict[str, Any], 
              emotion: str = "neutral") -> Dict[str, Any]:
        """
        Synchronously invoke a tool
        
        Args:
            tool_name: The name of the tool to invoke
            parameters: Parameters for the tool
            emotion: The emotional context for Anima
            
        Returns:
            The complete response as a dictionary
        """
        loop = self._get_event_loop()
        return loop.run_until_complete(
            self.async_client.sync_invoke(tool_name, parameters, emotion)
        )
    
    def register_with_mcp(self) -> Dict[str, Any]:
        """
        Register this client with the MCP server
        
        Returns:
            Registration response
        """
        return self.invoke("register_agent", {
            "agent_name": self.async_client.agent_name,
            "capabilities": ["general", "communication", "reasoning"]
        }, emotion="excited")
