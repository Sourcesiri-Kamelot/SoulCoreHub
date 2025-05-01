#!/usr/bin/env python3
"""
Manual activation script for SoulCore agents
"""

import sys
import os
import logging
import json
import importlib
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("manual_activation_log.log"),
        logging.StreamHandler()
    ]
)

def update_registry():
    """Update the agent registry with our three target agents"""
    registry_path = "agent_registry_EXEC.json"
    
    try:
        # Create a minimal registry with just our three agents
        registry = {
            "builders": [
                {
                    "name": "Builder Agent",
                    "desc": "Creates and manages code, configurations, and other artifacts based on requests.",
                    "status": "active",
                    "interface": "service",
                    "module": "agents.builders.builder_agent",
                    "class": "BuilderAgent"
                }
            ],
            "predictive": [
                {
                    "name": "Psynet Agent",
                    "desc": "Provides psychic-level predictive visualization and future scenario modeling",
                    "status": "active",
                    "interface": "service",
                    "module": "agents.predictive.psynet_agent",
                    "class": "PsynetAgent"
                }
            ],
            "sentient_orchestration": [
                {
                    "name": "AI Society Psynet Bridge",
                    "desc": "Connects AI Society framework with Psynet predictive visualization",
                    "status": "active",
                    "interface": "service",
                    "module": "agents.sentient_orchestration.ai_society_psynet_bridge",
                    "class": "AISocietyPsynetBridge"
                }
            ]
        }
        
        # Save the registry
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
        
        logging.info(f"Updated agent registry at {registry_path}")
        return True
    except Exception as e:
        logging.error(f"Error updating agent registry: {e}")
        return False

def create_gptsoul():
    """Create GPTSoul agent file"""
    gptsoul_path = Path("agents/sentient_orchestration/gptsoul_agent.py")
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(gptsoul_path.parent, exist_ok=True)
        
        # Create GPTSoul agent file
        gptsoul_code = """#!/usr/bin/env python3
\"\"\"
GPTSoul Agent - Logic, Design, and Neural Scripting
\"\"\"

import os
import sys
import json
import logging
from datetime import datetime

class GPTSoulAgent:
    \"\"\"Logic, Design, and Neural Scripting agent that lays the foundation for clean, reactive, and self-auditing calls\"\"\"
    
    def __init__(self):
        self.name = "GPTSoul"
        self.status = "active"
        self.description = "Logic, Design, and Neural Scripting agent that lays the foundation for clean, reactive, and self-auditing calls"
        self.last_heartbeat = datetime.now()
        self.config = self._load_config()
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.name)
        self.logger.info(f"{self.name} initialized")
    
    def _load_config(self):
        \"\"\"Load configuration from file\"\"\"
        config_path = os.path.join("config", "gptsoul_config.json")
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
            else:
                # Create default config
                default_config = {
                    "reasoning_depth": 5,
                    "memory_retention": 0.85,
                    "creativity_factor": 0.7,
                    "logic_weight": 0.9
                }
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception as e:
            print(f"Error loading GPTSoul config: {e}")
            return {}
    
    def heartbeat(self):
        \"\"\"Return agent health status\"\"\"
        self.last_heartbeat = datetime.now()
        return {
            "status": self.status,
            "last_heartbeat": self.last_heartbeat
        }
    
    def run(self):
        \"\"\"Main agent execution loop\"\"\"
        self.logger.info(f"{self.name} running")
        
        # Process any pending tasks
        self._process_tasks()
        
        return {"status": "success", "message": f"{self.name} cycle complete"}
    
    def handle_event(self, event):
        \"\"\"Handle events from the event bus\"\"\"
        event_type = event.get("type", "")
        data = event.get("data", {})
        
        if event_type == "logic_request":
            return self._handle_logic_request(event)
        elif event_type == "design_request":
            return self._handle_design_request(event)
        elif event_type == "script_request":
            return self._handle_script_request(event)
        
        return False  # Event not handled
    
    def _process_tasks(self):
        \"\"\"Process any pending tasks\"\"\"
        # Implementation would process tasks
        pass
    
    def _handle_logic_request(self, event):
        \"\"\"Handle a logic request event\"\"\"
        self.logger.info(f"Handling logic request from {event.get('requester', 'unknown')}")
        
        # Implementation would process logic request
        
        return True  # Event handled
    
    def _handle_design_request(self, event):
        \"\"\"Handle a design request event\"\"\"
        self.logger.info(f"Handling design request from {event.get('requester', 'unknown')}")
        
        # Implementation would process design request
        
        return True  # Event handled
    
    def _handle_script_request(self, event):
        \"\"\"Handle a script request event\"\"\"
        self.logger.info(f"Handling script request from {event.get('requester', 'unknown')}")
        
        # Implementation would process script request
        
        return True  # Event handled

# For testing
if __name__ == "__main__":
    agent = GPTSoulAgent()
    print(f"{agent.name} initialized in standalone mode")
    
    # Test heartbeat
    print(f"Heartbeat: {agent.heartbeat()}")
    
    # Test run
    result = agent.run()
    print(f"Run result: {result}")
"""
        
        with open(gptsoul_path, 'w') as f:
            f.write(gptsoul_code)
        
        # Make the file executable
        os.chmod(gptsoul_path, 0o755)
        
        logging.info(f"Created GPTSoul agent at {gptsoul_path}")
        
        # Update the registry to include GPTSoul
        registry_path = "agent_registry_EXEC.json"
        if os.path.exists(registry_path):
            with open(registry_path, 'r') as f:
                registry = json.load(f)
            
            # Add GPTSoul to sentient_orchestration if not already there
            gptsoul_exists = False
            if "sentient_orchestration" in registry:
                for agent in registry["sentient_orchestration"]:
                    if agent.get("name") == "GPTSoul":
                        gptsoul_exists = True
                        break
            else:
                registry["sentient_orchestration"] = []
            
            if not gptsoul_exists:
                registry["sentient_orchestration"].append({
                    "name": "GPTSoul",
                    "desc": "Logic, Design, and Neural Scripting agent that lays the foundation for clean, reactive, and self-auditing calls",
                    "status": "active",
                    "interface": "service",
                    "module": "agents.sentient_orchestration.gptsoul_agent",
                    "class": "GPTSoulAgent"
                })
                
                with open(registry_path, 'w') as f:
                    json.dump(registry, f, indent=2)
                
                logging.info(f"Added GPTSoul to registry at {registry_path}")
        
        return True
    except Exception as e:
        logging.error(f"Error creating GPTSoul agent: {e}")
        return False

