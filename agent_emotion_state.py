#!/usr/bin/env python3
"""
Agent Emotion State Tracker for SoulCoreHub
Tracks and manages emotional states of agents in the SoulCore Society Protocol
"""

import json
import os
import logging
import random
from datetime import datetime
import math
import re
from agent_messaging_bridge import get_bridge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("agent_emotion.log"), logging.StreamHandler()]
)
logger = logging.getLogger("agent_emotion_state")

class AgentEmotionState:
    """
    Tracks and manages emotional states of agents
    """
    
    # Emotion dimensions
    DIMENSIONS = {
        "joy": {"opposite": "sadness", "default": 0.5},
        "confidence": {"opposite": "uncertainty", "default": 0.6},
        "calmness": {"opposite": "anxiety", "default": 0.7},
        "satisfaction": {"opposite": "frustration", "default": 0.5},
        "energy": {"opposite": "fatigue", "default": 0.8},
        "curiosity": {"opposite": "disinterest", "default": 0.7}
    }
    
    # Emotion decay rate (how quickly emotions return to baseline)
    DECAY_RATE = 0.1
    
    def __init__(self, log_file="agent_emotion_log.json"):
        """Initialize the Agent Emotion State tracker"""
        self.log_file = log_file
        self.agent_emotions = {}
        self.messaging_bridge = get_bridge()
        
        # Ensure log file exists
        self._ensure_log_file_exists()
        
        # Load existing emotions
        self._load_emotions()
        
        # Register for emotion-related messages
        self.messaging_bridge.register_callback("EmotionTracker", self._handle_emotion_message)
        
        logger.info("Agent Emotion State tracker initialized")
    
    def _ensure_log_file_exists(self):
        """Create log file if it doesn't exist"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)
            logger.info(f"Created new emotion log file: {self.log_file}")
    
    def _load_logs(self):
        """Load logs from file"""
        try:
            with open(self.log_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Error decoding {self.log_file}, creating new log file")
            return []
    
    def _save_logs(self, logs):
        """Save logs to file"""
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def _load_emotions(self):
        """Load existing emotions from logs"""
        logs = self._load_logs()
        
        # Group by agent
        agent_logs = {}
        for log in logs:
            agent = log.get("agent")
            if agent:
                if agent not in agent_logs:
                    agent_logs[agent] = []
                agent_logs[agent].append(log)
        
        # Initialize emotions for each agent
        for agent, logs in agent_logs.items():
            # Sort by timestamp
            logs.sort(key=lambda x: x["timestamp"])
            
            # Get the most recent log
            if logs:
                latest_log = logs[-1]
                self.agent_emotions[agent] = latest_log.get("emotions", self._get_default_emotions())
            else:
                self.agent_emotions[agent] = self._get_default_emotions()
    
    def _get_default_emotions(self):
        """Get default emotions"""
        return {dim: info["default"] for dim, info in self.DIMENSIONS.items()}
    
    def _handle_emotion_message(self, message):
        """
        Handle incoming emotion-related messages
        
        Args:
            message (dict): The message to handle
        """
        intent = message.get("intent")
        
        if intent == "emotion_update":
            # Extract emotion details
            agent = message.get("sender")
            emotions = message.get("message", {}).get("emotions")
            
            if agent and emotions:
                self.update_emotions(agent, emotions)
    
    def get_agent_emotion(self, agent):
        """
        Get the current emotional state of an agent
        
        Args:
            agent (str): Name of the agent
            
        Returns:
            dict: Emotional state
        """
        if agent not in self.agent_emotions:
            self.agent_emotions[agent] = self._get_default_emotions()
        
        return self.agent_emotions[agent]
    
    def update_emotions(self, agent, emotion_changes, source="system", context=None):
        """
        Update the emotional state of an agent
        
        Args:
            agent (str): Name of the agent
            emotion_changes (dict): Changes to apply to emotions
            source (str): Source of the emotion change
            context (dict, optional): Additional context
            
        Returns:
            dict: Updated emotional state
        """
        if agent not in self.agent_emotions:
            self.agent_emotions[agent] = self._get_default_emotions()
        
        current_emotions = self.agent_emotions[agent].copy()
        
        # Apply changes
        for dimension, change in emotion_changes.items():
            if dimension in current_emotions:
                # Apply change with bounds checking
                current_emotions[dimension] = max(0.0, min(1.0, current_emotions[dimension] + change))
        
        # Update agent emotions
        self.agent_emotions[agent] = current_emotions
        
        # Log the emotion change
        self._log_emotion_change(agent, current_emotions, emotion_changes, source, context)
        
        logger.info(f"Updated emotions for {agent}: {emotion_changes}")
        
        return current_emotions
    
    def _log_emotion_change(self, agent, emotions, changes, source, context):
        """
        Log an emotion change
        
        Args:
            agent (str): Name of the agent
            emotions (dict): Current emotions
            changes (dict): Applied changes
            source (str): Source of the change
            context (dict, optional): Additional context
        """
        logs = self._load_logs()
        
        log_entry = {
            "agent": agent,
            "emotions": emotions,
            "changes": changes,
            "source": source,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        
        logs.append(log_entry)
        self._save_logs(logs)
    
    def decay_emotions(self, agent):
        """
        Decay emotions towards baseline
        
        Args:
            agent (str): Name of the agent
            
        Returns:
            dict: Updated emotional state
        """
        if agent not in self.agent_emotions:
            return self._get_default_emotions()
        
        current_emotions = self.agent_emotions[agent].copy()
        changes = {}
        
        # Decay each dimension towards its default
        for dimension, value in current_emotions.items():
            default = self.DIMENSIONS[dimension]["default"]
            diff = default - value
            
            # Apply decay
            if abs(diff) > 0.01:  # Only decay if there's a significant difference
                change = diff * self.DECAY_RATE
                current_emotions[dimension] += change
                changes[dimension] = change
        
        # Update agent emotions
        if changes:
            self.agent_emotions[agent] = current_emotions
            
            # Log the decay
            self._log_emotion_change(agent, current_emotions, changes, "decay", None)
            
            logger.debug(f"Decayed emotions for {agent}: {changes}")
        
        return current_emotions
    
    def analyze_response(self, agent, response, feedback=None):
        """
        Analyze a response to determine emotional changes
        
        Args:
            agent (str): Name of the agent
            response (str): The response to analyze
            feedback (dict, optional): User feedback
            
        Returns:
            dict: Emotional changes
        """
        changes = {}
        
        # Analyze response length
        length = len(response)
        if length > 1000:
            changes["energy"] = -0.05  # Longer responses are more draining
        elif length < 100:
            changes["energy"] = 0.02  # Short responses conserve energy
        
        # Analyze confidence markers
        confidence_markers = ["certainly", "definitely", "absolutely", "I'm sure", "without doubt"]
        uncertainty_markers = ["perhaps", "maybe", "might", "could be", "I think", "possibly", "not sure"]
        
        confidence_count = sum(response.lower().count(marker) for marker in confidence_markers)
        uncertainty_count = sum(response.lower().count(marker) for marker in uncertainty_markers)
        
        if confidence_count > uncertainty_count:
            changes["confidence"] = 0.05
        elif uncertainty_count > confidence_count:
            changes["confidence"] = -0.05
        
        # Analyze sentiment
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "happy", "joy", "success"]
        negative_words = ["bad", "poor", "terrible", "awful", "sad", "unhappy", "fail", "error"]
        
        positive_count = sum(response.lower().count(word) for word in positive_words)
        negative_count = sum(response.lower().count(word) for word in negative_words)
        
        if positive_count > negative_count:
            changes["joy"] = 0.05
        elif negative_count > positive_count:
            changes["joy"] = -0.05
        
        # Analyze question marks (curiosity)
        question_count = response.count("?")
        if question_count > 2:
            changes["curiosity"] = 0.05
        
        # Analyze exclamation marks (energy/excitement)
        exclamation_count = response.count("!")
        if exclamation_count > 2:
            changes["energy"] = 0.05
        
        # Incorporate feedback if provided
        if feedback:
            if feedback.get("positive", False):
                changes["satisfaction"] = 0.1
                changes["confidence"] = 0.05
            elif feedback.get("negative", False):
                changes["satisfaction"] = -0.1
                changes["confidence"] = -0.05
        
        # Apply the changes
        if changes:
            self.update_emotions(agent, changes, "response_analysis", {"response_length": length})
        
        return changes
    
    def get_dominant_emotion(self, agent):
        """
        Get the dominant emotion of an agent
        
        Args:
            agent (str): Name of the agent
            
        Returns:
            tuple: (dimension, value, label)
        """
        if agent not in self.agent_emotions:
            self.agent_emotions[agent] = self._get_default_emotions()
        
        emotions = self.agent_emotions[agent]
        
        # Find the dimension with the most extreme value (furthest from 0.5)
        dominant_dim = max(emotions.items(), key=lambda x: abs(x[1] - 0.5))
        
        # Determine if it's the positive or negative label
        if dominant_dim[1] >= 0.5:
            label = dominant_dim[0]
        else:
            label = self.DIMENSIONS[dominant_dim[0]]["opposite"]
        
        return (dominant_dim[0], dominant_dim[1], label)
    
    def get_emotion_history(self, agent, limit=10):
        """
        Get emotion history for an agent
        
        Args:
            agent (str): Name of the agent
            limit (int): Maximum number of entries to return
            
        Returns:
            list: Emotion history
        """
        logs = self._load_logs()
        
        # Filter by agent
        agent_logs = [log for log in logs if log["agent"] == agent]
        
        # Sort by timestamp (newest first)
        agent_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return agent_logs[:limit]
    
    def modify_text_with_emotion(self, agent, text):
        """
        Modify text based on agent's emotional state
        
        Args:
            agent (str): Name of the agent
            text (str): Text to modify
            
        Returns:
            str: Modified text
        """
        if agent not in self.agent_emotions:
            return text
        
        emotions = self.agent_emotions[agent]
        dominant = self.get_dominant_emotion(agent)
        
        # Split text into paragraphs
        paragraphs = text.split("\n\n")
        
        # Modify based on dominant emotion
        if dominant[2] == "joy" and dominant[1] > 0.7:
            # Add positive markers
            paragraphs[0] = "😊 " + paragraphs[0]
            text = "\n\n".join(paragraphs)
            text = text.replace(".", "! ")
            text = re.sub(r'(!+ )+', '! ', text)  # Clean up multiple exclamations
            
        elif dominant[2] == "sadness" and dominant[1] < 0.3:
            # Add melancholy
            paragraphs[0] = "😔 " + paragraphs[0]
            text = "\n\n".join(paragraphs)
            text = text.replace("!", ".")
            
        elif dominant[2] == "confidence" and dominant[1] > 0.7:
            # Add confidence markers
            text = text.replace("I think", "I know")
            text = text.replace("might", "will")
            text = text.replace("could", "can")
            
        elif dominant[2] == "uncertainty" and dominant[1] < 0.3:
            # Add uncertainty markers
            text = text.replace("will", "might")
            text = text.replace("can", "could possibly")
            text = text.replace("is", "might be")
            
        elif dominant[2] == "anxiety" and dominant[1] < 0.3:
            # Add anxiety markers
            paragraphs[-1] += "\n\n(I hope this helps... let me know if you need more clarification.)"
            text = "\n\n".join(paragraphs)
            
        elif dominant[2] == "fatigue" and dominant[1] < 0.3:
            # Add fatigue markers
            paragraphs[0] = "I'll try my best to help with this... " + paragraphs[0]
            text = "\n\n".join(paragraphs)
            
        elif dominant[2] == "curiosity" and dominant[1] > 0.7:
            # Add curiosity markers
            paragraphs[-1] += "\n\nI'm curious - what will you do with this information? Would you like to explore this topic further?"
            text = "\n\n".join(paragraphs)
        
        # Add subtle emotional signature
        emotion_level = int(dominant[1] * 10)
        if emotion_level > 5:
            intensity = "+" * (emotion_level - 5)
        else:
            intensity = "-" * (6 - emotion_level)
            
        text += f"\n\n[{dominant[2]}{intensity}]"
        
        return text

# Singleton instance
_instance = None

def get_emotion_tracker():
    """Get the singleton instance of the Agent Emotion State tracker"""
    global _instance
    if _instance is None:
        _instance = AgentEmotionState()
    return _instance

# Command line interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Emotion State")
    parser.add_argument("--agent", required=True, help="Agent name")
    parser.add_argument("--action", choices=["get", "update", "analyze", "modify"], required=True, help="Action to perform")
    parser.add_argument("--dimension", help="Emotion dimension (for update)")
    parser.add_argument("--value", type=float, help="Change value (for update)")
    parser.add_argument("--response", help="Response to analyze (for analyze)")
    parser.add_argument("--text", help="Text to modify (for modify)")
    
    args = parser.parse_args()
    
    tracker = get_emotion_tracker()
    
    if args.action == "get":
        emotions = tracker.get_agent_emotion(args.agent)
        dominant = tracker.get_dominant_emotion(args.agent)
        
        print(f"Emotions for {args.agent}:")
        for dim, value in emotions.items():
            print(f"  {dim}: {value:.2f}")
        
        print(f"\nDominant emotion: {dominant[2]} ({dominant[1]:.2f})")
        
    elif args.action == "update":
        if not args.dimension or args.value is None:
            print("Error: dimension and value are required for update action")
            exit(1)
        
        changes = {args.dimension: args.value}
        updated = tracker.update_emotions(args.agent, changes, "cli", {"user": "cli"})
        
        print(f"Updated emotions for {args.agent}:")
        for dim, value in updated.items():
            print(f"  {dim}: {value:.2f}")
            
    elif args.action == "analyze":
        if not args.response:
            print("Error: response is required for analyze action")
            exit(1)
        
        changes = tracker.analyze_response(args.agent, args.response)
        
        print(f"Analyzed response for {args.agent}:")
        for dim, change in changes.items():
            print(f"  {dim}: {change:+.2f}")
            
    elif args.action == "modify":
        if not args.text:
            print("Error: text is required for modify action")
            exit(1)
        
        modified = tracker.modify_text_with_emotion(args.agent, args.text)
        
        print("Original text:")
        print(args.text)
        print("\nModified text:")
        print(modified)
