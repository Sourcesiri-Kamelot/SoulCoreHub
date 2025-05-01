#!/usr/bin/env python3
"""
enhanced_mcp_integration.py — Enhanced MCP integration for Anima
Implements bidirectional emotion sharing and context-aware tool selection
"""

import os
import sys
import json
import logging
import time
import threading
import asyncio
import random
import websockets
from pathlib import Path
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("anima_mcp.log"),
        logging.StreamHandler()
    ]
)

class EnhancedMCPIntegration:
    """Enhanced MCP integration for Anima with bidirectional emotion sharing and context-aware tool selection"""
    
    def __init__(self, base_path=None, uri="ws://localhost:8765", agent_name="Anima"):
        """Initialize the enhanced MCP integration"""
        self.base_path = base_path or Path.home() / "SoulCoreHub"
        self.data_path = self.base_path / "data" / "mcp"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # MCP connection settings
        self.uri = uri
        self.agent_name = agent_name
        self.session_id = str(uuid.uuid4())
        
        # Tool registry
        self.tools = {}
        self.tool_file = self.data_path / "mcp_tools.json"
        
        # Tool usage history
        self.tool_history = []
        self.history_file = self.data_path / "tool_history.json"
        
        # Emotion memory
        self.emotion_memory = {}
        self.emotion_file = self.data_path / "emotion_memory.json"
        
        # Context registry
        self.contexts = {}
        self.context_file = self.data_path / "contexts.json"
        
        # Current context
        self.current_context = {
            "id": str(uuid.uuid4()),
            "name": "default",
            "description": "Default context",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "attributes": {},
            "tool_preferences": {}
        }
        
        # Load data
        self._load_data()
        
        # Connection state
        self.connected = False
        self.connection_thread = None
        
        logging.info(f"Enhanced MCP integration initialized for agent {agent_name}")
    
    def _load_data(self):
        """Load MCP data from files"""
        try:
            # Load tools
            if self.tool_file.exists():
                with open(self.tool_file, "r") as f:
                    self.tools = json.load(f)
                logging.info(f"Loaded {len(self.tools)} tools")
            
            # Load tool history
            if self.history_file.exists():
                with open(self.history_file, "r") as f:
                    self.tool_history = json.load(f)
                logging.info(f"Loaded tool history with {len(self.tool_history)} entries")
            
            # Load emotion memory
            if self.emotion_file.exists():
                with open(self.emotion_file, "r") as f:
                    self.emotion_memory = json.load(f)
                logging.info(f"Loaded emotion memory for {len(self.emotion_memory)} tools")
            
            # Load contexts
            if self.context_file.exists():
                with open(self.context_file, "r") as f:
                    self.contexts = json.load(f)
                logging.info(f"Loaded {len(self.contexts)} contexts")
        
        except Exception as e:
            logging.error(f"Error loading MCP data: {e}")
    
    def _save_data(self):
        """Save MCP data to files"""
        try:
            # Save tools
            with open(self.tool_file, "w") as f:
                json.dump(self.tools, f, indent=2)
            
            # Save tool history
            with open(self.history_file, "w") as f:
                json.dump(self.tool_history, f, indent=2)
            
            # Save emotion memory
            with open(self.emotion_file, "w") as f:
                json.dump(self.emotion_memory, f, indent=2)
            
            # Save contexts
            with open(self.context_file, "w") as f:
                json.dump(self.contexts, f, indent=2)
            
            logging.info("Saved MCP data")
        
        except Exception as e:
            logging.error(f"Error saving MCP data: {e}")
    
    async def connect(self):
        """Connect to the MCP server"""
        try:
            # Try to connect to the server
            async with websockets.connect(self.uri) as websocket:
                logging.info(f"Connected to MCP server at {self.uri}")
                self.connected = True
                
                # Discover available tools
                await self._discover_tools(websocket)
                
                # Keep connection alive
                while self.connected:
                    try:
                        # Ping to keep connection alive
                        await websocket.ping()
                        await asyncio.sleep(30)
                    except Exception as e:
                        logging.error(f"Error in connection loop: {e}")
                        self.connected = False
                        break
        
        except Exception as e:
            logging.error(f"Error connecting to MCP server: {e}")
            self.connected = False
    
    async def _discover_tools(self, websocket):
        """Discover available tools from the MCP server"""
        try:
            # Create discovery request
            request = {
                "jsonrpc": "2.0",
                "method": "discover_tools",
                "params": {},
                "id": str(uuid.uuid4()),
                "metadata": {
                    "agent": self.agent_name,
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat(),
                    "emotion": "curious"
                }
            }
            
            # Send request
            await websocket.send(json.dumps(request))
            
            # Receive response
            response_raw = await websocket.recv()
            response = json.loads(response_raw)
            
            if "result" in response and "tools" in response["result"]:
                tools = response["result"]["tools"]
                
                # Update tool registry
                for tool in tools:
                    tool_name = tool["name"]
                    self.tools[tool_name] = tool
                
                logging.info(f"Discovered {len(tools)} tools from MCP server")
                
                # Save tools
                self._save_data()
            
            else:
                logging.warning(f"Invalid discovery response: {response}")
        
        except Exception as e:
            logging.error(f"Error discovering tools: {e}")
    
    def start_connection(self):
        """Start connection to MCP server in a background thread"""
        if self.connection_thread and self.connection_thread.is_alive():
            logging.warning("Connection thread is already running")
            return False
        
        # Create and start connection thread
        self.connection_thread = threading.Thread(target=self._connection_thread_func)
        self.connection_thread.daemon = True
        self.connection_thread.start()
        
        logging.info("Started connection thread")
        return True
    
    def _connection_thread_func(self):
        """Connection thread function"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self.connect())
        except Exception as e:
            logging.error(f"Error in connection thread: {e}")
        finally:
            loop.close()
    
    def stop_connection(self):
        """Stop connection to MCP server"""
        self.connected = False
        logging.info("Stopping connection to MCP server")
    
    async def invoke_tool_async(self, tool_name, params=None, emotion="neutral", context_attributes=None):
        """Invoke a tool through the MCP server with emotional context"""
        if params is None:
            params = {}
        
        if context_attributes is None:
            context_attributes = {}
        
        # Update current context with provided attributes
        for key, value in context_attributes.items():
            self.current_context["attributes"][key] = value
        
        self.current_context["last_updated"] = datetime.now().isoformat()
        
        # Create metadata with emotional context
        metadata = {
            "agent": self.agent_name,
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "emotion": emotion,
            "context_id": self.current_context["id"],
            "context_name": self.current_context["name"]
        }
        
        # Create request
        request = {
            "jsonrpc": "2.0",
            "method": tool_name,
            "params": params,
            "id": str(uuid.uuid4()),
            "metadata": metadata
        }
        
        logging.info(f"Invoking tool {tool_name} with emotion: {emotion}")
        
        try:
            async with websockets.connect(self.uri) as websocket:
                # Send request
                await websocket.send(json.dumps(request))
                
                # Receive response
                response_raw = await websocket.recv()
                response = json.loads(response_raw)
                
                # Extract emotion from response if available
                response_emotion = "neutral"
                if "metadata" in response and "emotion" in response["metadata"]:
                    response_emotion = response["metadata"]["emotion"]
                
                # Record emotional memory
                self._record_emotion(tool_name, emotion, response_emotion)
                
                # Record tool usage
                self._record_tool_usage(tool_name, params, response, emotion, response_emotion)
                
                # Update tool preferences in current context
                self._update_tool_preference(tool_name)
                
                # Save data periodically
                if len(self.tool_history) % 10 == 0:
                    self._save_data()
                
                return response
        
        except Exception as e:
            logging.error(f"Error invoking tool {tool_name}: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32000,
                    "message": f"Connection error: {str(e)}"
                },
                "id": request["id"]
            }
    
    def invoke_tool(self, tool_name, params=None, emotion="neutral", context_attributes=None):
        """Synchronous version of invoke_tool_async"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                self.invoke_tool_async(tool_name, params, emotion, context_attributes)
            )
            return result
        finally:
            loop.close()
    
    def _record_emotion(self, tool_name, request_emotion, response_emotion):
        """Record emotional memory for a tool"""
        if tool_name not in self.emotion_memory:
            self.emotion_memory[tool_name] = {
                "emotions_sent": {},
                "emotions_received": {},
                "last_emotion_sent": request_emotion,
                "last_emotion_received": response_emotion,
                "last_used": datetime.now().isoformat()
            }
        
        # Update emotion counts
        emotions_sent = self.emotion_memory[tool_name]["emotions_sent"]
        emotions_sent[request_emotion] = emotions_sent.get(request_emotion, 0) + 1
        
        emotions_received = self.emotion_memory[tool_name]["emotions_received"]
        emotions_received[response_emotion] = emotions_received.get(response_emotion, 0) + 1
        
        # Update last emotions
        self.emotion_memory[tool_name]["last_emotion_sent"] = request_emotion
        self.emotion_memory[tool_name]["last_emotion_received"] = response_emotion
        self.emotion_memory[tool_name]["last_used"] = datetime.now().isoformat()
    
    def _record_tool_usage(self, tool_name, params, response, request_emotion, response_emotion):
        """Record tool usage history"""
        usage = {
            "tool": tool_name,
            "timestamp": datetime.now().isoformat(),
            "params": params,
            "success": "error" not in response,
            "emotion_sent": request_emotion,
            "emotion_received": response_emotion,
            "context_id": self.current_context["id"],
            "context_name": self.current_context["name"]
        }
        
        self.tool_history.append(usage)
        
        # Limit history size
        if len(self.tool_history) > 1000:
            self.tool_history = self.tool_history[-1000:]
    
    def _update_tool_preference(self, tool_name):
        """Update tool preference in current context"""
        preferences = self.current_context["tool_preferences"]
        
        if tool_name not in preferences:
            preferences[tool_name] = {
                "count": 1,
                "last_used": datetime.now().isoformat()
            }
        else:
            preferences[tool_name]["count"] += 1
            preferences[tool_name]["last_used"] = datetime.now().isoformat()
    
    def get_tool_emotion(self, tool_name):
        """Get the emotional profile of a tool"""
        if tool_name not in self.emotion_memory:
            return {
                "preferred_emotion": "neutral",
                "last_emotion_sent": "neutral",
                "last_emotion_received": "neutral",
                "emotional_profile": {}
            }
        
        memory = self.emotion_memory[tool_name]
        
        # Determine preferred emotion (most successful)
        preferred_emotion = "neutral"
        max_count = 0
        
        for emotion, count in memory["emotions_sent"].items():
            if count > max_count:
                preferred_emotion = emotion
                max_count = count
        
        return {
            "preferred_emotion": preferred_emotion,
            "last_emotion_sent": memory["last_emotion_sent"],
            "last_emotion_received": memory["last_emotion_received"],
            "emotional_profile": {
                "sent": memory["emotions_sent"],
                "received": memory["emotions_received"]
            }
        }
    
    def create_context(self, name, description="", attributes=None):
        """Create a new context"""
        context_id = str(uuid.uuid4())
        
        context = {
            "id": context_id,
            "name": name,
            "description": description,
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "attributes": attributes or {},
            "tool_preferences": {}
        }
        
        self.contexts[context_id] = context
        self._save_data()
        
        return context_id
    
    def switch_context(self, context_id):
        """Switch to a different context"""
        if context_id not in self.contexts:
            logging.warning(f"Context {context_id} not found")
            return False
        
        self.current_context = self.contexts[context_id]
        logging.info(f"Switched to context: {self.current_context['name']}")
        return True
    
    def get_current_context(self):
        """Get the current context"""
        return self.current_context
    
    def update_context_attribute(self, key, value):
        """Update an attribute in the current context"""
        self.current_context["attributes"][key] = value
        self.current_context["last_updated"] = datetime.now().isoformat()
        self._save_data()
    
    def select_tool_for_task(self, task_description, context_attributes=None):
        """Select the most appropriate tool for a task based on context"""
        if context_attributes:
            # Update context with provided attributes
            for key, value in context_attributes.items():
                self.current_context["attributes"][key] = value
            
            self.current_context["last_updated"] = datetime.now().isoformat()
        
        # This is a simplified implementation
        # In a real system, this would use more sophisticated matching
        
        # Get all tools
        available_tools = list(self.tools.values())
        if not available_tools:
            return None
        
        # Score tools based on description match and context preferences
        scored_tools = []
        
        for tool in available_tools:
            score = 0
            tool_name = tool["name"]
            
            # Score based on description match
            if "description" in tool:
                # Simple word matching
                description_words = set(tool["description"].lower().split())
                task_words = set(task_description.lower().split())
                matching_words = description_words.intersection(task_words)
                
                # Add score based on matching words
                score += len(matching_words) * 0.2
            
            # Score based on context preferences
            preferences = self.current_context["tool_preferences"]
            if tool_name in preferences:
                # Add score based on usage count in this context
                score += min(1.0, preferences[tool_name]["count"] / 5)
            
            # Score based on parameter match with context attributes
            if "parameters" in tool:
                for param_name, param_info in tool["parameters"].items():
                    if param_name in self.current_context["attributes"]:
                        # Parameter can be filled from context
                        score += 0.3
            
            scored_tools.append((tool, score))
        
        # Sort by score
        scored_tools.sort(key=lambda x: x[1], reverse=True)
        
        # Return the highest scoring tool
        if scored_tools and scored_tools[0][1] > 0:
            return scored_tools[0][0]
        
        # If no good match, return a generic tool or None
        return None
    
    def get_tool_history(self, tool_name=None, limit=10):
        """Get tool usage history"""
        if tool_name:
            # Filter by tool name
            history = [entry for entry in self.tool_history if entry["tool"] == tool_name]
        else:
            history = self.tool_history
        
        # Sort by timestamp (newest first)
        history.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return history[:limit]
    
    def get_available_tools(self):
        """Get available tools"""
        return list(self.tools.values())
    
    def get_tool_by_name(self, tool_name):
        """Get a tool by name"""
        return self.tools.get(tool_name)

