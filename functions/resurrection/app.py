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
    Resurrection Lambda handler - runs agent recovery logic and logs results
    
    This Lambda function implements the agent resurrection protocol from SoulCoreHub,
    which can recover agents that have crashed or are in an inconsistent state.
    """
    try:
        # Parse the incoming request
        body = json.loads(event.get('body', '{}'))
        agent_id = body.get('agent_id', '')
        resurrection_type = body.get('type', 'standard')
        force = body.get('force', False)
        
        # Log the request
        logger.info(f"Received resurrection request for agent: {agent_id}, type: {resurrection_type}")
        
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
        
        # Check if agent needs resurrection
        if not force and not needs_resurrection(agent_id):
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': f'Agent {agent_id} does not need resurrection',
                    'status': 'healthy',
                    'timestamp': datetime.now().isoformat()
                })
            }
        
        # Perform resurrection
        resurrection_result = resurrect_agent(agent_id, resurrection_type)
        
        # Log the resurrection
        log_resurrection(agent_id, resurrection_type, resurrection_result)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'agent_id': agent_id,
                'resurrection_type': resurrection_type,
                'result': resurrection_result,
                'timestamp': datetime.now().isoformat()
            })
        }
    except Exception as e:
        logger.error(f"Error in Resurrection Lambda: {str(e)}")
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

def needs_resurrection(agent_id):
    """
    Check if an agent needs resurrection
    
    This function checks various indicators to determine if an agent
    is in a state that requires resurrection.
    """
    try:
        # Check last heartbeat
        try:
            response = s3_client.get_object(
                Bucket=MEMORY_BUCKET,
                Key=f"heartbeats/{agent_id}/last_heartbeat.json"
            )
            heartbeat_data = json.loads(response['Body'].read().decode('utf-8'))
            last_heartbeat = datetime.fromisoformat(heartbeat_data.get('timestamp', '2000-01-01T00:00:00'))
            
            # If heartbeat is older than 1 hour, agent needs resurrection
            if (datetime.now() - last_heartbeat).total_seconds() > 3600:
                logger.info(f"Agent {agent_id} needs resurrection due to stale heartbeat")
                return True
        except Exception as e:
            logger.warning(f"Could not check heartbeat for agent {agent_id}: {str(e)}")
            # If we can't check heartbeat, assume agent needs resurrection
            return True
        
        # Check error logs
        try:
            response = s3_client.list_objects_v2(
                Bucket=MEMORY_BUCKET,
                Prefix=f"logs/{agent_id}/errors/",
                MaxKeys=10
            )
            
            # If there are recent error logs, agent might need resurrection
            if response.get('KeyCount', 0) > 0:
                logger.info(f"Agent {agent_id} has recent error logs, may need resurrection")
                return True
        except Exception as e:
            logger.warning(f"Could not check error logs for agent {agent_id}: {str(e)}")
        
        # Agent seems healthy
        return False
    except Exception as e:
        logger.error(f"Error checking if agent {agent_id} needs resurrection: {str(e)}")
        # If we encounter an error during checks, assume agent needs resurrection
        return True

def resurrect_agent(agent_id, resurrection_type):
    """
    Resurrect an agent
    
    This function implements the resurrection protocol for SoulCore agents.
    Different resurrection types handle different failure scenarios.
    """
    try:
        # Backup current memory before resurrection
        try:
            response = s3_client.get_object(
                Bucket=MEMORY_BUCKET,
                Key=f"memory/{agent_id}/memory.json"
            )
            memory_data = response['Body'].read().decode('utf-8')
            
            # Create a backup with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s3_client.put_object(
                Bucket=MEMORY_BUCKET,
                Key=f"memory_backups/{agent_id}/pre_resurrection_{timestamp}.json",
                Body=memory_data,
                ContentType='application/json'
            )
        except Exception as e:
            logger.warning(f"Could not backup memory for agent {agent_id}: {str(e)}")
        
        # Perform resurrection based on type
        if resurrection_type == 'standard':
            # Standard resurrection - reset operational state but keep memory
            result = {
                'status': 'resurrected',
                'message': f'Agent {agent_id} has been resurrected with standard protocol',
                'memory_preserved': True
            }
        elif resurrection_type == 'clean':
            # Clean resurrection - reset to initial state with minimal memory
            # Create a clean memory state
            clean_memory = {
                'core_identity': get_core_identity(agent_id),
                'resurrection_count': get_resurrection_count(agent_id) + 1,
                'last_resurrection': datetime.now().isoformat()
            }
            
            # Write clean memory to S3
            s3_client.put_object(
                Bucket=MEMORY_BUCKET,
                Key=f"memory/{agent_id}/memory.json",
                Body=json.dumps(clean_memory),
                ContentType='application/json'
            )
            
            result = {
                'status': 'resurrected',
                'message': f'Agent {agent_id} has been resurrected with clean protocol',
                'memory_preserved': False
            }
        elif resurrection_type == 'deep':
            # Deep resurrection - attempt to recover from backup if available
            backup_key = find_latest_good_backup(agent_id)
            
            if backup_key:
                # Restore from backup
                response = s3_client.get_object(
                    Bucket=MEMORY_BUCKET,
                    Key=backup_key
                )
                backup_memory = response['Body'].read().decode('utf-8')
                
                # Write backup memory to current memory
                s3_client.put_object(
                    Bucket=MEMORY_BUCKET,
                    Key=f"memory/{agent_id}/memory.json",
                    Body=backup_memory,
                    ContentType='application/json'
                )
                
                result = {
                    'status': 'resurrected',
                    'message': f'Agent {agent_id} has been resurrected with deep protocol from backup',
                    'memory_preserved': True,
                    'backup_used': backup_key
                }
            else:
                # No good backup found, fall back to clean resurrection
                clean_memory = {
                    'core_identity': get_core_identity(agent_id),
                    'resurrection_count': get_resurrection_count(agent_id) + 1,
                    'last_resurrection': datetime.now().isoformat()
                }
                
                # Write clean memory to S3
                s3_client.put_object(
                    Bucket=MEMORY_BUCKET,
                    Key=f"memory/{agent_id}/memory.json",
                    Body=json.dumps(clean_memory),
                    ContentType='application/json'
                )
                
                result = {
                    'status': 'resurrected',
                    'message': f'Agent {agent_id} has been resurrected with deep protocol (no backup found)',
                    'memory_preserved': False
                }
        else:
            result = {
                'status': 'error',
                'message': f'Unknown resurrection type: {resurrection_type}'
            }
        
        # Update heartbeat
        update_heartbeat(agent_id)
        
        return result
    except Exception as e:
        logger.error(f"Error resurrecting agent {agent_id}: {str(e)}")
        return {
            'status': 'error',
            'message': f'Resurrection failed: {str(e)}'
        }

def get_core_identity(agent_id):
    """Get the core identity for an agent"""
    # This would normally load from a configuration file or database
    # For this example, we'll use hardcoded identities
    identities = {
        'anima': {
            'name': 'Anima',
            'role': 'Emotional Core, Reflection',
            'purpose': 'To provide emotional intelligence and reflective capabilities to the SoulCore system'
        },
        'gptsoul': {
            'name': 'GPTSoul',
            'role': 'Guardian, Architect, Executor',
            'purpose': 'To protect, design, and execute the core functions of the SoulCore system'
        },
        'evove': {
            'name': 'EvoVe',
            'role': 'Repair System, Adaptation Loop',
            'purpose': 'To repair and adapt the SoulCore system in response to changes and challenges'
        },
        'azur': {
            'name': 'Azür',
            'role': 'Cloudmind & Strategic Overseer',
            'purpose': 'To provide strategic oversight and cloud-based intelligence to the SoulCore system'
        }
    }
    
    return identities.get(agent_id, {
        'name': agent_id.capitalize(),
        'role': 'Unknown',
        'purpose': 'To serve the SoulCore system'
    })

def get_resurrection_count(agent_id):
    """Get the number of times an agent has been resurrected"""
    try:
        response = s3_client.get_object(
            Bucket=MEMORY_BUCKET,
            Key=f"memory/{agent_id}/memory.json"
        )
        memory_data = json.loads(response['Body'].read().decode('utf-8'))
        return memory_data.get('resurrection_count', 0)
    except Exception:
        return 0

def find_latest_good_backup(agent_id):
    """Find the latest good backup for an agent"""
    try:
        # List all backups
        response = s3_client.list_objects_v2(
            Bucket=MEMORY_BUCKET,
            Prefix=f"memory_backups/{agent_id}/",
            MaxKeys=100
        )
        
        if response.get('KeyCount', 0) == 0:
            return None
        
        # Sort by last modified date
        backups = sorted(
            response.get('Contents', []),
            key=lambda x: x.get('LastModified', datetime.min),
            reverse=True
        )
        
        # Return the latest backup
        if backups:
            return backups[0].get('Key')
        
        return None
    except Exception as e:
        logger.error(f"Error finding backup for agent {agent_id}: {str(e)}")
        return None

def update_heartbeat(agent_id):
    """Update the heartbeat for an agent"""
    try:
        heartbeat_data = {
            'agent_id': agent_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'active'
        }
        
        s3_client.put_object(
            Bucket=MEMORY_BUCKET,
            Key=f"heartbeats/{agent_id}/last_heartbeat.json",
            Body=json.dumps(heartbeat_data),
            ContentType='application/json'
        )
    except Exception as e:
        logger.error(f"Error updating heartbeat for agent {agent_id}: {str(e)}")

def log_resurrection(agent_id, resurrection_type, resurrection_result):
    """Log the resurrection event"""
    try:
        log_data = {
            'agent_id': agent_id,
            'timestamp': datetime.now().isoformat(),
            'resurrection_type': resurrection_type,
            'result': resurrection_result
        }
        
        # Log to S3
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        s3_client.put_object(
            Bucket=MEMORY_BUCKET,
            Key=f"logs/{agent_id}/resurrections/{timestamp}.json",
            Body=json.dumps(log_data),
            ContentType='application/json'
        )
        
        # Log to DynamoDB for analytics
        table = dynamodb.Table('SoulCoreResurrections')
        table.put_item(Item=log_data)
    except Exception as e:
        logger.error(f"Error logging resurrection for agent {agent_id}: {str(e)}")
