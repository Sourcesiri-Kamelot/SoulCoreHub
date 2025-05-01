#!/usr/bin/env python3
"""
Activate PsynetAgent for predictive visualization
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
        logging.FileHandler("psynet_activation_log.log"),
        logging.StreamHandler()
    ]
)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the agent loader
from agent_loader import load_agent_by_name, load_all_agents

def ensure_psynet_integration():
    """Ensure the PsynetIntegration module exists"""
    integration_path = Path("psynet_integration.py")
    
    if not integration_path.exists():
        logging.info("Creating PsynetIntegration module...")
        
        integration_code = """
# psynet_integration.py
# Integration module for Psynet predictive visualization

import json
import os
import time
from datetime import datetime

class PsynetIntegration:
    """Integration with Psynet predictive visualization system"""
    
    def __init__(self):
        self.visualization_queue = []
        self.prediction_models = {}
        self.last_update = datetime.now()
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        config_path = os.path.join("config", "psynet_config.json")
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
            else:
                # Create default config
                default_config = {
                    "prediction_types": ["market", "behavior", "performance", "society", "general"],
                    "visualization_types": ["trend", "network", "heatmap", "timeline", "scenario"],
                    "confidence_thresholds": {
                        "low": 0.3,
                        "medium": 0.6,
                        "high": 0.85
                    },
                    "update_frequency": 3600,  # seconds
                    "retention_period": 30,  # days
                    "default_time_horizon": 14  # days
                }
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception as e:
            print(f"Error loading Psynet config: {e}")
            return {}
    
    def handle_prediction_request(self, request):
        """Handle a prediction request"""
        prediction_type = request.get("prediction_type", "general")
        parameters = request.get("parameters", {})
        time_horizon = parameters.get("time_horizon", self.config.get("default_time_horizon", 14))
        
        # In a real implementation, this would use actual prediction models
        # For now, we'll return a simulated prediction
        
        prediction_id = f"pred_{int(time.time())}"
        confidence = 0.75
        
        result = {
            "prediction_id": prediction_id,
            "type": prediction_type,
            "time_horizon": time_horizon,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
            "data": self._generate_prediction_data(prediction_type, parameters),
            "visualization_id": None
        }
        
        # Generate visualization if requested
        if request.get("visualize", True):
            visualization_id = self.render_prediction(result)
            result["visualization_id"] = visualization_id
        
        return result
    
    def render_prediction(self, prediction):
        """Render a visualization of a prediction"""
        visualization_id = f"viz_{int(time.time())}"
        
        # In a real implementation, this would generate actual visualizations
        # For now, we'll just return an ID
        
        return visualization_id
    
    def render_scenario(self, scenario_request):
        """Render a visualization of a specific scenario"""
        scenario_type = scenario_request.get("scenario_type", "general")
        data = scenario_request.get("data", {})
        
        # In a real implementation, this would generate actual scenario visualizations
        # For now, we'll just return an ID
        
        scenario_id = f"scen_{int(time.time())}"
        
        return scenario_id
    
    def _generate_prediction_data(self, prediction_type, parameters):
        """Generate simulated prediction data"""
        if prediction_type == "market":
            return {
                "trend": "upward",
                "volatility": "medium",
                "key_events": [
                    {"day": 3, "description": "Significant uptick in volume"},
                    {"day": 7, "description": "Resistance level breakthrough"}
                ]
            }
        elif prediction_type == "behavior":
            return {
                "pattern": "cyclical",
                "intensity": "increasing",
                "key_factors": ["environmental", "social", "temporal"]
            }
        elif prediction_type == "performance":
            return {
                "trend": "stable",
                "efficiency": "high",
                "bottlenecks": ["resource_allocation", "communication_delays"]
            }
        elif prediction_type == "society":
            return {
                "cohesion": "strengthening",
                "activity_level": "high",
                "emerging_patterns": ["increased_collaboration", "specialization_shift"]
            }
        else:  # general
            return {
                "confidence_by_timeframe": {
                    "short_term": 0.85,
                    "medium_term": 0.65,
                    "long_term": 0.45
                },
                "key_factors": ["trend_continuation", "external_influences", "random_variance"]
            }
"""
        
        with open(integration_path, 'w') as f:
            f.write(integration_code)
        
        logging.info("PsynetIntegration module created")
    
    return True

def update_agent_registry(registry_path="config/agent_registry.json"):
    """Update the agent registry to include PsynetAgent if not already present"""
    try:
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        # Check if predictive category exists
        if "predictive" not in registry:
            registry["predictive"] = []
        
        # Check if PsynetAgent is already in the registry
        psynet_exists = False
        for agent in registry["predictive"]:
            if agent.get("name") == "Psynet Agent":
                psynet_exists = True
                break
        
        # Add PsynetAgent if not already in registry
        if not psynet_exists:
            registry["predictive"].append({
                "name": "Psynet Agent",
                "desc": "Provides psychic-level predictive visualization and future scenario modeling",
                "status": "active",
                "interface": "service",
                "module": "agents.predictive.psynet_agent",
                "class": "PsynetAgent"
            })
            
            # Save updated registry
            with open(registry_path, 'w') as f:
                json.dump(registry, f, indent=2)
            
            logging.info("Updated agent registry with PsynetAgent")
        
        # Also update the execution registry
        exec_registry_path = "agent_registry_EXEC.json"
        if os.path.exists(exec_registry_path):
            with open(exec_registry_path, 'r') as f:
                exec_registry = json.load(f)
            
            # Check if predictive category exists
            if "predictive" not in exec_registry:
                exec_registry["predictive"] = []
            
            # Check if PsynetAgent is already in the registry
            psynet_exists = False
            for agent in exec_registry["predictive"]:
                if agent.get("name") == "Psynet Agent":
                    psynet_exists = True
                    break
            
            # Add PsynetAgent if not already in registry
            if not psynet_exists:
                exec_registry["predictive"].append({
                    "name": "Psynet Agent",
                    "desc": "Provides psychic-level predictive visualization and future scenario modeling",
                    "status": "active",
                    "interface": "service",
                    "module": "agents.predictive.psynet_agent",
                    "class": "PsynetAgent"
                })
                
                # Save updated registry
                with open(exec_registry_path, 'w') as f:
                    json.dump(exec_registry, f, indent=2)
                
                logging.info("Updated execution registry with PsynetAgent")
        
        return True
    except Exception as e:
        logging.error(f"Error updating agent registry: {e}")
        return False

def main():
    """Main function to activate PsynetAgent"""
    try:
        # Ensure PsynetIntegration module exists
        ensure_psynet_integration()
        
        # Update agent registry
        update_agent_registry()
        
        # Load PsynetAgent
        logging.info("Loading PsynetAgent...")
        psynet_agent = load_agent_by_name("Psynet Agent")
        
        if not psynet_agent:
            logging.error("Failed to load PsynetAgent")
            return False
        
        # Run the agent
        logging.info("Running PsynetAgent...")
        result = psynet_agent.run()
        
        logging.info(f"PsynetAgent run result: {result}")
        
        # Test a prediction
        logging.info("Testing prediction...")
        test_prediction = psynet_agent.create_prediction(
            "market", 
            {"market": "crypto", "assets": ["BTC", "ETH"], "time_horizon": 14},
            "activation_script"
        )
        
        logging.info(f"Test prediction created: {test_prediction}")
        
        logging.info("PsynetAgent activation completed successfully")
        return True
    
    except Exception as e:
        logging.error(f"Error activating PsynetAgent: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
