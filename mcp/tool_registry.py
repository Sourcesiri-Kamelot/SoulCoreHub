"""
Tool Registry for MCP Server
Manages registration and access to tools
"""

import logging
import os
import importlib.util
from typing import Dict, Any, List, Optional

from mcp.core.tool import MCPTool

logger = logging.getLogger("ToolRegistry")

class ToolRegistry:
    """Registry for MCP tools"""
    
    def __init__(self):
        """Initialize the tool registry"""
        self.tools = {}
        logger.info("Tool Registry initialized")
    
    def register_tool(self, tool: MCPTool) -> bool:
        """
        Register a tool with the registry
        
        Args:
            tool: The tool to register
            
        Returns:
            True if registration was successful, False otherwise
        """
        if not isinstance(tool, MCPTool):
            logger.error(f"Cannot register tool: {tool} is not an instance of MCPTool")
            return False
        
        tool_name = tool.name
        
        if tool_name in self.tools:
            logger.warning(f"Tool {tool_name} is already registered. Overwriting.")
        
        self.tools[tool_name] = tool
        logger.info(f"Registered tool: {tool_name}")
        
        return True
    
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """
        Get a tool by name
        
        Args:
            tool_name: Name of the tool to get
            
        Returns:
            The tool if found, None otherwise
        """
        if tool_name not in self.tools:
            logger.warning(f"Tool {tool_name} not found in registry")
            return None
        
        return self.tools[tool_name]
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all registered tools
        
        Returns:
            List of tool metadata
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
                "required_parameters": tool.required_parameters
            }
            for tool in self.tools.values()
        ]
    
    def load_tools_from_directory(self, directory: str) -> int:
        """
        Load tools from a directory
        
        Args:
            directory: Directory containing tool modules
            
        Returns:
            Number of tools loaded
        """
        if not os.path.exists(directory) or not os.path.isdir(directory):
            logger.error(f"Tool directory not found: {directory}")
            return 0
        
        count = 0
        
        for filename in os.listdir(directory):
            if filename.endswith("_tool.py"):
                try:
                    # Load the module
                    module_path = os.path.join(directory, filename)
                    module_name = os.path.splitext(filename)[0]
                    
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    if spec is None or spec.loader is None:
                        logger.error(f"Could not load module spec for {module_path}")
                        continue
                        
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find and instantiate tool classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, MCPTool) and 
                            attr is not MCPTool):
                            
                            # Instantiate the tool
                            tool = attr()
                            
                            # Register the tool
                            if self.register_tool(tool):
                                count += 1
                
                except Exception as e:
                    logger.error(f"Error loading tool from {filename}: {str(e)}")
        
        logger.info(f"Loaded {count} tools from {directory}")
        return count

# Singleton instance
_registry = ToolRegistry()

def get_registry() -> ToolRegistry:
    """
    Get the tool registry singleton
    
    Returns:
        The tool registry singleton
    """
    return _registry
