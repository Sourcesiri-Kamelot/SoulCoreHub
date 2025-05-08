import json
import os
import sys
import boto3
import logging
import requests
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
    Neural Router Lambda handler - routes user input to the appropriate agent or MCP server
    
    This Lambda function analyzes user input and determines which agent or service
    should handle the request, then forwards it accordingly.
    """
    try:
        # Parse the incoming request
        body = json.loads(event.get('body', '{}'))
        user_input = body.get('input', '')
        session_id = body.get('session_id', 'default')
        
        # Log the request
        logger.info(f"Received routing request with session_id: {session_id}")
        
        # Analyze the input to determine the appropriate agent
        routing_result = analyze_and_route(user_input)
        
        # Save routing decision to DynamoDB for analytics
        save_routing_decision(session_id, user_input, routing_result)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'route': routing_result.get('route'),
                'confidence': routing_result.get('confidence'),
                'response': routing_result.get('response', ''),
                'timestamp': datetime.now().isoformat()
            })
        }
    except Exception as e:
        logger.error(f"Error in Neural Router: {str(e)}")
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

def analyze_and_route(user_input):
    """
    Analyze user input and determine the appropriate routing
    
    This function implements the core logic from neural_routing.py in the SoulCoreHub project.
    It determines which agent or MCP server should handle the request.
    """
    # This is a simplified version of the routing logic
    # In production, you would import the actual neural_routing module
    
    user_input_lower = user_input.lower()
    
    # Simple keyword-based routing
    if any(word in user_input_lower for word in ['emotion', 'feel', 'feeling', 'reflect']):
        return {
            'route': 'anima',
            'confidence': 0.85,
            'response': 'Routing to Anima for emotional processing'
        }
    elif any(word in user_input_lower for word in ['system', 'architecture', 'build', 'create']):
        return {
            'route': 'gptsoul',
            'confidence': 0.9,
            'response': 'Routing to GPTSoul for system architecture tasks'
        }
    elif any(word in user_input_lower for word in ['repair', 'fix', 'heal', 'recover']):
        return {
            'route': 'evove',
            'confidence': 0.8,
            'response': 'Routing to EvoVe for system repair'
        }
    elif any(word in user_input_lower for word in ['cloud', 'strategy', 'plan']):
        return {
            'route': 'azur',
            'confidence': 0.75,
            'response': 'Routing to Azür for strategic planning'
        }
    elif any(word in user_input_lower for word in ['mcp', 'context', 'knowledge']):
        return {
            'route': 'mcp_server',
            'confidence': 0.7,
            'response': 'Routing to MCP server for contextual processing'
        }
    else:
        # Default to GPTSoul as the main coordinator
        return {
            'route': 'gptsoul',
            'confidence': 0.6,
            'response': 'No specific routing detected, defaulting to GPTSoul'
        }

def save_routing_decision(session_id, user_input, routing_result):
    """Save the routing decision to DynamoDB for analytics"""
    try:
        table = dynamodb.Table('SoulCoreRouting')
        table.put_item(
            Item={
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'user_input': user_input,
                'route': routing_result.get('route'),
                'confidence': routing_result.get('confidence')
            }
        )
    except Exception as e:
        logger.error(f"Error saving routing decision: {str(e)}")
