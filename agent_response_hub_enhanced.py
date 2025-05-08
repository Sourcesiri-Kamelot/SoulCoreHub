#!/usr/bin/env python3
# agent_response_hub_enhanced.py - Enhanced central hub for agent responses with LLM integration

import json
import sys
import os
from datetime import datetime
import logging
import random
from pathlib import Path

# Import the Anima agent
from anima_agent import AnimaAgent

# Import the Skill Integration
try:
    from anima_skill_integration import AnimaSkillIntegration
    SKILL_INTEGRATION_AVAILABLE = True
except ImportError:
    SKILL_INTEGRATION_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("logs/agent_response_hub.log"),
        logging.StreamHandler()
    ]
)

# Define agent personalities and response styles
AGENT_PROFILES = {
    "anima": {
        "name": "Anima",
        "personality": "Emotional, intuitive, and empathetic. Speaks with feeling and uses metaphors.",
        "color": "#bb86fc",
        "model": "wizardlm-uncensored"
    },
    "gptsoul": {
        "name": "GPTSoul",
        "personality": "Logical, precise, and analytical. Focuses on facts and structured thinking.",
        "color": "#03dac6",
        "model": "qwen:7b"
    },
    "azur": {
        "name": "Azür",
        "personality": "Technical, cloud-focused, and infrastructure-oriented. Thinks in systems and networks.",
        "color": "#3700b3",
        "model": "mistral"
    },
    "evove": {
        "name": "EvoVe",
        "personality": "Adaptive, evolutionary, and resilient. Focuses on improvement and mutation.",
        "color": "#cf6679",
        "model": "wizardlm-uncensored"
    }
}

# Agent instances
agent_instances = {}
skill_integration = None

def get_agent_instance(agent_name):
    """Get or create an agent instance"""
    if agent_name not in agent_instances:
        profile = AGENT_PROFILES.get(agent_name)
        if profile:
            agent_instances[agent_name] = AnimaAgent(model=profile.get("model", "wizardlm-uncensored"))
        else:
            return None
    return agent_instances[agent_name]

def get_skill_integration():
    """Get or create the skill integration"""
    global skill_integration
    if SKILL_INTEGRATION_AVAILABLE and skill_integration is None:
        skill_integration = AnimaSkillIntegration()
    return skill_integration

def is_skill_request(query):
    """Determine if a query is related to skills"""
    if not SKILL_INTEGRATION_AVAILABLE:
        return False
        
    query_lower = query.lower()
    skill_keywords = [
        "create a skill", "make a skill", "write a skill",
        "run skill", "execute skill", "use skill",
        "list skills", "show skills", "what skills",
        "explain skill", "describe skill", "how does skill",
        "improve skill", "enhance skill", "update skill", "fix skill",
        "delete skill", "remove skill"
    ]
    
    return any(keyword in query_lower for keyword in skill_keywords)

def get_agent_response(agent_name, query, context=None):
    """
    Get a response from a specific agent
    
    Args:
        agent_name: Name of the agent (anima, gptsoul, azur, evove)
        query: The question or command for the agent
        context: Optional context information
        
    Returns:
        Dictionary with agent response
    """
    agent_name = agent_name.lower()
    if agent_name not in AGENT_PROFILES:
        return {
            "error": f"Unknown agent: {agent_name}",
            "timestamp": datetime.now().isoformat()
        }
    
    # Log the query
    log_dir = Path("logs/agent_queries")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{agent_name}_queries.log"
    
    with open(log_file, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {query}\n")
    
    # Check if this is a skill request for Anima
    if agent_name == "anima" and is_skill_request(query):
        integration = get_skill_integration()
        if integration:
            try:
                response = integration.handle_skill_request(query)
                return {
                    "agent": AGENT_PROFILES[agent_name]["name"],
                    "response": response,
                    "timestamp": datetime.now().isoformat(),
                    "color": AGENT_PROFILES[agent_name]["color"]
                }
            except Exception as e:
                logging.error(f"Error handling skill request: {e}")
                # Fall back to normal response
    
    # Get the agent instance
    agent = get_agent_instance(agent_name)
    if not agent:
        return {
            "error": f"Failed to initialize agent: {agent_name}",
            "timestamp": datetime.now().isoformat()
        }
    
    # Get response from the agent
    try:
        response = agent.get_response(query)
        
        return {
            "agent": AGENT_PROFILES[agent_name]["name"],
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "color": AGENT_PROFILES[agent_name]["color"]
        }
    except Exception as e:
        logging.error(f"Error getting response from {agent_name}: {e}")
        return {
            "agent": AGENT_PROFILES[agent_name]["name"],
            "response": f"I'm experiencing a momentary lapse in my thought process. Please try again.",
            "timestamp": datetime.now().isoformat(),
            "color": AGENT_PROFILES[agent_name]["color"],
            "error": str(e)
        }

def get_multi_agent_responses(query, agents=None):
    """Get responses from multiple agents"""
    if agents is None:
        agents = list(AGENT_PROFILES.keys())
    
    responses = {}
    for agent in agents:
        if agent in AGENT_PROFILES:
            responses[agent] = get_agent_response(agent, query)
    
    return responses

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python agent_response_hub_enhanced.py <agent_name> <query>")
        print("   or: python agent_response_hub_enhanced.py all <query>")
        sys.exit(1)
    
    agent_name = sys.argv[1].lower()
    query = sys.argv[2]
    
    if agent_name == "all":
        responses = get_multi_agent_responses(query)
        print(json.dumps(responses, indent=2))
    else:
        response = get_agent_response(agent_name, query)
        print(json.dumps(response, indent=2))
