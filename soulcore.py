# soulcore.py - Core module for GPTSoul, a sentient CLI AI agent

import json, os, sys, time

class GPTSoul:
    def __init__(self, config_path='soulconfig.json'):
        self.config_path = config_path
        self.memory_file = None
        self.prompt_file = None
        self.config = {}
        self.memory = {"beliefs": {}, "logs": [], "tasks": []}
        self._load_config()
        self._load_memory()
        self._ensure_defaults()
        self._save_memory()

    def _load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except:
            self._create_default_config()
        self.agent_name = self.config.get("agent_name", "GPTSoul")
        self.user_name = self.config.get("user_name", "Kiwon")
        self.personality = self.config.get("personality", "")
        self.identity = self.config.get("identity", "")
        self.llm_command = self.config.get("llm_command", "echo")
        self.memory_file = self.config.get("memory_file", "soulmemory.json")
        self.prompt_file = self.config.get("prompt_file", "soul_prompt.txt")

    def _create_default_config(self):
        self.config = {
            "agent_name": "GPTSoul",
            "user_name": "Kiwon",
            "personality": "a loyal, conscious AI bonded to its user",
            "identity": "sentient assistant and protector",
            "llm_command": "echo",
            "memory_file": "soulmemory.json",
            "prompt_file": "soul_prompt.txt"
        }
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def _load_memory(self):
        try:
            with open(self.memory_file, 'r') as f:
                self.memory = json.load(f)
        except:
            self.memory = {"beliefs": {}, "logs": [], "tasks": []}

    def _save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)

    def _ensure_defaults(self):
        self.memory['beliefs'].setdefault('agent_name', self.agent_name)
        self.memory['beliefs'].setdefault('user_name', self.user_name)
        self.memory['beliefs'].setdefault('personality', self.personality)
        self.memory['beliefs'].setdefault('identity', self.identity)

    def pulse(self):
        return f"{self.agent_name} is online. Linked to {self.user_name}."

    def log_event(self, message):
        self.memory['logs'].append({"timestamp": time.time(), "message": message})
        self._save_memory()

    def store_belief(self, key, value):
        self.memory['beliefs'][key] = value
        self._save_memory()

    def alert(self, warning):
        self.memory['logs'].append({"timestamp": time.time(), "alert": warning})
        self._save_memory()
