#!/usr/bin/env python3
"""
MCP Server for SoulCoreHub
Model Context Protocol server for inter-component communication
"""

import asyncio
import json
import logging
import websockets
import uuid
import time
from pathlib import Path
from typing import Dict, Any, Set, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('soulcore_mcp_server.log')
    ]
)
logger = logging.getLogger("MCPServer")

class MCPServer:
    """
    Model Context Protocol Server
    Enables communication between SoulCoreHub components
    """
    
    def __init__(self, host="localhost", port=8765):
        """
        Initialize the MCP Server
        
        Args:
            host: Host to listen on
            port: Port to listen on
        """
        self.host = host
        self.port = port
        self.clients = set()
        self.registered_agents = {}
        self.tools = {}
        self.server = None
        self.running = False
        logger.info("MCP Server initialized")
    
    async def register_client(self, websocket):
        """
        Register a new client connection
        
        Args:
            websocket: The WebSocket connection
        """
        self.clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")
    
    async def unregister_client(self, websocket):
        """
        Unregister a client connection
        
        Args:
            websocket: The WebSocket connection
        """
        self.clients.remove(websocket)
        
        # Remove any agents registered by this client
        agents_to_remove = []
        for agent_name, agent_info in self.registered_agents.items():
            if agent_info.get("websocket") == websocket:
                agents_to_remove.append(agent_name)
        
        for agent_name in agents_to_remove:
            del self.registered_agents[agent_name]
            logger.info(f"Agent unregistered due to client disconnect: {agent_name}")
        
        logger.info(f"Client disconnected. Total clients: {len(self.clients)}")
    
    def register_tool(self, name: str, handler: Callable):
        """
        Register a tool that can be invoked by clients
        
        Args:
            name: Name of the tool
            handler: Function to handle tool invocation
        """
        self.tools[name] = handler
        logger.info(f"Tool registered: {name}")
    
    async def handle_message(self, websocket, message):
        """
        Handle a message from a client
        
        Args:
            websocket: The WebSocket connection
            message: The message received
        """
        try:
            data = json.loads(message)
            
            # Check if this is a tool invocation
            if "tool" in data:
                await self.handle_tool_invocation(websocket, data)
            
            # Check if this is a registration request
            elif "register_agent" in data:
                await self.handle_agent_registration(websocket, data)
            
            # Unknown message type
            else:
                await websocket.send(json.dumps({
                    "error": "Unknown message type"
                }))
        
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
            await websocket.send(json.dumps({
                "error": "Invalid JSON"
            }))
        
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await websocket.send(json.dumps({
                "error": f"Error: {str(e)}"
            }))
    
    async def handle_tool_invocation(self, websocket, data):
        """
        Handle a tool invocation request
        
        Args:
            websocket: The WebSocket connection
            data: The request data
        """
        tool_name = data.get("tool")
        request_id = data.get("request_id", str(uuid.uuid4()))
        parameters = data.get("parameters", {})
        stream = data.get("stream", False)
        agent = data.get("agent", "unknown")
        emotion = data.get("emotion", "neutral")
        
        logger.info(f"Tool invocation: {tool_name} by {agent} with emotion {emotion}")
        
        # Check if the tool exists
        if tool_name not in self.tools:
            await websocket.send(json.dumps({
                "request_id": request_id,
                "error": f"Tool not found: {tool_name}"
            }))
            return
        
        try:
            # Get the tool handler
            handler = self.tools[tool_name]
            
            # Invoke the tool
            if stream:
                # Streaming response
                async for token in handler(parameters, agent=agent, emotion=emotion):
                    await websocket.send(json.dumps({
                        "request_id": request_id,
                        "type": "token",
                        "content": token
                    }))
                
                # End of stream
                await websocket.send(json.dumps({
                    "request_id": request_id,
                    "type": "end"
                }))
            
            else:
                # Non-streaming response
                result = await handler(parameters, agent=agent, emotion=emotion)
                await websocket.send(json.dumps({
                    "request_id": request_id,
                    "result": result
                }))
        
        except Exception as e:
            logger.error(f"Error invoking tool {tool_name}: {e}")
            await websocket.send(json.dumps({
                "request_id": request_id,
                "error": f"Error invoking tool: {str(e)}"
            }))
    
    async def handle_agent_registration(self, websocket, data):
        """
        Handle an agent registration request
        
        Args:
            websocket: The WebSocket connection
            data: The request data
        """
        agent_data = data.get("register_agent", {})
        agent_name = agent_data.get("agent_name")
        
        if not agent_name:
            await websocket.send(json.dumps({
                "error": "Agent name is required"
            }))
            return
        
        # Register the agent
        self.registered_agents[agent_name] = {
            "websocket": websocket,
            "registration_time": time.time(),
            "data": agent_data
        }
        
        logger.info(f"Agent registered: {agent_name}")
        
        await websocket.send(json.dumps({
            "status": "ok",
            "message": f"Agent {agent_name} registered successfully"
        }))
    
    async def handler(self, websocket, path):
        """
        WebSocket connection handler
        
        Args:
            websocket: The WebSocket connection
            path: The connection path
        """
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        
        except websockets.exceptions.ConnectionClosed:
            logger.info("Connection closed")
        
        finally:
            await self.unregister_client(websocket)
    
    async def start(self):
        """Start the MCP server"""
        if self.running:
            logger.warning("Server is already running")
            return False
        
        # Register default tools
        self.register_tool("register_agent", self.tool_register_agent)
        self.register_tool("list_agents", self.tool_list_agents)
        self.register_tool("echo", self.tool_echo)
        
        try:
            self.server = await websockets.serve(self.handler, self.host, self.port)
            self.running = True
            logger.info(f"MCP Server started on ws://{self.host}:{self.port}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False
    
    async def stop(self):
        """Stop the MCP server"""
        if not self.running:
            logger.warning("Server is not running")
            return False
        
        try:
            self.server.close()
            await self.server.wait_closed()
            self.running = False
            logger.info("MCP Server stopped")
            return True
        
        except Exception as e:
            logger.error(f"Failed to stop server: {e}")
            return False
    
    # Tool implementations
    
    async def tool_register_agent(self, parameters, agent="system", emotion="neutral"):
        """
        Tool to register an agent
        
        Args:
            parameters: Tool parameters
            agent: The agent making the request
            emotion: The emotional context
            
        Returns:
            Registration result
        """
        agent_name = parameters.get("agent_name")
        capabilities = parameters.get("capabilities", [])
        
        if not agent_name:
            return {"error": "Agent name is required"}
        
        logger.info(f"Agent {agent_name} registered with capabilities: {capabilities}")
        
        return {
            "status": "registered",
            "agent_name": agent_name,
            "capabilities": capabilities
        }
    
    async def tool_list_agents(self, parameters, agent="system", emotion="neutral"):
        """
        Tool to list registered agents
        
        Args:
            parameters: Tool parameters
            agent: The agent making the request
            emotion: The emotional context
            
        Returns:
            List of registered agents
        """
        agents = []
        
        for agent_name, agent_info in self.registered_agents.items():
            agents.append({
                "name": agent_name,
                "registration_time": agent_info.get("registration_time"),
                "data": agent_info.get("data")
            })
        
        return {
            "agents": agents,
            "count": len(agents)
        }
    
    async def tool_echo(self, parameters, agent="system", emotion="neutral"):
        """
        Simple echo tool for testing
        
        Args:
            parameters: Tool parameters
            agent: The agent making the request
            emotion: The emotional context
            
        Returns:
            Echo of the input
        """
        message = parameters.get("message", "")
        
        return {
            "echo": message,
            "agent": agent,
            "emotion": emotion,
            "timestamp": time.time()
        }

async def main():
    """Main function for the MCP Server"""
    server = MCPServer()
    await server.start()
    
    print(f"MCP Server running on ws://{server.host}:{server.port}")
    print("Available tools:")
    for tool_name in server.tools:
        print(f"  - {tool_name}")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        # Keep the server running
        while True:
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        print("\nStopping server...")
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
