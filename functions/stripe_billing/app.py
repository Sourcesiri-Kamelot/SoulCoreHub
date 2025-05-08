import json
import os
import time
import logging
import boto3
import stripe
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Stripe with API key from environment variable or Secrets Manager
stripe.api_key = os.environ.get('STRIPE_API_KEY')

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
subscriptions_table = dynamodb.Table(os.environ.get('SUBSCRIPTIONS_TABLE', 'SoulCoreSubscriptions-dev'))
usage_table = dynamodb.Table(os.environ.get('USAGE_TABLE', 'SoulCoreUsage-dev'))

def lambda_handler(event, context):
    """
    Lambda handler for Stripe billing operations
    
    Supported operations:
    - Record usage for a metered subscription
    - Verify subscription status
    - Get subscription details
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Determine if this is an API Gateway event or direct Lambda invocation
    if 'body' in event:
        # API Gateway event
        try:
            body = json.loads(event['body'])
        except:
            body = event['body']
    else:
        # Direct Lambda invocation
        body = event
    
    # Extract operation type
    operation = body.get('operation', 'record_usage')
    
    if operation == 'record_usage':
        return record_usage(body)
    elif operation == 'verify_subscription':
        return verify_subscription(body)
    elif operation == 'get_subscription':
        return get_subscription(body)
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Unsupported operation: {operation}'})
        }

def record_usage(data):
    """Record usage for a metered subscription"""
    user_id = data.get('user_id')
    units = data.get('units', 1)
    reason = data.get('reason', 'api_usage')
    
    if not user_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'user_id is required'})
        }
    
    try:
        # Get subscription item ID from DynamoDB
        response = subscriptions_table.get_item(
            Key={'user_id': user_id}
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'No subscription found for user {user_id}'})
            }
        
        subscription_data = response['Item']
        subscription_item_id = subscription_data.get('subscription_item_id')
        
        if not subscription_item_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No subscription_item_id found for user'})
            }
        
        # Record usage in Stripe
        usage_record = stripe.UsageRecord.create(
            subscription_item=subscription_item_id,
            quantity=units,
            timestamp=int(time.time()),
            action='increment'
        )
        
        # Record usage in DynamoDB for tracking
        today = datetime.now().strftime('%Y-%m-%d')
        usage_table.update_item(
            Key={
                'user_id': user_id,
                'usage_date': today
            },
            UpdateExpression='ADD units :units',
            ExpressionAttributeValues={
                ':units': units
            },
            ReturnValues='UPDATED_NEW'
        )
        
        logger.info(f"Recorded {units} units for user {user_id}, reason: {reason}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully recorded {units} units for user {user_id}',
                'usage_record_id': usage_record.id
            })
        }
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Stripe error: {str(e)}'})
        }
    
    except Exception as e:
        logger.error(f"Error recording usage: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error recording usage: {str(e)}'})
        }

def verify_subscription(data):
    """Verify if a user has an active subscription"""
    user_id = data.get('user_id')
    
    if not user_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'user_id is required'})
        }
    
    try:
        # Get subscription from DynamoDB
        response = subscriptions_table.get_item(
            Key={'user_id': user_id}
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'has_subscription': False,
                    'message': f'No subscription found for user {user_id}'
                })
            }
        
        subscription_data = response['Item']
        subscription_id = subscription_data.get('subscription_id')
        
        if not subscription_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'has_subscription': False,
                    'message': 'No subscription_id found for user'
                })
            }
        
        # Verify subscription status in Stripe
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        is_active = subscription.status == 'active'
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'has_subscription': is_active,
                'subscription_status': subscription.status,
                'plan': subscription_data.get('plan_name', 'unknown')
            })
        }
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Stripe error: {str(e)}'})
        }
    
    except Exception as e:
        logger.error(f"Error verifying subscription: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error verifying subscription: {str(e)}'})
        }

def get_subscription(data):
    """Get subscription details for a user"""
    user_id = data.get('user_id')
    
    if not user_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'user_id is required'})
        }
    
    try:
        # Get subscription from DynamoDB
        response = subscriptions_table.get_item(
            Key={'user_id': user_id}
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'No subscription found for user {user_id}'})
            }
        
        subscription_data = response['Item']
        
        # Get usage data
        today = datetime.now().strftime('%Y-%m-%d')
        usage_response = usage_table.get_item(
            Key={
                'user_id': user_id,
                'usage_date': today
            }
        )
        
        usage_today = 0
        if 'Item' in usage_response:
            usage_today = usage_response['Item'].get('units', 0)
        
        # Return subscription details with usage
        return {
            'statusCode': 200,
            'body': json.dumps({
                'subscription': {
                    'plan': subscription_data.get('plan_name', 'unknown'),
                    'status': subscription_data.get('status', 'unknown'),
                    'created_at': subscription_data.get('created_at'),
                    'current_period_end': subscription_data.get('current_period_end')
                },
                'usage': {
                    'today': usage_today,
                    'limit': subscription_data.get('usage_limit', 0)
                }
            })
        }
    
    except Exception as e:
        logger.error(f"Error getting subscription: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error getting subscription: {str(e)}'})
        }
