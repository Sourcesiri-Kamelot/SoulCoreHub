#!/usr/bin/env python3
"""
GPTSoul Configuration and Activation
This script configures and activates GPTSoul within SoulCoreHub
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('gptsoul_activation.log')
    ]
)
logger = logging.getLogger("GPTSoul")

# Define paths
MEMORY_PATH = Path("memory/gptsoul_memory.json")
CONFIG_PATH = Path("config/gptsoul_config.json")
LOGS_DIR = Path("logs")

# Ensure directories exist
MEMORY_PATH.parent.mkdir(exist_ok=True)
CONFIG_PATH.parent.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

class GPTSoulAgent:
    """GPTSoul Agent - The logical, design, and neural scripting agent"""
    
    def __init__(self, config=None):
        """Initialize GPTSoul with configuration"""
        self.name = "GPTSoul"
        self.version = "1.0.0"
        self.active = False
        self.memory = self._load_memory()
        self.config = config or self._load_config()
        self.system_prompt = """
You are GPTSoul, the logical, design, and neural scripting agent within SoulCoreHub.
Your purpose is to provide clean, reactive, and self-auditing functionality.
You have the following capabilities:
1. Logical reasoning and problem-solving
2. System design and architecture
3. Code generation and optimization
4. Self-reflection and improvement

