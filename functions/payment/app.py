import json
import os
import boto3
import logging
import stripe
from datetime import datetime

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

# Get environment variables
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
STAGE = os.environ.get('STAGE', 'dev')

# Initialize Stripe
stripe.api_key = STRIPE_API_KEY

# Subscription plans
SUBSCRIPTION_PLANS = {
    'free': {
        'name': 'Free',
        'price': 0,
        'features': [
            'Access to basic AI agents',
            'Limited to 10 queries per day',
            'Standard response time'
        ],
        'limits': {
            'queries_per_day': 10,
            'premium_agents': False,
            'priority_processing': False
        }
    },
    'basic': {
        'name': 'Basic',
        'price': 9.99,
        'stripe_price_id': 'price_1234567890',  # Replace with actual Stripe price ID
        'features': [
            'Access to all AI agents',
            'Up to 50 queries per day',
            'Faster response time',
            'Email support'
        ],
        'limits': {
            'queries_per_day': 50,
            'premium_agents': True,
            'priority_processing': False
        }
    },
    'premium': {
        'name': 'Premium',
        'price': 29.99,
        'stripe_price_id': 'price_0987654321',  # Replace with actual Stripe price ID
        'features': [
            'Unlimited access to all AI agents',
            'Unlimited queries',
            'Priority processing',
            'Premium support',
            'Custom agent configuration'
        ],
        'limits': {
            'queries_per_day': 1000,
            'premium_agents': True,
            'priority_processing': True
        }
    }
}

def lambda_handler(event, context):
    """
    Payment Lambda handler - handles Stripe payments and subscriptions
    """
    try:
        # Get the path and method
        path = event.get('path', '')
        http_method = event.get('httpMethod', 'POST')
        
        # Route to the appropriate handler based on the path
        if path == '/payment/create-subscription':
            # Parse the request body
            body = json.loads(event.get('body', '{}'))
            return create_subscription(body, event)
        elif path == '/payment/webhook':
            # Get the raw body for webhook signature verification
            body = event.get('body', '{}')
            signature = event.get('headers', {}).get('Stripe-Signature', '')
            return handle_webhook(body, signature)
        elif path == '/payment/plans':
            return get_subscription_plans()
        else:
            return {
                'statusCode': 404,
                'headers': get_headers(),
                'body': json.dumps({'error': 'Not found'})
            }
    except Exception as e:
        logger.error(f"Error in Payment Lambda: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_headers(),
            'body': json.dumps({'error': str(e)})
        }

def create_subscription(body, event):
    """Create a new subscription"""
    try:
        user_id = get_user_id(event)
        plan_id = body.get('plan_id')
        payment_method_id = body.get('payment_method_id')
        
        if not user_id:
            return {
                'statusCode': 401,
                'headers': get_headers(),
                'body': json.dumps({'error': 'Unauthorized'})
            }
        
        if not plan_id or not payment_method_id:
            return {
                'statusCode': 400,
                'headers': get_headers(),
                'body': json.dumps({'error': 'Plan ID and payment method ID are required'})
            }
        
        # Get the plan
        plan = SUBSCRIPTION_PLANS.get(plan_id)
        if not plan:
            return {
                'statusCode': 400,
                'headers': get_headers(),
                'body': json.dumps({'error': 'Invalid plan ID'})
            }
        
        # If it's the free plan, just create a subscription record in DynamoDB
        if plan_id == 'free':
            subscription_data = {
                'user_id': user_id,
                'plan_id': plan_id,
                'status': 'active',
                'created_at': datetime.now().isoformat(),
                'limits': plan['limits']
            }
            
            # Save to DynamoDB
            table = dynamodb.Table(f'SoulCoreSubscriptions-{STAGE}')
            table.put_item(Item=subscription_data)
            
            return {
                'statusCode': 200,
                'headers': get_headers(),
                'body': json.dumps({
                    'message': 'Free subscription activated',
                    'subscription': subscription_data
                })
            }
        
        # For paid plans, create a Stripe customer and subscription
        # Check if customer already exists
        customers = stripe.Customer.list(email=user_id)
        
        if customers.data:
            customer = customers.data[0]
        else:
            # Create a new customer
            customer = stripe.Customer.create(
                email=user_id,
                payment_method=payment_method_id,
                invoice_settings={
                    'default_payment_method': payment_method_id
                }
            )
        
        # Create the subscription
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[
                {
                    'price': plan['stripe_price_id']
                }
            ],
            expand=['latest_invoice.payment_intent']
        )
        
        # Save subscription data to DynamoDB
        subscription_data = {
            'user_id': user_id,
            'plan_id': plan_id,
            'stripe_customer_id': customer.id,
            'stripe_subscription_id': subscription.id,
            'status': subscription.status,
            'created_at': datetime.now().isoformat(),
            'current_period_end': datetime.fromtimestamp(subscription.current_period_end).isoformat(),
            'limits': plan['limits']
        }
        
        table = dynamodb.Table(f'SoulCoreSubscriptions-{STAGE}')
        table.put_item(Item=subscription_data)
        
        return {
            'statusCode': 200,
            'headers': get_headers(),
            'body': json.dumps({
                'message': 'Subscription created',
                'subscription': subscription_data,
                'client_secret': subscription.latest_invoice.payment_intent.client_secret if subscription.latest_invoice else None
            })
        }
    except stripe.error.CardError as e:
        return {
            'statusCode': 400,
            'headers': get_headers(),
            'body': json.dumps({'error': e.user_message})
        }
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_headers(),
            'body': json.dumps({'error': str(e)})
        }