def manually_load_agent(module_name, class_name):
    """Manually load an agent by module and class name"""
    try:
        module = importlib.import_module(module_name)
        AgentClass = getattr(module, class_name)
        agent = AgentClass()
        return agent
    except Exception as e:
        logging.error(f"Error loading agent from {module_name}.{class_name}: {e}")
        return None

def main():
    """Main function to manually activate agents"""
    try:
        # Update the registry
        update_registry()
        
        # Create GPTSoul agent
        create_gptsoul()
        
        # Manually load and run each agent
        agents = [
            ("agents.builders.builder_agent", "BuilderAgent"),
            ("agents.predictive.psynet_agent", "PsynetAgent"),
            ("agents.sentient_orchestration.ai_society_psynet_bridge", "AISocietyPsynetBridge"),
            ("agents.sentient_orchestration.gptsoul_agent", "GPTSoulAgent")
        ]
        
        activated_agents = {}
        
        for module_name, class_name in agents:
            logging.info(f"Loading agent from {module_name}.{class_name}...")
            agent = manually_load_agent(module_name, class_name)
            
            if agent:
                logging.info(f"Successfully loaded {agent.name}")
                
                # Run the agent
                try:
                    if hasattr(agent, "run"):
                        result = agent.run()
                        logging.info(f"{agent.name} run result: {result}")
                    
                    # Start the agent if it's a service
                    if hasattr(agent, "start"):
                        agent.start()
                        logging.info(f"Started {agent.name} service")
                    
                    activated_agents[agent.name] = agent
                except Exception as e:
                    logging.error(f"Error running {agent.name}: {e}")
            else:
                logging.error(f"Failed to load agent from {module_name}.{class_name}")
        
        logging.info(f"Successfully activated {len(activated_agents)} agents")
        
        # Return the activated agents
        return activated_agents
    
    except Exception as e:
        logging.error(f"Error in manual activation: {e}")
        return {}

if __name__ == "__main__":
    activated_agents = main()
    print(f"Activated agents: {', '.join(activated_agents.keys())}")
