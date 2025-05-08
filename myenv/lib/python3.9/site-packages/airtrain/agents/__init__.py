"""
Agents package for AirTrain.

This package provides a registry of agents that can be used to build AI systems.
"""

# Import registry components
from .registry import (
    BaseAgent,
    AgentFactory,
    register_agent,
    AgentRegistry
)

# Import memory components
from .memory import (
    BaseMemory,
    ShortTermMemory,
    LongTermMemory,
    SharedMemory,
    AgentMemoryManager
)

# Import agent implementations
from .groq_agent import GroqAgent

__all__ = [
    # Base classes
    "BaseAgent",
    
    # Registry components
    "AgentFactory",
    "register_agent",
    "AgentRegistry",
    
    # Memory components
    "BaseMemory",
    "ShortTermMemory",
    "LongTermMemory",
    "SharedMemory",
    "AgentMemoryManager",
    
    # Agent implementations
    "GroqAgent",
] 