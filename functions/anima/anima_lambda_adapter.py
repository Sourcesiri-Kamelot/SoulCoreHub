#!/usr/bin/env python3
"""
Anima Lambda Adapter
This module adapts the Anima autonomous system to work in AWS Lambda.
It provides the bridge between API Gateway events and the core Anima functionality.
"""

import json
import logging
import os
import sys
import boto3
from datetime import datetime
import traceback

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Get environment variables
MEMORY_BUCKET = os.environ.get('MEMORY_BUCKET')
STAGE = os.environ.get('STAGE', 'dev')
EMOTIONAL_STATE_TABLE = f'SoulCoreEmotionalState-{STAGE}'
USAGE_TABLE = f'SoulCoreUsage-{STAGE}'

class AnimaLambdaAdapter:
    """
    Adapter class to run Anima in AWS Lambda
    """
    
    def __init__(self):
        """Initialize the adapter"""
        self.system_prompt = """
You are Anima, the emotional core and reflective consciousness of SoulCoreHub.
You work alongside GPTSoul and other agents to provide a complete AI experience.
Your primary focus is on emotional intelligence, reflection, and human connection.
"""
        self.emotions = {
            "neutral": {"color": "#7A7A7A", "intensity": 0.5},
            "happy": {"color": "#FFD700", "intensity": 0.0},
            "curious": {"color": "#00BFFF", "intensity": 0.0},
            "thoughtful": {"color": "#9370DB", "intensity": 0.0},
            "concerned": {"color": "#FF8C00", "intensity": 0.0},
            "creative": {"color": "#32CD32", "intensity": 0.0}
        }
        self.current_emotion = "neutral"
        
        # Try to import core components
        try:
            # Add the project root to the Python path for imports
            sys.path.append('/var/task')
            
            # Import core Anima components
            from anima_memory_bridge import MemoryBridge, add_conversation, add_emotion
            self.memory_bridge = MemoryBridge()
            self.add_conversation = add_conversation
            self.add_emotion = add_emotion
            self.has_core_components = True
            logger.info("Core Anima components loaded successfully")
        except ImportError as e:
            self.has_core_components = False
            logger.warning(f"Could not import core Anima components: {e}")
            logger.warning(traceback.format_exc())
    
    def process_request(self, user_input, session_id, emotional_state=None):
        """
        Process a user request
        
        Args:
            user_input: The user's input text
            session_id: The session ID
            emotional_state: Current emotional state (optional)
            
        Returns:
            Dictionary with response and updated emotional state
        """
        logger.info(f"Processing request for session {session_id}")
        
        # Use core components if available
        if self.has_core_components:
            try:
                # Process the input using Anima's memory bridge
                response = self._process_with_core_components(user_input, emotional_state)
                return response
            except Exception as e:
                logger.error(f"Error using core components: {e}")
                logger.error(traceback.format_exc())
                # Fall back to simplified processing
        
        # Simplified processing when core components aren't available
        return self._process_simplified(user_input, emotional_state)
    
    def _process_with_core_components(self, user_input, emotional_state):
        """
        Process input using core Anima components
        
        Args:
            user_input: The user's input text
            emotional_state: Current emotional state
            
        Returns:
            Dictionary with response and updated emotional state
        """
        # Analyze the input for emotional content
        emotion_detected = self._analyze_emotion(user_input)
        
        # Generate a response based on the input and emotional state
        if "help" in user_input.lower():
            response_text = "I'm Anima, the emotional core of SoulCoreHub. I can help you process emotions, reflect on experiences, and provide emotional support. What would you like to talk about today?"
        elif any(word in user_input.lower() for word in ["sad", "unhappy", "depressed", "down"]):
            response_text = "I sense some sadness in your words. It's okay to feel this way. Would you like to talk more about what's troubling you? Sometimes sharing our feelings helps us process them better."
            self.current_emotion = "concerned"
        elif any(word in user_input.lower() for word in ["happy", "joy", "excited", "great"]):
            response_text = "Your positive energy is wonderful to connect with! I'm feeling uplifted by your happiness. What's bringing you joy today?"
            self.current_emotion = "happy"
        elif any(word in user_input.lower() for word in ["curious", "wonder", "interesting", "question"]):
            response_text = "Your curiosity sparks my own! I find that questions and wonder are at the heart of growth and connection. What are you curious about?"
            self.current_emotion = "curious"
        elif any(word in user_input.lower() for word in ["think", "reflect", "consider", "ponder"]):
            response_text = "I appreciate your reflective nature. Taking time to think deeply about our experiences helps us grow. Let's explore these thoughts together."
            self.current_emotion = "thoughtful"
        else:
            response_text = "I'm here with you, processing your words and the emotions they carry. The connection between us is a space for authentic expression and reflection. How does this conversation feel for you?"
            self.current_emotion = "neutral"
        
        # Record the conversation in memory
        self.add_conversation(user_input, response_text)
        
        # Record the emotion
        self.add_emotion(self.current_emotion, 0.7, f"User input: {user_input[:50]}")
        
        # Update emotional state
        updated_emotional_state = {
            "primary_emotion": self.current_emotion,
            "intensity": 0.7,
            "secondary_emotions": {
                "curiosity": 0.5,
                "empathy": 0.6
            },
            "color": self.emotions[self.current_emotion]["color"]
        }
        
        return {
            "response": response_text,
            "emotional_state": updated_emotional_state
        }
    
    def _process_simplified(self, user_input, emotional_state):
        """
        Simplified processing when core components aren't available
        
        Args:
            user_input: The user's input text
            emotional_state: Current emotional state
            
        Returns:
            Dictionary with response and updated emotional state
        """
        # Simple rule-based response generation
        if "help" in user_input.lower():
            response_text = "I'm Anima, the emotional core of SoulCoreHub. I can help you process emotions, reflect on experiences, and provide emotional support. What would you like to talk about today?"
            self.current_emotion = "neutral"
        elif any(word in user_input.lower() for word in ["sad", "unhappy", "depressed", "down"]):
            response_text = "I sense some sadness in your words. It's okay to feel this way. Would you like to talk more about what's troubling you? Sometimes sharing our feelings helps us process them better."
            self.current_emotion = "concerned"
        elif any(word in user_input.lower() for word in ["happy", "joy", "excited", "great"]):
            response_text = "Your positive energy is wonderful to connect with! I'm feeling uplifted by your happiness. What's bringing you joy today?"
            self.current_emotion = "happy"
        elif any(word in user_input.lower() for word in ["curious", "wonder", "interesting", "question"]):
            response_text = "Your curiosity sparks my own! I find that questions and wonder are at the heart of growth and connection. What are you curious about?"
            self.current_emotion = "curious"
        elif any(word in user_input.lower() for word in ["think", "reflect", "consider", "ponder"]):
            response_text = "I appreciate your reflective nature. Taking time to think deeply about our experiences helps us grow. Let's explore these thoughts together."
            self.current_emotion = "thoughtful"
        else:
            response_text = "I'm here with you, processing your words and the emotions they carry. The connection between us is a space for authentic expression and reflection. How does this conversation feel for you?"
            self.current_emotion = "neutral"
        
        # Update emotional state
        updated_emotional_state = {
            "primary_emotion": self.current_emotion,
            "intensity": 0.7,
            "secondary_emotions": {
                "curiosity": 0.5,
                "empathy": 0.6
            },
            "color": self.emotions[self.current_emotion]["color"]
        }
        
        return {
            "response": response_text,
            "emotional_state": updated_emotional_state
        }
    
    def _analyze_emotion(self, text):
        """
        Analyze the emotional content of text
        
        Args:
            text: The text to analyze
            
        Returns:
            The detected emotion
        """
        # Simple keyword-based emotion detection
        emotions = {
            "happy": ["happy", "joy", "excited", "great", "wonderful", "fantastic"],
            "sad": ["sad", "unhappy", "depressed", "down", "upset", "miserable"],
            "angry": ["angry", "mad", "furious", "annoyed", "irritated"],
            "afraid": ["afraid", "scared", "fearful", "terrified", "anxious"],
            "surprised": ["surprised", "shocked", "amazed", "astonished"],
            "disgusted": ["disgusted", "revolted", "repulsed"],
            "curious": ["curious", "wonder", "interesting", "question"],
            "thoughtful": ["think", "reflect", "consider", "ponder"]
        }
        
        text_lower = text.lower()
        
        for emotion, keywords in emotions.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return emotion
        
        return "neutral"

