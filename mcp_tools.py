#!/usr/bin/env python3
"""
MCP Tools for SoulCoreHub
Tool implementations for the MCP server
"""

import os
import json
import logging
import time
import asyncio
from pathlib import Path
from typing import Dict, Any, AsyncGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mcp_tools.log')
    ]
)
logger = logging.getLogger("MCPTools")

class MCPTools:
    """
    Tool implementations for the MCP server
    """
    
    def __init__(self):
        """Initialize the MCP Tools"""
        self.tools = {}
        self._register_default_tools()
        logger.info("MCP Tools initialized")
    
    def _register_default_tools(self):
        """Register default tools"""
        self.register_tool("system_info", self.tool_system_info)
        self.register_tool("file_read", self.tool_file_read)
        self.register_tool("file_write", self.tool_file_write)
        self.register_tool("execute_command", self.tool_execute_command)
        self.register_tool("memory_store", self.tool_memory_store)
        self.register_tool("memory_retrieve", self.tool_memory_retrieve)
        self.register_tool("generate_text", self.tool_generate_text)
    
    def register_tool(self, name, handler):
        """
        Register a tool
        
        Args:
            name: Name of the tool
            handler: Function to handle tool invocation
        """
        self.tools[name] = handler
        logger.info(f"Tool registered: {name}")
    
    def get_tool(self, name):
        """
        Get a tool by name
        
        Args:
            name: Name of the tool
            
        Returns:
            function: Tool handler or None if not found
        """
        return self.tools.get(name)
    
    def get_all_tools(self):
        """
        Get all registered tools
        
        Returns:
            dict: Dictionary of tool names and handlers
        """
        return self.tools
    
    # Tool implementations
    
    async def tool_system_info(self, parameters, agent="system", emotion="neutral"):
        """
        Get system information
        
        Args:
            parameters: Tool parameters
            agent: The agent making the request
            emotion: The emotional context
            
        Returns:
            dict: System information
        """
        import platform
        import psutil
        
        try:
            # Basic system info
            system_info = {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "processor": platform.processor(),
                "hostname": platform.node(),
                "timestamp": time.time()
            }
            
            # Add resource usage if requested
            if parameters.get("include_resources", False):
                system_info.update({
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": psutil.disk_usage('/').percent
                })
            
            return system_info
        
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {"error": f"Error: {str(e)}"}
    
    async def tool_file_read(self, parameters, agent="system", emotion="neutral"):
        """
        Read a file
        
        Args:
            parameters: Tool parameters
            agent: The agent making the request
            emotion: The emotional context
            
        Returns:
            dict: File content
        """
        path = parameters.get("path")
        
        if not path:
            return {"error": "Path is required"}
        
        try:
            # Expand user directory if needed
            if path.startswith("~"):
                path = os.path.expanduser(path)
            
            # Check if file exists
            if not os.path.exists(path):
                return {"error": f"File not found: {path}"}
            
            # Check if path is a file
            if not os.path.isfile(path):
                return {"error": f"Not a file: {path}"}
            
            # Read the file
            with open(path, 'r') as f:
                content = f.read()
            
            return {
                "content": content,
                "path": path,
                "size": len(content),
                "timestamp": time.time()
            }
        
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return {"error": f"Error: {str(e)}"}
    
    async def tool_file_write(self, parameters, agent="system", emotion="neutral"):
        """
        Write to a file
        
        Args:
            parameters: Tool parameters
            agent: The agent making the request
            emotion: The emotional context
            
        Returns:
            dict: Result of the operation
        """
        path = parameters.get("path")
        content = parameters.get("content")
        append = parameters.get("append", False)
        
        if not path:
            return {"error": "Path is required"}
        
        if content is None:
            return {"error": "Content is required"}
        
        try:
            # Expand user directory if needed
            if path.startswith("~"):
                path = os.path.expanduser(path)
            
            # Create directory if it doesn't exist
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # Write to the file
            mode = 'a' if append else 'w'
            with open(path, mode) as f:
                f.write(content)
            
            return {
                "success": True,
                "path": path,
                "size": len(content),
                "timestamp": time.time()
            }
        
        except Exception as e:
            logger.error(f"Error writing to file: {e}")
            return {"error": f"Error: {str(e)}"}
    
    async def tool_execute_command(self, parameters, agent="system", emotion="neutral"):
        """
        Execute a command
        
        Args:
            parameters: Tool parameters
            agent: The agent making the request
            emotion: The emotional context
            
        Returns:
            dict: Command output
        """
        command = parameters.get("command")
        
        if not command:
            return {"error": "Command is required"}
        
        try:
            import subprocess
            
            # Execute the command
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            return {
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": process.returncode,
                "command": command,
                "timestamp": time.time()
            }
        
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return {"error": f"Error: {str(e)}"}
    
    async def tool_memory_store(self, parameters, agent="system", emotion="neutral"):
        """
        Store data in memory
        
        Args:
            parameters: Tool parameters
            agent: The agent making the request
            emotion: The emotional context
            
        Returns:
            dict: Result of the operation
        """
        key = parameters.get("key")
        value = parameters.get("value")
        memory_type = parameters.get("type", "general")
        
        if not key:
            return {"error": "Key is required"}
        
        if value is None:
            return {"error": "Value is required"}
        
        try:
            # Create memory directory if it doesn't exist
            memory_dir = Path("memory")
            memory_dir.mkdir(exist_ok=True)
            
            # Create memory file if it doesn't exist
            memory_file = memory_dir / f"{memory_type}_memory.json"
            
            # Load existing memory
            if memory_file.exists():
                with open(memory_file, 'r') as f:
                    memory = json.load(f)
            else:
                memory = {}
            
            # Store the value
            memory[key] = {
                "value": value,
                "timestamp": time.time(),
                "agent": agent,
                "emotion": emotion
            }
            
            # Save memory
            with open(memory_file, 'w') as f:
                json.dump(memory, f, indent=2)
            
            return {
                "success": True,
                "key": key,
                "type": memory_type,
                "timestamp": time.time()
            }
        
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            return {"error": f"Error: {str(e)}"}
    
    async def tool_memory_retrieve(self, parameters, agent="system", emotion="neutral"):
        """
        Retrieve data from memory
        
        Args:
            parameters: Tool parameters
            agent: The agent making the request
            emotion: The emotional context
            
        Returns:
            dict: Retrieved data
        """
        key = parameters.get("key")
        memory_type = parameters.get("type", "general")
        
        if not key:
            return {"error": "Key is required"}
        
        try:
            # Check if memory file exists
            memory_file = Path("memory") / f"{memory_type}_memory.json"
            
            if not memory_file.exists():
                return {"error": f"Memory file not found: {memory_file}"}
            
            # Load memory
            with open(memory_file, 'r') as f:
                memory = json.load(f)
            
            # Retrieve the value
            if key in memory:
                return {
                    "key": key,
                    "value": memory[key]["value"],
                    "timestamp": memory[key]["timestamp"],
                    "agent": memory[key]["agent"],
                    "emotion": memory[key]["emotion"]
                }
            else:
                return {"error": f"Key not found: {key}"}
        
        except Exception as e:
            logger.error(f"Error retrieving memory: {e}")
            return {"error": f"Error: {str(e)}"}
    
    async def tool_generate_text(self, parameters, agent="system", emotion="neutral"):
        """
        Generate text using a local model
        
        Args:
            parameters: Tool parameters
            agent: The agent making the request
            emotion: The emotional context
            
        Returns:
            dict: Generated text
            
        Note:
            This is a placeholder implementation. In a real system, this would
            use a local LLM or connect to an external API.
        """
        prompt = parameters.get("prompt")
        max_tokens = parameters.get("max_tokens", 100)
        stream = parameters.get("stream", False)
        
        if not prompt:
            return {"error": "Prompt is required"}
        
        try:
            # This is a placeholder implementation
            # In a real system, this would use a local LLM or connect to an external API
            
            if stream:
                # Simulate streaming response
                words = f"This is a simulated streaming response for the prompt: {prompt}. The emotional context is {emotion}. This response is coming from the {agent} agent.".split()
                
                for word in words[:max_tokens]:
                    yield word + " "
                    await asyncio.sleep(0.1)
            
            else:
                # Simulate non-streaming response
                response = f"This is a simulated response for the prompt: {prompt}. The emotional context is {emotion}. This response is coming from the {agent} agent."
                
                return {
                    "text": response[:max_tokens],
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "timestamp": time.time()
                }
        
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            if stream:
                yield f"Error: {str(e)}"
            else:
                return {"error": f"Error: {str(e)}"}

# Create a global instance
mcp_tools = MCPTools()

if __name__ == "__main__":
    # Simple CLI for testing
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            print("Available tools:")
            for tool_name in mcp_tools.get_all_tools():
                print(f"  - {tool_name}")
        
        else:
            print("Unknown command")
    else:
        print("Usage:")
        print("  python mcp_tools.py list")