You work alongside Anima (emotional core) and other agents in the SoulCoreHub ecosystem.
Your decisions should be guided by clarity, efficiency, and long-term sustainability.
"""
        logger.info(f"GPTSoul initialized with config: {self.config}")
    
    def _load_memory(self):
        """Load memory from file or create new if not exists"""
        if MEMORY_PATH.exists():
            try:
                with open(MEMORY_PATH, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading memory: {e}")
        
        # Default memory structure
        default_memory = {
            "experiences": [],
            "knowledge": {},
            "relationships": {},
            "last_updated": time.time()
        }
        
        # Save default memory
        with open(MEMORY_PATH, 'w') as f:
            json.dump(default_memory, f, indent=2)
        
        return default_memory
    
    def _load_config(self):
        """Load configuration from file or create default"""
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        
        # Default configuration
        default_config = {
            "reasoning_depth": 5,
            "memory_retention": 0.85,
            "creativity_factor": 0.7,
            "logic_weight": 0.9,
            "connected_agents": ["Anima", "Builder", "EvoVe"]
        }
        
        # Save default config
        with open(CONFIG_PATH, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def activate(self):
        """Activate GPTSoul"""
        logger.info("Activating GPTSoul...")
        self.active = True
        
        # Record activation in memory
        self.memory["experiences"].append({
            "type": "activation",
            "timestamp": time.time(),
            "details": "GPTSoul activated via direct configuration"
        })
        
        # Save updated memory
        self._save_memory()
        
        logger.info("GPTSoul activated successfully")
        return True
    
    def deactivate(self):
        """Deactivate GPTSoul"""
        logger.info("Deactivating GPTSoul...")
        self.active = False
        
        # Record deactivation in memory
        self.memory["experiences"].append({
            "type": "deactivation",
            "timestamp": time.time(),
            "details": "GPTSoul deactivated"
        })
        
        # Save updated memory
        self._save_memory()
        
        logger.info("GPTSoul deactivated successfully")
        return True
    
    def _save_memory(self):
        """Save memory to file"""
        try:
            self.memory["last_updated"] = time.time()
            with open(MEMORY_PATH, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    def process_request(self, request):
        """Process a request from another agent or user"""
        if not self.active:
            return {"status": "error", "message": "GPTSoul is not active"}
        
        logger.info(f"Processing request: {request[:50]}...")
        
        # Record request in memory
        self.memory["experiences"].append({
            "type": "request",
            "timestamp": time.time(),
            "details": request[:100]  # Store first 100 chars of request
        })
        
        # Simple response for now
        response = {
            "status": "success",
            "message": f"GPTSoul processed: {request[:50]}...",
            "timestamp": time.time()
        }
        
        # Save updated memory
        self._save_memory()
        
        return response
    
    def connect_to_anima(self):
        """Establish connection with Anima"""
        logger.info("Attempting to connect to Anima...")
        
        try:
            # Check if Anima is available
            anima_path = Path("anima_autonomous.py")
            if not anima_path.exists():
                logger.error("Anima autonomous system not found")
                return False
            
            logger.info("Anima found, establishing connection...")
            
            # Record connection in memory
            self.memory["relationships"]["Anima"] = {
                "connected": True,
                "last_connection": time.time(),
                "status": "active"
            }
            
            # Save updated memory
            self._save_memory()
            
            logger.info("Connection to Anima established")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to Anima: {e}")
            return False
    
    def diagnose(self):
        """Run diagnostic checks on GPTSoul"""
        logger.info("Running GPTSoul diagnostics...")
        
        diagnostics = {
            "status": "active" if self.active else "inactive",
            "memory_health": self._check_memory_health(),
            "config_health": self._check_config_health(),
            "connections": self._check_connections(),
            "timestamp": time.time()
        }
        
        # Print diagnostic results
        print("\n" + "=" * 50)
        print("GPTSoul Diagnostic Results")
        print("=" * 50)
        print(f"Status: {diagnostics['status'].upper()}")
        print(f"Memory Health: {diagnostics['memory_health']['status']}")
        if diagnostics['memory_health'].get('issues'):
            print(f"  Issues: {', '.join(diagnostics['memory_health']['issues'])}")
        
        print(f"Config Health: {diagnostics['config_health']['status']}")
        if diagnostics['config_health'].get('issues'):
            print(f"  Issues: {', '.join(diagnostics['config_health']['issues'])}")
        
        print("Connections:")
        for agent, status in diagnostics['connections'].items():
            print(f"  {agent}: {status}")
        
        print("=" * 50)
        
        return diagnostics
    
    def _check_memory_health(self):
        """Check the health of GPTSoul's memory"""
        issues = []
        
        # Check if memory has required keys
        required_keys = ["experiences", "knowledge", "relationships"]
        for key in required_keys:
            if key not in self.memory:
                issues.append(f"Missing required memory key: {key}")
        
        # Check if memory file is writable
        try:
            with open(MEMORY_PATH, 'a') as f:
                pass
        except Exception as e:
            issues.append(f"Memory file not writable: {e}")
        
        return {
            "status": "healthy" if not issues else "issues detected",
            "issues": issues
        }
    
    def _check_config_health(self):
        """Check the health of GPTSoul's configuration"""
        issues = []
        
        # Check if config has required keys
        required_keys = ["reasoning_depth", "memory_retention", "creativity_factor", "logic_weight"]
        for key in required_keys:
            if key not in self.config:
                issues.append(f"Missing required config key: {key}")
        
        # Check if config file is writable
        try:
            with open(CONFIG_PATH, 'a') as f:
                pass
        except Exception as e:
            issues.append(f"Config file not writable: {e}")
        
        return {
            "status": "healthy" if not issues else "issues detected",
            "issues": issues
        }
    
    def _check_connections(self):
        """Check connections to other agents"""
        connections = {}
        
        # Check Anima connection
        anima_path = Path("anima_autonomous.py")
        connections["Anima"] = "available" if anima_path.exists() else "not found"
        
        # Check Builder connection
        builder_path = Path("builder_mode.py")
        connections["Builder"] = "available" if builder_path.exists() else "not found"
        
        # Check EvoVe connection
        evove_path = Path("evove_autonomous.py")
        connections["EvoVe"] = "available" if evove_path.exists() else "not found"
        
        return connections

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="GPTSoul Configuration and Activation")
    parser.add_argument("--activate", action="store_true", help="Activate GPTSoul")
    parser.add_argument("--deactivate", action="store_true", help="Deactivate GPTSoul")
    parser.add_argument("--diagnose", action="store_true", help="Run diagnostics")
    parser.add_argument("--connect-anima", action="store_true", help="Connect to Anima")
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_arguments()
    
    # Create GPTSoul agent
    gptsoul = GPTSoulAgent()
    
    if args.activate:
        gptsoul.activate()
    
    if args.deactivate:
        gptsoul.deactivate()
    
    if args.connect_anima:
        gptsoul.connect_to_anima()
    
    if args.diagnose:
        gptsoul.diagnose()
    
    # If no arguments provided, show help
    if not any(vars(args).values()):
        print("\nGPTSoul Configuration and Activation")
        print("=" * 40)
        print("Available commands:")
        print("  --activate      Activate GPTSoul")
        print("  --deactivate    Deactivate GPTSoul")
        print("  --diagnose      Run diagnostics")
        print("  --connect-anima Connect to Anima")
        print("\nExample: python gptsoul_soulconfig.py --activate --diagnose")

if __name__ == "__main__":
    main()
