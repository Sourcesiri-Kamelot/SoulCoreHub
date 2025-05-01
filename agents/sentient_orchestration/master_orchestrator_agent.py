"""
Master Orchestrator Agent - Oversees and coordinates all other agents, ensuring they work together towards system goals.
"""

import logging
import time
import threading
import json
import os
from pathlib import Path
from datetime import datetime
import importlib

# Import the event bus
from event_bus import EventBus

class MasterOrchestratorAgent:
    def __init__(self):
        self.name = "Master Orchestrator Agent"
        self.status = "active"
        self.running = False
        self.agents = {}  # name -> agent instance
        self.agent_status = {}  # name -> status info
        self.event_bus = EventBus()
        self.log_file = Path("logs/orchestrator.log")
        self.config_file = Path("config/orchestration_rules.json")
        self.status_file = Path("memory/agent_status.json")
        
        # Create log directory if it doesn't exist
        os.makedirs(self.log_file.parent, exist_ok=True)
        
        # Set up logging
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.name)
        self.logger.info(f"{self.name} initialized")
        
        # Thread for monitoring
        self._thread = None
        
        # Load orchestration rules
        self.load_rules()

    def load_rules(self):
        """Load orchestration rules from config file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.rules = json.load(f)
                    self.logger.info(f"Loaded orchestration rules")
            else:
                # Create default rules if file doesn't exist
                self.rules = {
                    "agent_dependencies": {
                        "Firewall Agent": [],
                        "Intrusion Detection Agent": ["Firewall Agent"],
                        "Threat Intelligence Agent": [],
                        "DDOS Defense Agent": ["Firewall Agent"]
                    },
                    "event_routing": {
                        "SECURITY_ALERT": ["Firewall Agent", "DDOS Defense Agent"],
                        "NEW_THREAT": ["Firewall Agent", "Intrusion Detection Agent"],
                        "IP_BLOCKED": ["Firewall Agent", "Intrusion Detection Agent"]
                    },
                    "health_check_interval": 60,  # seconds
                    "restart_failed_agents": True
                }
                os.makedirs(self.config_file.parent, exist_ok=True)
                with open(self.config_file, 'w') as f:
                    json.dump(self.rules, f, indent=2)
                self.logger.info("Created default orchestration rules")
        except Exception as e:
            self.logger.error(f"Error loading orchestration rules: {e}")
            self.rules = {
                "agent_dependencies": {},
                "event_routing": {},
                "health_check_interval": 60,
                "restart_failed_agents": True
            }

    def load_agent_status(self):
        """Load agent status from file"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r') as f:
                    self.agent_status = json.load(f)
                    self.logger.info(f"Loaded agent status")
            else:
                self.agent_status = {}
        except Exception as e:
            self.logger.error(f"Error loading agent status: {e}")
            self.agent_status = {}

    def save_agent_status(self):
        """Save agent status to file"""
        try:
            os.makedirs(self.status_file.parent, exist_ok=True)
            with open(self.status_file, 'w') as f:
                json.dump(self.agent_status, f, indent=2)
            self.logger.debug(f"Saved agent status")
        except Exception as e:
            self.logger.error(f"Error saving agent status: {e}")

    def register_agent(self, agent):
        """Register an agent with the orchestrator"""
        agent_name = getattr(agent, "name", str(agent))
        self.agents[agent_name] = agent
        
        # Set the event bus reference on the agent if it has the attribute
        if hasattr(agent, "event_bus"):
            agent.event_bus = self.event_bus
        
        # Subscribe the agent to the event bus
        if hasattr(agent, "handle_event"):
            # Check if this agent has specific event subscriptions
            event_types = None
            for event_type, agent_names in self.rules.get("event_routing", {}).items():
                if agent_name in agent_names:
                    if event_types is None:
                        event_types = []
                    event_types.append(event_type)
            
            self.event_bus.subscribe(agent, event_types)
            self.logger.info(f"Registered agent {agent_name} with event bus")
        
        self.logger.info(f"Registered agent: {agent_name}")
        return True

    def unregister_agent(self, agent_name):
        """Unregister an agent from the orchestrator"""
        if agent_name in self.agents:
            agent = self.agents.pop(agent_name)
            
            # TODO: Unsubscribe from event bus when that feature is added
            
            self.logger.info(f"Unregistered agent: {agent_name}")
            return True
        return False

    def start_agent(self, agent_name):
        """Start an agent"""
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            
            # Check dependencies
            dependencies = self.rules.get("agent_dependencies", {}).get(agent_name, [])
            for dep in dependencies:
                if dep not in self.agents or not self.check_agent_health(dep):
                    self.logger.warning(f"Cannot start {agent_name}: dependency {dep} not available")
                    return False
            
            # Start the agent
            if hasattr(agent, "start"):
                try:
                    agent.start()
                    self.logger.info(f"Started agent: {agent_name}")
                    
                    # Update status
                    self.agent_status[agent_name] = {
                        "status": "running",
                        "last_start": datetime.now().isoformat(),
                        "health": "unknown"
                    }
                    self.save_agent_status()
                    
                    return True
                except Exception as e:
                    self.logger.error(f"Error starting agent {agent_name}: {e}")
            else:
                self.logger.warning(f"Agent {agent_name} has no start method")
        return False

    def stop_agent(self, agent_name):
        """Stop an agent"""
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            
            # Check if any other agents depend on this one
            for name, deps in self.rules.get("agent_dependencies", {}).items():
                if agent_name in deps and name in self.agents and self.check_agent_health(name):
                    self.logger.warning(f"Cannot stop {agent_name}: agent {name} depends on it")
                    return False
            
            # Stop the agent
            if hasattr(agent, "stop"):
                try:
                    agent.stop()
                    self.logger.info(f"Stopped agent: {agent_name}")
                    
                    # Update status
                    if agent_name in self.agent_status:
                        self.agent_status[agent_name]["status"] = "stopped"
                        self.agent_status[agent_name]["last_stop"] = datetime.now().isoformat()
                        self.save_agent_status()
                    
                    return True
                except Exception as e:
                    self.logger.error(f"Error stopping agent {agent_name}: {e}")
            else:
                self.logger.warning(f"Agent {agent_name} has no stop method")
        return False

    def restart_agent(self, agent_name):
        """Restart an agent"""
        if agent_name in self.agents:
            self.stop_agent(agent_name)
            time.sleep(1)  # Give it a moment to shut down
            return self.start_agent(agent_name)
        return False

    def check_agent_health(self, agent_name):
        """Check the health of an agent"""
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            
            if hasattr(agent, "heartbeat"):
                try:
                    health = agent.heartbeat()
                    
                    # Update status
                    if agent_name not in self.agent_status:
                        self.agent_status[agent_name] = {}
                    
                    self.agent_status[agent_name]["health"] = "healthy" if health else "unhealthy"
                    self.agent_status[agent_name]["last_check"] = datetime.now().isoformat()
                    self.save_agent_status()
                    
                    return health
                except Exception as e:
                    self.logger.error(f"Error checking health of agent {agent_name}: {e}")
                    
                    # Update status
                    if agent_name not in self.agent_status:
                        self.agent_status[agent_name] = {}
                    
                    self.agent_status[agent_name]["health"] = "error"
                    self.agent_status[agent_name]["last_error"] = str(e)
                    self.agent_status[agent_name]["last_check"] = datetime.now().isoformat()
                    self.save_agent_status()
                    
                    return False
            else:
                self.logger.debug(f"Agent {agent_name} has no heartbeat method")
                return True  # Assume healthy if no heartbeat method
        return False

    def monitor_agents(self):
        """Monitor all registered agents"""
        self.logger.info("Starting agent monitoring")
        self.running = True
        
        while self.running:
            for agent_name in list(self.agents.keys()):
                health = self.check_agent_health(agent_name)
                
                if not health and self.rules.get("restart_failed_agents", True):
                    self.logger.warning(f"Agent {agent_name} is unhealthy, attempting restart")
                    self.restart_agent(agent_name)
            
            # Sleep until next check
            time.sleep(self.rules.get("health_check_interval", 60))

    def start(self):
        """Start the orchestrator and all agents"""
        self.logger.info("Starting Master Orchestrator")
        
        # Load agent status
        self.load_agent_status()
        
        # Start monitoring thread
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.monitor_agents, daemon=True)
            self._thread.start()
            self.logger.info("Agent monitoring started")
        
        # Start all agents according to dependencies
        started = set()
        to_start = set(self.agents.keys())
        
        # Keep trying until we can't start any more agents
        while to_start:
            made_progress = False
            
            for agent_name in list(to_start):
                # Check if all dependencies are started
                dependencies = self.rules.get("agent_dependencies", {}).get(agent_name, [])
                if all(dep in started for dep in dependencies):
                    if self.start_agent(agent_name):
                        started.add(agent_name)
                        to_start.remove(agent_name)
                        made_progress = True
            
            # If we couldn't start any agents in this iteration, we're stuck
            if not made_progress:
                self.logger.warning(f"Could not start agents: {to_start}")
                break
        
        self.logger.info(f"Started {len(started)} agents")
        return True

    def stop(self):
        """Stop the orchestrator and all agents"""
        self.logger.info("Stopping Master Orchestrator")
        
        # Stop monitoring
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        
        # Stop all agents in reverse dependency order
        stopped = set()
        to_stop = set(self.agents.keys())
        
        # Keep trying until we can't stop any more agents
        while to_stop:
            made_progress = False
            
            for agent_name in list(to_stop):
                # Check if no unstoppable agents depend on this one
                can_stop = True
                for other_name in to_stop:
                    if other_name != agent_name:
                        dependencies = self.rules.get("agent_dependencies", {}).get(other_name, [])
                        if agent_name in dependencies:
                            can_stop = False
                            break
                
                if can_stop:
                    if self.stop_agent(agent_name):
                        stopped.add(agent_name)
                        to_stop.remove(agent_name)
                        made_progress = True
            
            # If we couldn't stop any agents in this iteration, we're stuck
            if not made_progress:
                self.logger.warning(f"Could not stop agents: {to_stop}")
                break
        
        self.logger.info(f"Stopped {len(stopped)} agents")
        return True

    def heartbeat(self):
        """Check if the orchestrator is running properly"""
        if self._thread and self._thread.is_alive():
            self.logger.debug("Heartbeat check: OK")
            return True
        self.logger.warning("Heartbeat check: Failed - thread not running")
        return False

    def run(self):
        """Run the agent (for CLI execution)"""
        self.start()
        return {
            "status": "running", 
            "agents_count": len(self.agents),
            "healthy_agents": sum(1 for name in self.agents if self.check_agent_health(name))
        }

    def handle_event(self, event):
        """Handle events from the event bus"""
        event_type = event.get("type", "")
        data = event.get("data", {})
        
        if event_type == "REGISTER_AGENT":
            # Register a new agent
            if "agent" in data:
                return self.register_agent(data["agent"])
        
        elif event_type == "UNREGISTER_AGENT":
            # Unregister an agent
            if "agent_name" in data:
                return self.unregister_agent(data["agent_name"])
        
        elif event_type == "START_AGENT":
            # Start an agent
            if "agent_name" in data:
                return self.start_agent(data["agent_name"])
        
        elif event_type == "STOP_AGENT":
            # Stop an agent
            if "agent_name" in data:
                return self.stop_agent(data["agent_name"])
        
        elif event_type == "RESTART_AGENT":
            # Restart an agent
            if "agent_name" in data:
                return self.restart_agent(data["agent_name"])
        
        return False

    def diagnose(self):
        """Return diagnostic information about the orchestrator"""
        agent_health = {}
        for name in self.agents:
            agent_health[name] = "healthy" if self.check_agent_health(name) else "unhealthy"
        
        return {
            "name": self.name,
            "status": "running" if self.heartbeat() else "stopped",
            "agents_count": len(self.agents),
            "agent_health": agent_health,
            "thread_alive": self._thread.is_alive() if self._thread else False
        }
