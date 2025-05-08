#!/usr/bin/env python3
"""
Registry Validator - Validates and consolidates agent registry files
"""

import os
import json
import importlib
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("registry_validator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RegistryValidator")

class RegistryValidator:
    """Validates and consolidates agent registry files"""
    
    def __init__(self):
        """Initialize the registry validator"""
        self.registry_files = [
            "agent_registry.json",
            "config/agent_registry2.json",
            "config/agent_registry_EXEC2.json"
        ]
        self.output_file = "config/agent_registry_combined.json"
        self.valid_agents = {}
        self.invalid_agents = {}
    
    def validate_registry(self):
        """Validate all registry files and consolidate them"""
        # Process each registry file
        for registry_file in self.registry_files:
            self.process_registry_file(registry_file)
        
        # Save the consolidated registry
        self.save_consolidated_registry()
        
        # Print summary
        self.print_summary()
        
        return len(self.valid_agents), len(self.invalid_agents)
    
    def process_registry_file(self, registry_file):
        """Process a single registry file"""
        if not os.path.exists(registry_file):
            logger.warning(f"Registry file not found: {registry_file}")
            return
        
        try:
            with open(registry_file, 'r') as f:
                data = json.load(f)
            
            logger.info(f"Processing registry file: {registry_file}")
            
            # Process each category and agent
            for category, agents in data.items():
                if category not in self.valid_agents:
                    self.valid_agents[category] = []
                
                if category not in self.invalid_agents:
                    self.invalid_agents[category] = []
                
                for agent in agents:
                    # Validate the agent
                    if self.validate_agent(agent):
                        self.valid_agents[category].append(agent)
                        logger.info(f"Valid agent: {agent.get('name', 'Unknown')}")
                    else:
                        self.invalid_agents[category].append(agent)
                        logger.warning(f"Invalid agent: {agent.get('name', 'Unknown')}")
        
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in registry file: {registry_file}")
        except Exception as e:
            logger.error(f"Error processing registry file {registry_file}: {e}")
    
    def validate_agent(self, agent):
        """Validate a single agent"""
        # Check required fields
        required_fields = ["name", "module", "class", "status"]
        for field in required_fields:
            if field not in agent:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Check if the agent is active
        if agent["status"] != "active":
            logger.info(f"Agent {agent['name']} is not active")
            return True  # Still valid, just not active
        
        # Check if the module exists
        try:
            module_name = agent["module"]
            class_name = agent["class"]
            
            # Try to import the module
            try:
                module = importlib.import_module(module_name)
            except ModuleNotFoundError:
                logger.warning(f"Module not found: {module_name}")
                return False
            
            # Check if the class exists in the module
            if not hasattr(module, class_name):
                logger.warning(f"Class {class_name} not found in module {module_name}")
                return False
            
            # All checks passed
            return True
        
        except Exception as e:
            logger.error(f"Error validating agent {agent.get('name', 'Unknown')}: {e}")
            return False
    
    def save_consolidated_registry(self):
        """Save the consolidated registry"""
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        # Save the consolidated registry
        try:
            with open(self.output_file, 'w') as f:
                json.dump(self.valid_agents, f, indent=2)
            
            logger.info(f"Saved consolidated registry to {self.output_file}")
        except Exception as e:
            logger.error(f"Error saving consolidated registry: {e}")
    
    def print_summary(self):
        """Print a summary of the validation results"""
        valid_count = sum(len(agents) for agents in self.valid_agents.values())
        invalid_count = sum(len(agents) for agents in self.invalid_agents.values())
        
        print("\n=== Registry Validation Summary ===")
        print(f"Valid agents: {valid_count}")
        print(f"Invalid agents: {invalid_count}")
        print(f"Consolidated registry saved to: {self.output_file}")
        
        if invalid_count > 0:
            print("\nInvalid agents:")
            for category, agents in self.invalid_agents.items():
                if agents:
                    print(f"\n[{category}]")
                    for agent in agents:
                        print(f"  • {agent.get('name', 'Unknown')}: {agent.get('module', 'Unknown')}.{agent.get('class', 'Unknown')}")

if __name__ == "__main__":
    validator = RegistryValidator()
    validator.validate_registry()
