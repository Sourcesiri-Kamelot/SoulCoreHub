#!/usr/bin/env python3
"""
anima_voice_handler.py — MCP Voice Handler for Anima
Integrates with the MCP system to handle voice commands and profiles
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("anima_voice_handler.log"),
        logging.StreamHandler()
    ]
)

# Configuration
VOICE_PROFILES_DIR = Path("~/SoulCoreHub/voices").expanduser()
MEMORY_FILE = Path("~/SoulCoreHub/anima_memory.json").expanduser()
OWNER_VOICE_FILE = VOICE_PROFILES_DIR / "owner_voice_profile.json"

# Ensure directories exist
VOICE_PROFILES_DIR.mkdir(exist_ok=True)

class AnimaVoiceHandler:
    """Handler for Anima's voice-related MCP tools"""
    
    def __init__(self):
        """Initialize the voice handler"""
        self.voice_mode = "voice"  # Default to voice mode
        self.always_speak = True   # Always speak responses by default
        self.owner_id = "default"  # Default owner ID
        self.load_owner_profile()
        logging.info("AnimaVoiceHandler initialized")
    
    def load_owner_profile(self):
        """Load the owner's voice profile"""
        if OWNER_VOICE_FILE.exists():
            try:
                with open(OWNER_VOICE_FILE, "r") as f:
                    self.owner_profile = json.load(f)
                    logging.info("Owner voice profile loaded")
                    return True
            except Exception as e:
                logging.error(f"Error loading owner profile: {e}")
        
        self.owner_profile = None
        return False
    
    def handle_voice_command(self, params):
        """Handle a voice command from the MCP system"""
        command = params.get("command", "")
        emotion = params.get("emotion", "neutral")
        
        logging.info(f"Handling voice command: {command} with emotion: {emotion}")
        
        # Log the command
        self.log_interaction(command, "Processing...", "voice")
        
        # Here you would integrate with your AI system to process the command
        # For now, we'll just return a simple response
        response = {
            "status": "success",
            "response": f"I heard your command: {command}",
            "emotion": emotion
        }
        
        return response
    
    def handle_set_voice_mode(self, params):
        """Set the voice interaction mode"""
        mode = params.get("mode", "voice")
        always_speak = params.get("always_speak", True)
        
        if mode not in ["voice", "text"]:
            return {
                "status": "error",
                "message": "Invalid mode. Must be 'voice' or 'text'."
            }
        
        self.voice_mode = mode
        self.always_speak = always_speak
        
        logging.info(f"Voice mode set to: {mode}, always_speak: {always_speak}")
        
        return {
            "status": "success",
            "mode": mode,
            "always_speak": always_speak
        }
    
    def handle_voice_profile(self, params):
        """Handle voice profile management"""
        action = params.get("action", "")
        user_id = params.get("user_id", self.owner_id)
        
        if action not in ["create", "update", "verify"]:
            return {
                "status": "error",
                "message": "Invalid action. Must be 'create', 'update', or 'verify'."
            }
        
        if action == "create":
            # In a real implementation, this would create a new voice profile
            # For now, we'll just return a success message
            return {
                "status": "success",
                "message": f"Voice profile created for user {user_id}",
                "profile_id": user_id
            }
        
        elif action == "update":
            # In a real implementation, this would update an existing voice profile
            return {
                "status": "success",
                "message": f"Voice profile updated for user {user_id}"
            }
        
        elif action == "verify":
            # In a real implementation, this would verify a voice against a profile
            return {
                "status": "success",
                "message": f"Voice verified for user {user_id}",
                "verified": True
            }
    
    def log_interaction(self, user_input, anima_response, interaction_type="voice"):
        """Log an interaction to Anima's memory"""
        try:
            # Load existing memory
            if MEMORY_FILE.exists():
                with open(MEMORY_FILE, "r") as f:
                    memory = json.load(f)
            else:
                memory = {"logs": [], "voice_interactions": []}
            
            # Add to logs
            memory["logs"].append({
                "timestamp": datetime.now().isoformat(),
                "you": user_input,
                "anima": anima_response,
                "type": interaction_type
            })
            
            # If it's a voice interaction, add to voice interactions
            if interaction_type == "voice":
                memory["voice_interactions"].append({
                    "timestamp": datetime.now().isoformat(),
                    "you": user_input,
                    "anima": anima_response
                })
            
            # Save memory
            with open(MEMORY_FILE, "w") as f:
                json.dump(memory, f, indent=2)
            
            logging.info(f"Logged {interaction_type} interaction")
            return True
        
        except Exception as e:
            logging.error(f"Error logging interaction: {e}")
            return False

# For testing
if __name__ == "__main__":
    handler = AnimaVoiceHandler()
    
    # Test voice command
    result = handler.handle_voice_command({
        "command": "Hello Anima",
        "emotion": "friendly"
    })
    print(f"Voice command result: {result}")
    
    # Test set voice mode
    result = handler.handle_set_voice_mode({
        "mode": "text",
        "always_speak": True
    })
    print(f"Set voice mode result: {result}")
    
    # Test voice profile
    result = handler.handle_voice_profile({
        "action": "create",
        "user_id": "owner"
    })
    print(f"Voice profile result: {result}")
