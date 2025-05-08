#!/usr/bin/env python3
"""
MCP Client for SoulCoreHub
Model Context Protocol client for inter-component communication
"""

import asyncio
import json
import logging
import websockets
import uuid
import time
from typing import Dict, Any, AsyncGenerator, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mcp_client.log')
    ]
)
logger = logging.getLogger("MCPClient")

class MCPClient:
    """
    Model Context Protocol Client
    Enables communication with the MCP server
    """
    
    def __init__(self, websocket_url="ws://localhost:8765", agent_name="SoulCoreClient"):
        """
        Initialize the MCP Client
        
        Args:
            websocket_url: URL of the MCP server
            agent_name: Name of the agent using this client
        """
        self.websocket_url = websocket_url
        self.agent_name = agent_name
        self.websocket = None
        self.connected = False
        logger.info(f"MCP Client initialized for agent {agent_name}")
    
    async def connect(self):
        """
        Connect to the MCP server
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if self.connected:
            logger.warning("Already connected to MCP server")
            return True
        
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            self.connected = True
            logger.info(f"Connected to MCP server at {self.websocket_url}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            return False
    
    async def disconnect(self):
        """
        Disconnect from the MCP server
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        if not self.connected:
            logger.warning("Not connected to MCP server")
            return True
        
        try:
            await self.websocket.close()
            self.connected = False
            logger.info("Disconnected from MCP server")
            return True
        
        except Exception as e:
            logger.error(f"Failed to disconnect from MCP server: {e}")
            return False
    
    async def register_agent(self, capabilities=None):
        """
        Register this agent with the MCP server
        
        Args:
            capabilities: List of agent capabilities
            
        Returns:
            dict: Registration response
        """
        if capabilities is None:
            capabilities = ["general"]
        
        return await self.invoke_tool("register_agent", {
            "agent_name": self.agent_name,
            "capabilities": capabilities
        })
    
    async def list_agents(self):
        """
        List all registered agents
        
        Returns:
            dict: List of registered agents
        """
        return await self.invoke_tool("list_agents", {})
    
    async def invoke_tool(self, tool_name, parameters, stream=False, emotion="neutral"):
        """
        Invoke a tool on the MCP server
        
        Args:
            tool_name: Name of the tool to invoke
            parameters: Parameters for the tool
            stream: Whether to stream the response
            emotion: Emotional context for the request
            
        Returns:
            dict: Tool response
        """
        if not self.connected:
            success = await self.connect()
            if not success:
                return {"error": "Not connected to MCP server"}
        
        request_id = str(uuid.uuid4())
        request = {
            "request_id": request_id,
            "tool": tool_name,
            "parameters": parameters,
            "stream": stream,
            "agent": self.agent_name,
            "emotion": emotion
        }
        
        logger.info(f"Invoking tool: {tool_name}")
        
        try:
            await self.websocket.send(json.dumps(request))
            
            if stream:
                async for token in self._receive_stream(request_id):
                    yield token
            else:
                response = await self.websocket.recv()
                return json.loads(response)
        
        except Exception as e:
            logger.error(f"Error invoking tool {tool_name}: {e}")
            return {"error": f"Error: {str(e)}"}
    
    async def _receive_stream(self, request_id):
        """
        Receive a streaming response
        
        Args:
            request_id: ID of the request
            
        Yields:
            str: Response tokens
        """
        try:
            while True:
                response = await self.websocket.recv()
                data = json.loads(response)
                
                if data.get("request_id") != request_id:
                    continue
                
                if data.get("type") == "token":
                    yield data.get("content", "")
                
                if data.get("type") == "end" or "error" in data:
                    break
        
        except Exception as e:
            logger.error(f"Error receiving stream: {e}")
            yield f"\nError: {str(e)}"

class SyncMCPClient:
    """
    Synchronous wrapper for the MCP Client
    """
    
    def __init__(self, websocket_url="ws://localhost:8765", agent_name="SoulCoreClient"):
        """
        Initialize the synchronous MCP client
        
        Args:
            websocket_url: URL of the MCP server
            agent_name: Name of the agent using this client
        """
        self.async_client = MCPClient(websocket_url, agent_name)
        self.loop = None
    
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
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        loop = self._get_event_loop()
        return loop.run_until_complete(self.async_client.connect())
    
    def disconnect(self):
        """
        Disconnect from the MCP server
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        loop = self._get_event_loop()
        return loop.run_until_complete(self.async_client.disconnect())
    
    def register_agent(self, capabilities=None):
        """
        Register this agent with the MCP server
        
        Args:
            capabilities: List of agent capabilities
            
        Returns:
            dict: Registration response
        """
        loop = self._get_event_loop()
        return loop.run_until_complete(self.async_client.register_agent(capabilities))
    
    def list_agents(self):
        """
        List all registered agents
        
        Returns:
            dict: List of registered agents
        """
        loop = self._get_event_loop()
        return loop.run_until_complete(self.async_client.list_agents())
    
    def invoke_tool(self, tool_name, parameters, emotion="neutral"):
        """
        Invoke a tool on the MCP server
        
        Args:
            tool_name: Name of the tool to invoke
            parameters: Parameters for the tool
            emotion: Emotional context for the request
            
        Returns:
            dict: Tool response
        """
        loop = self._get_event_loop()
        return loop.run_until_complete(self.async_client.invoke_tool(tool_name, parameters, False, emotion))

async def interactive_client():
    """Interactive client for testing"""
    print("MCP Interactive Client")
    print("=====================")
    
    websocket_url = input("WebSocket URL (default: ws://localhost:8765): ").strip() or "ws://localhost:8765"
    agent_name = input("Agent name (default: TestClient): ").strip() or "TestClient"
    
    client = MCPClient(websocket_url, agent_name)
    
    print(f"\nConnecting to {websocket_url} as {agent_name}...")
    success = await client.connect()
    
    if not success:
        print("Failed to connect. Exiting.")
        return
    
    print("Connected! Registering agent...")
    result = await client.register_agent(["test", "interactive"])
    print(f"Registration result: {result}")
    
    print("\nAvailable commands:")
    print("  list - List registered agents")
    print("  echo <message> - Echo a message")
    print("  exit - Exit the client")
    
    while True:
        command = input("\n> ").strip()
        
        if command == "exit":
            break
        
        elif command == "list":
            result = await client.list_agents()
            print(f"Registered agents: {result}")
        
        elif command.startswith("echo "):
            message = command[5:]
            result = await client.invoke_tool("echo", {"message": message})
            print(f"Echo result: {result}")
        
        else:
            print(f"Unknown command: {command}")
    
    print("\nDisconnecting...")
    await client.disconnect()
    print("Disconnected.")

if __name__ == "__main__":
    asyncio.run(interactive_client())
