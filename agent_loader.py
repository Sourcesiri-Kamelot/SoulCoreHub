#!/usr/bin/env python3
"""
Agent Loader for SoulCoreHub
Loads and initializes agents from the agent registry
"""

import os
import json
import importlib
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent_loader.log')
    ]
)
logger = logging.getLogger("AgentLoader")

# Default paths
DEFAULT_REGISTRY_PATH = Path("agent_registry_core.json")
FALLBACK_REGISTRY_PATH = Path("core_agents.json")

def load_registry(registry_path=None):
    """
    Load the agent registry from a JSON file
    
    Args:
        registry_path: Path to the registry file (optional)
        
    Returns:
        dict: The agent registry data
    """
    if registry_path is None:
        # Try default path first
        if DEFAULT_REGISTRY_PATH.exists():
            registry_path = DEFAULT_REGISTRY_PATH
        # Fall back to alternative if needed
        elif FALLBACK_REGISTRY_PATH.exists():
            registry_path = FALLBACK_REGISTRY_PATH
        else:
            logger.error("No agent registry file found")
            return None
    
    try:
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        logger.info(f"Loaded agent registry from {registry_path}")
        return registry
    except Exception as e:
        logger.error(f"Failed to load agent registry: {e}")
        return None

def load_agent_by_name(agent_name, registry_path=None):
    """
    Load a specific agent by name
    
    Args:
        agent_name: Name of the agent to load
        registry_path: Path to the registry file (optional)
        
    Returns:
        object: The agent instance or None if not found
    """
    registry = load_registry(registry_path)
    if not registry:
        return None
    
    # Search for the agent in all categories
    agent_data = None
    for category, agents in registry.items():
        for agent in agents:
            if agent.get("name") == agent_name:
                agent_data = agent
                break
        if agent_data:
            break
    
    if not agent_data:
        logger.error(f"Agent '{agent_name}' not found in registry")
        return None
    
    return load_agent_from_data(agent_data)

def load_agent_from_data(agent_data):
    """
    Load an agent from its registry data
    
    Args:
        agent_data: Dictionary containing agent configuration
        
    Returns:
        object: The agent instance or None if loading fails
    """
    if agent_data.get("status") != "active":
        logger.info(f"Agent '{agent_data.get('name')}' is not active, skipping")
        return None
    
    try:
        module_name = agent_data.get("module")
        class_name = agent_data.get("class")
        
        # Try to import the module
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            logger.warning(f"Module '{module_name}' not found, creating placeholder")
            return create_placeholder_agent(agent_data)
        
        # Try to get the class
        try:
            agent_class = getattr(module, class_name)
        except AttributeError:
            logger.warning(f"Class '{class_name}' not found in module '{module_name}', creating placeholder")
            return create_placeholder_agent(agent_data)
        
        # Create an instance of the agent
        agent = agent_class()
        logger.info(f"Successfully loaded agent '{agent_data.get('name')}'")
        return agent
    
    except Exception as e:
        logger.error(f"Failed to load agent '{agent_data.get('name')}': {e}")
        return create_placeholder_agent(agent_data)

def create_placeholder_agent(agent_data):
    """
    Create a placeholder agent when the actual agent cannot be loaded
    
    Args:
        agent_data: Dictionary containing agent configuration
        
    Returns:
        object: A placeholder agent
    """
    class PlaceholderAgent:
        def __init__(self, data):
            self.name = data.get("name")
            self.description = data.get("desc")
            self.is_placeholder = True
        
        def __str__(self):
            return f"PlaceholderAgent({self.name})"
    
    logger.info(f"Created placeholder for agent '{agent_data.get('name')}'")
    return PlaceholderAgent(agent_data)

def load_all_agents(registry_path=None, category=None):
    """
    Load all active agents from the registry
    
    Args:
        registry_path: Path to the registry file (optional)
        category: Only load agents from this category (optional)
        
    Returns:
        list: List of agent instances
    """
    registry = load_registry(registry_path)
    if not registry:
        return []
    
    agents = []
    
    # Process each category in the registry
    for cat, agent_list in registry.items():
        # Skip if a specific category was requested and this isn't it
        if category and cat != category:
            continue
        
        # Load each agent in the category
        for agent_data in agent_list:
            if agent_data.get("status") == "active":
                agent = load_agent_from_data(agent_data)
                if agent:
                    agents.append(agent)
    
    logger.info(f"Loaded {len(agents)} agents")
    return agents

def init_registry(output_path=None):
    """
    Initialize a new agent registry with default values
    
    Args:
        output_path: Path to save the new registry (optional)
        
    Returns:
        bool: True if successful, False otherwise
    """
    if output_path is None:
        output_path = DEFAULT_REGISTRY_PATH
    
    # Check if file already exists
    if os.path.exists(output_path):
        logger.warning(f"Registry file already exists at {output_path}")
        return False
    
    # Create a basic registry structure
    registry = {
        "core": [
            {
                "name": "GPTSoul",
                "desc": "Guardian, Architect, and Executor of the SoulCoreHub system",
                "status": "active",
                "priority": "high",
                "interface": "service",
                "module": "agents.core.gptsoul_agent",
                "class": "GPTSoulAgent"
            },
            {
                "name": "Anima",
                "desc": "Emotional Core and Reflection system",
                "status": "active",
                "priority": "medium",
                "interface": "interactive",
                "module": "agents.core.anima_agent",
                "class": "AnimaAgent"
            }
        ],
        "utility": [
            {
                "name": "Builder",
                "desc": "Project creation and code generation",
                "status": "active",
                "priority": "medium",
                "interface": "interactive",
                "module": "agents.utility.builder_agent",
                "class": "BuilderAgent"
            }
        ]
    }
    
    try:
        with open(output_path, 'w') as f:
            json.dump(registry, f, indent=2)
        logger.info(f"Created new agent registry at {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create agent registry: {e}")
        return False

if __name__ == "__main__":
    # Simple CLI for testing
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            registry = load_registry()
            if registry:
                print("Available agents:")
                for category, agents in registry.items():
                    print(f"\n{category.upper()}:")
                    for agent in agents:
                        status = "✅" if agent.get("status") == "active" else "❌"
                        print(f"  {status} {agent.get('name')} - {agent.get('desc')}")
        
        elif command == "load" and len(sys.argv) > 2:
            agent_name = sys.argv[2]
            agent = load_agent_by_name(agent_name)
            if agent:
                print(f"Loaded agent: {agent}")
            else:
                print(f"Failed to load agent: {agent_name}")
        
        elif command == "init":
            output_path = sys.argv[2] if len(sys.argv) > 2 else None
            success = init_registry(output_path)
            if success:
                print("Registry initialized successfully")
            else:
                print("Failed to initialize registry")
        
        else:
            print("Unknown command")
    else:
        print("Usage:")
        print("  python agent_loader.py list")
        print("  python agent_loader.py load <agent_name>")
        print("  python agent_loader.py init [output_path]")
