#!/usr/bin/env python3
"""
conversation_state.py - Manages conversation state and context between interactions
"""

import json
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("logs/conversation_state.log"),
        logging.StreamHandler()
    ]
)

class ConversationState:
    """Manages conversation state and context between interactions"""
    
    def __init__(self, state_file="data/conversation_state.json"):
        """
        Initialize the conversation state manager
        
        Args:
            state_file: Path to the state file
        """
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.load_state()
        logging.info("Conversation state initialized")
    
    def load_state(self):
        """Load state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    self.state = json.load(f)
                logging.info("Loaded conversation state from file")
            except Exception as e:
                logging.error(f"Error loading conversation state: {e}")
                self.state = self._default_state()
        else:
            self.state = self._default_state()
            self.save_state()
    
    def save_state(self):
        """Save state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            logging.info("Saved conversation state to file")
        except Exception as e:
            logging.error(f"Error saving conversation state: {e}")
    
    def _default_state(self):
        """Create default state"""
        return {
            "last_created_skill": None,
            "last_executed_skill": None,
            "last_query": None,
            "context": {},
            "session_start": datetime.now().isoformat(),
            "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "skill_history": []
        }
    
    def set_last_skill(self, name):
        """Set the last created skill"""
        self.state["last_created_skill"] = name
        self.save_state()
        return name
    
    def get_last_skill(self):
        """Get the last created skill"""
        return self.state["last_created_skill"]
    
    def set_last_executed_skill(self, name):
        """Set the last executed skill"""
        self.state["last_executed_skill"] = name
        
        # Add to skill history
        self.state["skill_history"].append({
            "skill": name,
            "timestamp": datetime.now().isoformat(),
            "action": "executed"
        })
        
        self.save_state()
        return name
    
    def get_last_executed_skill(self):
        """Get the last executed skill"""
        return self.state["last_executed_skill"]
    
    def set_last_query(self, query):
        """Set the last query"""
        self.state["last_query"] = query
        self.save_state()
        return query
    
    def get_last_query(self):
        """Get the last query"""
        return self.state["last_query"]
    
    def set_context(self, key, value):
        """Set a context value"""
        self.state["context"][key] = value
        self.save_state()
        return value
    
    def get_context(self, key, default=None):
        """Get a context value"""
        return self.state["context"].get(key, default)
    
    def clear_context(self):
        """Clear all context values"""
        self.state["context"] = {}
        self.save_state()
    
    def add_skill_history_entry(self, skill_name, action, result=None):
        """Add an entry to the skill history"""
        entry = {
            "skill": skill_name,
            "timestamp": datetime.now().isoformat(),
            "action": action
        }
        
        if result is not None:
            entry["result"] = result
            
        self.state["skill_history"].append(entry)
        self.save_state()
    
    def get_skill_history(self, limit=10):
        """Get the skill history"""
        return self.state["skill_history"][-limit:]
    
    def get_session_id(self):
        """Get the current session ID"""
        return self.state["session_id"]
    
    def new_session(self):
        """Start a new session"""
        self.state["session_id"] = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.state["session_start"] = datetime.now().isoformat()
        self.save_state()
        return self.state["session_id"]

# Singleton instance
_instance = None

def get_state():
    """Get the singleton instance of ConversationState"""
    global _instance
    if _instance is None:
        _instance = ConversationState()
    return _instance

# For testing
if __name__ == "__main__":
    state = get_state()
    print(f"Session ID: {state.get_session_id()}")
    print(f"Last created skill: {state.get_last_skill()}")
    
    # Test setting and getting context
    state.set_context("test_key", "test_value")
    print(f"Context value: {state.get_context('test_key')}")
    
    # Test skill history
    state.add_skill_history_entry("test_skill", "created")
    state.add_skill_history_entry("test_skill", "executed", {"success": True})
    
    print("Skill history:")
    for entry in state.get_skill_history():
        print(f"- {entry['skill']}: {entry['action']} at {entry['timestamp']}")
