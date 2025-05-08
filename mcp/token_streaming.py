"""
Token Streaming Module for SoulCoreHub
Implements word-by-word response streaming similar to Amazon Q
"""

import json
import uuid
import asyncio
import websockets
from typing import AsyncGenerator, Dict, Any, Optional

class TokenStreamingClient:
    def __init__(self, websocket_url: str = "ws://localhost:8765", agent_name: str = "SoulCore"):
        self.websocket_url = websocket_url
        self.agent_name = agent_name
    
    async def _establish_connection(self):
        """Establish a websocket connection to the MCP server"""
        try:
            return await websockets.connect(self.websocket_url)
        except Exception as e:
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
        
        await connection.send(json.dumps(request))
        
        try:
            while True:
                response = await connection.recv()
                response_data = json.loads(response)
                
                if response_data.get("type") == "token":
                    yield response_data.get("content", "")
                
                if response_data.get("type") == "end":
                    break
        finally:
            await connection.close()

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
        
        await connection.send(json.dumps(request))
        response = await connection.recv()
        await connection.close()
        
        return json.loads(response)
