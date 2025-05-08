#!/usr/bin/env python3
"""
Agent Selector - Interactive tool to load and select agents from SoulCoreHub
"""

import os
import sys
import json
import importlib
import logging
from agent_loader import load_all_agents, load_agent_by_name
from agents.sentient_orchestration.master_orchestrator_agent import MasterOrchestratorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="soulcorehub.log",
    filemode="a"
)
logger = logging.getLogger("AgentSelector")

class AgentSelector:
    """Interactive agent selector for SoulCoreHub"""
    
    def __init__(self):
        """Initialize the agent selector"""
        self.master_orch = MasterOrchestratorAgent()
        self.registry_files = [
            "agent_registry.json",
            "config/agent_registry2.json",
            "config/agent_registry_EXEC2.json"
        ]
        self.loaded_agents = {}
        self.active_agent = None
        self.nlp_processor = None
        
        # Try to load NLP processor if available
        try:
            from agents.nlp.intent_processor import IntentProcessor
            self.nlp_processor = IntentProcessor()
            logger.info("NLP processor loaded successfully")
        except ImportError:
            logger.warning("NLP processor not available")
    
    def load_all_registry_agents(self):
        """Load all agents from all registry files"""
        total_loaded = 0
        
        for registry_file in self.registry_files:
            if not os.path.exists(registry_file):
                logger.warning(f"Registry file not found: {registry_file}")
                continue
                
            try:
                with open(registry_file, "r") as f:
                    data = json.load(f)
                
                for category, agents in data.items():
                    for agent_info in agents:
                        if agent_info.get("status") != "active":
                            continue
                            
                        try:
                            name = agent_info.get("name", "Unknown")
                            module_path = agent_info["module"]
                            class_name = agent_info["class"]
                            
                            # Try to import the module
                            try:
                                module = importlib.import_module(module_path)
                            except ModuleNotFoundError:
                                logger.warning(f"Module not found: {module_path}")
                                continue
                            
                            # Get the agent class
                            if not hasattr(module, class_name):
                                logger.warning(f"Class {class_name} not found in module {module_path}")
                                continue
                                
                            agent_class = getattr(module, class_name)
                            
                            # Instantiate the agent
                            agent = agent_class()
                            
                            # Add heartbeat method if missing
                            if not hasattr(agent, "heartbeat"):
                                agent.heartbeat = lambda: True
                            
                            # Register with orchestrator
                            self.master_orch.register_agent(agent)
                            
                            # Add to our local dictionary
                            agent_name = getattr(agent, "name", name)
                            self.loaded_agents[agent_name] = {
                                "agent": agent,
                                "category": category,
                                "description": agent_info.get("desc", "No description available")
                            }
                            
                            logger.info(f"Loaded agent: {agent_name}")
                            total_loaded += 1
                            
                        except Exception as e:
                            logger.error(f"Error loading agent {agent_info.get('name', '?')}: {e}")
            
            except Exception as e:
                logger.error(f"Error loading registry {registry_file}: {e}")
        
        # Add Builder Agent if not already loaded
        if "Builder Agent" not in self.loaded_agents:
            try:
                from agents.builder_agent import BuilderAgent
                builder = BuilderAgent()
                self.master_orch.register_agent(builder)
                self.loaded_agents["Builder Agent"] = {
                    "agent": builder,
                    "category": "builders",
                    "description": "Creates and manages code, configurations, and other artifacts based on requests."
                }
                logger.info("Created default Builder Agent")
                total_loaded += 1
            except Exception as e:
                logger.error(f"Could not create default Builder Agent: {e}")
        
        logger.info(f"Total agents loaded: {total_loaded}")
        return total_loaded
    
    def display_agents(self):
        """Display all loaded agents grouped by category"""
        if not self.loaded_agents:
            print("No agents loaded. Use 'load' command to load agents.")
            return
        
        # Group agents by category
        categories = {}
        for name, info in self.loaded_agents.items():
            category = info["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append((name, info["description"]))
        
        # Display agents by category
        print("\n=== Available Agents ===")
        for category, agents in categories.items():
            print(f"\n[{category.upper()}]")
            for i, (name, desc) in enumerate(agents, 1):
                active = " (ACTIVE)" if self.active_agent and self.active_agent.name == name else ""
                print(f"  {i}. {name}{active}: {desc}")
        
        print("\nUse 'select <agent_name>' to choose an agent.")
    
    def select_agent(self, name):
        """Select an agent by name"""
        if not name:
            print("Please specify an agent name.")
            return False
        
        # Check if the agent exists
        if name not in self.loaded_agents:
            print(f"Agent '{name}' not found.")
            return False
        
        # Set the active agent
        self.active_agent = self.loaded_agents[name]["agent"]
        print(f"Selected agent: {name}")
        return True
    
    def process_command(self, command):
        """Process a command"""
        if not command:
            return True
        
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd == "exit" or cmd == "quit":
            return False
        
        elif cmd == "load":
            self.load_all_registry_agents()
            self.display_agents()
        
        elif cmd == "list":
            self.display_agents()
        
        elif cmd == "select":
            self.select_agent(args)
        
        elif cmd == "help":
            self.show_help()
        
        elif cmd == "status":
            self.show_status()
        
        elif self.active_agent:
            # Send the command to the active agent
            if hasattr(self.active_agent, "handle_input"):
                try:
                    response = self.active_agent.handle_input(command)
                    print(f"\n{response}\n")
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print(f"Agent '{self.active_agent.name}' cannot process commands.")
        
        else:
            # Try to interpret the command as a build request
            if "build" in cmd.lower() or "create" in cmd.lower() or "app" in cmd.lower() or "project" in cmd.lower():
                if "Builder Agent" in self.loaded_agents:
                    builder = self.loaded_agents["Builder Agent"]["agent"]
                    response = builder.handle_input(command)
                    print(f"\n{response}\n")
                else:
                    print("Builder Agent not loaded. Use 'load' command to load agents.")
            else:
                print("No agent selected. Use 'select <agent_name>' to choose an agent.")
        
        return True
    
    def show_help(self):
        """Show help information"""
        print("\n=== Agent Selector Help ===")
        print("  load              - Load all agents from registry files")
        print("  list              - List all loaded agents")
        print("  select <name>     - Select an agent by name")
        print("  status            - Show system status")
        print("  help              - Show this help message")
        print("  exit/quit         - Exit the program")
        print("\nWhen an agent is selected, all commands are sent to that agent.")
        print("You can also use build/create commands directly to interact with the Builder Agent.")
    
    def show_status(self):
        """Show system status"""
        print("\n=== System Status ===")
        print(f"Loaded agents: {len(self.loaded_agents)}")
        print(f"Active agent: {self.active_agent.name if self.active_agent else 'None'}")
        print(f"NLP processor: {'Available' if self.nlp_processor else 'Not available'}")
        
        # Show orchestrator status
        if hasattr(self.master_orch, "diagnose"):
            status = self.master_orch.diagnose()
            print(f"Orchestrator status: {status['status']}")
            print(f"Orchestrator thread alive: {status['thread_alive']}")
    
    def run(self):
        """Run the agent selector"""
        print("=== SoulCoreHub Agent Selector ===")
        print("Type 'help' for available commands.")
        
        # Load agents
        self.load_all_registry_agents()
        self.display_agents()
        
        # Start the orchestrator
        self.master_orch.start()
        
        # Main loop
        running = True
        while running:
            try:
                prompt = input("\n🧠 AGENT> " if not self.active_agent else f"\n🧠 {self.active_agent.name}> ")
                running = self.process_command(prompt)
            except KeyboardInterrupt:
                print("\nExiting...")
                running = False
            except Exception as e:
                print(f"Error: {e}")
        
        # Stop the orchestrator
        self.master_orch.stop()

if __name__ == "__main__":
    selector = AgentSelector()
    selector.run()
