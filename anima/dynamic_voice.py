#!/usr/bin/env python3
"""
dynamic_voice.py — Advanced voice processing system for Anima
Implements dynamic voice speed based on content importance and multiple voice personalities
"""

import os
import sys
import json
import logging
import pyttsx3
import threading
import time
import random
import re
from pathlib import Path
from datetime import datetime
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
from nltk.tokenize import sent_tokenize

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("anima_voice.log"),
        logging.StreamHandler()
    ]
)

class DynamicVoice:
    """Advanced voice processing system with dynamic speed and multiple personalities"""
    
    def __init__(self, base_path=None):
        """Initialize the dynamic voice system"""
        self.base_path = base_path or Path.home() / "SoulCoreHub" / "voices"
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Voice engines
        self.engines = {}
        self.current_engine = None
        
        # Voice personalities
        self.personalities = {
            "default": {
                "name": "Default",
                "description": "Anima's default voice personality",
                "voice_id": None,  # Will use system default
                "base_speed": 170,
                "base_volume": 1.0,
                "base_pitch": 1.0,
                "emotion_modifiers": {
                    "joy": {"speed": 1.1, "volume": 1.1, "pitch": 1.05},
                    "sadness": {"speed": 0.9, "volume": 0.9, "pitch": 0.95},
                    "anger": {"speed": 1.2, "volume": 1.2, "pitch": 1.1},
                    "fear": {"speed": 1.1, "volume": 0.9, "pitch": 1.05},
                    "surprise": {"speed": 1.2, "volume": 1.1, "pitch": 1.1},
                    "disgust": {"speed": 0.95, "volume": 1.0, "pitch": 0.95},
                    "trust": {"speed": 1.0, "volume": 1.0, "pitch": 1.0},
                    "anticipation": {"speed": 1.05, "volume": 1.05, "pitch": 1.02},
                    "interest": {"speed": 1.05, "volume": 1.0, "pitch": 1.0},
                    "serenity": {"speed": 0.9, "volume": 0.9, "pitch": 0.98},
                    "acceptance": {"speed": 1.0, "volume": 1.0, "pitch": 1.0},
                    "apprehension": {"speed": 1.05, "volume": 0.95, "pitch": 1.02},
                    "distraction": {"speed": 1.1, "volume": 0.9, "pitch": 1.0},
                    "pensiveness": {"speed": 0.85, "volume": 0.9, "pitch": 0.95},
                    "boredom": {"speed": 0.9, "volume": 0.8, "pitch": 0.95},
                    "annoyance": {"speed": 1.1, "volume": 1.1, "pitch": 1.05},
                    "vigilance": {"speed": 1.05, "volume": 1.0, "pitch": 1.0}
                }
            },
            "teacher": {
                "name": "Teacher",
                "description": "A calm, patient, and knowledgeable voice",
                "voice_id": None,  # Will be set if available
                "base_speed": 150,
                "base_volume": 1.0,
                "base_pitch": 1.0,
                "emotion_modifiers": {
                    "joy": {"speed": 1.05, "volume": 1.05, "pitch": 1.02},
                    "interest": {"speed": 1.0, "volume": 1.05, "pitch": 1.0}
                    # Other emotions will use default modifiers
                }
            },
            "companion": {
                "name": "Companion",
                "description": "A friendly, warm, and empathetic voice",
                "voice_id": None,  # Will be set if available
                "base_speed": 160,
                "base_volume": 1.0,
                "base_pitch": 1.02,
                "emotion_modifiers": {
                    "joy": {"speed": 1.1, "volume": 1.1, "pitch": 1.05},
                    "sadness": {"speed": 0.9, "volume": 0.95, "pitch": 0.98}
                    # Other emotions will use default modifiers
                }
            },
            "guide": {
                "name": "Guide",
                "description": "A confident, authoritative, and clear voice",
                "voice_id": None,  # Will be set if available
                "base_speed": 165,
                "base_volume": 1.1,
                "base_pitch": 0.98,
                "emotion_modifiers": {
                    "trust": {"speed": 1.0, "volume": 1.1, "pitch": 1.0},
                    "vigilance": {"speed": 1.1, "volume": 1.1, "pitch": 1.0}
                    # Other emotions will use default modifiers
                }
            }
        }
        
        # Current personality
        self.current_personality = "default"
        
        # Voice history
        self.voice_history = []
        self.voice_history_file = self.base_path / "voice_history.json"
        
        # Load voice history
        self._load_voice_history()
        
        # Initialize engines
        self._initialize_engines()
        
        logging.info("Dynamic voice system initialized")
    
    def _load_voice_history(self):
        """Load voice history from file"""
        try:
            if self.voice_history_file.exists():
                with open(self.voice_history_file, "r") as f:
                    self.voice_history = json.load(f)
                logging.info(f"Loaded voice history with {len(self.voice_history)} entries")
        except Exception as e:
            logging.error(f"Error loading voice history: {e}")
            self.voice_history = []
    
    def _save_voice_history(self):
        """Save voice history to file"""
        try:
            # Ensure directory exists
            self.voice_history_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Keep only the last 1000 entries
            if len(self.voice_history) > 1000:
                self.voice_history = self.voice_history[-1000:]
            
            with open(self.voice_history_file, "w") as f:
                json.dump(self.voice_history, f, indent=2)
            logging.info(f"Saved voice history with {len(self.voice_history)} entries")
        except Exception as e:
            logging.error(f"Error saving voice history: {e}")
    
    def _initialize_engines(self):
        """Initialize voice engines for each personality"""
        try:
            # Initialize default engine
            default_engine = pyttsx3.init()
            self.engines["default"] = default_engine
            self.current_engine = default_engine
            
            # Get available voices
            voices = default_engine.getProperty('voices')
            
            # Try to find appropriate voices for each personality
            for i, voice in enumerate(voices):
                voice_name = voice.name.lower()
                
                # Assign voices based on characteristics in the name
                if "female" in voice_name:
                    if "default" in self.personalities and not self.personalities["default"]["voice_id"]:
                        self.personalities["default"]["voice_id"] = voice.id
                
                if "male" in voice_name:
                    if "guide" in self.personalities and not self.personalities["guide"]["voice_id"]:
                        self.personalities["guide"]["voice_id"] = voice.id
                
                # Just assign any remaining voices
                if i == 0 and "teacher" in self.personalities and not self.personalities["teacher"]["voice_id"]:
                    self.personalities["teacher"]["voice_id"] = voice.id
                
                if i == len(voices) - 1 and "companion" in self.personalities and not self.personalities["companion"]["voice_id"]:
                    self.personalities["companion"]["voice_id"] = voice.id
            
            # Set up the default engine
            personality = self.personalities["default"]
            default_engine.setProperty('rate', personality["base_speed"])
            default_engine.setProperty('volume', personality["base_volume"])
            
            if personality["voice_id"]:
                default_engine.setProperty('voice', personality["voice_id"])
            
            logging.info(f"Initialized {len(voices)} voices")
        
        except Exception as e:
            logging.error(f"Error initializing voice engines: {e}")
    
    def set_personality(self, personality_name):
        """Set the current voice personality"""
        if personality_name not in self.personalities:
            logging.warning(f"Unknown personality: {personality_name}")
            return False
        
        try:
            self.current_personality = personality_name
            personality = self.personalities[personality_name]
            
            # Configure the engine
            self.current_engine = self.engines["default"]  # We're using a single engine for all personalities
            self.current_engine.setProperty('rate', personality["base_speed"])
            self.current_engine.setProperty('volume', personality["base_volume"])
            
            if personality["voice_id"]:
                self.current_engine.setProperty('voice', personality["voice_id"])
            
            logging.info(f"Set personality to {personality_name}")
            return True
        
        except Exception as e:
            logging.error(f"Error setting personality: {e}")
            return False
    
    def get_available_personalities(self):
        """Get available voice personalities"""
        return list(self.personalities.keys())
    
    def _analyze_content_importance(self, text):
        """Analyze content to determine importance of each sentence"""
        # This is a simplified implementation
        # In a real system, this would use more sophisticated NLP
        
        # Split text into sentences
        sentences = sent_tokenize(text)
        
        # Calculate importance for each sentence
        importances = []
        for sentence in sentences:
            # Simple heuristics for importance
            importance = 0.5  # Default importance
            
            # Length-based importance (longer sentences might be more important)
            words = len(sentence.split())
            if words > 20:
                importance += 0.1
            elif words < 5:
                importance -= 0.1
            
            # Keyword-based importance
            keywords = ["important", "critical", "essential", "key", "significant", 
                       "crucial", "vital", "necessary", "remember", "note",
                       "warning", "danger", "caution", "alert", "attention"]
            
            for keyword in keywords:
                if keyword in sentence.lower():
                    importance += 0.15
                    break
            
            # Question-based importance
            if "?" in sentence:
                importance += 0.1
            
            # Exclamation-based importance
            if "!" in sentence:
                importance += 0.1
            
            # Cap importance between 0.1 and 1.0
            importance = max(0.1, min(1.0, importance))
            importances.append(importance)
        
        return list(zip(sentences, importances))
    
    def speak(self, text, emotion="neutral", wait=True, analyze_importance=True):
        """Speak text with dynamic speed based on content importance"""
        if not text:
            return False
        
        try:
            # Get current personality
            personality = self.personalities[self.current_personality]
            
            # Get emotion modifiers
            emotion_modifiers = personality["emotion_modifiers"].get(
                emotion, 
                personality["emotion_modifiers"].get("neutral", {"speed": 1.0, "volume": 1.0, "pitch": 1.0})
            )
            
            # Base properties
            base_speed = personality["base_speed"]
            base_volume = personality["base_volume"]
            
            if analyze_importance:
                # Analyze content importance
                sentence_importances = self._analyze_content_importance(text)
                
                # Speak each sentence with appropriate speed
                for sentence, importance in sentence_importances:
                    # Adjust speed based on importance and emotion
                    # More important sentences are spoken more slowly
                    importance_factor = 1.0 - (importance - 0.5)  # Convert to speed factor
                    speed = base_speed * emotion_modifiers["speed"] * importance_factor
                    
                    # Set properties
                    self.current_engine.setProperty('rate', speed)
                    self.current_engine.setProperty('volume', base_volume * emotion_modifiers["volume"])
                    
                    # Speak the sentence
                    self.current_engine.say(sentence)
                    
                    # Log to history
                    self.voice_history.append({
                        "text": sentence,
                        "personality": self.current_personality,
                        "emotion": emotion,
                        "importance": importance,
                        "speed": speed,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Run the engine
                if wait:
                    self.current_engine.runAndWait()
                else:
                    threading.Thread(target=self.current_engine.runAndWait).start()
            
            else:
                # Speak the entire text with emotion-based speed
                speed = base_speed * emotion_modifiers["speed"]
                
                # Set properties
                self.current_engine.setProperty('rate', speed)
                self.current_engine.setProperty('volume', base_volume * emotion_modifiers["volume"])
                
                # Speak the text
                self.current_engine.say(text)
                
                # Log to history
                self.voice_history.append({
                    "text": text,
                    "personality": self.current_personality,
                    "emotion": emotion,
                    "importance": 0.5,  # Default importance
                    "speed": speed,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Run the engine
                if wait:
                    self.current_engine.runAndWait()
                else:
                    threading.Thread(target=self.current_engine.runAndWait).start()
            
            # Save history periodically
            if len(self.voice_history) % 10 == 0:
                self._save_voice_history()
            
            return True
        
        except Exception as e:
            logging.error(f"Error speaking: {e}")
            return False
    
    def speak_with_personality(self, text, personality, emotion="neutral", wait=True, analyze_importance=True):
        """Speak text with a specific personality"""
        # Save current personality
        current = self.current_personality
        
        # Set new personality
        if not self.set_personality(personality):
            return False
        
        # Speak
        result = self.speak(text, emotion, wait, analyze_importance)
        
        # Restore original personality
        self.set_personality(current)
        
        return result
    
    def get_voice_history(self, limit=10):
        """Get recent voice history"""
        return self.voice_history[-limit:]
    
    def add_personality(self, name, description, base_speed=170, base_volume=1.0, base_pitch=1.0, voice_id=None):
        """Add a new voice personality"""
        if name in self.personalities:
            logging.warning(f"Personality already exists: {name}")
            return False
        
        self.personalities[name] = {
            "name": name,
            "description": description,
            "voice_id": voice_id,
            "base_speed": base_speed,
            "base_volume": base_volume,
            "base_pitch": base_pitch,
            "emotion_modifiers": {
                # Default modifiers
                "joy": {"speed": 1.1, "volume": 1.1, "pitch": 1.05},
                "sadness": {"speed": 0.9, "volume": 0.9, "pitch": 0.95}
            }
        }
        
        logging.info(f"Added new personality: {name}")
        return True
    
    def save_personalities(self):
        """Save voice personalities to file"""
        try:
            personalities_file = self.base_path / "voice_personalities.json"
            
            with open(personalities_file, "w") as f:
                json.dump(self.personalities, f, indent=2)
            
            logging.info(f"Saved {len(self.personalities)} voice personalities")
            return True
        
        except Exception as e:
            logging.error(f"Error saving voice personalities: {e}")
            return False
    
    def load_personalities(self):
        """Load voice personalities from file"""
        try:
            personalities_file = self.base_path / "voice_personalities.json"
            
            if personalities_file.exists():
                with open(personalities_file, "r") as f:
                    self.personalities = json.load(f)
                
                logging.info(f"Loaded {len(self.personalities)} voice personalities")
                return True
            
            return False
        
        except Exception as e:
            logging.error(f"Error loading voice personalities: {e}")
            return False

# For testing
if __name__ == "__main__":
    voice = DynamicVoice()
    
    # Test different personalities
    personalities = voice.get_available_personalities()
    print(f"Available personalities: {personalities}")
    
    # Test speaking with different personalities
    for personality in personalities:
        print(f"\nTesting personality: {personality}")
        voice.speak_with_personality(
            f"Hello, I am Anima using the {personality} voice personality. How do you like my voice?",
            personality,
            emotion="joy"
        )
        time.sleep(1)
    
    # Test dynamic speed based on content importance
    print("\nTesting dynamic speed based on content importance:")
    voice.set_personality("default")
    voice.speak(
        "This is a normal sentence. IMPORTANT: This sentence contains critical information that you should pay attention to! " +
        "This is another normal sentence. WARNING: Be careful about this potential issue.",
        emotion="neutral",
        analyze_importance=True
    )
    
    # Test different emotions
    print("\nTesting different emotions:")
    emotions = ["joy", "sadness", "anger", "fear", "surprise"]
    for emotion in emotions:
        print(f"Emotion: {emotion}")
        voice.speak(f"This is how I sound when I'm feeling {emotion}.", emotion=emotion)
        time.sleep(1)
    
    # Get voice history
    history = voice.get_voice_history()
    print("\nVoice history:")
    for entry in history:
        print(f"- {entry['text']} (personality: {entry['personality']}, emotion: {entry['emotion']}, speed: {entry['speed']:.1f})")
