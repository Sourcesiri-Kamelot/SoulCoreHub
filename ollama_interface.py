#!/usr/bin/env python3
# ollama_interface.py - Interface for Ollama LLM integration

import json
import sys
import os
import requests
from datetime import datetime

class OllamaInterface:
    """Interface for interacting with Ollama LLMs"""
    
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.available_models = self._get_available_models()
        
    def _get_available_models(self):
        """Get list of available models from Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return [model["name"] for model in response.json().get("models", [])]
            return []
        except Exception as e:
            print(f"Error getting available models: {e}")
            return []
    
    def generate(self, prompt, model="qwen", system_prompt=None, max_tokens=1000):
        """Generate a response from the specified model"""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "max_tokens": max_tokens
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error connecting to Ollama: {e}"
    
    def chat(self, messages, model="qwen", max_tokens=1000):
        """Chat with the specified model using a message history"""
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "max_tokens": max_tokens
        }
            
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                return response.json().get("message", {}).get("content", "")
            else:
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error connecting to Ollama: {e}"
    
    def get_agent_instruction(self, agent_name, task, model="qwen"):
        """Get instructions for an agent using Ollama"""
        system_prompt = f"""You are providing instructions to the {agent_name} agent in the SoulCore system.
Your task is to create clear, specific instructions that align with {agent_name}'s capabilities and personality.
Be concise but comprehensive."""
        
        prompt = f"""Task for {agent_name}: {task}

Create specific instructions for {agent_name} to accomplish this task.
Include any relevant parameters, approaches, or considerations.
Format your response as direct instructions to {agent_name}."""
        
        return self.generate(prompt, model, system_prompt)
    
    def log_interaction(self, model, prompt, response):
        """Log the interaction with Ollama"""
        log_dir = os.path.join("logs", "ollama")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{model}_interactions.log")
        
        with open(log_file, "a") as f:
            f.write(f"[{datetime.now().isoformat()}]\n")
            f.write(f"PROMPT: {prompt}\n")
            f.write(f"RESPONSE: {response}\n")
            f.write("-" * 50 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ollama_interface.py <model> <prompt>")
        print("   or: python ollama_interface.py instruct <agent_name> <task>")
        sys.exit(1)
    
    ollama = OllamaInterface()
    
    if sys.argv[1] == "instruct":
        if len(sys.argv) < 4:
            print("Usage: python ollama_interface.py instruct <agent_name> <task>")
            sys.exit(1)
        agent_name = sys.argv[2]
        task = sys.argv[3]
        response = ollama.get_agent_instruction(agent_name, task)
        print(json.dumps({"agent": agent_name, "task": task, "instructions": response}, indent=2))
    else:
        model = sys.argv[1]
        prompt = sys.argv[2]
        response = ollama.generate(prompt, model)
        ollama.log_interaction(model, prompt, response)
        print(response)
