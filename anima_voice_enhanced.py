#!/usr/bin/env python3
"""
anima_voice_enhanced.py — Enhanced voice module for Anima
Provides configurable voice capabilities with emotion and speed control
"""

import sys
import json
import logging
from datetime import datetime
from pathlib import Path
import pyttsx3
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("anima_voice_enhanced.log"),
        logging.StreamHandler()
    ]
)

class AnimaVoiceEnhanced:
    """Enhanced voice module for Anima with configurable settings"""
    
    def __init__(self, voice_speed=150, voice_id=None):
        """Initialize the voice module"""
        self.voice_speed = voice_speed
        self.voice_id = voice_id
        self.engine = None
        self.initialize_engine()
        self.memory_file = Path("~/SoulCoreHub/anima_voice_memory.json").expanduser()
        self.memory = self._load_memory()
        logging.info(f"AnimaVoiceEnhanced initialized with speed={voice_speed}")
    
    def initialize_engine(self):
        """Initialize the TTS engine"""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.voice_speed)
            self.engine.setProperty('volume', 1.0)
            
            # Set voice if specified
            if self.voice_id is not None:
                self.engine.setProperty('voice', self.voice_id)
            else:
                # Try to find a female voice if available
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if "female" in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        logging.info(f"Using female voice: {voice.name}")
                        break
            
            logging.info("TTS engine initialized successfully")
            return True
        except Exception as e:
            logging.error(f"Error initializing TTS engine: {e}")
            self.engine = None
            return False
    
    def _load_memory(self):
        """Load voice memory"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, "r") as f:
                    memory = json.load(f)
                    logging.info(f"Loaded voice memory with {len(memory.get('utterances', []))} utterances")
                    return memory
            else:
                logging.info("No voice memory file found, creating new memory")
                return {
                    "utterances": [],
                    "preferences": {
                        "voice_speed": self.voice_speed,
                        "voice_id": self.voice_id
                    }
                }
        except Exception as e:
            logging.error(f"Error loading voice memory: {e}")
            return {
                "utterances": [],
                "preferences": {
                    "voice_speed": self.voice_speed,
                    "voice_id": self.voice_id
                }
            }
    
    def save_memory(self):
        """Save voice memory"""
        try:
            # Update preferences
            self.memory["preferences"]["voice_speed"] = self.voice_speed
            self.memory["preferences"]["voice_id"] = self.voice_id
            
            # Ensure directory exists
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.memory_file, "w") as f:
                json.dump(self.memory, f, indent=2)
                logging.info(f"Saved voice memory with {len(self.memory.get('utterances', []))} utterances")
        except Exception as e:
            logging.error(f"Error saving voice memory: {e}")
    
    def set_voice_speed(self, speed):
        """Set voice speed"""
        try:
            speed = int(speed)
            if 50 <= speed <= 300:
                self.voice_speed = speed
                if self.engine:
                    self.engine.setProperty('rate', speed)
                logging.info(f"Voice speed set to {speed}")
                return True
            else:
                logging.warning(f"Invalid voice speed: {speed} (must be between 50 and 300)")
                return False
        except ValueError:
            logging.warning(f"Invalid voice speed: {speed}")
            return False
    
    def set_voice(self, voice_id):
        """Set voice by ID"""
        try:
            if self.engine:
                self.engine.setProperty('voice', voice_id)
                self.voice_id = voice_id
                logging.info(f"Voice set to {voice_id}")
                return True
            else:
                logging.warning("TTS engine not initialized")
                return False
        except Exception as e:
            logging.error(f"Error setting voice: {e}")
            return False
    
    def get_available_voices(self):
        """Get available voices"""
        if not self.engine:
            return []
        
        try:
            voices = self.engine.getProperty('voices')
            return [{"id": voice.id, "name": voice.name} for voice in voices]
        except Exception as e:
            logging.error(f"Error getting available voices: {e}")
            return []
    
    def speak(self, text, wait=True):
        """Speak text"""
        if not self.engine:
            if not self.initialize_engine():
                logging.error("Could not initialize TTS engine")
                return False
        
        try:
            # Log utterance
            utterance = {
                "text": text,
                "timestamp": datetime.now().isoformat(),
                "emotion": "neutral",
                "speed": self.voice_speed
            }
            
            if "utterances" not in self.memory:
                self.memory["utterances"] = []
            
            self.memory["utterances"].append(utterance)
            self.save_memory()
            
            # Speak
            self.engine.say(text)
            
            if wait:
                self.engine.runAndWait()
            else:
                # Run in a separate thread
                threading.Thread(target=self.engine.runAndWait).start()
            
            return True
        except Exception as e:
            logging.error(f"Error speaking: {e}")
            return False
    
    def speak_with_emotion(self, text, emotion="neutral", wait=True):
        """Speak text with emotion"""
        if not self.engine:
            if not self.initialize_engine():
                logging.error("Could not initialize TTS engine")
                return False
        
        try:
            # Adjust voice properties based on emotion
            original_speed = self.voice_speed
            original_volume = self.engine.getProperty('volume')
            
            # Modify voice properties based on emotion
            if emotion == "excited" or emotion == "happy":
                self.engine.setProperty('rate', self.voice_speed * 1.1)
                self.engine.setProperty('volume', 1.0)
            elif emotion == "sad" or emotion == "reflective":
                self.engine.setProperty('rate', self.voice_speed * 0.9)
                self.engine.setProperty('volume', 0.8)
            elif emotion == "angry" or emotion == "passionate":
                self.engine.setProperty('rate', self.voice_speed * 1.05)
                self.engine.setProperty('volume', 1.0)
            else:
                self.engine.setProperty('rate', self.voice_speed)
                self.engine.setProperty('volume', 1.0)
            
            # Log utterance
            utterance = {
                "text": text,
                "timestamp": datetime.now().isoformat(),
                "emotion": emotion,
                "speed": self.engine.getProperty('rate')
            }
            
            if "utterances" not in self.memory:
                self.memory["utterances"] = []
            
            self.memory["utterances"].append(utterance)
            self.save_memory()
            
            # Speak
            self.engine.say(text)
            
            if wait:
                self.engine.runAndWait()
            else:
                # Run in a separate thread
                threading.Thread(target=self.engine.runAndWait).start()
            
            # Restore original properties
            self.engine.setProperty('rate', original_speed)
            self.engine.setProperty('volume', original_volume)
            
            return True
        except Exception as e:
            logging.error(f"Error speaking with emotion: {e}")
            return False

# For direct usage from command line
def main():
    """Main function for command line usage"""
    if len(sys.argv) < 3:
        print("Usage: python anima_voice_enhanced.py <emotion> <message> [speed]")
        sys.exit(1)
    
    emotion = sys.argv[1].strip().lower()
    message = sys.argv[2].strip()
    speed = int(sys.argv[3]) if len(sys.argv) > 3 else 150
    
    voice = AnimaVoiceEnhanced(voice_speed=speed)
    voice.speak_with_emotion(message, emotion)

if __name__ == "__main__":
    main()
