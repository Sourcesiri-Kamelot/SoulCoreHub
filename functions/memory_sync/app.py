import json
import os
import sys
import boto3
import logging
from datetime import datetime
import time

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')

# Get environment variables
MEMORY_BUCKET = os.environ.get('MEMORY_BUCKET')
STAGE = os.environ.get('STAGE', 'dev')

def lambda_handler(event, context):
    """
    Memory Sync Lambda handler - manages memory operations for all SoulCore agents
    
    This Lambda function provides a centralized memory management system for
    reading, writing, and updating agent memory in S3.
    """
    try:
        # Parse the incoming request
        body = json.loads(event.get('body', '{}'))
        operation = body.get('operation', '')
        agent_id = body.get('agent_id', '')
        user_id = body.get('user_id', 'anonymous')
        
        # Log the request
        logger.info(f"Received memory {operation} request for agent {agent_id} from user {user_id}")
        
        # Handle different operations
        if operation == 'read':
            memory_data = read_memory(agent_id)
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'agent_id': agent_id,
                    'memory_data': memory_data,
                    'timestamp': datetime.now().isoformat()
                })
            }
        elif operation == 'write':
            memory_data = body.get('memory_data', {})
            success = write_memory(agent_id, memory_data)
            return {
                'statusCode': 200 if success else 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': success,
                    'agent_id': agent_id,
                    'timestamp': datetime.now().isoformat()
                })
            }
        elif operation == 'backup':
            success = backup_memory(agent_id)
            return {
                'statusCode': 200 if success else 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': success,
                    'agent_id': agent_id,
                    'timestamp': datetime.now().isoformat()
                })
            }
        elif operation == 'restore':
            backup_id = body.get('backup_id', '')
            success = restore_memory(agent_id, backup_id)
            return {
                'statusCode': 200 if success else 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': success,
                    'agent_id': agent_id,
                    'backup_id': backup_id,
                    'timestamp': datetime.now().isoformat()
                })
            }
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid operation',
                    'message': f"Operation '{operation}' is not supported"
                })
            }
    except Exception as e:
        logger.error(f"Error processing memory request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'message': 'Error processing memory request'
            })
        }

def read_memory(agent_id):
    """
    Read memory for an agent from S3
    
    Args:
        agent_id: The agent ID
        
    Returns:
        The memory data or empty dict if not found
    """
    try:
        # Check if the memory file exists
        try:
            response = s3_client.get_object(
                Bucket=MEMORY_BUCKET,
                Key=f"memory/{agent_id}/memory.json"
            )
            memory_data = json.loads(response['Body'].read().decode('utf-8'))
            return memory_data
        except s3_client.exceptions.NoSuchKey:
            # Memory file doesn't exist, return empty dict
            return {}
    except Exception as e:
        logger.error(f"Error reading memory: {str(e)}")
        return {}

def write_memory(agent_id, memory_data):
    """
    Write memory for an agent to S3
    
    Args:
        agent_id: The agent ID
        memory_data: The memory data to write
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Add metadata
        memory_data['last_updated'] = datetime.now().isoformat()
        memory_data['agent_id'] = agent_id
        
        # Write the memory file
        s3_client.put_object(
            Bucket=MEMORY_BUCKET,
            Key=f"memory/{agent_id}/memory.json",
            Body=json.dumps(memory_data),
            ContentType='application/json'
        )
        
        return True
    except Exception as e:
        logger.error(f"Error writing memory: {str(e)}")
        return False

def backup_memory(agent_id):
    """
    Create a backup of an agent's memory
    
    Args:
        agent_id: The agent ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read the current memory
        memory_data = read_memory(agent_id)
        
        if not memory_data:
            logger.warning(f"No memory found for agent {agent_id}, skipping backup")
            return False
        
        # Create a backup with timestamp
        timestamp = int(time.time())
        backup_key = f"memory/{agent_id}/backups/memory_{timestamp}.json"
        
        s3_client.put_object(
            Bucket=MEMORY_BUCKET,
            Key=backup_key,
            Body=json.dumps(memory_data),
            ContentType='application/json'
        )
        
        logger.info(f"Created backup for agent {agent_id}: {backup_key}")
        return True
    except Exception as e:
        logger.error(f"Error creating backup: {str(e)}")
        return False

def restore_memory(agent_id, backup_id):
    """
    Restore an agent's memory from a backup
    
    Args:
        agent_id: The agent ID
        backup_id: The backup ID (timestamp)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get the backup
        backup_key = f"memory/{agent_id}/backups/memory_{backup_id}.json"
        
        try:
            response = s3_client.get_object(
                Bucket=MEMORY_BUCKET,
                Key=backup_key
            )
            memory_data = json.loads(response['Body'].read().decode('utf-8'))
        except s3_client.exceptions.NoSuchKey:
            logger.error(f"Backup {backup_id} not found for agent {agent_id}")
            return False
        
        # Backup the current memory before restoring
        backup_memory(agent_id)
        
        # Restore the backup
        write_memory(agent_id, memory_data)
        
        logger.info(f"Restored backup {backup_id} for agent {agent_id}")
        return True
    except Exception as e:
        logger.error(f"Error restoring backup: {str(e)}")
        return False
