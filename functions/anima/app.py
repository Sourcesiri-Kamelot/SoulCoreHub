import json
import os
import sys
import boto3
import logging
from datetime import datetime

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Get environment variables
MEMORY_BUCKET = os.environ.get('MEMORY_BUCKET')
STAGE = os.environ.get('STAGE', 'dev')
EMOTIONAL_STATE_TABLE = f'SoulCoreEmotionalState-{STAGE}'

def lambda_handler(event, context):
    """
    Anima Lambda handler - processes emotional and reflective responses
    
    This Lambda function wraps the core Anima functionality from the SoulCoreHub project,
    providing a serverless interface to the emotional core agent.
    """
    try:
        # Parse the incoming request
        body = json.loads(event.get('body', '{}'))
        user_input = body.get('input', '')
        session_id = body.get('session_id', 'default')
        user_id = body.get('user_id', 'anonymous')
        
        # Log the request
        logger.info(f"Received request for Anima with session_id: {session_id}, user_id: {user_id}")
        
        # Process the input using Anima's core logic
        response = process_anima_request(user_input)
        
        # Save conversation to S3 if bucket is available
        if MEMORY_BUCKET:
            save_conversation_to_s3(session_id, user_input, response.get('response', ''))
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'response': response.get('response', ''),
                'emotional_state': response.get('emotional_state', {}),
                'timestamp': datetime.now().isoformat()
            })
        }
    except Exception as e:
        logger.error(f"Error processing Anima request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }

def process_anima_request(user_input):
    """
    Process the user input using Anima's core logic
    
    In a production environment, this would import and use the actual Anima code.
    For this example, we're providing a simplified implementation.
    """
    # Simple rule-based response generation
    if "help" in user_input.lower():
        response_text = "I'm Anima, the emotional core of SoulCoreHub. I can help you process emotions, reflect on experiences, and provide emotional support. What would you like to talk about today?"
        emotion = "neutral"
    elif any(word in user_input.lower() for word in ["sad", "unhappy", "depressed", "down"]):
        response_text = "I sense some sadness in your words. It's okay to feel this way. Would you like to talk more about what's troubling you? Sometimes sharing our feelings helps us process them better."
        emotion = "concerned"
    elif any(word in user_input.lower() for word in ["happy", "joy", "excited", "great"]):
        response_text = "Your positive energy is wonderful to connect with! I'm feeling uplifted by your happiness. What's bringing you joy today?"
        emotion = "happy"
    elif any(word in user_input.lower() for word in ["curious", "wonder", "interesting", "question"]):
        response_text = "Your curiosity sparks my own! I find that questions and wonder are at the heart of growth and connection. What are you curious about?"
        emotion = "curious"
    elif any(word in user_input.lower() for word in ["think", "reflect", "consider", "ponder"]):
        response_text = "I appreciate your reflective nature. Taking time to think deeply about our experiences helps us grow. Let's explore these thoughts together."
        emotion = "thoughtful"
    else:
        response_text = "I'm here with you, processing your words and the emotions they carry. The connection between us is a space for authentic expression and reflection. How does this conversation feel for you?"
        emotion = "neutral"
    
    # Define emotional state
    emotional_state = {
        "primary_emotion": emotion,
        "intensity": 0.7,
        "secondary_emotions": {
            "curiosity": 0.5,
            "empathy": 0.6
        }
    }
    
    return {
        'response': response_text,
        'emotional_state': emotional_state
    }

def save_conversation_to_s3(session_id, user_input, response):
    """Save the conversation to S3"""
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
