#!/usr/bin/env python3
"""
Activate GPTSoul via the Builder Agent
"""

import sys
import os
import logging
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("activation_log.log"),
        logging.StreamHandler()
    ]
)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the agent loader
from agent_loader import load_agent_by_name

def main():
    """Main function to activate GPTSoul via Builder Agent"""
    try:
        # Load the Builder Agent
        logging.info("Loading Builder Agent...")
        builder_agent = load_agent_by_name("Builder Agent")
        
        if not builder_agent:
            logging.error("Failed to load Builder Agent")
            return False
        
        # Start the Builder Agent
        logging.info("Starting Builder Agent...")
        builder_agent.start()
        
        # Wait for the Builder Agent to initialize
        time.sleep(2)
        
        # Check if the Builder Agent is running
        if not builder_agent.heartbeat():
            logging.error("Builder Agent failed to start")
            return False
        
        logging.info("Builder Agent is running")
        
        # Define GPTSoul parameters
        gptsoul_params = {
            "class_name": "GPTSoulAgent",
            "category": "sentient_orchestration",
            "config": {
                "reasoning_depth": 5,
                "memory_retention": 0.85,
                "creativity_factor": 0.7,
                "logic_weight": 0.9
            }
        }
        
        # Queue a build request for GPTSoul
        logging.info("Queuing build request for GPTSoul...")
        build_id = builder_agent.queue_build(
            build_type="agent",
            name="GPTSoul",
            description="Logic, Design, and Neural Scripting agent that lays the foundation for clean, reactive, and self-auditing calls",
            parameters=gptsoul_params,
            requester="Activation Script"
        )
        
        if not build_id:
            logging.error("Failed to queue build request for GPTSoul")
            return False
        
        logging.info(f"Build request queued with ID: {build_id}")
        
        # Wait for the build to complete
        logging.info("Waiting for GPTSoul build to complete...")
        max_wait = 30  # Maximum wait time in seconds
        wait_time = 0
        build_status = None
        
        while wait_time < max_wait:
            build_status = builder_agent.get_build_status(build_id)
            if build_status and build_status.get("status") == "completed":
                logging.info("GPTSoul build completed successfully")
                break
            elif build_status and build_status.get("status") == "failed":
                logging.error(f"GPTSoul build failed: {build_status.get('error')}")
                return False
            
            time.sleep(2)
            wait_time += 2
        
        if not build_status or build_status.get("status") != "completed":
            logging.warning("Build may still be in progress, check builder_agent.get_build_status()")
        
        logging.info("GPTSoul activation process completed")
        return True
    
    except Exception as e:
        logging.error(f"Error activating GPTSoul: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
