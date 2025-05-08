#!/usr/bin/env python3
"""
Query Interpreter for SoulCoreHub
Connects fusion_protocol.py to chat interfaces and query processing
"""

import json
import logging
import os
import sys
from fusion_protocol import get_fusion_protocol
from agent_messaging_bridge import get_bridge
from agent_emotion_state import get_emotion_tracker
import time
import threading
import queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("query_interpreter.log"), logging.StreamHandler()]
)
logger = logging.getLogger("query_interpreter")

class QueryInterpreter:
    """
    Interprets user queries and routes them to appropriate agents or fusion protocol
    """
    
    def __init__(self):
        """Initialize the Query Interpreter"""
        self.fusion_protocol = get_fusion_protocol()
        self.messaging_bridge = get_bridge()
        self.emotion_tracker = get_emotion_tracker()
        
        # Start the messaging bridge if not already running
        self.messaging_bridge.start()
        
        # Register for responses from agents
        self.messaging_bridge.register_callback("QueryInterpreter", self._handle_agent_response)
        
        # Response queue for synchronous operations
        self.response_queue = queue.Queue()
        
        # Active queries
        self.active_queries = {}
        
        logger.info("Query Interpreter initialized")
    
    def _handle_agent_response(self, message):
        """
        Handle responses from agents
        
        Args:
            message (dict): The message to handle
        """
        intent = message.get("intent")
        
        if intent == "query_response":
            # Put the response in the queue
            self.response_queue.put(message)
            
        elif intent == "fusion_response":
            # Handle fusion response
            fusion_data = message.get("message", {})
            query_id = fusion_data.get("query_id")
            
            if query_id and query_id in self.active_queries:
                # Put the response in the queue
                self.response_queue.put(message)
    
    def process_query(self, query, source="cli", timeout=60, force_fusion=False, specific_agents=None):
        """
        Process a user query
        
        Args:
            query (str): The user query
            source (str): Source of the query (e.g., "cli", "web")
            timeout (int): Timeout in seconds
            force_fusion (bool): Force using fusion even if not recommended
            specific_agents (list): Specific agents to use
            
        Returns:
            dict: Response data
        """
        # Check if query should use fusion
        should_fuse, recommended_agents = self.fusion_protocol.should_fuse(query)
        
        # Override with specific agents if provided
        if specific_agents and len(specific_agents) >= 2:
            should_fuse = True
            recommended_agents = specific_agents
        elif force_fusion:
            should_fuse = True
            # Use recommended agents or default to Anima + GPTSoul
            if not recommended_agents or len(recommended_agents) < 2:
                recommended_agents = ["Anima", "GPTSoul"]
        
        # Generate a unique query ID
        query_id = f"query_{int(time.time())}_{hash(query) % 10000}"
        self.active_queries[query_id] = {
            "query": query,
            "source": source,
            "timestamp": time.time()
        }
        
        try:
            if should_fuse:
                # Use fusion protocol
                logger.info(f"Using fusion for query: {query}")
                logger.info(f"Selected agents: {recommended_agents}")
                
                fusion_id = self.fusion_protocol.request_fusion(
                    requester="QueryInterpreter",
                    agents=recommended_agents,
                    query=query,
                    context={"source": source, "query_id": query_id},
                    timeout=timeout
                )
                
                # Wait for response
                start_time = time.time()
                while time.time() - start_time < timeout:
                    try:
                        message = self.response_queue.get(timeout=1)
                        
                        # Check if this is the response we're waiting for
                        if message.get("intent") == "fusion_response":
                            fusion_data = message.get("message", {})
                            if fusion_data.get("query_id") == query_id:
                                # Clean up
                                if query_id in self.active_queries:
                                    del self.active_queries[query_id]
                                
                                # Return the response
                                return {
                                    "type": "fusion",
                                    "query": query,
                                    "response": fusion_data.get("response"),
                                    "agents": fusion_data.get("agents"),
                                    "individual_responses": fusion_data.get("individual_responses"),
                                    "processing_time": time.time() - start_time
                                }
                        
                        # Put other messages back in the queue
                        self.response_queue.put(message)
                        
                    except queue.Empty:
                        # Check fusion status
                        status = self.fusion_protocol.get_fusion_status(fusion_id)
                        if status["status"] == "completed":
                            # Fusion completed but we missed the message
                            # This shouldn't happen normally, but just in case
                            if query_id in self.active_queries:
                                del self.active_queries[query_id]
                            
                            return {
                                "type": "fusion",
                                "query": query,
                                "response": "Fusion completed but response was not received. Please check fusion logs.",
                                "agents": recommended_agents,
                                "processing_time": time.time() - start_time
                            }
                
                # Timeout
                logger.warning(f"Timeout waiting for fusion response: {query}")
                
                if query_id in self.active_queries:
                    del self.active_queries[query_id]
                
                return {
                    "type": "error",
                    "query": query,
                    "response": "Timeout waiting for response from agents.",
                    "processing_time": time.time() - start_time
                }
                
            else:
                # Use single agent (default to GPTSoul for general queries)
                agent = "GPTSoul"
                
                # Select agent based on query content
                if any(word in query.lower() for word in ["emotion", "feel", "sentiment", "mood"]):
                    agent = "Anima"
                elif any(word in query.lower() for word in ["evolve", "adapt", "improve", "repair"]):
                    agent = "EvoVe"
                elif any(word in query.lower() for word in ["strategy", "plan", "cloud", "oversee"]):
                    agent = "Azür"
                
                logger.info(f"Using single agent for query: {agent}")
                
                # Send query to agent
                self.messaging_bridge.send_message(
                    "QueryInterpreter",
                    agent,
                    "query_request",
                    {
                        "query": query,
                        "query_id": query_id,
                        "source": source
                    }
                )
                
                # Wait for response
                start_time = time.time()
                while time.time() - start_time < timeout:
                    try:
                        message = self.response_queue.get(timeout=1)
                        
                        # Check if this is the response we're waiting for
                        if message.get("intent") == "query_response":
                            response_data = message.get("message", {})
                            if response_data.get("query_id") == query_id:
                                # Clean up
                                if query_id in self.active_queries:
                                    del self.active_queries[query_id]
                                
                                # Analyze response for emotional changes
                                response_text = response_data.get("response", "")
                                self.emotion_tracker.analyze_response(agent, response_text)
                                
                                # Modify response based on emotional state
                                modified_response = self.emotion_tracker.modify_text_with_emotion(agent, response_text)
                                
                                # Return the response
                                return {
                                    "type": "single",
                                    "query": query,
                                    "response": modified_response,
                                    "agent": agent,
                                    "processing_time": time.time() - start_time
                                }
                        
                        # Put other messages back in the queue
                        self.response_queue.put(message)
                        
                    except queue.Empty:
                        pass
                
                # Timeout
                logger.warning(f"Timeout waiting for response from {agent}: {query}")
                
                if query_id in self.active_queries:
                    del self.active_queries[query_id]
                
                return {
                    "type": "error",
                    "query": query,
                    "response": f"Timeout waiting for response from {agent}.",
                    "processing_time": time.time() - start_time
                }
        
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            
            if query_id in self.active_queries:
                del self.active_queries[query_id]
            
            return {
                "type": "error",
                "query": query,
                "response": f"Error processing query: {str(e)}",
                "processing_time": 0
            }

