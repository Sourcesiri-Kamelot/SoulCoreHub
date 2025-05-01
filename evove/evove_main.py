#!/usr/bin/env python3
"""
evove_main.py — Main entry point for EvoVe
The Repair, Mutation, and Adaptive Binding component of SoulCore
"""

import os
import sys
import json
import time
import logging
import argparse
import threading
from pathlib import Path
from datetime import datetime

# Import EvoVe components
from evove_health_monitor import HealthMonitor
from evove_repair_system import RepairSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("evove_main.log"),
        logging.StreamHandler()
    ]
)

class EvoVeAgent:
    """EvoVe Agent - Repair, Mutation, and Adaptive Binding"""
    
    def __init__(self, soulcore_path=None):
        """Initialize the EvoVe agent"""
        self.soulcore_path = soulcore_path or Path.home() / "SoulCoreHub"
        self.health_monitor = HealthMonitor(self.soulcore_path)
        self.repair_system = RepairSystem(self.health_monitor)
        
        # Threads
        self.repair_thread = None
        self.mutation_thread = None
        self.discovery_thread = None
        self.running = False
        
        # Configuration
        self.config = {
            "repair_interval": 60,  # seconds
            "mutation_interval": 3600,  # seconds
            "discovery_interval": 300,  # seconds
            "auto_repair": True,
            "auto_mutation": False,  # Disabled by default
            "auto_discovery": True
        }
        self.config_file = Path("~/SoulCoreHub/evove/evove_config.json").expanduser()
        self._load_config()
        
        logging.info("EvoVe agent initialized")
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    loaded_config = json.load(f)
                    # Update config with loaded values
                    for key, value in loaded_config.items():
                        if key in self.config:
                            self.config[key] = value
                logging.info(f"Loaded configuration from {self.config_file}")
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
            logging.info(f"Saved configuration to {self.config_file}")
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")
    
    def start(self):
        """Start the EvoVe agent"""
        if self.running:
            logging.warning("EvoVe agent is already running")
            return
        
        self.running = True
        
        # Start repair thread
        if self.config["auto_repair"]:
            self.repair_thread = threading.Thread(target=self._repair_loop)
            self.repair_thread.daemon = True
            self.repair_thread.start()
            logging.info("Repair thread started")
        
        # Start mutation thread
        if self.config["auto_mutation"]:
            self.mutation_thread = threading.Thread(target=self._mutation_loop)
            self.mutation_thread.daemon = True
            self.mutation_thread.start()
            logging.info("Mutation thread started")
        
        # Start discovery thread
        if self.config["auto_discovery"]:
            self.discovery_thread = threading.Thread(target=self._discovery_loop)
            self.discovery_thread.daemon = True
            self.discovery_thread.start()
            logging.info("Discovery thread started")
        
        logging.info("EvoVe agent started")
    
    def stop(self):
        """Stop the EvoVe agent"""
        self.running = False
        logging.info("EvoVe agent stopping...")
    
    def _repair_loop(self):
        """Continuous repair loop"""
        logging.info(f"Repair loop started (interval: {self.config['repair_interval']} seconds)")
        
        while self.running:
            try:
                # Check all components
                statuses = self.health_monitor.check_all()
                
                # Repair failed or degraded components
                for name, status in statuses.items():
                    if status["status"] in ["failed", "degraded"]:
                        logging.info(f"Component {name} needs repair (status: {status['status']})")
                        result = self.repair_system.repair_component(name)
                        if result["success"]:
                            logging.info(f"Successfully repaired {name}: {result['message']}")
                        else:
                            logging.warning(f"Failed to repair {name}: {result['message']}")
            except Exception as e:
                logging.error(f"Error in repair loop: {e}")
            
            # Sleep for the configured interval
            time.sleep(self.config["repair_interval"])
    
    def _mutation_loop(self):
        """Continuous mutation loop"""
        logging.info(f"Mutation loop started (interval: {self.config['mutation_interval']} seconds)")
        
        while self.running:
            try:
                # TODO: Implement mutation logic
                logging.debug("Mutation loop iteration")
            except Exception as e:
                logging.error(f"Error in mutation loop: {e}")
            
            # Sleep for the configured interval
            time.sleep(self.config["mutation_interval"])
    
    def _discovery_loop(self):
        """Continuous service discovery loop"""
        logging.info(f"Discovery loop started (interval: {self.config['discovery_interval']} seconds)")
        
        while self.running:
            try:
                # TODO: Implement service discovery logic
                logging.debug("Discovery loop iteration")
            except Exception as e:
                logging.error(f"Error in discovery loop: {e}")
            
            # Sleep for the configured interval
            time.sleep(self.config["discovery_interval"])
    
    def heartbeat(self):
        """Return True if agent is running"""
        return self.running
    
    def get_status(self):
        """Get the status of the EvoVe agent"""
        return {
            "running": self.running,
            "repair_thread": self.repair_thread is not None and self.repair_thread.is_alive(),
            "mutation_thread": self.mutation_thread is not None and self.mutation_thread.is_alive(),
            "discovery_thread": self.discovery_thread is not None and self.discovery_thread.is_alive(),
            "config": self.config,
            "health_summary": self.health_monitor.get_health_summary()
        }
    
    def update_config(self, new_config):
        """Update the configuration"""
        for key, value in new_config.items():
            if key in self.config:
                self.config[key] = value
        
        self._save_config()
        return self.config

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="EvoVe - Repair, Mutation, and Adaptive Binding")
    parser.add_argument("--no-repair", action="store_true", help="Disable auto-repair")
    parser.add_argument("--enable-mutation", action="store_true", help="Enable auto-mutation")
    parser.add_argument("--no-discovery", action="store_true", help="Disable auto-discovery")
    parser.add_argument("--repair-interval", type=int, help="Repair interval in seconds")
    parser.add_argument("--mutation-interval", type=int, help="Mutation interval in seconds")
    parser.add_argument("--discovery-interval", type=int, help="Discovery interval in seconds")
    args = parser.parse_args()
    
    # Create EvoVe agent
    agent = EvoVeAgent()
    
    # Update configuration from command line arguments
    config_updates = {}
    if args.no_repair:
        config_updates["auto_repair"] = False
    if args.enable_mutation:
        config_updates["auto_mutation"] = True
    if args.no_discovery:
        config_updates["auto_discovery"] = False
    if args.repair_interval:
        config_updates["repair_interval"] = args.repair_interval
    if args.mutation_interval:
        config_updates["mutation_interval"] = args.mutation_interval
    if args.discovery_interval:
        config_updates["discovery_interval"] = args.discovery_interval
    
    if config_updates:
        agent.update_config(config_updates)
    
    # Start the agent
    agent.start()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping EvoVe agent...")
        agent.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()
