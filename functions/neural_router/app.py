import json
import os
import sys
import boto3
import logging
from datetime import datetime
import re

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
lambda_client = boto3.client('lambda')

# Get environment variables
STAGE = os.environ.get('STAGE', 'dev')

def lambda_handler(event, context):
    """
    Neural Router Lambda handler - routes user input to the appropriate agent
    
    This Lambda function analyzes user input and routes it to the appropriate
    agent Lambda function based on content analysis.
    """
    try:
        # Parse the incoming request
        body = json.loads(event.get('body', '{}'))
        user_input = body.get('input', '')
        session_id = body.get('session_id', 'default')
        user_id = body.get('user_id', 'anonymous')
        
        # Log the request
        logger.info(f"Received routing request with session_id: {session_id}, user_id: {user_id}")
        
        # For now, route everything to Anima since it's our only implemented function
        target_agent = "anima"
        confidence = 1.0
        
        logger.info(f"Routing to {target_agent} with confidence {confidence}")
        
        # Prepare the payload for the target Lambda
        payload = {
            'body': json.dumps({
                'input': user_input,
                'session_id': session_id,
                'user_id': user_id,
                'routing_info': {
                    'source': 'neural_router',
                    'confidence': confidence
                }
            })
        }
        
        # Get the function name from the current context
        current_function_name = context.function_name
        stack_name = "-".join(current_function_name.split('-')[:-1])  # Extract stack name
        
        # Construct the target function name
        target_function = f"{stack_name}-AnimaLambda-{current_function_name.split('-')[-1]}"
        
        logger.info(f"Invoking function: {target_function}")
        
        # Invoke the target Lambda function
        response = lambda_client.invoke(
            FunctionName=target_function,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        # Parse the response from the target Lambda
        response_payload = json.loads(response['Payload'].read().decode())
        
        return {
            'statusCode': response_payload.get('statusCode', 200),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': response_payload.get('body', '{}')
        }
    except Exception as e:
        logger.error(f"Error routing request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'message': 'Error routing your request. Please try again.'
            })
        }
