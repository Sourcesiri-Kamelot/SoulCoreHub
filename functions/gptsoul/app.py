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
    GPTSoul Lambda handler - processes strategic and executive responses
    
    This Lambda function wraps the core GPTSoul functionality from the SoulCoreHub project,
    providing a serverless interface to the guardian and architect agent.
    """
    try:
        # Parse the incoming request
        body = json.loads(event.get('body', '{}'))
        user_input = body.get('input', '')
        session_id = body.get('session_id', 'default')
        
        # Log the request
        logger.info(f"Received request for GPTSoul with session_id: {session_id}")
        
        # Load memory from S3
        memory = load_memory_from_s3('gptsoul')
        
        # Process the input using GPTSoul's core logic
        response = process_gptsoul_request(user_input, memory)
        
        # Update memory in S3
        save_memory_to_s3('gptsoul', response.get('memory', {}))
        
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
                'memory': response.get('memory', {}),
                'timestamp': datetime.now().isoformat()
            })
        }
    except Exception as e:
        logger.error(f"Error processing GPTSoul request: {str(e)}")
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

def process_gptsoul_request(user_input, memory):
    """
    Process the user input using GPTSoul's core logic
    
    In a production environment, this would import and use the actual GPTSoul code.
    For this example, we're providing a simplified implementation.
    """
    # This is a placeholder for the actual GPTSoul processing logic
    # In production, you would import the necessary modules from your SoulCoreHub project
    
    # Simulate GPTSoul processing
    if 'help' in user_input.lower():
        response = "I'm GPTSoul, the guardian and architect of SoulCoreHub. How can I assist you today?"
    elif 'status' in user_input.lower():
        response = "All systems are operational. The SoulCore network is stable and secure."
    else:
        response = "I've processed your request and am formulating a strategic response based on my understanding of your needs."
    
    # Update memory with this interaction
    if not memory:
        memory = {'interactions': []}
    
    memory['interactions'].append({
        'timestamp': datetime.now().isoformat(),
        'user_input': user_input,
        'response': response
    })
    
    # Limit memory size
    if len(memory['interactions']) > 10:
        memory['interactions'] = memory['interactions'][-10:]
    
    return {
        'response': f"GPTSoul: {response}",
        'memory': memory
    }

def load_memory_from_s3(agent_id):
    """Load memory from S3"""
    try:
        response = s3_client.get_object(
            Bucket=MEMORY_BUCKET,
            Key=f"memory/{agent_id}/memory.json"
        )
        return json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        logger.warning(f"Could not load memory from S3: {str(e)}")
        return {}

def save_memory_to_s3(agent_id, memory):
    """Save memory to S3"""
    try:
        s3_client.put_object(
            Bucket=MEMORY_BUCKET,
            Key=f"memory/{agent_id}/memory.json",
            Body=json.dumps(memory),
            ContentType='application/json'
        )
    except Exception as e:
        logger.error(f"Error saving memory to S3: {str(e)}")

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
            Key=f"conversations/gptsoul/{session_id}/{timestamp}.json",
            Body=json.dumps(conversation),
            ContentType='application/json'
        )
    except Exception as e:
        logger.error(f"Error saving conversation to S3: {str(e)}")
