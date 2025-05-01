#!/usr/bin/env python3
"""
anima_enhanced_core.py — Enhanced core for Anima with all advanced capabilities
Integrates hierarchical memory, dynamic voice, multimodal integration, autonomous learning, and enhanced MCP
"""

import os
import sys
import json
import logging
import time
import threading
import asyncio
from pathlib import Path
from datetime import datetime

# Import enhanced components
from hierarchical_memory import HierarchicalMemory
from dynamic_voice import DynamicVoice
from multimodal_integration import MultimodalIntegration
from autonomous_learning import AutonomousLearning
from enhanced_mcp_integration import EnhancedMCPIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("anima_enhanced_core.log"),
        logging.StreamHandler()
    ]
)

class AnimaEnhancedCore:
    """Enhanced core for Anima with all advanced capabilities"""
    
    def __init__(self, base_path=None):
        """Initialize the enhanced Anima core"""
        self.base_path = base_path or Path.home() / "SoulCoreHub"
        
        # Initialize components
        logging.info("Initializing hierarchical memory...")
        self.memory = HierarchicalMemory(self.base_path)
        
        logging.info("Initializing dynamic voice...")
        self.voice = DynamicVoice(self.base_path)
        
        logging.info("Initializing multimodal integration...")
        self.multimodal = MultimodalIntegration(self.base_path)
        
        logging.info("Initializing autonomous learning...")
        self.learning = AutonomousLearning(self.base_path)
        
        logging.info("Initializing enhanced MCP integration...")
        self.mcp = EnhancedMCPIntegration(self.base_path)
        
        # Core settings
        self.settings = {
            "voice_enabled": True,
            "voice_speed": 170,
            "current_voice_personality": "default",
            "memory_consolidation_interval": 3600,  # 1 hour
            "learning_interval": 7200,  # 2 hours
            "environment_monitoring_interval": 60,  # 1 minute
            "default_emotion": "neutral",
            "multimodal_enabled": True,
            "autonomous_learning_enabled": True
        }
        self.settings_file = self.base_path / "anima_enhanced_settings.json"
        
        # Load settings
        self._load_settings()
        
        # Current state
        self.current_emotion = self.settings["default_emotion"]
        self.current_context = {}
        self.running = False
        self.main_thread = None
        
        logging.info("Anima enhanced core initialized")
    
    def _load_settings(self):
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, "r") as f:
                    loaded_settings = json.load(f)
                    # Update settings with loaded values
                    for key, value in loaded_settings.items():
                        if key in self.settings:
                            self.settings[key] = value
                logging.info("Loaded settings")
        except Exception as e:
            logging.error(f"Error loading settings: {e}")
    
    def _save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=2)
            logging.info("Saved settings")
        except Exception as e:
            logging.error(f"Error saving settings: {e}")
    
    def start(self):
        """Start the enhanced Anima core"""
        if self.running:
            logging.warning("Anima enhanced core is already running")
            return False
        
        try:
            # Start MCP connection
            logging.info("Starting MCP connection...")
            self.mcp.start_connection()
            
            # Start memory consolidation
            logging.info("Starting memory consolidation...")
            self.memory.start_consolidation(self.settings["memory_consolidation_interval"])
            
            # Start autonomous learning if enabled
            if self.settings["autonomous_learning_enabled"]:
                logging.info("Starting autonomous learning...")
                self.learning.start_autonomous_learning(self.settings["learning_interval"])
            
            # Start environment monitoring if multimodal is enabled
            if self.settings["multimodal_enabled"]:
                logging.info("Starting environment monitoring...")
                self.multimodal.start_environment_monitoring(self.settings["environment_monitoring_interval"])
            
            # Set voice personality
            if self.settings["voice_enabled"]:
                logging.info(f"Setting voice personality to {self.settings['current_voice_personality']}...")
                self.voice.set_personality(self.settings["current_voice_personality"])
            
            # Set running state
            self.running = True
            
            # Speak startup message
            if self.settings["voice_enabled"]:
                self.voice.speak("Anima enhanced core is now running.", "excited")
            
            logging.info("Anima enhanced core started")
            return True
        
        except Exception as e:
            logging.error(f"Error starting Anima enhanced core: {e}")
            return False
    
    def stop(self):
        """Stop the enhanced Anima core"""
        if not self.running:
            logging.warning("Anima enhanced core is not running")
            return False
        
        try:
            # Stop MCP connection
            logging.info("Stopping MCP connection...")
            self.mcp.stop_connection()
            
            # Stop memory consolidation
            logging.info("Stopping memory consolidation...")
            self.memory.stop_consolidation()
            
            # Stop autonomous learning if enabled
            if self.settings["autonomous_learning_enabled"]:
                logging.info("Stopping autonomous learning...")
                self.learning.stop_autonomous_learning()
            
            # Stop environment monitoring if multimodal is enabled
            if self.settings["multimodal_enabled"]:
                logging.info("Stopping environment monitoring...")
                self.multimodal.stop_environment_monitoring()
            
            # Speak shutdown message
            if self.settings["voice_enabled"]:
                self.voice.speak("Anima enhanced core is shutting down.", "serene")
            
            # Set running state
            self.running = False
            
            logging.info("Anima enhanced core stopped")
            return True
        
        except Exception as e:
            logging.error(f"Error stopping Anima enhanced core: {e}")
            return False
    
    def process_input(self, user_input, context=None):
        """Process user input and generate a response"""
        if not self.running:
            return "Anima enhanced core is not running. Please start it first."
        
        try:
            timestamp = datetime.now().isoformat()
            context = context or {}
            
            # Add input to sensory memory
            self.memory.add_memory(
                user_input,
                memory_type="sensory",
                emotions=[self.current_emotion],
                context=context
            )
            
            # Determine appropriate response emotion based on input
            response_emotion = self._determine_response_emotion(user_input)
            
            # Generate response (simplified implementation)
            response = self._generate_response(user_input, response_emotion, context)
            
            # Add response to working memory
            self.memory.add_memory(
                response,
                memory_type="working",
                emotions=[response_emotion],
                context={"user_input": user_input, **context}
            )
            
            # Learn from this interaction
            self.learning.learn_from_interaction(user_input, response, context)
            
            # Speak response if voice is enabled
            if self.settings["voice_enabled"]:
                self.voice.speak(response, response_emotion)
            
            # Update current emotion
            self.current_emotion = response_emotion
            
            return response
        
        except Exception as e:
            logging.error(f"Error processing input: {e}")
            return f"I'm sorry, I encountered an error while processing your input: {str(e)}"
    
    def _determine_response_emotion(self, user_input):
        """Determine appropriate response emotion based on user input"""
        # This is a simplified implementation
        # In a real system, this would use more sophisticated sentiment analysis
        
        # Check for explicit emotion words
        positive_emotions = {"happy", "glad", "excited", "pleased", "joy", "love", "like", "good"}
        negative_emotions = {"sad", "angry", "upset", "disappointed", "frustrated", "hate", "dislike", "bad"}
        curious_words = {"what", "how", "why", "when", "where", "who", "which", "?"}
        
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in positive_emotions):
            return "joy"
        
        if any(word in user_input_lower for word in negative_emotions):
            return "compassionate"
        
        if any(word in user_input_lower for word in curious_words):
            return "curious"
        
        # Default to neutral with some randomness
        emotions = ["neutral", "thoughtful", "interested", "curious", "serene"]
        return random.choice(emotions)
    
    def _generate_response(self, user_input, emotion, context):
        """Generate a response to user input"""
        # This is a placeholder for response generation
        # In a real implementation, this would use an LLM or other response generation method
        
        # For now, use MCP to generate a response if available
        try:
            # Try to find a suitable tool for this input
            tool = self.mcp.select_tool_for_task(user_input, context)
            
            if tool:
                # Use the selected tool
                tool_name = tool["name"]
                tool_emotion = self.mcp.get_tool_emotion(tool_name)["preferred_emotion"]
                
                # Invoke the tool
                response = self.mcp.invoke_tool(
                    tool_name,
                    {"input": user_input},
                    emotion=tool_emotion,
                    context_attributes=context
                )
                
                if "result" in response:
                    return str(response["result"])
            
            # If no tool or tool failed, fall back to a simple response
            return f"I processed your input: '{user_input}' with emotion: {emotion}"
        
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return f"I'm thinking about your input: '{user_input}'"
    
    def set_voice_personality(self, personality):
        """Set the voice personality"""
        if not self.voice.set_personality(personality):
            return False
        
        self.settings["current_voice_personality"] = personality
        self._save_settings()
        return True
    
    def set_voice_speed(self, speed):
        """Set the voice speed"""
        if not self.voice.set_voice_speed(speed):
            return False
        
        self.settings["voice_speed"] = speed
        self._save_settings()
        return True
    
    def enable_voice(self, enabled=True):
        """Enable or disable voice"""
        self.settings["voice_enabled"] = enabled
        self._save_settings()
        return True
    
    def enable_multimodal(self, enabled=True):
        """Enable or disable multimodal integration"""
        self.settings["multimodal_enabled"] = enabled
        
        if enabled and self.running:
            self.multimodal.start_environment_monitoring(self.settings["environment_monitoring_interval"])
        elif not enabled and self.running:
            self.multimodal.stop_environment_monitoring()
        
        self._save_settings()
        return True
    
    def enable_autonomous_learning(self, enabled=True):
        """Enable or disable autonomous learning"""
        self.settings["autonomous_learning_enabled"] = enabled
        
        if enabled and self.running:
            self.learning.start_autonomous_learning(self.settings["learning_interval"])
        elif not enabled and self.running:
            self.learning.stop_autonomous_learning()
        
        self._save_settings()
        return True
    
    def capture_image(self):
        """Capture and analyze an image from the camera"""
        if not self.settings["multimodal_enabled"]:
            return {"error": "Multimodal integration is disabled"}
        
        return self.multimodal.capture_image_from_camera()
    
    def analyze_audio(self, duration=5):
        """Record and analyze audio"""
        if not self.settings["multimodal_enabled"]:
            return {"error": "Multimodal integration is disabled"}
        
        return self.multimodal.analyze_audio(duration=duration)
    
    def get_environment_status(self):
        """Get the current environment status"""
        if not self.settings["multimodal_enabled"]:
            return {"error": "Multimodal integration is disabled"}
        
        return self.multimodal.get_environment_status()
    
    def get_next_curiosity_topic(self):
        """Get the next topic to explore based on curiosity"""
        return self.learning.get_next_curiosity_topic()
    
    def get_memory_stats(self):
        """Get memory statistics"""
        return self.memory.get_memory_stats()
    
    def get_learning_stats(self):
        """Get learning statistics"""
        return self.learning.get_learning_stats()
    
    def get_status(self):
        """Get the status of the enhanced Anima core"""
        return {
            "running": self.running,
            "current_emotion": self.current_emotion,
            "voice_enabled": self.settings["voice_enabled"],
            "voice_personality": self.settings["current_voice_personality"],
            "voice_speed": self.settings["voice_speed"],
            "multimodal_enabled": self.settings["multimodal_enabled"],
            "autonomous_learning_enabled": self.settings["autonomous_learning_enabled"],
            "memory_stats": self.get_memory_stats(),
            "learning_stats": self.get_learning_stats(),
            "environment": self.get_environment_status() if self.settings["multimodal_enabled"] else None
        }
    
    def update_settings(self, new_settings):
        """Update settings"""
        for key, value in new_settings.items():
            if key in self.settings:
                self.settings[key] = value
        
        self._save_settings()
        return self.settings

