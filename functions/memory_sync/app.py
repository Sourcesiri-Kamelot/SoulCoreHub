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

# Get environment variables
MEMORY_BUCKET = os.environ.get('MEMORY_BUCKET')

# Add the project root to the Python path for imports
sys.path.append('/var/task')

def lambda_handler(event, context):
    """
    Memory Sync Lambda handler - updates and saves memory state to S3
    
    This Lambda function handles memory operations for all SoulCore agents,
    providing a centralized way to read, write, and update memory states.
    """
    try:
        # Parse the incoming request
        body = json.loads(event.get('body', '{}'))
        operation = body.get('operation', '')
        agent_id = body.get('agent_id', '')
        memory_data = body.get('memory_data', {})
        
        # Log the request
        logger.info(f"Received memory {operation} request for agent: {agent_id}")
        
        if not agent_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing agent_id parameter'
                })
            }
        
        result = {}
        
        # Process based on operation type
        if operation == 'read':
            result = read_memory(agent_id)
        elif operation == 'write':
            result = write_memory(agent_id, memory_data)
        elif operation == 'update':
            result = update_memory(agent_id, memory_data)
        elif operation == 'backup':
            result = backup_memory(agent_id)
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': f'Unknown operation: {operation}'
                })
            }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
    except Exception as e:
        logger.error(f"Error in Memory Sync: {str(e)}")
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

def read_memory(agent_id):
    """Read memory from S3 for the specified agent"""
    try:
        response = s3_client.get_object(
            Bucket=MEMORY_BUCKET,
            Key=f"memory/{agent_id}/memory.json"
        )
        memory_data = json.loads(response['Body'].read().decode('utf-8'))
        return {
            'success': True,
            'agent_id': agent_id,
            'memory_data': memory_data,
            'timestamp': datetime.now().isoformat()
        }
    except s3_client.exceptions.NoSuchKey:
        logger.warning(f"No memory found for agent {agent_id}, returning empty memory")
        return {
            'success': True,
            'agent_id': agent_id,
            'memory_data': {},
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error reading memory for agent {agent_id}: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def write_memory(agent_id, memory_data):
    """Write memory to S3 for the specified agent"""
    try:
        s3_client.put_object(
            Bucket=MEMORY_BUCKET,
            Key=f"memory/{agent_id}/memory.json",
            Body=json.dumps(memory_data),
            ContentType='application/json'
        )
        return {
            'success': True,
            'agent_id': agent_id,
            'operation': 'write',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error writing memory for agent {agent_id}: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def update_memory(agent_id, memory_update):
    """Update memory for the specified agent"""
    try:
        # First read existing memory
        existing_memory = {}
        try:
            response = s3_client.get_object(
                Bucket=MEMORY_BUCKET,
                Key=f"memory/{agent_id}/memory.json"
            )
            existing_memory = json.loads(response['Body'].read().decode('utf-8'))
        except s3_client.exceptions.NoSuchKey:
            logger.info(f"No existing memory found for agent {agent_id}, creating new memory")
        
        # Update memory with new data
        # This is a simple update that merges dictionaries
        # For more complex memory structures, you would need custom merge logic
        if isinstance(existing_memory, dict) and isinstance(memory_update, dict):
            existing_memory.update(memory_update)
        else:
            # If not dictionaries, just replace with the update
            existing_memory = memory_update
        
        # Write updated memory back to S3
        s3_client.put_object(
            Bucket=MEMORY_BUCKET,
            Key=f"memory/{agent_id}/memory.json",
            Body=json.dumps(existing_memory),
            ContentType='application/json'
        )
        
        return {
            'success': True,
            'agent_id': agent_id,
            'operation': 'update',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error updating memory for agent {agent_id}: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def backup_memory(agent_id):
    """Create a backup of the agent's memory"""
    try:
        # First read existing memory
        try:
            response = s3_client.get_object(
                Bucket=MEMORY_BUCKET,
                Key=f"memory/{agent_id}/memory.json"
            )
            memory_data = response['Body'].read().decode('utf-8')
        except s3_client.exceptions.NoSuchKey:
            logger.warning(f"No memory found for agent {agent_id}, nothing to backup")
            return {
                'success': False,
                'error': f"No memory found for agent {agent_id}",
                'timestamp': datetime.now().isoformat()
            }
        
        # Create a backup with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        s3_client.put_object(
            Bucket=MEMORY_BUCKET,
            Key=f"memory_backups/{agent_id}/{timestamp}.json",
            Body=memory_data,
            ContentType='application/json'
        )
        
        return {
            'success': True,
            'agent_id': agent_id,
            'operation': 'backup',
            'backup_location': f"memory_backups/{agent_id}/{timestamp}.json",
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error backing up memory for agent {agent_id}: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
