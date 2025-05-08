#!/usr/bin/env python3
"""
Anima NLP Intent Parser
This module provides natural language processing capabilities for Anima,
allowing it to understand user intent and route commands appropriately.
"""

import re
import json
import logging
from pathlib import Path
import time
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/anima_nlp.log')
    ]
)
logger = logging.getLogger("AnimaNLP")

class IntentParser:
    """
    Intent Parser for Anima
    Parses natural language to determine user intent and extract parameters
    """
    
    def __init__(self):
        """Initialize the intent parser"""
        self.intents = self._load_intents()
        self.command_tree = self._load_command_tree()
        self.recent_intents = []
        self.intent_stats = defaultdict(int)
        logger.info("Anima NLP Intent Parser initialized")
    
    def _load_intents(self):
        """Load intent patterns from file or use defaults"""
        intent_path = Path("config/anima_intents.json")
        
        if intent_path.exists():
            try:
                with open(intent_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading intents: {e}")
        
        # Default intents
        default_intents = {
            "create": {
                "patterns": [
                    r"create (?:a |an )?(?P<item>\w+)",
                    r"make (?:a |an )?(?P<item>\w+)",
                    r"generate (?:a |an )?(?P<item>\w+)"
                ],
                "parameters": ["item"],
                "examples": ["create a file", "make a project", "generate a report"]
            },
            "search": {
                "patterns": [
                    r"search (?:for )?(?P<query>.+)",
                    r"find (?P<query>.+)",
                    r"look (?:for )?(?P<query>.+)"
                ],
                "parameters": ["query"],
                "examples": ["search for documents", "find my files", "look for images"]
            },
            "activate": {
                "patterns": [
                    r"activate (?P<component>\w+)",
                    r"start (?P<component>\w+)",
                    r"launch (?P<component>\w+)"
                ],
                "parameters": ["component"],
                "examples": ["activate builder", "start anima", "launch system"]
            },
            "status": {
                "patterns": [
                    r"(?:what is|show|get|check) (?:the )?status",
                    r"system status",
                    r"status report"
                ],
                "parameters": [],
                "examples": ["what is the status", "show status", "system status"]
            },
            "help": {
                "patterns": [
                    r"help",
                    r"(?:show|list) commands",
                    r"what can you do"
                ],
                "parameters": [],
                "examples": ["help", "show commands", "what can you do"]
            }
        }
        
        # Save default intents
        intent_path.parent.mkdir(exist_ok=True)
        with open(intent_path, 'w') as f:
            json.dump(default_intents, f, indent=2)
        
        return default_intents
    
    def _load_command_tree(self):
        """Load command tree from file or use defaults"""
        tree_path = Path("config/anima_command_tree.json")
        
        if tree_path.exists():
            try:
                with open(tree_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading command tree: {e}")
        
        # Default command tree
        default_tree = {
            "create": {
                "file": {"handler": "create_file", "params": ["name", "content"]},
                "project": {"handler": "create_project", "params": ["name", "type"]},
                "report": {"handler": "create_report", "params": ["type", "period"]}
            },
            "search": {
                "handler": "search_items",
                "params": ["query", "type"]
            },
            "activate": {
                "builder": {"handler": "activate_builder"},
                "anima": {"handler": "activate_anima"},
                "system": {"handler": "activate_system"}
            },
            "status": {
                "handler": "show_status"
            },
            "help": {
                "handler": "show_help"
            }
        }
        
        # Save default command tree
        tree_path.parent.mkdir(exist_ok=True)
        with open(tree_path, 'w') as f:
            json.dump(default_tree, f, indent=2)
        
        return default_tree
    
    def parse_intent(self, text):
        """
        Parse text to determine intent and extract parameters
        
        Args:
            text: The text to parse
            
        Returns:
            A dictionary with intent, confidence, and parameters
        """
        text = text.strip().lower()
        
        # Track this intent request
        self._track_intent_request(text)
        
        best_match = None
        best_confidence = 0
        best_params = {}
        
        # Check each intent
        for intent_name, intent_data in self.intents.items():
            for pattern in intent_data["patterns"]:
                match = re.search(pattern, text)
                if match:
                    # Calculate confidence based on how much of the text is matched
                    match_length = match.end() - match.start()
                    confidence = match_length / len(text)
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = intent_name
                        
                        # Extract parameters
                        best_params = match.groupdict()
        
        # If no match found, return unknown intent
        if not best_match:
            return {
                "intent": "unknown",
                "confidence": 0,
                "parameters": {},
                "text": text
            }
        
        # Return the parsed intent
        result = {
            "intent": best_match,
            "confidence": best_confidence,
            "parameters": best_params,
            "text": text
        }
        
        # Track this successful intent
        self._track_intent_success(best_match)
        
        return result
    
    def _track_intent_request(self, text):
        """Track an intent request"""
        self.recent_intents.append({
            "text": text,
            "timestamp": time.time()
        })
        
        # Keep only the last 20 intents
        if len(self.recent_intents) > 20:
            self.recent_intents.pop(0)
    
    def _track_intent_success(self, intent):
        """Track a successful intent match"""
        self.intent_stats[intent] += 1
    
    def get_command_handler(self, intent_result):
        """
        Get the appropriate command handler for an intent
        
        Args:
            intent_result: The result from parse_intent
            
        Returns:
            A dictionary with handler and parameters
        """
        intent = intent_result["intent"]
        
        # Unknown intent has no handler
        if intent == "unknown":
            return {
                "handler": "unknown_intent",
                "parameters": intent_result["parameters"]
            }
        
        # Find the handler in the command tree
        try:
            handler_info = self._find_handler_in_tree(self.command_tree, intent, intent_result["parameters"])
            return handler_info
        except Exception as e:
            logger.error(f"Error finding handler: {e}")
            return {
                "handler": "error_handler",
                "parameters": intent_result["parameters"],
                "error": str(e)
            }
    
    def _find_handler_in_tree(self, tree, intent, parameters):
        """
        Find the appropriate handler in the command tree
        
        Args:
            tree: The command tree or subtree
            intent: The intent name
            parameters: The parameters from the intent
            
        Returns:
            A dictionary with handler and parameters
        """
        # If intent is not in tree, return error
        if intent not in tree:
            return {
                "handler": "unknown_intent",
                "parameters": parameters
            }
        
        # Get the subtree for this intent
        subtree = tree[intent]
        
        # If the subtree has a handler, return it
        if "handler" in subtree:
            return {
                "handler": subtree["handler"],
                "parameters": parameters
            }
        
        # Otherwise, try to navigate deeper based on parameters
        for param, value in parameters.items():
            if value in subtree:
                return self._find_handler_in_tree(subtree, value, parameters)
        
        # If no matching parameter, return the first handler found
        for key, value in subtree.items():
            if isinstance(value, dict) and "handler" in value:
                return {
                    "handler": value["handler"],
                    "parameters": parameters
                }
        
        # If no handler found, return error
        return {
            "handler": "unknown_intent",
            "parameters": parameters
        }
    
    def get_intent_stats(self):
        """Get statistics about intent usage"""
        return {
            "total_requests": len(self.recent_intents),
            "intent_counts": dict(self.intent_stats),
            "recent_intents": self.recent_intents[-5:]  # Last 5 intents
        }
    
    def add_intent(self, intent_name, patterns, parameters=None, examples=None):
        """
        Add a new intent to the parser
        
        Args:
            intent_name: The name of the intent
            patterns: List of regex patterns for this intent
            parameters: List of parameter names (optional)
            examples: List of example phrases (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if intent_name in self.intents:
            logger.warning(f"Intent {intent_name} already exists, updating")
        
        self.intents[intent_name] = {
            "patterns": patterns,
            "parameters": parameters or [],
            "examples": examples or []
        }
        
        # Save updated intents
        intent_path = Path("config/anima_intents.json")
        with open(intent_path, 'w') as f:
            json.dump(self.intents, f, indent=2)
        
        return True

# Create a singleton instance
intent_parser = IntentParser()

def parse_text(text):
    """
    Parse text to determine intent and extract parameters
    
    Args:
        text: The text to parse
        
    Returns:
        A dictionary with intent, confidence, and parameters
    """
    return intent_parser.parse_intent(text)

def get_command_handler(intent_result):
    """
    Get the appropriate command handler for an intent
    
    Args:
        intent_result: The result from parse_intent
        
    Returns:
        A dictionary with handler and parameters
    """
    return intent_parser.get_command_handler(intent_result)

if __name__ == "__main__":
    # Test the intent parser
    test_phrases = [
        "create a new file",
        "search for my documents",
        "activate builder mode",
        "what is the system status",
        "help me understand what you can do",
        "this is a random phrase that doesn't match any intent"
    ]
    
    print("Testing Anima NLP Intent Parser")
    print("=" * 40)
    
    for phrase in test_phrases:
        intent_result = parse_text(phrase)
        handler_info = get_command_handler(intent_result)
        
        print(f"\nPhrase: \"{phrase}\"")
        print(f"Intent: {intent_result['intent']} (confidence: {intent_result['confidence']:.2f})")
        print(f"Parameters: {intent_result['parameters']}")
        print(f"Handler: {handler_info['handler']}")
    
    print("\n" + "=" * 40)
    print("Intent Stats:", intent_parser.get_intent_stats())
