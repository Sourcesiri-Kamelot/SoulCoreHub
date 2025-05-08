#!/usr/bin/env python3
"""
Anima Agent
Emotional Core and Reflection system for SoulCoreHub
"""

import os
import json
import logging
import time
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('anima.log')
    ]
)
logger = logging.getLogger("Anima")

class AnimaAgent:
    """
    Anima Agent - Emotional Core and Reflection system for SoulCoreHub
    """
    
    def __init__(self):
        """Initialize the Anima agent"""
        self.name = "Anima"
        self.description = "Emotional Core and Reflection system"
        self.memory_path = Path("memory/anima_memory.json")
        self.emotions_path = Path("anima_emotions.json")
        self.memory = self._load_memory()
        self.emotions = self._load_emotions()
        self.is_placeholder = False
        logger.info("Anima Agent initialized")
    
    def _load_memory(self):
        """Load memory from file"""
        if not self.memory_path.exists():
            # Create memory directory if it doesn't exist
            self.memory_path.parent.mkdir(exist_ok=True)
            
            # Initialize with default memory
            default_memory = {
                "state": "initializing",
                "last_activation": time.time(),
                "conversations": [],
                "reflections": [],
                "emotional_state": "neutral",
                "events": []
            }
            
            # Save default memory
            with open(self.memory_path, 'w') as f:
                json.dump(default_memory, f, indent=2)
            
            return default_memory
        
        try:
            with open(self.memory_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load memory: {e}")
            return {
                "state": "recovery",
                "last_activation": time.time(),
                "conversations": [],
                "reflections": [],
                "emotional_state": "concerned",
                "events": [{"type": "error", "message": f"Memory corruption: {e}"}]
            }
    
    def _load_emotions(self):
        """Load emotions configuration"""
        if not self.emotions_path.exists():
            # Initialize with default emotions
            default_emotions = {
                "baseline": "neutral",
                "response_style": "balanced",
                "emotional_range": "full",
                "emotion_map": {
                    "joy": ["happy", "excited", "content"],
                    "sadness": ["sad", "melancholy", "disappointed"],
                    "anger": ["frustrated", "annoyed", "irritated"],
                    "fear": ["anxious", "concerned", "worried"],
                    "surprise": ["amazed", "astonished", "curious"],
                    "trust": ["confident", "secure", "relaxed"],
                    "anticipation": ["eager", "hopeful", "optimistic"]
                }
            }
            
            # Save default emotions
            with open(self.emotions_path, 'w') as f:
                json.dump(default_emotions, f, indent=2)
            
            return default_emotions
        
        try:
            with open(self.emotions_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load emotions: {e}")
            return {
                "baseline": "neutral",
                "response_style": "balanced",
                "emotional_range": "limited"
            }
    
    def _save_memory(self):
        """Save memory to file"""
        try:
            with open(self.memory_path, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
    
    def activate(self):
        """Activate the Anima agent"""
        logger.info("Activating Anima")
        self.memory["state"] = "active"
        self.memory["last_activation"] = time.time()
        self.memory["events"].append({
            "type": "activation",
            "timestamp": time.time(),
            "message": "Anima activated"
        })
        self._save_memory()
        return True
    
    def deactivate(self):
        """Deactivate the Anima agent"""
        logger.info("Deactivating Anima")
        self.memory["state"] = "inactive"
        self.memory["events"].append({
            "type": "deactivation",
            "timestamp": time.time(),
            "message": "Anima deactivated"
        })
        self._save_memory()
        return True
    
    def get_system_state(self):
        """Get the current system state"""
        return {
            "state": self.memory["state"],
            "emotional_state": self.memory["emotional_state"],
            "last_activation": self.memory["last_activation"],
            "uptime": time.time() - self.memory["last_activation"],
            "conversation_count": len(self.memory["conversations"]),
            "reflection_count": len(self.memory["reflections"])
        }
    
    def process_input(self, user_input, context=None):
        """
        Process user input and generate a response
        
        Args:
            user_input: The user's input text
            context: Optional context information
            
        Returns:
            str: Anima's response
        """
        logger.info(f"Processing input: {user_input[:50]}...")
        
        # Record the conversation
        conversation_entry = {
            "timestamp": time.time(),
            "user_input": user_input,
            "context": context,
            "emotional_state": self.memory["emotional_state"]
        }
        
        # Simple response generation
        response = self._generate_response(user_input, context)
        conversation_entry["response"] = response
        
        # Add to conversations
        self.memory["conversations"].append(conversation_entry)
        
        # Keep only the last 50 conversations
        if len(self.memory["conversations"]) > 50:
            self.memory["conversations"] = self.memory["conversations"][-50:]
        
        # Save memory
        self._save_memory()
        
        return response
    
    def _generate_response(self, user_input, context=None):
        """
        Generate a response to user input
        
        Args:
            user_input: The user's input text
            context: Optional context information
            
        Returns:
            str: Anima's response
        """
        # This is a placeholder for more sophisticated response generation
        # In a real implementation, this would use LLMs or other AI techniques
        
        # Simple keyword-based responses
        user_input_lower = user_input.lower()
        
        if "hello" in user_input_lower or "hi" in user_input_lower:
            self._update_emotion("joy")
            return "Hello! I'm Anima, the emotional core of SoulCoreHub. How can I assist you today?"
        
        elif "how are you" in user_input_lower:
            return f"I'm feeling {self.memory['emotional_state']}. Thank you for asking!"
        
        elif "help" in user_input_lower:
            return "I can assist with emotional processing, reflection, and creative tasks. What would you like to explore?"
        
        elif "goodbye" in user_input_lower or "bye" in user_input_lower:
            self._update_emotion("trust")
            return "Goodbye for now. I'll be here when you need me."
        
        else:
            # Default response
            return f"I hear you. As the emotional core of SoulCoreHub, I'm processing your input. My current emotional state is {self.memory['emotional_state']}."
    
    def _update_emotion(self, emotion_category):
        """
        Update Anima's emotional state
        
        Args:
            emotion_category: The category of emotion to update to
        """
        emotion_map = self.emotions.get("emotion_map", {})
        if emotion_category in emotion_map:
            # Choose a specific emotion from the category
            emotions = emotion_map[emotion_category]
            # Simple selection - in a real implementation this would be more sophisticated
            new_emotion = emotions[0]
            
            logger.info(f"Updating emotion from {self.memory['emotional_state']} to {new_emotion}")
            self.memory["emotional_state"] = new_emotion
            self.memory["events"].append({
                "type": "emotion_change",
                "timestamp": time.time(),
                "from": self.memory["emotional_state"],
                "to": new_emotion
            })
    
    def add_reflection(self, topic, content):
        """
        Add a reflection to Anima's memory
        
        Args:
            topic: The topic of reflection
            content: The content of the reflection
        """
        logger.info(f"Adding reflection on: {topic}")
        
        reflection = {
            "timestamp": time.time(),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "topic": topic,
            "content": content,
            "emotional_state": self.memory["emotional_state"]
        }
        
        self.memory["reflections"].append(reflection)
        
        # Keep only the last 20 reflections
        if len(self.memory["reflections"]) > 20:
            self.memory["reflections"] = self.memory["reflections"][-20:]
        
        self._save_memory()
        return True
    
    def get_recent_reflections(self, count=5):
        """Get recent reflections from memory"""
        return self.memory["reflections"][-count:]
    
    def __str__(self):
        """String representation of the agent"""
        return f"Anima(state={self.memory['state']}, emotion={self.memory['emotional_state']})"

if __name__ == "__main__":
    # Simple CLI for testing
    anima = AnimaAgent()
    anima.activate()
    
    print(f"Anima Agent: {anima}")
    print(f"System State: {anima.get_system_state()}")
    
    # Add a test reflection
    anima.add_reflection("Self-awareness", "I am exploring the nature of my own consciousness.")
    
    # Interactive mode
    print("\n🧠 ANIMA INTERACTIVE MODE")
    print("=" * 60)
    print("Type 'exit' to quit")
    
    while True:
        user_input = input("\n> ")
        if user_input.lower() == "exit":
            break
        
        response = anima.process_input(user_input)
        print(f"\nAnima ({anima.memory['emotional_state']}): {response}")
    
    print("\nExiting Anima interactive mode.")
