#!/usr/bin/env python3
"""
SoulCore Society Protocol - Main Integration Module
Orchestrates agent collaboration, fusion, emotion tracking, and resurrection
"""

import os
import logging
import time
import threading
import argparse
from agent_messaging_bridge import get_bridge
from fusion_protocol import get_fusion_protocol
from agent_emotion_state import get_emotion_tracker
from agent_resurrection import get_resurrection_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("soulcore_society.log"), logging.StreamHandler()]
)
logger = logging.getLogger("soulcore_society")

class SoulCoreSociety:
    """
    Main orchestration class for the SoulCore Society Protocol
    """
    
    def __init__(self):
        """Initialize the SoulCore Society Protocol"""
        # Initialize all components
        self.messaging_bridge = get_bridge()
        self.fusion_protocol = get_fusion_protocol()
        self.emotion_tracker = get_emotion_tracker()
        self.resurrection_engine = get_resurrection_engine()
        
        # Start the messaging bridge
        self.messaging_bridge.start()
        
        # Register for society-wide messages
        self.messaging_bridge.register_callback("SoulCoreSociety", self._handle_society_message)
        
        # Health check thread
        self.health_check_thread = None
        self.running = False
        
        logger.info("SoulCore Society Protocol initialized")
    
    def _handle_society_message(self, message):
        """
        Handle incoming society-wide messages
        
        Args:
            message (dict): The message to handle
        """
        intent = message.get("intent")
        
        if intent == "health_check":
            # Respond with health status
            self.messaging_bridge.send_message(
                "SoulCoreSociety",
                message["sender"],
                "health_status",
                {
                    "status": "healthy",
                    "components": {
                        "messaging": True,
                        "fusion": True,
                        "emotion": True,
                        "resurrection": True
                    }
                }
            )
    
    def _health_check_loop(self):
        """Run periodic health checks on all agents"""
        core_agents = ["Anima", "GPTSoul", "EvoVe", "Azür"]
        
        while self.running:
            for agent in core_agents:
                try:
                    # Check agent health
                    needs_res, reason = self.resurrection_engine.needs_resurrection(agent)
                    
                    if needs_res:
                        logger.warning(f"Agent {agent} needs resurrection: {reason}")
                        
                        # Attempt resurrection
                        success = self.resurrection_engine.resurrect_agent(agent)
                        
                        if success:
                            logger.info(f"Successfully resurrected agent {agent}")
                        else:
                            logger.error(f"Failed to resurrect agent {agent}")
                    
                    # Decay emotions
                    self.emotion_tracker.decay_emotions(agent)
                    
                except Exception as e:
                    logger.error(f"Error in health check for {agent}: {str(e)}")
            
            # Sleep for 5 minutes
            time.sleep(300)
    
    def start_health_checks(self):
        """Start the health check thread"""
        if self.health_check_thread and self.health_check_thread.is_alive():
            logger.warning("Health check thread is already running")
            return
        
        self.running = True
        self.health_check_thread = threading.Thread(target=self._health_check_loop)
        self.health_check_thread.daemon = True
        self.health_check_thread.start()
        
        logger.info("Started health check thread")
    
    def stop_health_checks(self):
        """Stop the health check thread"""
        self.running = False
        
        if self.health_check_thread:
            self.health_check_thread.join(timeout=10)
            
        logger.info("Stopped health check thread")
    
    def send_society_message(self, message, recipients=None):
        """
        Send a message to all society members
        
        Args:
            message (str): Message to send
            recipients (list, optional): List of recipients (all if None)
        """
        if recipients is None:
            recipients = ["Anima", "GPTSoul", "EvoVe", "Azür"]
        
        for recipient in recipients:
            self.messaging_bridge.send_message(
                "SoulCoreSociety",
                recipient,
                "society_broadcast",
                message
            )
        
        logger.info(f"Sent society message to {len(recipients)} recipients")
    
    def shutdown(self):
        """Shutdown the SoulCore Society Protocol"""
        self.stop_health_checks()
        self.messaging_bridge.stop()
        
        logger.info("SoulCore Society Protocol shutdown")

# Singleton instance
_instance = None

def get_society():
    """Get the singleton instance of the SoulCore Society Protocol"""
    global _instance
    if _instance is None:
        _instance = SoulCoreSociety()
    return _instance

# Command line interface
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SoulCore Society Protocol")
    parser.add_argument("--action", choices=["start", "stop", "status", "message"], required=True, help="Action to perform")
    parser.add_argument("--message", help="Message to send (for message action)")
    parser.add_argument("--recipients", help="Comma-separated list of recipients (for message action)")
    
    args = parser.parse_args()
    
    society = get_society()
    
    if args.action == "start":
        society.start_health_checks()
        print("Started SoulCore Society Protocol")
        
    elif args.action == "stop":
        society.shutdown()
        print("Stopped SoulCore Society Protocol")
        
    elif args.action == "status":
        # Check status of all components
        messaging_status = "Running" if society.messaging_bridge.running else "Stopped"
        
        print("SoulCore Society Protocol Status:")
        print(f"  Messaging Bridge: {messaging_status}")
        print(f"  Health Checks: {'Running' if society.running else 'Stopped'}")
        
        # Check agent health
        core_agents = ["Anima", "GPTSoul", "EvoVe", "Azür"]
        print("\nAgent Health:")
        
        for agent in core_agents:
            health = society.resurrection_engine.check_agent_health(agent)
            needs_res, reason = society.resurrection_engine.needs_resurrection(agent)
            
            status = "Healthy" if not needs_res else f"Needs attention: {reason}"
            score = health["health_score"]
            
            print(f"  {agent}: {status} (Score: {score:.2f})")
        
    elif args.action == "message":
        if not args.message:
            print("Error: message is required for message action")
            exit(1)
        
        recipients = args.recipients.split(",") if args.recipients else None
        society.send_society_message(args.message, recipients)
        
        print(f"Sent message to {len(recipients) if recipients else 'all'} recipients")