# For testing
if __name__ == "__main__":
    mcp = EnhancedMCPIntegration()
    
    # Start connection
    print("Starting connection to MCP server...")
    mcp.start_connection()
    
    # Wait for connection
    time.sleep(2)
    
    # Create a test context
    print("\nCreating test context...")
    context_id = mcp.create_context("TestContext", "A test context", {
        "user": "TestUser",
        "task": "Testing MCP integration",
        "location": "Test environment"
    })
    
    # Get available tools
    tools = mcp.get_available_tools()
    print(f"\nAvailable tools: {len(tools)}")
    for tool in tools:
        print(f"- {tool['name']}")
    
    # Test tool invocation if tools are available
    if tools:
        tool = tools[0]
        print(f"\nTesting tool invocation: {tool['name']}")
        
        # Invoke with different emotions
        emotions = ["curious", "excited", "neutral"]
        for emotion in emotions:
            print(f"\nInvoking with emotion: {emotion}")
            response = mcp.invoke_tool(tool["name"], {}, emotion)
            print(f"Response: {response}")
            
            # Get tool emotion
            emotion_profile = mcp.get_tool_emotion(tool["name"])
            print(f"Tool emotion profile: {emotion_profile}")
    
    # Test context-aware tool selection
    print("\nTesting context-aware tool selection...")
    selected_tool = mcp.select_tool_for_task("I need to search for information")
    if selected_tool:
        print(f"Selected tool: {selected_tool['name']}")
    else:
        print("No suitable tool found")
    
    # Stop connection
    print("\nStopping connection...")
    mcp.stop_connection()
    
    # Wait for connection to close
    time.sleep(1)
    print("Done")
