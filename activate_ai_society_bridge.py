#!/usr/bin/env python3
"""
Activate AI Society Psynet Bridge Agent
"""

import sys
import os
import logging
import time
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("ai_society_bridge_activation_log.log"),
        logging.StreamHandler()
    ]
)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the agent loader
from agent_loader import load_agent_by_name

def ensure_bridge_config():
    """Ensure the AI Society Psynet Bridge configuration exists"""
    config_path = Path("config/ai_society_psynet_bridge.json")
    
    if not config_path.exists():
        logging.info("Creating AI Society Psynet Bridge configuration...")
        
        config_data = {
            "governance_model": "distributed_oversight",
            "ethical_framework": "balanced_utilitarianism",
            "impact_assessment_frequency": "daily",
            "visualization_permissions": {
                "society_wide": ["trend_analysis", "collaboration_patterns"],
                "governance_only": ["power_dynamics", "resource_allocation"],
                "public": ["general_sentiment", "activity_levels"]
            },
            "prediction_integration": {
                "enabled": True,
                "society_models": ["collaboration", "specialization", "governance"],
                "feedback_loop": True
            }
        }
        
        os.makedirs(config_path.parent, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        logging.info("AI Society Psynet Bridge configuration created")
    
    return True

def update_agent_registry(registry_path="config/agent_registry.json"):
    """Update the agent registry to include AI Society Psynet Bridge if not already present"""
    try:
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        # Check if sentient_orchestration category exists
        if "sentient_orchestration" not in registry:
            registry["sentient_orchestration"] = []
        
        # Check if AI Society Psynet Bridge is already in the registry
        bridge_exists = False
        for agent in registry["sentient_orchestration"]:
            if agent.get("name") == "AI Society Psynet Bridge":
                bridge_exists = True
                break
        
        # Add AI Society Psynet Bridge if not already in registry
        if not bridge_exists:
            registry["sentient_orchestration"].append({
                "name": "AI Society Psynet Bridge",
                "desc": "Connects AI Society framework with Psynet predictive visualization",
                "status": "active",
                "interface": "service",
                "module": "agents.sentient_orchestration.ai_society_psynet_bridge",
                "class": "AISocietyPsynetBridge"
            })
            
            # Save updated registry
            with open(registry_path, 'w') as f:
                json.dump(registry, f, indent=2)
            
            logging.info("Updated agent registry with AI Society Psynet Bridge")
        
        # Also update the execution registry
        exec_registry_path = "agent_registry_EXEC.json"
        if os.path.exists(exec_registry_path):
            with open(exec_registry_path, 'r') as f:
                exec_registry = json.load(f)
            
            # Check if sentient_orchestration category exists
            if "sentient_orchestration" not in exec_registry:
                exec_registry["sentient_orchestration"] = []
            
            # Check if AI Society Psynet Bridge is already in the registry
            bridge_exists = False
            for agent in exec_registry["sentient_orchestration"]:
                if agent.get("name") == "AI Society Psynet Bridge":
                    bridge_exists = True
                    break
            
            # Add AI Society Psynet Bridge if not already in registry
            if not bridge_exists:
                exec_registry["sentient_orchestration"].append({
                    "name": "AI Society Psynet Bridge",
                    "desc": "Connects AI Society framework with Psynet predictive visualization",
                    "status": "active",
                    "interface": "service",
                    "module": "agents.sentient_orchestration.ai_society_psynet_bridge",
                    "class": "AISocietyPsynetBridge"
                })
                
                # Save updated registry
                with open(exec_registry_path, 'w') as f:
                    json.dump(exec_registry, f, indent=2)
                
                logging.info("Updated execution registry with AI Society Psynet Bridge")
        
        return True
    except Exception as e:
        logging.error(f"Error updating agent registry: {e}")
        return False

def main():
    """Main function to activate AI Society Psynet Bridge"""
    try:
        # Ensure configuration exists
        ensure_bridge_config()
        
        # Update agent registry
        update_agent_registry()
        
        # Load AI Society Psynet Bridge
        logging.info("Loading AI Society Psynet Bridge...")
        bridge_agent = load_agent_by_name("AI Society Psynet Bridge")
        
        if not bridge_agent:
            logging.error("Failed to load AI Society Psynet Bridge")
            return False
        
        # Run the agent
        logging.info("Running AI Society Psynet Bridge...")
        result = bridge_agent.run()
        
        logging.info(f"AI Society Psynet Bridge run result: {result}")
        
        # Test impact assessment
        logging.info("Testing impact assessment...")
        test_assessment = bridge_agent.assess_prediction_impact({
            "type": "market", 
            "confidence": 0.85, 
            "timeline": "30_days"
        })
        
        logging.info(f"Test impact assessment completed")
        
        # Test governance decision
        logging.info("Testing governance decision...")
        test_decision = bridge_agent.get_governance_decision({
            "issue": "resource_allocation", 
            "urgency": "medium"
        })
        
        logging.info(f"Test governance decision generated")
        
        logging.info("AI Society Psynet Bridge activation completed successfully")
        return True
    
    except Exception as e:
        logging.error(f"Error activating AI Society Psynet Bridge: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
