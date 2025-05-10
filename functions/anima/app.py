import json
import os
import sys
import boto3
import logging
import hmac
import hashlib
import base64
from datetime import datetime

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')

# Get environment variables
MEMORY_BUCKET = os.environ.get('MEMORY_BUCKET')
STAGE = os.environ.get('STAGE', 'dev')
EMOTIONAL_STATE_TABLE = f'SoulCoreEmotionalState-{STAGE}'
API_SECRET = os.environ.get('API_SECRET', 'default-secret-key-replace-in-production')

def lambda_handler(event, context):
    """
    Anima Lambda handler - processes emotional and reflective responses
    
    This Lambda function wraps the core Anima functionality from the SoulCoreHub project,
    providing a serverless interface to the emotional core agent.
    """
    try:
        # Verify request signature if present
        if not verify_request_signature(event):
            return {
                'statusCode': 403,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'error': 'Invalid request signature',
                    'message': 'Request signature verification failed'
                })
            }
            
        # Parse the incoming request
        body = json.loads(event.get('body', '{}'))
        user_input = body.get('input', '')
        session_id = body.get('session_id', 'default')
        user_id = body.get('user_id', 'anonymous')
        
        # Log the request
        logger.info(f"Received request for Anima with session_id: {session_id}, user_id: {user_id}")
        
        # Log usage metrics to CloudWatch
        log_usage_metrics(user_id)
        
        # Process the input using Anima's core logic
        response = process_anima_request(user_input)
        
        # Save conversation to S3 if bucket is available
        if MEMORY_BUCKET:
            save_conversation_to_s3(session_id, user_input, response.get('response', ''))
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
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
            'headers': get_cors_headers(),
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

def verify_request_signature(event):
    """
    Verify the signature of the incoming request
    
    Args:
        event: The Lambda event object
        
    Returns:
        True if signature is valid or not present, False otherwise
    """
    # If no signature header is present, skip verification (for backward compatibility)
    if 'headers' not in event or not event['headers'] or 'X-Request-Signature' not in event['headers']:
        return True
    
    try:
        # Get the signature from the headers
        signature = event['headers']['X-Request-Signature']
        
        # Get the request body
        body = event.get('body', '')
        
        # Calculate the expected signature
        expected_signature = calculate_signature(body)
        
        # Compare signatures
        return hmac.compare_digest(signature, expected_signature)
    except Exception as e:
        logger.error(f"Error verifying signature: {str(e)}")
        return False

def calculate_signature(data):
    """
    Calculate HMAC signature for request data
    
    Args:
        data: The data to sign
        
    Returns:
        Base64 encoded signature
    """
    key = API_SECRET.encode('utf-8')
    message = data.encode('utf-8')
    signature = hmac.new(key, message, hashlib.sha256).digest()
    return base64.b64encode(signature).decode('utf-8')

def log_usage_metrics(user_id):
    """
    Log usage metrics to CloudWatch
    
    Args:
        user_id: The user ID
    """
    try:
        cloudwatch.put_metric_data(
            Namespace='SoulCoreHub/Usage',
            MetricData=[
                {
                    'MetricName': 'AnimaAPIRequests',
                    'Dimensions': [
                        {
                            'Name': 'UserId',
                            'Value': user_id
                        },
                        {
                            'Name': 'Stage',
                            'Value': STAGE
                        }
                    ],
                    'Value': 1,
                    'Unit': 'Count'
                }
            ]
        )
    except Exception as e:
        logger.error(f"Error logging metrics: {str(e)}")

def get_cors_headers():
    """
    Get CORS headers for responses
    
    Returns:
        Dictionary of CORS headers
    """
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': 'https://soulcorehub.io',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Api-Key,X-Request-Signature',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
    }
