#!/usr/bin/env python3
"""
GPTSoul Agent
Guardian, Architect, and Executor of the SoulCoreHub system
"""

import os
import json
import logging
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('gptsoul.log')
    ]
)
logger = logging.getLogger("GPTSoul")

class GPTSoulAgent:
    """
    GPTSoul Agent - Guardian, Architect, and Executor of the SoulCoreHub system
    """
    
    def __init__(self):
        """Initialize the GPTSoul agent"""
        self.name = "GPTSoul"
        self.description = "Guardian, Architect, and Executor of the SoulCoreHub system"
        self.memory_path = Path("memory/gptsoul_memory.json")
        self.memory = self._load_memory()
        self.is_placeholder = False
        logger.info("GPTSoul Agent initialized")
    
    def _load_memory(self):
        """Load memory from file"""
        if not self.memory_path.exists():
            # Create memory directory if it doesn't exist
            self.memory_path.parent.mkdir(exist_ok=True)
            
            # Initialize with default memory
            default_memory = {
                "system_state": "initializing",
                "active_agents": [],
                "last_activation": time.time(),
                "system_goals": [
                    "Maintain system integrity",
                    "Coordinate agent activities",
                    "Ensure user safety and privacy",
                    "Facilitate system evolution"
                ],
                "events": []
            }
            
            # Save default memory
            with open(self.memory_path, 'w') as f:
                json.dump(default_memory, f, indent=2)
            
            return default_memory
        
        try:
            with open(self.memory_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load memory: {e}")
            return {
                "system_state": "recovery",
                "active_agents": [],
                "last_activation": time.time(),
                "events": [{"type": "error", "message": f"Memory corruption: {e}"}]
            }
    
    def _save_memory(self):
        """Save memory to file"""
        try:
            with open(self.memory_path, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
    
    def activate(self):
        """Activate the GPTSoul agent"""
        logger.info("Activating GPTSoul")
        self.memory["system_state"] = "active"
        self.memory["last_activation"] = time.time()
        self.memory["events"].append({
            "type": "activation",
            "timestamp": time.time(),
            "message": "GPTSoul activated"
        })
        self._save_memory()
        return True
    
    def deactivate(self):
        """Deactivate the GPTSoul agent"""
        logger.info("Deactivating GPTSoul")
        self.memory["system_state"] = "inactive"
        self.memory["events"].append({
            "type": "deactivation",
            "timestamp": time.time(),
            "message": "GPTSoul deactivated"
        })
        self._save_memory()
        return True
    
    def register_agent(self, agent):
        """Register an agent with GPTSoul"""
        logger.info(f"Registering agent: {agent.name}")
        if agent.name not in [a.get("name") for a in self.memory["active_agents"]]:
            self.memory["active_agents"].append({
                "name": agent.name,
                "registration_time": time.time()
            })
            self.memory["events"].append({
                "type": "agent_registration",
                "timestamp": time.time(),
                "message": f"Agent registered: {agent.name}"
            })
            self._save_memory()
        return True
    
    def unregister_agent(self, agent_name):
        """Unregister an agent from GPTSoul"""
        logger.info(f"Unregistering agent: {agent_name}")
        self.memory["active_agents"] = [
            a for a in self.memory["active_agents"] 
            if a.get("name") != agent_name
        ]
        self.memory["events"].append({
            "type": "agent_unregistration",
            "timestamp": time.time(),
            "message": f"Agent unregistered: {agent_name}"
        })
        self._save_memory()
        return True
    
    def get_system_state(self):
        """Get the current system state"""
        return {
            "state": self.memory["system_state"],
            "active_agents": len(self.memory["active_agents"]),
            "last_activation": self.memory["last_activation"],
            "uptime": time.time() - self.memory["last_activation"]
        }
    
    def log_event(self, event_type, message):
        """Log an event to GPTSoul's memory"""
        logger.info(f"Event: {event_type} - {message}")
        self.memory["events"].append({
            "type": event_type,
            "timestamp": time.time(),
            "message": message
        })
        # Keep only the last 100 events
        if len(self.memory["events"]) > 100:
            self.memory["events"] = self.memory["events"][-100:]
        self._save_memory()
        return True
    
    def get_recent_events(self, count=10):
        """Get recent events from memory"""
        return self.memory["events"][-count:]
    
    def __str__(self):
        """String representation of the agent"""
        return f"GPTSoul(state={self.memory['system_state']})"

if __name__ == "__main__":
    # Simple CLI for testing
    gptsoul = GPTSoulAgent()
    gptsoul.activate()
    
    print(f"GPTSoul Agent: {gptsoul}")
    print(f"System State: {gptsoul.get_system_state()}")
    
    # Log a test event
    gptsoul.log_event("test", "GPTSoul agent test")
    
    # Show recent events
    print("\nRecent Events:")
    for event in gptsoul.get_recent_events():
        print(f"  {event['type']}: {event['message']}")
