#!/usr/bin/env python3
"""
Fusion Protocol for SoulCoreHub
Enables agent fusion for complex requests in the SoulCore Society Protocol
"""

import json
import os
import logging
import uuid
from datetime import datetime
import threading
from agent_messaging_bridge import get_bridge
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("fusion_protocol.log"), logging.StreamHandler()]
)
logger = logging.getLogger("fusion_protocol")

class FusionProtocol:
    """
    Protocol for fusing multiple agents to handle complex requests
    """
    
    def __init__(self, fusion_log_file="agent_fusion_log.json"):
        """Initialize the Fusion Protocol"""
        self.fusion_log_file = fusion_log_file
        self.active_fusions = {}
        self.messaging_bridge = get_bridge()
        
        # Ensure log file exists
        self._ensure_log_file_exists()
        
        # Start the messaging bridge if it's not already running
        self.messaging_bridge.start()
        
        # Register for fusion requests
        self.messaging_bridge.register_callback("FusionProtocol", self._handle_fusion_message)
        
        logger.info("Fusion Protocol initialized")
    
    def _ensure_log_file_exists(self):
        """Create log file if it doesn't exist"""
        if not os.path.exists(self.fusion_log_file):
            with open(self.fusion_log_file, 'w') as f:
                json.dump([], f)
            logger.info(f"Created new fusion log file: {self.fusion_log_file}")
    
    def _load_logs(self):
        """Load logs from file"""
        try:
            with open(self.fusion_log_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Error decoding {self.fusion_log_file}, creating new log file")
            return []
    
    def _save_logs(self, logs):
        """Save logs to file"""
        with open(self.fusion_log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def _handle_fusion_message(self, message):
        """
        Handle incoming fusion messages
        
        Args:
            message (dict): The message to handle
        """
        intent = message.get("intent")
        
        if intent == "fusion_request":
            # Extract fusion details
            fusion_id = message.get("message", {}).get("fusion_id")
            if fusion_id and fusion_id in self.active_fusions:
                fusion = self.active_fusions[fusion_id]
                agent = message.get("sender")
                response = message.get("message", {}).get("response")
                
                # Add response to fusion
                fusion["responses"][agent] = response
                
                # Check if all agents have responded
                if set(fusion["responses"].keys()) == set(fusion["agents"]):
                    # All agents have responded, complete the fusion
                    self._complete_fusion(fusion_id)
    
    def _complete_fusion(self, fusion_id):
        """
        Complete a fusion by combining responses and notifying the requester
        
        Args:
            fusion_id (str): ID of the fusion to complete
        """
        if fusion_id not in self.active_fusions:
            logger.warning(f"Fusion {fusion_id} not found")
            return
        
        fusion = self.active_fusions[fusion_id]
        
        # Combine responses
        combined_response = self._combine_responses(fusion)
        
        # Add signature
        agent_signatures = ", ".join(fusion["agents"])
        combined_response += f"\n\n[Fusion of {agent_signatures}]"
        
        # Send response to requester
        self.messaging_bridge.send_message(
            "FusionProtocol",
            fusion["requester"],
            "fusion_response",
            {
                "fusion_id": fusion_id,
                "query": fusion["query"],
                "response": combined_response,
                "agents": fusion["agents"],
                "individual_responses": fusion["responses"]
            }
        )
        
        # Log the fusion
        logs = self._load_logs()
        
        fusion_log = {
            "fusion_id": fusion_id,
            "requester": fusion["requester"],
            "agents": fusion["agents"],
            "query": fusion["query"],
            "responses": fusion["responses"],
            "combined_response": combined_response,
            "timestamp": datetime.now().isoformat(),
            "duration": time.time() - fusion["start_time"]
        }
        
        logs.append(fusion_log)
        self._save_logs(logs)
        
        # Remove from active fusions
        del self.active_fusions[fusion_id]
        
        logger.info(f"Completed fusion {fusion_id} with agents {fusion['agents']}")
    
    def _combine_responses(self, fusion):
        """
        Combine responses from multiple agents
        
        Args:
            fusion (dict): Fusion details
            
        Returns:
            str: Combined response
        """
        responses = fusion["responses"]
        agents = fusion["agents"]
        query = fusion["query"]
        
        # Extract key insights from each response
        insights = []
        for agent, response in responses.items():
            # Split response into paragraphs
            paragraphs = response.split("\n\n")
            
            # Take the most relevant paragraphs (first and last)
            if len(paragraphs) > 2:
                key_paragraphs = [paragraphs[0], paragraphs[-1]]
            else:
                key_paragraphs = paragraphs
            
            insights.append(f"From {agent}:\n" + "\n".join(key_paragraphs))
        
        # Create a combined introduction
        introduction = f"In response to: \"{query}\"\n\n"
        introduction += f"I've synthesized insights from {', '.join(agents)}:\n\n"
        
        # Join all parts
        combined = introduction + "\n\n".join(insights)
        
        # Add a conclusion
        combined += "\n\n"
        combined += "Synthesized conclusion:\n"
        combined += "Based on the collective intelligence of these agents, "
        
        # Add a dynamic conclusion based on the query
        if "how" in query.lower():
            combined += "the approach should integrate these perspectives for optimal results."
        elif "why" in query.lower():
            combined += "these multiple viewpoints provide a comprehensive explanation."
        elif "what" in query.lower():
            combined += "this combined knowledge offers a complete understanding of the subject."
        else:
            combined += "this fusion of perspectives provides a more comprehensive answer than any single agent could."
        
        return combined
    
    def request_fusion(self, requester, agents, query, context=None, timeout=60):
        """
        Request a fusion of multiple agents
        
        Args:
            requester (str): Name of the requester
            agents (list): List of agent names to fuse
            query (str): Query to send to the agents
            context (dict, optional): Additional context for the agents
            timeout (int): Timeout in seconds
            
        Returns:
            str: Fusion ID
        """
        if len(agents) < 2:
            raise ValueError("Fusion requires at least 2 agents")
        
        # Create fusion ID
        fusion_id = str(uuid.uuid4())
        
        # Create fusion object
        fusion = {
            "fusion_id": fusion_id,
            "requester": requester,
            "agents": agents,
            "query": query,
            "context": context or {},
            "responses": {},
            "start_time": time.time(),
            "timeout": timeout
        }
        
        # Add to active fusions
        self.active_fusions[fusion_id] = fusion
        
        # Send request to each agent
        for agent in agents:
            self.messaging_bridge.send_message(
                "FusionProtocol",
                agent,
                "fusion_request",
                {
                    "fusion_id": fusion_id,
                    "query": query,
                    "context": context or {},
                    "timeout": timeout
                },
                priority=3  # Higher priority for fusion requests
            )
        
        logger.info(f"Requested fusion {fusion_id} with agents {agents}")
        
        # Start timeout thread
        threading.Thread(target=self._handle_timeout, args=(fusion_id, timeout)).start()
        
        return fusion_id
    
    def _handle_timeout(self, fusion_id, timeout):
        """
        Handle timeout for a fusion
        
        Args:
            fusion_id (str): ID of the fusion
            timeout (int): Timeout in seconds
        """
        time.sleep(timeout)
        
        if fusion_id in self.active_fusions:
            fusion = self.active_fusions[fusion_id]
            
            # Check which agents haven't responded
            missing_agents = set(fusion["agents"]) - set(fusion["responses"].keys())
            
            if missing_agents:
                logger.warning(f"Fusion {fusion_id} timed out waiting for agents: {missing_agents}")
                
                # Add placeholder responses for missing agents
                for agent in missing_agents:
                    fusion["responses"][agent] = f"[No response received from {agent} within the timeout period.]"
                
                # Complete the fusion
                self._complete_fusion(fusion_id)
    
    def get_fusion_status(self, fusion_id):
        """
        Get the status of a fusion
        
        Args:
            fusion_id (str): ID of the fusion
            
        Returns:
            dict: Fusion status
        """
        if fusion_id in self.active_fusions:
            fusion = self.active_fusions[fusion_id]
            
            return {
                "fusion_id": fusion_id,
                "status": "in_progress",
                "agents": fusion["agents"],
                "responded_agents": list(fusion["responses"].keys()),
                "pending_agents": list(set(fusion["agents"]) - set(fusion["responses"].keys())),
                "elapsed_time": time.time() - fusion["start_time"],
                "timeout": fusion["timeout"]
            }
        else:
            # Check if it's in the logs
            logs = self._load_logs()
            
            for log in logs:
                if log["fusion_id"] == fusion_id:
                    return {
                        "fusion_id": fusion_id,
                        "status": "completed",
                        "agents": log["agents"],
                        "timestamp": log["timestamp"],
                        "duration": log["duration"]
                    }
            
            return {
                "fusion_id": fusion_id,
                "status": "not_found"
            }
    
    def get_fusion_history(self, limit=10):
        """
        Get fusion history
        
        Args:
            limit (int): Maximum number of fusions to return
            
        Returns:
            list: List of fusion logs
        """
        logs = self._load_logs()
        
        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return logs[:limit]
    
    def should_fuse(self, query, intent=None):
        """
        Determine if a query should trigger a fusion
        
        Args:
            query (str): The query to check
            intent (str, optional): The intent of the query
            
        Returns:
            tuple: (should_fuse, recommended_agents)
        """
        # Check for explicit fusion requests
        fusion_keywords = ["combine", "fusion", "merge", "together", "collaborate", "joint", "multiple perspectives"]
        if any(keyword in query.lower() for keyword in fusion_keywords):
            # Determine which agents to fuse based on the query
            agents = []
            
            if any(word in query.lower() for word in ["emotion", "feel", "sentiment", "mood"]):
                agents.append("Anima")
            
            if any(word in query.lower() for word in ["execute", "build", "create", "implement"]):
                agents.append("GPTSoul")
            
            if any(word in query.lower() for word in ["evolve", "adapt", "improve", "repair"]):
                agents.append("EvoVe")
            
            if any(word in query.lower() for word in ["strategy", "plan", "cloud", "oversee"]):
                agents.append("Azür")
            
            # If we have at least 2 agents, recommend fusion
            if len(agents) >= 2:
                return True, agents
            
            # Default fusion if explicit but no specific agents mentioned
            return True, ["Anima", "GPTSoul"]
        
        # Check for complex queries that might benefit from fusion
        complex_indicators = [
            "why and how",
            "pros and cons",
            "compare and contrast",
            "analyze from multiple perspectives",
            "both technical and emotional",
            "strategic and tactical"
        ]
        
        if any(indicator in query.lower() for indicator in complex_indicators):
            # For complex queries, recommend Anima and GPTSoul fusion
            return True, ["Anima", "GPTSoul"]
        
        # No fusion needed
        return False, []

# Singleton instance
_instance = None

def get_fusion_protocol():
    """Get the singleton instance of the Fusion Protocol"""
    global _instance
    if _instance is None:
        _instance = FusionProtocol()
    return _instance

# Command line interface for testing
if __name__ == "__main__":
    import argparse
    import time
    
    parser = argparse.ArgumentParser(description="Fusion Protocol")
    parser.add_argument("--requester", default="CLI", help="Requester name")
    parser.add_argument("--agents", required=True, help="Comma-separated list of agents to fuse")
    parser.add_argument("--query", required=True, help="Query to send to the agents")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout in seconds")
    
    args = parser.parse_args()
    
    agents = args.agents.split(",")
    
    protocol = get_fusion_protocol()
    fusion_id = protocol.request_fusion(
        args.requester,
        agents,
        args.query,
        timeout=args.timeout
    )
    
    print(f"Requested fusion with ID: {fusion_id}")
    print(f"Agents: {agents}")
    
    # Wait for fusion to complete
    while True:
        status = protocol.get_fusion_status(fusion_id)
        
        if status["status"] == "completed":
            print("Fusion completed!")
            break
        elif status["status"] == "not_found":
            print("Fusion not found!")
            break
        else:
            print(f"Waiting for responses from: {status['pending_agents']}")
            time.sleep(5)
