
import os
import json
import time
import threading
import logging
from datetime import datetime

class MasterOrchestratorAgent:
    def __init__(self, name="Master Orchestrator Agent", config_file="config/orchestration_rules.json", status_file="config/agent_status.json"):
        self.name = name
        self.agents = {}
        self.running = False
        self._thread = None
        self.logger = logging.getLogger(self.name)
        self.config_file = config_file
        self.status_file = status_file
        self.agent_status = {}
        self.rules = {}

        self.load_rules()
        self.load_agent_status()

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self.monitor_agents, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join()

    def heartbeat(self):
        return self.running

    def infer(self, prompt):
        self.logger.info(f"Infer received: {prompt}")
        prompt_lower = prompt.lower().strip()

        if prompt_lower == "status":
            return self.diagnose()
        elif prompt_lower == "list agents":
            return self.list_agents()
        elif prompt_lower.startswith("run "):
            agent_name = prompt[4:].strip()
            return self.route_to_agent(agent_name, "Run")
        elif "build" in prompt_lower or "app" in prompt_lower:
            return self.route_to_agent("Builder Agent", prompt)

        self.logger.warning(f"Unhandled prompt: {prompt}")
        return f"🤖 I heard: '{prompt}', but I don’t yet know how to handle that."

    def handle_input(self, prompt):
        return self.infer(prompt)

    def route_to_agent(self, agent_name, message):
        agent = self.agents.get(agent_name)
        if not agent:
            return f"❌ Agent '{agent_name}' not found."

        if hasattr(agent, "handle_input"):
            try:
                response = agent.handle_input(message)
                return f"✅ Response from {agent_name}: {response}"
            except Exception as e:
                return f"⚠️ Error while communicating with '{agent_name}': {str(e)}"
        return f"❌ Agent '{agent_name}' cannot process messages."

    def diagnose(self):
        agent_health = {
            name: "healthy" if self.check_agent_health(name) else "unhealthy"
            for name in self.agents
        }
        return {
            "name": self.name,
            "status": "running" if self.heartbeat() else "stopped",
            "agents_count": len(self.agents),
            "agent_health": agent_health,
            "thread_alive": self._thread.is_alive() if self._thread else False
        }

    def list_agents(self):
        if not self.agents:
            return "⚠️ No agents are currently loaded."
        return "🤖 Registered agents:\n" + "\n".join(f"• {name}" for name in self.agents)

    def load_rules(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.rules = json.load(f)
                    self.logger.info("Loaded orchestration rules")
            else:
                self.rules = {
                    "agent_dependencies": {},
                    "event_routing": {},
                    "health_check_interval": 60,
                    "restart_failed_agents": True
                }
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                with open(self.config_file, 'w') as f:
                    json.dump(self.rules, f, indent=2)
                self.logger.info("Created default orchestration rules")
        except Exception as e:
            self.logger.error(f"Error loading orchestration rules: {e}")
            self.rules = {}

    def save_agent_status(self):
        try:
            os.makedirs(os.path.dirname(self.status_file), exist_ok=True)
            with open(self.status_file, 'w') as f:
                json.dump(self.agent_status, f, indent=2)
            self.logger.debug("Saved agent status")
        except Exception as e:
            self.logger.error(f"Error saving agent status: {e}")

    def load_agent_status(self):
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r') as f:
                    self.agent_status = json.load(f)
                    self.logger.info("Loaded agent status")
            else:
                self.agent_status = {}
        except Exception as e:
            self.logger.error(f"Error loading agent status: {e}")
            self.agent_status = {}

    def register_agent(self, agent):
        agent_name = getattr(agent, "name", str(agent))
        self.agents[agent_name] = agent

    def stop_agent(self, agent_name):
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            for name, deps in self.rules.get("agent_dependencies", {}).items():
                if agent_name in deps and name in self.agents and self.check_agent_health(name):
                    self.logger.warning(f"Cannot stop {agent_name}: agent {name} depends on it")
                    return False

            if hasattr(agent, "stop"):
                try:
                    agent.stop()
                    self.logger.info(f"Stopped agent: {agent_name}")
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

    def start_agent(self, agent_name):
        self.logger.warning(f"Start logic not implemented for {agent_name}")
        return False

    def restart_agent(self, agent_name):
        if agent_name in self.agents:
            self.stop_agent(agent_name)
            time.sleep(1)
            return self.start_agent(agent_name)
        return False

    def check_agent_health(self, agent_name):
        if agent_name not in self.agents:
            return False

        agent = self.agents[agent_name]
        if hasattr(agent, "heartbeat"):
            try:
                health = agent.heartbeat()
                if agent_name not in self.agent_status:
                    self.agent_status[agent_name] = {}
                self.agent_status[agent_name]["health"] = "healthy" if health else "unhealthy"
                self.agent_status[agent_name]["last_check"] = datetime.now().isoformat()
                self.save_agent_status()
                return health
            except Exception as e:
                self.logger.error(f"Error checking health of agent {agent_name}: {e}")
                if agent_name not in self.agent_status:
                    self.agent_status[agent_name] = {}
                self.agent_status[agent_name]["health"] = "error"
                self.agent_status[agent_name]["last_check"] = datetime.now().isoformat()
                self.save_agent_status()
                return False
        else:
            self.logger.warning(f"Agent '{agent_name}' does not implement a heartbeat() method.")
            return False

    def monitor_agents(self):
        while self.running:
            for agent_name in list(self.agents.keys()):
                if agent_name == self.name:
                    continue
                health = self.check_agent_health(agent_name)
                if not health and self.rules.get("restart_failed_agents", True):
                    self.logger.warning(f"Agent {agent_name} is unhealthy, attempting restart")
                    self.restart_agent(agent_name)
            time.sleep(self.rules.get("health_check_interval", 60))