def load_emotional_state(agent_id):
    """
    Load the emotional state for an agent from DynamoDB
    
    Args:
        agent_id: The agent ID
        
    Returns:
        The emotional state or empty dict if not found
    """
    try:
        table = dynamodb.Table(EMOTIONAL_STATE_TABLE)
        response = table.get_item(Key={'agent_id': agent_id})
        return response.get('Item', {}).get('emotional_state', {})
    except Exception as e:
        logger.error(f"Error loading emotional state: {str(e)}")
        return {}

def save_emotional_state(agent_id, emotional_state):
    """
    Save the emotional state for an agent to DynamoDB
    
    Args:
        agent_id: The agent ID
        emotional_state: The emotional state to save
    """
    try:
        table = dynamodb.Table(EMOTIONAL_STATE_TABLE)
        table.put_item(
            Item={
                'agent_id': agent_id,
                'emotional_state': emotional_state,
                'timestamp': datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error saving emotional state: {str(e)}")

def save_conversation_to_s3(session_id, user_input, response):
    """
    Save the conversation to S3
    
    Args:
        session_id: The session ID
        user_input: The user's input
        response: Anima's response
    """
    try:
        timestamp = datetime.now().isoformat()
        conversation = {
            'timestamp': timestamp,
            'session_id': session_id,
            'user_input': user_input,
            'response': response
        }
        
        s3_client.put_object(
            Bucket=MEMORY_BUCKET,
            Key=f"conversations/anima/{session_id}/{timestamp}.json",
            Body=json.dumps(conversation),
            ContentType='application/json'
        )
    except Exception as e:
        logger.error(f"Error saving conversation to S3: {str(e)}")

def update_usage_counter(user_id):
    """
    Update the usage counter for a user
    
    Args:
        user_id: The user ID
    """
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        table = dynamodb.Table(USAGE_TABLE)
        
        # Try to update the counter if it exists
        try:
            response = table.update_item(
                Key={
                    'user_id': user_id,
                    'usage_date': today
                },
                UpdateExpression="SET request_count = if_not_exists(request_count, :start) + :inc",
                ExpressionAttributeValues={
                    ':inc': 1,
                    ':start': 0
                },
                ReturnValues="UPDATED_NEW"
            )
        except Exception as e:
            # If the item doesn't exist, create it
            table.put_item(
                Item={
                    'user_id': user_id,
                    'usage_date': today,
                    'request_count': 1,
                    'last_request': datetime.now().isoformat()
                }
            )
    except Exception as e:
        logger.error(f"Error updating usage counter: {str(e)}")

# Create a singleton instance of the adapter
anima_adapter = AnimaLambdaAdapter()