# Singleton instance
_instance = None

def get_query_interpreter():
    """Get the singleton instance of the Query Interpreter"""
    global _instance
    if _instance is None:
        _instance = QueryInterpreter()
    return _instance

# Command line interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Query Interpreter")
    parser.add_argument("--query", help="Query to process")
    parser.add_argument("--fusion", action="store_true", help="Force fusion")
    parser.add_argument("--agents", help="Comma-separated list of agents to use")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout in seconds")
    
    args = parser.parse_args()
    
    if args.query:
        interpreter = get_query_interpreter()
        
        specific_agents = args.agents.split(",") if args.agents else None
        
        response = interpreter.process_query(
            args.query,
            force_fusion=args.fusion,
            specific_agents=specific_agents,
            timeout=args.timeout
        )
        
        print("\n" + "="*50)
        print(f"Query: {args.query}")
        print(f"Type: {response['type']}")
        
        if response['type'] == 'fusion':
            print(f"Agents: {', '.join(response['agents'])}")
        elif response['type'] == 'single':
            print(f"Agent: {response['agent']}")
        
        print(f"Processing time: {response['processing_time']:.2f}s")
        print("="*50)
        print(f"\n{response['response']}\n")
    else:
        # Interactive mode
        interpreter = get_query_interpreter()
        
        print("SoulCoreHub Query Interpreter")
        print("Type 'exit' to quit")
        print("Type 'fusion:' to force fusion")
        print("Type 'agents:Anima,GPTSoul:' to specify agents")
        
        while True:
            try:
                user_input = input("\n> ")
                
                if user_input.lower() == 'exit':
                    break
                
                force_fusion = False
                specific_agents = None
                
                # Check for fusion prefix
                if user_input.startswith("fusion:"):
                    force_fusion = True
                    user_input = user_input[7:].strip()
                
                # Check for agents prefix
                if user_input.startswith("agents:"):
                    parts = user_input.split(":", 2)
                    if len(parts) >= 3:
                        specific_agents = parts[1].split(",")
                        user_input = parts[2].strip()
                
                response = interpreter.process_query(
                    user_input,
                    force_fusion=force_fusion,
                    specific_agents=specific_agents
                )
                
                if response['type'] == 'fusion':
                    print(f"\n[Fusion of {', '.join(response['agents'])}]")
                elif response['type'] == 'single':
                    print(f"\n[{response['agent']}]")
                
                print(f"{response['response']}")
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
