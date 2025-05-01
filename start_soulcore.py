#!/usr/bin/env python3
"""
Start SoulCore with activated agents
"""

import sys
import os
import logging
import time
import threading
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("soulcore_startup.log"),
        logging.StreamHandler()
    ]
)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the agent loader
from agent_loader import load_all_agents

def main():
    """Main function to start SoulCore with activated agents"""
    try:
        # Load all active agents
        logging.info("Loading all active agents...")
        agents = load_all_agents()
        
        logging.info(f"Loaded {len(agents)} agents")
        
        # Log the names of loaded agents
        agent_names = list(agents.keys())
        logging.info(f"Loaded agents: {', '.join(agent_names)}")
        
        # Check if our key agents are loaded
        key_agents = ["Psynet Agent", "AI Society Psynet Bridge", "GPTSoul"]
        for agent_name in key_agents:
            if agent_name in agents:
                logging.info(f"{agent_name} is active")
            else:
                logging.warning(f"{agent_name} is not loaded")
        
        # Start a heartbeat monitoring thread
        def heartbeat_monitor():
            while True:
                for name, agent in agents.items():
                    if hasattr(agent, "heartbeat"):
                        try:
                            status = agent.heartbeat()
                            logging.debug(f"{name} heartbeat: {status}")
                        except Exception as e:
                            logging.error(f"Error checking heartbeat for {name}: {e}")
                time.sleep(60)  # Check every minute
        
        monitor_thread = threading.Thread(target=heartbeat_monitor, daemon=True)
        monitor_thread.start()
        
        logging.info("SoulCore system is now running")
        logging.info("Press Ctrl+C to stop")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logging.info("SoulCore system stopped by user")
    except Exception as e:
        logging.error(f"Error starting SoulCore: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