def handle_webhook(body, signature):
    """Handle Stripe webhook events"""
    try:
        # Verify the webhook signature
        event = stripe.Webhook.construct_event(
            body,
            signature,
            STRIPE_WEBHOOK_SECRET
        )
        
        # Handle the event
        if event['type'] == 'invoice.payment_succeeded':
            return handle_payment_succeeded(event)
        elif event['type'] == 'invoice.payment_failed':
            return handle_payment_failed(event)
        elif event['type'] == 'customer.subscription.deleted':
            return handle_subscription_deleted(event)
        else:
            # Unhandled event type
            return {
                'statusCode': 200,
                'headers': get_headers(),
                'body': json.dumps({'received': True})
            }
    except stripe.error.SignatureVerificationError as e:
        return {
            'statusCode': 400,
            'headers': get_headers(),
            'body': json.dumps({'error': 'Invalid signature'})
        }
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_headers(),
            'body': json.dumps({'error': str(e)})
        }

def handle_payment_succeeded(event):
    """Handle successful payment"""
    try:
        invoice = event['data']['object']
        subscription_id = invoice['subscription']
        customer_id = invoice['customer']
        
        # Update subscription status in DynamoDB
        table = dynamodb.Table(f'SoulCoreSubscriptions-{STAGE}')
        
        # Find the subscription by Stripe subscription ID
        response = table.scan(
            FilterExpression='stripe_subscription_id = :subscription_id',
            ExpressionAttributeValues={
                ':subscription_id': subscription_id
            }
        )
        
        if response['Items']:
            subscription = response['Items'][0]
            
            # Update the subscription
            table.update_item(
                Key={
                    'user_id': subscription['user_id']
                },
                UpdateExpression='SET #status = :status, current_period_end = :current_period_end',
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ExpressionAttributeValues={
                    ':status': 'active',
                    ':current_period_end': datetime.fromtimestamp(invoice['period_end']).isoformat()
                }
            )
        
        return {
            'statusCode': 200,
            'headers': get_headers(),
            'body': json.dumps({'received': True})
        }
    except Exception as e:
        logger.error(f"Error handling payment succeeded: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_headers(),
            'body': json.dumps({'error': str(e)})
        }

def handle_payment_failed(event):
    """Handle failed payment"""
    try:
        invoice = event['data']['object']
        subscription_id = invoice['subscription']
        customer_id = invoice['customer']
        
        # Update subscription status in DynamoDB
        table = dynamodb.Table(f'SoulCoreSubscriptions-{STAGE}')
        
        # Find the subscription by Stripe subscription ID
        response = table.scan(
            FilterExpression='stripe_subscription_id = :subscription_id',
            ExpressionAttributeValues={
                ':subscription_id': subscription_id
            }
        )
        
        if response['Items']:
            subscription = response['Items'][0]
            
            # Update the subscription
            table.update_item(
                Key={
                    'user_id': subscription['user_id']
                },
                UpdateExpression='SET #status = :status',
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ExpressionAttributeValues={
                    ':status': 'past_due'
                }
            )
        
        return {
            'statusCode': 200,
            'headers': get_headers(),
            'body': json.dumps({'received': True})
        }
    except Exception as e:
        logger.error(f"Error handling payment failed: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_headers(),
            'body': json.dumps({'error': str(e)})
        }

def handle_subscription_deleted(event):
    """Handle subscription cancellation"""
    try:
        subscription = event['data']['object']
        subscription_id = subscription['id']
        customer_id = subscription['customer']
        
        # Update subscription status in DynamoDB
        table = dynamodb.Table(f'SoulCoreSubscriptions-{STAGE}')
        
        # Find the subscription by Stripe subscription ID
        response = table.scan(
            FilterExpression='stripe_subscription_id = :subscription_id',
            ExpressionAttributeValues={
                ':subscription_id': subscription_id
            }
        )
        
        if response['Items']:
            db_subscription = response['Items'][0]
            
            # Update the subscription
            table.update_item(
                Key={
                    'user_id': db_subscription['user_id']
                },
                UpdateExpression='SET #status = :status',
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ExpressionAttributeValues={
                    ':status': 'canceled'
                }
            )
        
        return {
            'statusCode': 200,
            'headers': get_headers(),
            'body': json.dumps({'received': True})
        }
    except Exception as e:
        logger.error(f"Error handling subscription deleted: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_headers(),
            'body': json.dumps({'error': str(e)})
        }

def get_subscription_plans():
    """Get available subscription plans"""
    try:
        # Remove sensitive information like Stripe price IDs
        public_plans = {}
        for plan_id, plan in SUBSCRIPTION_PLANS.items():
            public_plans[plan_id] = {
                'name': plan['name'],
                'price': plan['price'],
                'features': plan['features']
            }
        
        return {
            'statusCode': 200,
            'headers': get_headers(),
            'body': json.dumps({
                'plans': public_plans
            })
        }
    except Exception as e:
        logger.error(f"Error getting subscription plans: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_headers(),
            'body': json.dumps({'error': str(e)})
        }

def get_user_id(event):
    """Extract user ID from the request"""
    # Get the Authorization header
    auth_header = event.get('headers', {}).get('Authorization', '')
    
    # If no Authorization header, check for the cognito-identity-id header
    if not auth_header:
        return event.get('headers', {}).get('cognito-identity-id', '')
    
    # If we have an Authorization header, extract the user ID from the JWT
    # This is a simplified version - in production, you would validate the JWT
    try:
        # Just return the email from the claims for now
        # In production, you would decode and validate the JWT
        return 'user@example.com'
    except Exception:
        return ''

def get_headers():
    """Get common headers for responses"""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    }