# For testing
if __name__ == "__main__":
    anima = AnimaEnhancedCore()
    
    # Start Anima
    print("Starting Anima enhanced core...")
    anima.start()
    
    # Process some inputs
    print("\nProcessing inputs...")
    inputs = [
        "Hello, how are you today?",
        "What can you tell me about consciousness?",
        "I'm feeling happy today!",
        "Can you explain how your memory works?"
    ]
    
    for user_input in inputs:
        print(f"\nUser: {user_input}")
        response = anima.process_input(user_input)
        print(f"Anima: {response}")
        time.sleep(1)
    
    # Get status
    print("\nAnima status:")
    status = anima.get_status()
    print(f"Running: {status['running']}")
    print(f"Current emotion: {status['current_emotion']}")
    print(f"Voice personality: {status['voice_personality']}")
    
    # Try different voice personality
    print("\nChanging voice personality to 'teacher'...")
    anima.set_voice_personality("teacher")
    
    # Process another input with new voice
    print("\nUser: What is the meaning of life?")
    response = anima.process_input("What is the meaning of life?")
    print(f"Anima (teacher): {response}")
    
    # Get next curiosity topic
    topic = anima.get_next_curiosity_topic()
    if topic:
        print(f"\nNext curiosity topic: {topic['topic']} (score: {topic['score']:.2f})")
    
    # Try multimodal if enabled
    if anima.settings["multimodal_enabled"]:
        print("\nGetting environment status...")
        env = anima.get_environment_status()
        print(f"Room activity: {env['room_activity']}")
        print(f"Time of day: {env['time_of_day']}")
    
    # Stop Anima
    print("\nStopping Anima enhanced core...")
    anima.stop()
    print("Done")
