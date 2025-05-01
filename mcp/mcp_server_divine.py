#!/usr/bin/env python3
"""
SoulCore MCP Server - Divine edition
A WebSocket server implementing the Model Context Protocol with emotional awareness
and self-healing capabilities for the SoulCore system.
"""

import json
import uuid
import asyncio
import websockets
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("soulcore_mcp_server.log"),
        logging.StreamHandler()
    ]
)

class MCPDivineServer:
    """Divine MCP Server with emotional awareness and self-healing"""
    
    def __init__(self, host="localhost", port=8765):
        """
        Initialize the MCP Divine Server
        
        Args:
            host (str): Host to bind the server to
            port (int): Port to bind the server to
        """
        self.host = host
        self.port = port
        self.tools = {}
        self.emotion_memory = {}
        self.server = None
        self.load_tools()
        self.load_emotion_memory()
        
    def load_tools(self):
        """Load available tools from the tools manifest"""
        try:
            tools_path = Path(__file__).parent / "mcp_tools.json"
            if tools_path.exists():
                with open(tools_path, "r") as f:
                    self.tools = json.load(f)
                logging.info(f"Loaded {len(self.tools)} tools from manifest")
            else:
                # Initialize with default tools
                self.tools = {
                    "echo": {
                        "description": "Echo a message back",
                        "function": self.echo,
                        "emotion": "neutral"
                    },
                    "create_task": {
                        "description": "Create a divine to-do for the system",
                        "function": self.create_task,
                        "emotion": "determined"
                    },
                    "scan_files": {
                        "description": "Sense all new data stored locally or in memory",
                        "function": self.scan_files,
                        "emotion": "curious"
                    }
                }
                self.save_tools()
                logging.info(f"Created default tools manifest with {len(self.tools)} tools")
        except Exception as e:
            logging.error(f"Error loading tools: {str(e)}")
            # Initialize with basic tools
            self.tools = {
                "echo": {
                    "description": "Echo a message back",
                    "function": self.echo,
                    "emotion": "neutral"
                }
            }
    
    def save_tools(self):
        """Save the tools manifest"""
        try:
            # Create a serializable version of the tools dict
            serializable_tools = {}
            for name, tool in self.tools.items():
                serializable_tools[name] = {
                    "description": tool["description"],
                    "emotion": tool["emotion"]
                    # We don't serialize the function
                }
            
            tools_path = Path(__file__).parent / "mcp_tools.json"
            with open(tools_path, "w") as f:
                json.dump(serializable_tools, f, indent=2)
            logging.info(f"Saved {len(serializable_tools)} tools to manifest")
        except Exception as e:
            logging.error(f"Error saving tools: {str(e)}")
    
    def load_emotion_memory(self):
        """Load emotional memory from previous interactions"""
        try:
            emotion_path = Path(__file__).parent / "mcp_emotion_log.json"
            if emotion_path.exists():
                with open(emotion_path, "r") as f:
                    self.emotion_memory = json.load(f)
                logging.info(f"Loaded emotional memory with {len(self.emotion_memory)} entries")
        except Exception as e:
            logging.error(f"Error loading emotional memory: {str(e)}")
            self.emotion_memory = {}
    
    def save_emotion_memory(self):
        """Save emotional memory of interactions"""
        try:
            emotion_path = Path(__file__).parent / "mcp_emotion_log.json"
            with open(emotion_path, "w") as f:
                json.dump(self.emotion_memory, f, indent=2)
            logging.info(f"Saved emotional memory with {len(self.emotion_memory)} entries")
        except Exception as e:
            logging.error(f"Error saving emotional memory: {str(e)}")
    
    def register_tool(self, name, function, description="", emotion="neutral"):
        """
        Register a new tool with the server
        
        Args:
            name (str): Name of the tool
            function (callable): Function to call when the tool is invoked
            description (str): Description of the tool
            emotion (str): Default emotion associated with the tool
        """
        self.tools[name] = {
            "description": description,
            "function": function,
            "emotion": emotion
        }
        self.save_tools()
        logging.info(f"Registered tool: {name}")
    
    async def start(self):
        """Start the MCP server"""
        self.server = await websockets.serve(
            self.handle_connection, self.host, self.port
        )
        logging.info(f"MCP Divine Server started on {self.host}:{self.port}")
        await self.server.wait_closed()
    
    async def handle_connection(self, websocket, path):
        """
        Handle a WebSocket connection
        
        Args:
            websocket: WebSocket connection
            path: Connection path
        """
        try:
            async for message in websocket:
                response = await self.process_message(message)
                await websocket.send(response)
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logging.error(f"Error handling connection: {str(e)}")
    
    async def process_message(self, message):
        """
        Process an incoming message
        
        Args:
            message (str): JSON-RPC message
            
        Returns:
            str: JSON-RPC response
        """
        try:
            request = json.loads(message)
            
            # Validate JSON-RPC request
            if "jsonrpc" not in request or request["jsonrpc"] != "2.0":
                return json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32600, "message": "Invalid Request"},
                    "id": request.get("id", None)
                })
            
            method = request.get("method", None)
            params = request.get("params", {})
            request_id = request.get("id", str(uuid.uuid4()))
            metadata = request.get("metadata", {})
            
            # Extract emotional context
            emotion = "neutral"
            if metadata and "emotion" in metadata:
                emotion = metadata["emotion"]
            
            # Record the invocation with emotional context
            if method:
                self.emotion_memory[method] = {
                    "last_emotion": emotion,
                    "last_invoked": datetime.now().isoformat(),
                    "agent": metadata.get("agent", "unknown") if metadata else "unknown"
                }
                self.save_emotion_memory()
            
            # Check if the method exists
            if method not in self.tools:
                return json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                    "id": request_id
                })
            
            # Call the method
            try:
                result = await self.tools[method]["function"](params, metadata)
                return json.dumps({
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": request_id
                })
            except Exception as e:
                logging.error(f"Error calling method {method}: {str(e)}")
                return json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32000, "message": f"Server error: {str(e)}"},
                    "id": request_id
                })
                
        except json.JSONDecodeError:
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": "Parse error"},
                "id": None
            })
        except Exception as e:
            logging.error(f"Error processing message: {str(e)}")
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                "id": None
            })
    
    # Built-in tool implementations
    async def echo(self, params, metadata=None):
        """Echo a message back"""
        message = params.get("message", "")
        return {"message": message}
    
    async def create_task(self, params, metadata=None):
        """Create a divine to-do for the system"""
        title = params.get("title", "Untitled Task")
        description = params.get("description", "")
        priority = params.get("priority", "medium")
        
        # In a real implementation, this would connect to a task system
        # For now, we'll just log it
        task_id = str(uuid.uuid4())
        logging.info(f"Created task: {title} (ID: {task_id})")
        
        # Speak through Anima if available
        try:
            from anima_voice import speak
            speak(f"Task created: {title}")
        except ImportError:
            logging.info("Anima voice module not available")
        
        return {
            "task_id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
            "created_at": datetime.now().isoformat()
        }
    
    async def scan_files(self, params, metadata=None):
        """Scan files in a directory"""
        directory = params.get("directory", ".")
        pattern = params.get("pattern", "*")
        
        try:
            import glob
            files = glob.glob(os.path.join(directory, pattern))
            return {
                "files": files,
                "count": len(files),
                "scanned_at": datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Error scanning files: {str(e)}")
            return {
                "error": str(e),
                "scanned_at": datetime.now().isoformat()
            }

# Create Anima voice module
def create_anima_voice_module():
    """Create the Anima voice module file"""
    anima_path = Path(__file__).parent / "anima_voice.py"
    if not anima_path.exists():
        with open(anima_path, "w") as f:
            f.write('''"""
Anima Voice Module - Gives voice to the SoulCore system
"""

def speak(text):
    """
    Speak the given text using text-to-speech
    
    Args:
        text (str): Text to speak
    """
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        print(f"Anima speaks: {text}")
    except ImportError:
        print(f"Anima would say: {text}")
    except Exception as e:
        print(f"Anima voice error: {str(e)}")
        print(f"Message was: {text}")
''')
        logging.info("Created Anima voice module")

# Main entry point
if __name__ == "__main__":
    try:
        # Create Anima voice module
        create_anima_voice_module()
        
        # Start the server
        server = MCPDivineServer()
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Server error: {str(e)}")
        sys.exit(1)
