"""
Agent Registry System for AirTrain

This module provides a registry system for agents that can be used to build AI systems.
It includes:
- Base agent class
- Registration decorators
- Factory methods for agent creation
- Discovery utilities for finding available agents
"""

from abc import ABC, abstractmethod
import time
import uuid
from typing import List, Optional, Type, TypeVar, Union
import inspect

# Import tool registry components
from airtrain.tools import ToolFactory, BaseTool
from airtrain.telemetry import (
    telemetry,
    AgentRunTelemetryEvent,
    AgentStepTelemetryEvent,
    AgentEndTelemetryEvent,
    ModelInvocationTelemetryEvent,
    ErrorTelemetryEvent
)
from .memory import AgentMemoryManager


# Type variable for agent classes
A = TypeVar('A', bound='BaseAgent')

# Registry structure for agent classes
AGENT_REGISTRY = {}


class BaseAgent(ABC):
    """Base class for all agents."""
    
    # These will be set by the registration decorator
    agent_name: str = None
    
    def __init__(
        self, 
        name: str, 
        models: Optional[List[str]] = None, 
        tools: Optional[List[BaseTool]] = None
    ):
        """
        Initialize an agent.
        
        Args:
            name: Name of the agent instance
            models: List of model identifiers to use
            tools: List of tools the agent can use
        """
        self.name = name
        self.models = models or []
        self.tools = tools or []
        self.memory = AgentMemoryManager()
        
        # Generate unique agent ID for telemetry
        self.agent_id = f"{name}-{uuid.uuid4()}"
        self.start_time = None
        self.step_count = 0
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.errors = []
        
        # Initialize default short-term memory
        self.memory.create_short_term_memory("default")
    
    def add_tool(self, tool: BaseTool):
        """
        Add a tool to the agent.
        
        Args:
            tool: Tool instance to add
            
        Returns:
            Self for method chaining
        """
        self.tools.append(tool)
        return self
    
    def register_tools(self, tools: List[BaseTool]):
        """
        Register multiple tools with the agent.
        
        Args:
            tools: List of tool instances to add
            
        Returns:
            Self for method chaining
        """
        self.tools.extend(tools)
        return self
    
    def create_memory(self, name: str, max_messages: int = 10):
        """
        Create a new short-term memory.
        
        Args:
            name: Name for the memory
            max_messages: Maximum messages before summarization
            
        Returns:
            The created memory instance
        """
        return self.memory.create_short_term_memory(name, max_messages)
    
    def reset_memory(self, name: str = "default"):
        """
        Reset a specific short-term memory.
        
        Args:
            name: Name of the memory to reset
            
        Returns:
            Self for method chaining
        """
        self.memory.reset_short_term_memory(name)
        return self
    
    def start_run(self, task: str, model_name: str, model_provider: str):
        """
        Start an agent run and send telemetry.
        
        Args:
            task: Description of the task
            model_name: Name of the model being used
            model_provider: Provider of the model
            
        Returns:
            Self for method chaining
        """
        self.start_time = time.time()
        self.step_count = 0
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.errors = []
        
        # Send run event
        event = AgentRunTelemetryEvent(
            agent_id=self.agent_id,
            task=task,
            model_name=model_name,
            model_provider=model_provider,
            version=self._get_package_version(),
            source=self.__class__.__name__
        )
        telemetry.capture(event)
        return self
    
    def record_step(self, actions: List[dict], step_error: List[str] = None):
        """
        Record an agent step and send telemetry.
        
        Args:
            actions: List of actions taken in this step
            step_error: Optional list of errors encountered
            
        Returns:
            Self for method chaining
        """
        self.step_count += 1
        consecutive_failures = len(self.errors)
        
        # Send step event
        event = AgentStepTelemetryEvent(
            agent_id=self.agent_id,
            step=self.step_count,
            step_error=step_error or [],
            consecutive_failures=consecutive_failures,
            actions=actions
        )
        telemetry.capture(event)
        return self
    
    def record_model_usage(
        self, 
        model_name: str, 
        model_provider: str, 
        tokens: int, 
        prompt_tokens: int, 
        completion_tokens: int,
        duration_seconds: float, 
        error: str = None
    ):
        """
        Record model usage and send telemetry.
        
        Args:
            model_name: Name of the model used
            model_provider: Provider of the model
            tokens: Total tokens used
            prompt_tokens: Tokens used in the prompt
            completion_tokens: Tokens used in the completion
            duration_seconds: Duration of the model call
            error: Optional error message
            
        Returns:
            Self for method chaining
        """
        self.total_tokens += tokens
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        
        # Send model usage event
        event = ModelInvocationTelemetryEvent(
            agent_id=self.agent_id,
            model_name=model_name,
            model_provider=model_provider,
            tokens=tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            duration_seconds=duration_seconds,
            error=error
        )
        telemetry.capture(event)
        return self
    
    def end_run(self, is_done: bool, success: bool = None):
        """
        End an agent run and send telemetry.
        
        Args:
            is_done: Whether the agent completed its task
            success: Whether the agent was successful
            
        Returns:
            Self for method chaining
        """
        duration = time.time() - self.start_time if self.start_time else 0
        
        # Send end event
        event = AgentEndTelemetryEvent(
            agent_id=self.agent_id,
            steps=self.step_count,
            is_done=is_done,
            success=success,
            total_tokens=self.total_tokens,
            prompt_tokens=self.prompt_tokens,
            completion_tokens=self.completion_tokens,
            total_duration_seconds=duration,
            errors=self.errors
        )
        telemetry.capture(event)
        return self
    
    def record_error(self, error_type: str, error_message: str, component: str):
        """
        Record an error and send telemetry.
        
        Args:
            error_type: Type of the error
            error_message: Error message
            component: Component where the error occurred
            
        Returns:
            Self for method chaining
        """
        self.errors.append(error_message)
        
        # Send error event
        event = ErrorTelemetryEvent(
            error_type=error_type,
            error_message=error_message,
            component=component,
            agent_id=self.agent_id
        )
        telemetry.capture(event)
        return self
    
    def _get_package_version(self) -> str:
        """Get the package version for telemetry."""
        try:
            from airtrain import __version__
            return __version__
        except ImportError:
            return "unknown"
    
    @abstractmethod
    def process(self, user_input: str, memory_name: str = "default") -> str:
        """
        Process user input using a specific memory context.
        
        Args:
            user_input: User input to process
            memory_name: Name of the memory to use for context
            
        Returns:
            Agent's response
        """
        pass


