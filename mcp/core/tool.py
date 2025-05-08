"""
Base Tool class for MCP
"""

from typing import Dict, Any, List, Optional

class MCPTool:
    """Base class for all MCP tools"""
    
    def __init__(self, name: str, description: str, parameters: Dict[str, Any], required_parameters: List[str] = None):
        """
        Initialize the tool
        
        Args:
            name: Tool name
            description: Tool description
            parameters: Parameter schema
            required_parameters: List of required parameter names
        """
        self.name = name
        self.description = description
        self.parameters = parameters
        self.required_parameters = required_parameters or []
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool
        
        Args:
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        raise NotImplementedError("Tool must implement execute method")
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Optional[str]:
        """
        Validate parameters
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            Error message if validation fails, None otherwise
        """
        # Check required parameters
        for param in self.required_parameters:
            if param not in parameters:
                return f"Missing required parameter: {param}"
        
        return None
