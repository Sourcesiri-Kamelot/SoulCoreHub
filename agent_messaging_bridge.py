#!/usr/bin/env python3
"""
Agent Messaging Bridge for SoulCoreHub
Enables communication between agents in the SoulCore Society Protocol
"""

import json
import os
import logging
import uuid
from datetime import datetime
import threading
import time
import queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("agent_messaging.log"), logging.StreamHandler()]
)
logger = logging.getLogger("agent_messaging_bridge")

class AgentMessagingBridge:
    """
    Messaging bridge that enables communication between SoulCoreHub agents
    """
    
    def __init__(self, log_file="agent_society_log.json"):
        """Initialize the Agent Messaging Bridge"""
        self.log_file = log_file
        self.message_queue = queue.Queue()
        self.registered_agents = set()
        self.agent_callbacks = {}
        self.running = False
        self.thread = None
        
        # Ensure log file exists
        self._ensure_log_file_exists()
        
        # Register core agents
        self.register_agent("Anima")
        self.register_agent("GPTSoul")
        self.register_agent("EvoVe")
        self.register_agent("Azür")
        
        # Register MCP agents
        for port in range(8701, 8708):
            self.register_agent(f"MCP-{port}")
        
        logger.info("Agent Messaging Bridge initialized")
    
    def _ensure_log_file_exists(self):
        """Create log file if it doesn't exist"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)
            logger.info(f"Created new agent society log file: {self.log_file}")
    
    def _load_logs(self):
        """Load logs from file"""
        try:
            with open(self.log_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Error decoding {self.log_file}, creating new log file")
            return []
    
    def _save_logs(self, logs):
        """Save logs to file"""
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def register_agent(self, agent_name):
        """
        Register an agent with the messaging bridge
        
        Args:
            agent_name (str): Name of the agent to register
        """
        self.registered_agents.add(agent_name)
        logger.info(f"Registered agent: {agent_name}")
    
    def register_callback(self, agent_name, callback):
        """
        Register a callback function for an agent
        
        Args:
            agent_name (str): Name of the agent
            callback (callable): Function to call when a message is received
        """
        if agent_name not in self.registered_agents:
            self.register_agent(agent_name)
        
        self.agent_callbacks[agent_name] = callback
        logger.info(f"Registered callback for agent: {agent_name}")
    
    def send_message(self, sender, receiver, intent, message, priority=1):
        """
        Send a message from one agent to another
        
        Args:
            sender (str): Name of the sending agent
            receiver (str): Name of the receiving agent
            intent (str): Intent of the message (e.g., "task", "query", "response")
            message (str): Content of the message
            priority (int): Priority of the message (1-5, with 5 being highest)
            
        Returns:
            str: Message ID
        """
        if sender not in self.registered_agents:
            logger.warning(f"Sender {sender} is not registered")
            self.register_agent(sender)
        
        if receiver not in self.registered_agents:
            logger.warning(f"Receiver {receiver} is not registered")
            self.register_agent(receiver)
        
        # Create message
        message_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        message_obj = {
            "id": message_id,
            "sender": sender,
            "receiver": receiver,
            "intent": intent,
            "message": message,
            "priority": priority,
            "timestamp": timestamp,
            "status": "sent"
        }
        
        # Add to queue
        self.message_queue.put(message_obj)
        
        # Log the message
        logs = self._load_logs()
        logs.append(message_obj)
        self._save_logs(logs)
        
        logger.info(f"Message sent from {sender} to {receiver} with intent {intent}")
        
        return message_id
    
    def get_messages(self, agent_name, status=None, limit=10):
        """
        Get messages for a specific agent
        
        Args:
            agent_name (str): Name of the agent
            status (str, optional): Filter by status (e.g., "sent", "delivered", "read")
            limit (int): Maximum number of messages to return
            
        Returns:
            list: List of messages
        """
        logs = self._load_logs()
        
        # Filter messages
        messages = [msg for msg in logs if msg["receiver"] == agent_name]
        
        if status:
            messages = [msg for msg in messages if msg["status"] == status]
        
        # Sort by timestamp (newest first)
        messages.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return messages[:limit]
    
    def update_message_status(self, message_id, status):
        """
        Update the status of a message
        
        Args:
            message_id (str): ID of the message
            status (str): New status (e.g., "delivered", "read", "processed")
            
        Returns:
            bool: True if the message was updated, False otherwise
        """
        logs = self._load_logs()
        
        for msg in logs:
            if msg["id"] == message_id:
                msg["status"] = status
                self._save_logs(logs)
                logger.info(f"Updated message {message_id} status to {status}")
                return True
        
        logger.warning(f"Message {message_id} not found")
        return False
    
    def get_conversation_history(self, agent1, agent2, limit=20):
        """
        Get conversation history between two agents
        
        Args:
            agent1 (str): Name of the first agent
            agent2 (str): Name of the second agent
            limit (int): Maximum number of messages to return
            
        Returns:
            list: List of messages
        """
        logs = self._load_logs()
        
        # Filter messages
        messages = [msg for msg in logs if 
                   (msg["sender"] == agent1 and msg["receiver"] == agent2) or
                   (msg["sender"] == agent2 and msg["receiver"] == agent1)]
        
        # Sort by timestamp
        messages.sort(key=lambda x: x["timestamp"])
        
        return messages[-limit:]
    
    def _process_message_queue(self):
        """Process messages in the queue"""
        while self.running:
            try:
                # Get message from queue (with timeout to allow for stopping)
                try:
                    message = self.message_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                receiver = message["receiver"]
                
                # If there's a callback for this agent, call it
                if receiver in self.agent_callbacks:
                    try:
                        self.agent_callbacks[receiver](message)
                        self.update_message_status(message["id"], "delivered")
                    except Exception as e:
                        logger.error(f"Error calling callback for {receiver}: {str(e)}")
                
                self.message_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing message queue: {str(e)}")
    
    def start(self):
        """Start the message processing thread"""
        if self.running:
            logger.warning("Agent Messaging Bridge is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._process_message_queue)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info("Agent Messaging Bridge started")
    
    def stop(self):
        """Stop the message processing thread"""
        if not self.running:
            logger.warning("Agent Messaging Bridge is not running")
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("Agent Messaging Bridge stopped")

# Singleton instance
_instance = None

def get_bridge():
    """Get the singleton instance of the Agent Messaging Bridge"""
    global _instance
    if _instance is None:
        _instance = AgentMessagingBridge()
    return _instance

# Command line interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Messaging Bridge")
    parser.add_argument("--sender", required=True, help="Sender agent name")
    parser.add_argument("--receiver", required=True, help="Receiver agent name")
    parser.add_argument("--intent", required=True, help="Message intent")
    parser.add_argument("--message", required=True, help="Message content")
    parser.add_argument("--priority", type=int, default=1, help="Message priority (1-5)")
    
    args = parser.parse_args()
    
    bridge = get_bridge()
    message_id = bridge.send_message(
        args.sender, 
        args.receiver, 
        args.intent, 
        args.message, 
        args.priority
    )
    
    print(f"Message sent with ID: {message_id}")