class AgentRegistry:
    """Registry for agent classes."""
    
    @classmethod
    def register(cls, name: Optional[str] = None):
        """
        Decorator to register an agent class.
        
        Args:
            name: Optional name for the agent class
            
        Returns:
            Decorator function
        """
        def decorator(agent_class: Type[BaseAgent]) -> Type[BaseAgent]:
            """
            Register an agent class with the registry.
            
            Args:
                agent_class: Agent class to register
                
            Returns:
                The registered agent class
            """
            # Validate agent class
            if not issubclass(agent_class, BaseAgent):
                raise TypeError(
                    f"Agent class {agent_class.__name__} must inherit from BaseAgent"
                )
            
            # Check for required methods
            has_process = hasattr(agent_class, 'process')
            is_callable = inspect.isfunction(getattr(agent_class, 'process', None))
            if not has_process or not is_callable:
                raise TypeError(
                    f"Agent class {agent_class.__name__} must implement process method"
                )
            
            # Determine agent name
            agent_name = name or agent_class.__name__
            
            # Check for name conflict
            if agent_name in AGENT_REGISTRY:
                raise ValueError(f"Agent '{agent_name}' already registered")
            
            # Register the agent class
            AGENT_REGISTRY[agent_name] = agent_class
            
            # Add metadata to the class
            agent_class.agent_name = agent_name
            
            return agent_class
        
        return decorator
    
    @classmethod
    def get_agent_class(cls, name: str) -> Type[BaseAgent]:
        """
        Get agent class by name.
        
        Args:
            name: Name of the agent class
            
        Returns:
            The agent class
            
        Raises:
            ValueError: If agent not found
        """
        if name not in AGENT_REGISTRY:
            raise ValueError(f"Agent '{name}' not found in registry")
        return AGENT_REGISTRY[name]
    
    @classmethod
    def list_agents(cls) -> List[str]:
        """
        List all registered agents.
        
        Returns:
            List of agent names
        """
        return list(AGENT_REGISTRY.keys())


class AgentFactory:
    """Factory for creating agent instances."""
    
    @staticmethod
    def create_agent(
        agent_type: str, 
        name: Optional[str] = None, 
        models: Optional[List[str]] = None,
        tools: Optional[List[Union[str, BaseTool]]] = None,
        **kwargs
    ) -> BaseAgent:
        """
        Create an agent instance.
        
        Args:
            agent_type: Type of agent to create
            name: Name for the agent instance
            models: List of model identifiers
            tools: List of tools or tool names
            **kwargs: Additional arguments for the agent constructor
            
        Returns:
            Agent instance
        """
        # Get agent class
        agent_class = AgentRegistry.get_agent_class(agent_type)
        
        # Prepare name
        instance_name = name or f"{agent_type}_{id(agent_class)}"
        
        # Prepare tools
        tool_instances = []
        if tools:
            for tool in tools:
                if isinstance(tool, str):
                    # Assume it's a tool name
                    # Try stateless first, then stateful
                    try:
                        tool_instances.append(ToolFactory.get_tool(tool))
                    except ValueError:
                        try:
                            tool_instances.append(
                                ToolFactory.get_tool(tool, "stateful")
                            )
                        except ValueError:
                            raise ValueError(f"Tool '{tool}' not found in registry")
                else:
                    # Assume it's a tool instance
                    tool_instances.append(tool)
        
        # Create agent instance
        return agent_class(
            name=instance_name, 
            models=models, 
            tools=tool_instances, 
            **kwargs
        )
    
    @staticmethod
    def list_available_agents() -> List[str]:
        """
        List all available agent types.
        
        Returns:
            List of agent type names
        """
        return AgentRegistry.list_agents()


# Convenience decorator for registering agents
def register_agent(name: Optional[str] = None):
    """
    Decorator to register an agent class.
    
    Args:
        name: Optional name for the agent class
        
    Returns:
        Decorator function
    """
    return AgentRegistry.register(name) 