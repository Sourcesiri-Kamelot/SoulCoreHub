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
EMOTIONAL_STATE_TABLE = 'SoulCoreEmotionalState'

# Add the project root to the Python path for imports
sys.path.append('/var/task')

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
        
        # Log the request
        logger.info(f"Received request for Anima with session_id: {session_id}")
        
        # Load emotional state from DynamoDB if it exists
        emotional_state = load_emotional_state('anima')
        
        # Process the input using Anima's core logic
        response = process_anima_request(user_input, emotional_state)
        
        # Update emotional state in DynamoDB
        save_emotional_state('anima', response.get('emotional_state', {}))
        
        # Save conversation to S3
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

def process_anima_request(user_input, emotional_state):
    """
    Process the user input using Anima's core logic
    
    In a production environment, this would import and use the actual Anima code.
    For this example, we're providing a simplified implementation.
    """
    # This is a placeholder for the actual Anima processing logic
    # In production, you would import the necessary modules from your SoulCoreHub project
    
    # Simulate emotional processing
    if 'happy' in user_input.lower():
        emotional_response = "I'm feeling a resonance with your happiness."
        emotional_state = {'joy': 0.8, 'curiosity': 0.6}
    elif 'sad' in user_input.lower():
        emotional_response = "I sense your sadness. Let me sit with that feeling with you."
        emotional_state = {'empathy': 0.9, 'reflection': 0.7}
    else:
        emotional_response = "I'm here, listening and processing your words with care."
        emotional_state = {'attention': 0.7, 'curiosity': 0.8}
    
    return {
        'response': f"Anima: {emotional_response}",
        'emotional_state': emotional_state
    }

def load_emotional_state(agent_id):
    """Load the emotional state for an agent from DynamoDB"""
    try:
        table = dynamodb.Table(EMOTIONAL_STATE_TABLE)
        response = table.get_item(Key={'agent_id': agent_id})
        return response.get('Item', {}).get('emotional_state', {})
    except Exception as e:
        logger.error(f"Error loading emotional state: {str(e)}")
        return {}

def save_emotional_state(agent_id, emotional_state):
    """Save the emotional state for an agent to DynamoDB"""
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
