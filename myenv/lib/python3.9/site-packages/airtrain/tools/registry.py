"""
Tool Registry System for AirTrain

This module provides a registry system for tools that can be used by AI agents.
It supports both stateful tools (requiring fresh instances) and stateless tools 
(which can be shared/reused).

The registry system includes:
- Validation mechanisms for tools
- Registration decorators
- Factory methods for tool creation
- Discovery utilities for finding available tools
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Type, Any, Optional, TypeVar


# Type variable for tool classes
T = TypeVar('T', bound='BaseTool')

# Registry structure: {"stateful": {}, "stateless": {}}
TOOL_REGISTRY = {
    "stateful": {},
    "stateless": {}
}


class ToolValidationError(Exception):
    """Exception raised when a tool fails validation checks."""
    pass


class BaseTool(ABC):
    """Base class for all tools."""
    
    # These will be set by the registration decorator
    tool_name: str = None
    tool_type: str = None
    
    @abstractmethod
    def __call__(self, **kwargs) -> Any:
        """Execute the tool with the given parameters."""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary format for LLM function calling."""
        pass


class StatefulTool(BaseTool):
    """Base class for tools that maintain state and require fresh instances."""
    
    @classmethod
    @abstractmethod
    def create_instance(cls: Type[T]) -> T:
        """Create a new instance of the tool with fresh state."""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset the tool's internal state."""
        pass


class StatelessTool(BaseTool):
    """Base class for stateless tools that can be reused."""
    pass


def validate_tool(cls: Type[BaseTool], tool_type: str) -> Type[BaseTool]:
    """
    Validate that a tool class meets the requirements for its type.
    
    Args:
        cls: The tool class to validate
        tool_type: Either "stateful" or "stateless"
    
    Returns:
        The validated tool class
    
    Raises:
        ToolValidationError: If the tool does not meet requirements
    """
    # Check that the class implements the required methods
    if not hasattr(cls, '__call__') or not callable(getattr(cls, '__call__')):
        raise ToolValidationError(f"Tool {cls.__name__} must implement __call__ method")
    
    if not hasattr(cls, 'to_dict') or not callable(getattr(cls, 'to_dict')):
        raise ToolValidationError(f"Tool {cls.__name__} must implement to_dict method")
    
    # Validate stateful tool specific requirements
    if tool_type == "stateful":
        if not issubclass(cls, StatefulTool):
            raise ToolValidationError(
                f"Stateful tool {cls.__name__} must inherit from StatefulTool"
            )
        
        create_instance_attr = hasattr(cls, 'create_instance')
        create_instance_callable = callable(getattr(cls, 'create_instance', None))
        
        if not create_instance_attr or not create_instance_callable:
            raise ToolValidationError(
                f"Stateful tool {cls.__name__} must implement create_instance class method"
            )
        
        if not hasattr(cls, 'reset') or not callable(getattr(cls, 'reset')):
            raise ToolValidationError(
                f"Stateful tool {cls.__name__} must implement reset method"
            )
    
    # Validate stateless tool specific requirements
    if tool_type == "stateless":
        if not issubclass(cls, StatelessTool):
            raise ToolValidationError(
                f"Stateless tool {cls.__name__} must inherit from StatelessTool"
            )
    
    return cls


def register_tool(name: str, tool_type: str = "stateless"):
    """
    Decorator for registering a tool with the registry.
    
    Args:
        name: The name of the tool
        tool_type: Either "stateful" or "stateless"
    
    Returns:
        A decorator function that registers the tool
    
    Raises:
        ValueError: If the tool name is already registered or the tool type is invalid
    """
    if tool_type not in TOOL_REGISTRY:
        raise ValueError(
            f"Invalid tool type: {tool_type}. Must be either 'stateful' or 'stateless'"
        )
    
    def decorator(cls: Type[BaseTool]) -> Type[BaseTool]:
        if name in TOOL_REGISTRY[tool_type]:
            raise ValueError(f"Tool name '{name}' already registered in {tool_type} registry")
        
        # Validate the tool
        validated_cls = validate_tool(cls, tool_type)
        
        # Register the tool
        TOOL_REGISTRY[tool_type][name] = validated_cls
        
        # Add metadata to the class
        validated_cls.tool_name = name
        validated_cls.tool_type = tool_type
        
        return validated_cls
    
    return decorator


