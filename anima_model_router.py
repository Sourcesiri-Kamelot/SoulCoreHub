#!/usr/bin/env python3
"""
Anima Model Router
This module provides intelligent routing between different AI models
based on the task requirements, allowing Anima to use the most appropriate
model for each situation.
"""

import json
import logging
import time
from pathlib import Path
import os
import re
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/anima_model_router.log')
    ]
)
logger = logging.getLogger("AnimaModelRouter")

class ModelRouter:
    """
    Model Router for Anima
    Routes requests to the most appropriate AI model based on the task
    """
    
    def __init__(self):
        """Initialize the model router"""
        self.models = self._load_models()
        self.routing_rules = self._load_routing_rules()
        self.usage_stats = defaultdict(int)
        self.recent_routes = []
        self.max_recent = 50
        logger.info("Anima Model Router initialized")
    
    def _load_models(self):
        """Load model configurations from file or use defaults"""
        models_path = Path("config/anima_models.json")
        
        if models_path.exists():
            try:
                with open(models_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading models: {e}")
        
        # Default models
        default_models = {
            "gpt4": {
                "name": "GPT-4",
                "provider": "openai",
                "capabilities": ["reasoning", "creativity", "instruction", "code"],
                "max_tokens": 8192,
                "cost_per_token": 0.00003,
                "latency": "high"
            },
            "gpt3": {
                "name": "GPT-3.5 Turbo",
                "provider": "openai",
                "capabilities": ["reasoning", "instruction", "code"],
                "max_tokens": 4096,
                "cost_per_token": 0.000002,
                "latency": "medium"
            },
            "mistral": {
                "name": "Mistral 7B",
                "provider": "huggingface",
                "capabilities": ["reasoning", "instruction"],
                "max_tokens": 8192,
                "cost_per_token": 0,
                "latency": "medium"
            },
            "llama2": {
                "name": "Llama 2",
                "provider": "meta",
                "capabilities": ["reasoning", "instruction", "code"],
                "max_tokens": 4096,
                "cost_per_token": 0,
                "latency": "medium"
            },
            "stable-diffusion": {
                "name": "Stable Diffusion XL",
                "provider": "stability",
                "capabilities": ["image-generation"],
                "cost_per_image": 0.02,
                "latency": "high"
            },
            "whisper": {
                "name": "Whisper",
                "provider": "openai",
                "capabilities": ["speech-to-text"],
                "cost_per_minute": 0.006,
                "latency": "low"
            }
        }
        
        # Save default models
        models_path.parent.mkdir(exist_ok=True)
        with open(models_path, 'w') as f:
            json.dump(default_models, f, indent=2)
        
        return default_models
    
    def _load_routing_rules(self):
        """Load routing rules from file or use defaults"""
        rules_path = Path("config/anima_routing_rules.json")
        
        if rules_path.exists():
            try:
                with open(rules_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading routing rules: {e}")
        
        # Default routing rules
        default_rules = {
            "default": "gpt3",
            "task_rules": {
                "code_generation": {
                    "model": "gpt4",
                    "patterns": [
                        r"(?i)write (?:a |some )?code",
                        r"(?i)generate (?:a |some )?(?:function|class|script)",
                        r"(?i)implement (?:a |an )?algorithm"
                    ]
                },
                "creative_writing": {
                    "model": "gpt4",
                    "patterns": [
                        r"(?i)write (?:a |an )?(?:story|poem|essay|article)",
                        r"(?i)create (?:a |an )?(?:narrative|description)",
                        r"(?i)compose (?:a |an )?(?:letter|email|message)"
                    ]
                },
                "quick_answer": {
                    "model": "gpt3",
                    "patterns": [
                        r"(?i)what is",
                        r"(?i)how (?:do|does|can)",
                        r"(?i)when (?:is|was|will)",
                        r"(?i)who (?:is|was|are)"
                    ]
                },
                "image_generation": {
                    "model": "stable-diffusion",
                    "patterns": [
                        r"(?i)generate (?:a |an )?image",
                        r"(?i)create (?:a |an )?picture",
                        r"(?i)draw (?:a |an )?"
                    ]
                },
                "speech_recognition": {
                    "model": "whisper",
                    "patterns": [
                        r"(?i)transcribe",
                        r"(?i)speech to text",
                        r"(?i)convert audio"
                    ]
                }
            },
            "capability_fallbacks": {
                "reasoning": ["gpt4", "gpt3", "mistral", "llama2"],
                "creativity": ["gpt4", "gpt3", "llama2"],
                "code": ["gpt4", "gpt3", "llama2"],
                "image-generation": ["stable-diffusion"],
                "speech-to-text": ["whisper"]
            }
        }
        
        # Save default rules
        rules_path.parent.mkdir(exist_ok=True)
        with open(rules_path, 'w') as f:
            json.dump(default_rules, f, indent=2)
        
        return default_rules
    
    def route_request(self, request, task=None, required_capabilities=None):
        """
        Route a request to the most appropriate model
        
        Args:
            request: The text request to route
            task: Optional explicit task type
            required_capabilities: Optional list of required capabilities
            
        Returns:
            A dictionary with the selected model and routing info
        """
        start_time = time.time()
        
        # If task is explicitly provided, use it
        if task and task in self.routing_rules["task_rules"]:
            model_id = self.routing_rules["task_rules"][task]["model"]
            confidence = 1.0
            matched_rule = task
        else:
            # Otherwise, try to infer the task from the request
            model_id, confidence, matched_rule = self._infer_model_from_request(request)
        
        # If required capabilities are specified, ensure the model has them
        if required_capabilities:
            model_id = self._ensure_capabilities(model_id, required_capabilities)
        
        # Get the model details
        model = self.models.get(model_id)
        
        # If model not found, use default
        if not model:
            logger.warning(f"Model {model_id} not found, using default")
            model_id = self.routing_rules["default"]
            model = self.models.get(model_id)
            confidence = 0.5
            matched_rule = "default"
        
        # Record this routing decision
        routing_info = {
            "request": request[:100] if request else "",  # First 100 chars
            "selected_model": model_id,
            "confidence": confidence,
            "matched_rule": matched_rule,
            "timestamp": time.time(),
            "routing_time": time.time() - start_time
        }
        
        self._record_routing(model_id, routing_info)
        
        return {
            "model_id": model_id,
            "model": model,
            "confidence": confidence,
            "matched_rule": matched_rule,
            "routing_time": routing_info["routing_time"]
        }
    
    def _infer_model_from_request(self, request):
        """
        Infer the most appropriate model based on the request text
        
        Args:
            request: The text request
            
        Returns:
            Tuple of (model_id, confidence, matched_rule)
        """
        if not request:
            return self.routing_rules["default"], 0.5, "default"
        
        # Check each task rule
        for task, rule in self.routing_rules["task_rules"].items():
            for pattern in rule["patterns"]:
                if re.search(pattern, request):
                    return rule["model"], 0.8, task
        
        # If no match, use default
        return self.routing_rules["default"], 0.5, "default"
    
    def _ensure_capabilities(self, model_id, required_capabilities):
        """
        Ensure the selected model has all required capabilities,
        or find a fallback model that does
        
        Args:
            model_id: The initially selected model ID
            required_capabilities: List of required capabilities
            
        Returns:
            A model ID that has all required capabilities
        """
        model = self.models.get(model_id)
        
        # Check if the model has all required capabilities
        if model and all(cap in model["capabilities"] for cap in required_capabilities):
            return model_id
        
        # Find a model that has all required capabilities
        for capability in required_capabilities:
            if capability in self.routing_rules["capability_fallbacks"]:
                for fallback_model in self.routing_rules["capability_fallbacks"][capability]:
                    fallback = self.models.get(fallback_model)
                    if fallback and all(cap in fallback["capabilities"] for cap in required_capabilities):
                        logger.info(f"Using fallback model {fallback_model} for capabilities {required_capabilities}")
                        return fallback_model
        
        # If no suitable model found, return the original (may not have all capabilities)
        logger.warning(f"No model with all capabilities {required_capabilities} found, using {model_id}")
        return model_id
    
    def _record_routing(self, model_id, routing_info):
        """Record a routing decision for statistics"""
        self.usage_stats[model_id] += 1
        self.recent_routes.append(routing_info)
        
        # Keep only the most recent routes
        if len(self.recent_routes) > self.max_recent:
            self.recent_routes.pop(0)
    
    def get_usage_stats(self):
        """Get statistics about model usage"""
        return {
            "total_routes": sum(self.usage_stats.values()),
            "model_usage": dict(self.usage_stats),
            "recent_routes": self.recent_routes[-5:]  # Last 5 routes
        }
    
    def add_model(self, model_id, model_config):
        """
        Add a new model to the router
        
        Args:
            model_id: The ID of the model
            model_config: The model configuration
            
        Returns:
            True if successful, False otherwise
        """
        if model_id in self.models:
            logger.warning(f"Model {model_id} already exists, updating")
        
        self.models[model_id] = model_config
        
        # Save updated models
        models_path = Path("config/anima_models.json")
        with open(models_path, 'w') as f:
            json.dump(self.models, f, indent=2)
        
        return True
    
    def add_routing_rule(self, task, model_id, patterns):
        """
        Add a new routing rule
        
        Args:
            task: The task name
            model_id: The model ID to route to
            patterns: List of regex patterns for this task
            
        Returns:
            True if successful, False otherwise
        """
        if task in self.routing_rules["task_rules"]:
            logger.warning(f"Task rule {task} already exists, updating")
        
        self.routing_rules["task_rules"][task] = {
            "model": model_id,
            "patterns": patterns
        }
        
        # Save updated rules
        rules_path = Path("config/anima_routing_rules.json")
        with open(rules_path, 'w') as f:
            json.dump(self.routing_rules, f, indent=2)
        
        return True

# Create a singleton instance
model_router = ModelRouter()

def route_request(request, task=None, required_capabilities=None):
    """
    Route a request to the most appropriate model
    
    Args:
        request: The text request to route
        task: Optional explicit task type
        required_capabilities: Optional list of required capabilities
        
    Returns:
        A dictionary with the selected model and routing info
    """
    return model_router.route_request(request, task, required_capabilities)

if __name__ == "__main__":
    # Test the model router
    test_requests = [
        "Write a Python function to calculate Fibonacci numbers",
        "What is the capital of France?",
        "Generate an image of a sunset over mountains",
        "Write a short story about a robot learning to love",
        "Transcribe this audio file",
        "Explain how quantum computing works"
    ]
    
    print("Testing Anima Model Router")
    print("=" * 40)
    
    for request in test_requests:
        result = route_request(request)
        
        print(f"\nRequest: \"{request}\"")
        print(f"Selected Model: {result['model_id']} ({result['model']['name']})")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Matched Rule: {result['matched_rule']}")
        print(f"Routing Time: {result['routing_time']*1000:.2f}ms")
    
    print("\n" + "=" * 40)
    print("Usage Stats:", model_router.get_usage_stats())
