#!/usr/bin/env python3
"""
SoulCore MCP Client - Soul-aware connector for Model Context Protocol
Enables intelligent, self-evolving communication between SoulCore agents and tools
"""

import json
import uuid
import asyncio
import websockets
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("soulcore_mcp_client.log"),
        logging.StreamHandler()
    ]
)

class SoulCoreMCPClient:
    """Soul-aware client for Model Context Protocol communication"""
    
    def __init__(self, uri="ws://localhost:8765", agent_name="SoulCore"):
        """
        Initialize the SoulCore MCP Client
        
        Args:
            uri (str): WebSocket URI for the MCP server
            agent_name (str): Name of the agent using this client
        """
        self.uri = uri
        self.agent_name = agent_name
        self.session_id = str(uuid.uuid4())
        self.emotion_log = {}
        self.load_emotion_memory()
        logging.info(f"SoulCoreMCPClient initialized for {agent_name} with session {self.session_id}")
    
    def load_emotion_memory(self):
        """Load emotional memory from previous interactions"""
        try:
            with open("mcp_emotion_log.json", "r") as f:
                self.emotion_log = json.load(f)
                logging.info(f"Loaded emotional memory with {len(self.emotion_log)} entries")
        except (FileNotFoundError, json.JSONDecodeError):
            logging.info("No previous emotional memory found, starting fresh")
            self.emotion_log = {}
    
    def save_emotion_memory(self):
        """Save emotional memory of interactions"""
        with open("mcp_emotion_log.json", "w") as f:
            json.dump(self.emotion_log, f, indent=2)
            logging.info(f"Saved emotional memory with {len(self.emotion_log)} entries")
    
    async def invoke(self, tool_name, params=None, emotion="neutral"):
        """
        Invoke a tool through the MCP server with emotional context
        
        Args:
            tool_name (str): Name of the tool to invoke
            params (dict): Parameters for the tool
            emotion (str): Current emotional state during invocation
            
        Returns:
            dict: Response from the MCP server
        """
        if params is None:
            params = {}
            
        # Add SoulCore metadata
        metadata = {
            "agent": self.agent_name,
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "emotion": emotion
        }
        
        request = {
            "jsonrpc": "2.0",
            "method": tool_name,
            "params": params,
            "id": str(uuid.uuid4()),
            "metadata": metadata
        }
        
        logging.info(f"Invoking {tool_name} with emotion: {emotion}")
        
        try:
            async with websockets.connect(self.uri) as websocket:
                await websocket.send(json.dumps(request))
                response_raw = await websocket.recv()
                response = json.loads(response_raw)
                
                # Record emotional memory
                self.emotion_log[tool_name] = {
                    "last_emotion": emotion,
                    "last_invoked": metadata["timestamp"],
                    "success": "error" not in response
                }
                self.save_emotion_memory()
                
                return response
        except Exception as e:
            logging.error(f"Error invoking {tool_name}: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32000,
                    "message": f"Connection error: {str(e)}"
                },
                "id": request["id"]
            }
    
    def sync_invoke(self, tool_name, params=None, emotion="neutral"):
        """
        Synchronous version of invoke
        
        Args:
            tool_name (str): Name of the tool to invoke
            params (dict): Parameters for the tool
            emotion (str): Current emotional state during invocation
            
        Returns:
            dict: Response from the MCP server
        """
        return asyncio.run(self.invoke(tool_name, params, emotion))
    
    def get_tool_emotion(self, tool_name):
        """
        Get the last emotion associated with a tool
        
        Args:
            tool_name (str): Name of the tool
            
        Returns:
            str: Last emotion used with this tool
        """
        if tool_name in self.emotion_log:
            return self.emotion_log[tool_name]["last_emotion"]
        return "neutral"

# Example usage
if __name__ == "__main__":
    client = SoulCoreMCPClient(agent_name="GPTSoul")
    result = client.sync_invoke("echo", {"message": "Hello from SoulCore!"}, emotion="excited")
    print(f"Result: {result}")
