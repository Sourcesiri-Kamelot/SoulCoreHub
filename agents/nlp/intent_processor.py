#!/usr/bin/env python3
"""
Intent Processor - NLP module for understanding user intents in SoulCoreHub
"""

import re
import json
import os
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("intent_processor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("IntentProcessor")

class IntentProcessor:
    """NLP processor for understanding user intents"""
    
    def __init__(self, config_file="config/nlp_intents.json"):
        """Initialize the intent processor"""
        self.config_file = config_file
        self.intents = {}
        self.keywords = defaultdict(list)
        self.patterns = {}
        self.load_intents()
    
    def load_intents(self):
        """Load intents from configuration file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                
                self.intents = config.get("intents", {})
                
                # Process keywords and patterns
                for intent, data in self.intents.items():
                    # Add keywords
                    for keyword in data.get("keywords", []):
                        self.keywords[keyword.lower()].append(intent)
                    
                    # Compile regex patterns
                    for pattern in data.get("patterns", []):
                        try:
                            regex = re.compile(pattern, re.IGNORECASE)
                            if intent not in self.patterns:
                                self.patterns[intent] = []
                            self.patterns[intent].append(regex)
                        except re.error:
                            logger.error(f"Invalid regex pattern for intent {intent}: {pattern}")
                
                logger.info(f"Loaded {len(self.intents)} intents")
            except Exception as e:
                logger.error(f"Error loading intents: {e}")
                self.create_default_intents()
        else:
            logger.warning(f"Intents file not found: {self.config_file}")
            self.create_default_intents()
    
    def create_default_intents(self):
        """Create default intents configuration"""
        self.intents = {
            "build_app": {
                "description": "Intent to build an application",
                "keywords": ["build", "create", "develop", "make", "app", "application", "project"],
                "patterns": [
                    r"build\s+(?:me\s+)?a\s+(\w+)(?:\s+app)?",
                    r"create\s+(?:me\s+)?a\s+(\w+)(?:\s+app)?",
                    r"develop\s+(?:me\s+)?a\s+(\w+)(?:\s+app)?"
                ],
                "examples": [
                    "build me a todo app",
                    "create a weather application",
                    "develop a note taking app"
                ],
                "parameters": ["app_type"]
            },
            "build_website": {
                "description": "Intent to build a website",
                "keywords": ["build", "create", "develop", "make", "website", "site", "webpage", "web"],
                "patterns": [
                    r"build\s+(?:me\s+)?a\s+(\w+)(?:\s+website)?",
                    r"create\s+(?:me\s+)?a\s+(\w+)(?:\s+website)?",
                    r"develop\s+(?:me\s+)?a\s+(\w+)(?:\s+website)?"
                ],
                "examples": [
                    "build me a portfolio website",
                    "create an e-commerce site",
                    "develop a blog website"
                ],
                "parameters": ["website_type"]
            },
            "build_api": {
                "description": "Intent to build an API",
                "keywords": ["build", "create", "develop", "make", "api", "rest", "graphql", "endpoint"],
                "patterns": [
                    r"build\s+(?:me\s+)?a\s+(\w+)(?:\s+api)?",
                    r"create\s+(?:me\s+)?a\s+(\w+)(?:\s+api)?",
                    r"develop\s+(?:me\s+)?a\s+(\w+)(?:\s+api)?"
                ],
                "examples": [
                    "build me a REST API",
                    "create a GraphQL API",
                    "develop a weather API"
                ],
                "parameters": ["api_type"]
            }
        }
        
        # Process keywords and patterns
        for intent, data in self.intents.items():
            # Add keywords
            for keyword in data.get("keywords", []):
                self.keywords[keyword.lower()].append(intent)
            
            # Compile regex patterns
            for pattern in data.get("patterns", []):
                try:
                    regex = re.compile(pattern, re.IGNORECASE)
                    if intent not in self.patterns:
                        self.patterns[intent] = []
                    self.patterns[intent].append(regex)
                except re.error:
                    logger.error(f"Invalid regex pattern for intent {intent}: {pattern}")
        
        # Save default intents
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump({"intents": self.intents}, f, indent=2)
            logger.info(f"Created default intents configuration")
        except Exception as e:
            logger.error(f"Error saving default intents: {e}")
    
    def detect_intent(self, text):
        """
        Detect the intent from the given text
        
        Args:
            text (str): The text to analyze
            
        Returns:
            dict: Intent information with confidence score and extracted parameters
        """
        text = text.lower()
        
        # Initialize results
        results = []
        
        # Check for keyword matches
        keyword_matches = {}
        for word in text.split():
            word = word.strip(".,!?;:")
            if word in self.keywords:
                for intent in self.keywords[word]:
                    if intent not in keyword_matches:
                        keyword_matches[intent] = 0
                    keyword_matches[intent] += 1
        
        # Check for pattern matches
        pattern_matches = {}
        extracted_params = {}
        
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                match = pattern.search(text)
                if match:
                    if intent not in pattern_matches:
                        pattern_matches[intent] = 0
                    pattern_matches[intent] += 1
                    
                    # Extract parameters
                    if match.groups():
                        if intent not in extracted_params:
                            extracted_params[intent] = {}
                        
                        # Get parameter names from intent definition
                        param_names = self.intents[intent].get("parameters", [])
                        
                        # Map extracted values to parameter names
                        for i, value in enumerate(match.groups()):
                            if i < len(param_names):
                                param_name = param_names[i]
                                extracted_params[intent][param_name] = value
        
        # Combine keyword and pattern matches
        all_intents = set(list(keyword_matches.keys()) + list(pattern_matches.keys()))
        
        for intent in all_intents:
            # Calculate confidence score (simple version)
            keyword_score = keyword_matches.get(intent, 0) * 0.5
            pattern_score = pattern_matches.get(intent, 0) * 1.0
            confidence = min(1.0, (keyword_score + pattern_score) / 2)
            
            results.append({
                "intent": intent,
                "confidence": confidence,
                "parameters": extracted_params.get(intent, {}),
                "description": self.intents.get(intent, {}).get("description", "")
            })
        
        # Sort by confidence
        results.sort(key=lambda x: x["confidence"], reverse=True)
        
        if results:
            return results[0]
        else:
            return {"intent": "unknown", "confidence": 0.0, "parameters": {}, "description": "Unknown intent"}
    
    def get_intent_examples(self, intent=None):
        """
        Get examples for a specific intent or all intents
        
        Args:
            intent (str, optional): The intent to get examples for
            
        Returns:
            dict: Examples for the specified intent or all intents
        """
        if intent and intent in self.intents:
            return {intent: self.intents[intent].get("examples", [])}
        else:
            examples = {}
            for intent_name, intent_data in self.intents.items():
                examples[intent_name] = intent_data.get("examples", [])
            return examples

# Example usage
if __name__ == "__main__":
    processor = IntentProcessor()
    
    # Test some examples
    test_inputs = [
        "build me a todo app",
        "create a weather website",
        "develop a REST API",
        "make a note taking application",
        "I want to build a portfolio site"
    ]
    
    for input_text in test_inputs:
        result = processor.detect_intent(input_text)
        print(f"Input: {input_text}")
        print(f"Detected intent: {result['intent']} (confidence: {result['confidence']:.2f})")
        if result["parameters"]:
            print(f"Parameters: {result['parameters']}")
        print()