class ToolFactory:
    """Factory class for creating and managing tools."""
    
    @staticmethod
    def get_tool(name: str, tool_type: str = "stateless") -> BaseTool:
        """
        Get a tool instance by name and type.
        
        For stateful tools, this returns a fresh instance.
        For stateless tools, this returns a singleton instance.
        
        Args:
            name: The name of the tool
            tool_type: Either "stateful" or "stateless"
        
        Returns:
            An instance of the requested tool
        
        Raises:
            ValueError: If the tool or tool type is not found
        """
        if tool_type not in TOOL_REGISTRY:
            raise ValueError(f"Invalid tool type: {tool_type}")
        
        tool_cls = TOOL_REGISTRY[tool_type].get(name)
        if not tool_cls:
            raise ValueError(f"Tool '{name}' not found in {tool_type} registry")
        
        # Handle stateful tools - always create a fresh instance
        if tool_type == "stateful":
            instance = tool_cls.create_instance()
            instance.reset()  # Ensure the instance is in a clean state
            return instance
        
        # Handle stateless tools - reuse the same instance
        # We use a singleton pattern here with lazy initialization
        if not hasattr(tool_cls, '_instance'):
            tool_cls._instance = tool_cls()
        
        return tool_cls._instance
    
    @staticmethod
    def list_tools(tool_type: Optional[str] = None) -> Dict[str, List[str]]:
        """
        List all registered tools, optionally filtered by type.
        
        Args:
            tool_type: Optional filter for tool type
        
        Returns:
            A dictionary mapping tool types to lists of tool names
        """
        if tool_type:
            if tool_type not in TOOL_REGISTRY:
                raise ValueError(f"Invalid tool type: {tool_type}")
            return {tool_type: list(TOOL_REGISTRY[tool_type].keys())}
        
        return {t_type: list(tools.keys()) for t_type, tools in TOOL_REGISTRY.items()}
    
    @staticmethod
    def get_tool_definitions(tool_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get tool definitions for all registered tools or tools of a specific type.
        
        This is useful for preparing tools for LLM function calling.
        
        Args:
            tool_type: Optional filter for tool type
        
        Returns:
            A list of tool definitions in dictionary format
        """
        tool_defs = []
        
        if tool_type:
            if tool_type not in TOOL_REGISTRY:
                raise ValueError(f"Invalid tool type: {tool_type}")
            registry = {tool_type: TOOL_REGISTRY[tool_type]}
        else:
            registry = TOOL_REGISTRY
        
        for t_type, tools in registry.items():
            for name, cls in tools.items():
                # For stateless tools, we can use the singleton instance
                if t_type == "stateless":
                    if not hasattr(cls, '_instance'):
                        cls._instance = cls()
                    tool_defs.append(cls._instance.to_dict())
                # For stateful tools, we need to create a temporary instance
                else:
                    instance = cls.create_instance()
                    tool_defs.append(instance.to_dict())
        
        return tool_defs


def get_default_tools(tool_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get tool definitions for all registered tools.
    
    This is a convenience function that delegates to ToolFactory.get_tool_definitions.
    
    Args:
        tool_type: Optional filter for tool type
    
    Returns:
        A list of tool definitions in dictionary format
    """
    return ToolFactory.get_tool_definitions(tool_type)


def execute_tool_call(tool_call: Dict[str, Any]) -> Any:
    """
    Execute a tool call based on LLM function calling format.
    
    Args:
        tool_call: A dictionary containing the tool call details
    
    Returns:
        The result of executing the tool call
    
    Raises:
        ValueError: If the tool is not found or the call format is invalid
    """
    import json
    
    # Extract tool details from the call
    function_details = tool_call.get("function", {})
    function_name = function_details.get("name")
    
    if not function_name:
        raise ValueError("Invalid tool call format: Missing function name")
    
    # Try to find the tool in both registries
    tool = None
    tool_type = None
    
    for t_type in TOOL_REGISTRY:
        if function_name in TOOL_REGISTRY[t_type]:
            tool_type = t_type
            break
    
    if not tool_type:
        raise ValueError(f"Tool '{function_name}' not found in any registry")
    
    # Get a tool instance
    tool = ToolFactory.get_tool(function_name, tool_type)
    
    # Parse arguments
    try:
        arguments = json.loads(function_details.get("arguments", "{}"))
    except json.JSONDecodeError:
        raise ValueError(f"Invalid arguments format for tool '{function_name}'")
    
    # Execute the tool
    try:
        result = tool(**arguments)
        return result
    except Exception as e:
        return f"Error executing tool '{function_name}': {str(e)}" 