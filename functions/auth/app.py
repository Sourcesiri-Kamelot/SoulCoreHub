import json
import os
import boto3
import logging
from datetime import datetime

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
cognito_idp = boto3.client('cognito-idp')
dynamodb = boto3.resource('dynamodb')

# Get environment variables
USER_POOL_ID = os.environ.get('USER_POOL_ID')
USER_POOL_CLIENT_ID = os.environ.get('USER_POOL_CLIENT_ID')
STAGE = os.environ.get('STAGE', 'dev')

def lambda_handler(event, context):
    """
    Auth Lambda handler - handles user authentication and registration
    """
    try:
        # Get the path and method
        path = event.get('path', '')
        http_method = event.get('httpMethod', 'POST')
        
        # Parse the request body
        body = json.loads(event.get('body', '{}'))
        
        # Route to the appropriate handler based on the path
        if path == '/auth/register':
            return register_user(body)
        elif path == '/auth/login':
            return login_user(body)
        elif path == '/auth/forgot-password':
            return forgot_password(body)
        elif path == '/auth/reset-password':
            return reset_password(body)
        else:
            return {
                'statusCode': 404,
                'headers': get_headers(),
                'body': json.dumps({'error': 'Not found'})
            }
    except Exception as e:
        logger.error(f"Error in Auth Lambda: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_headers(),
            'body': json.dumps({'error': str(e)})
        }

def register_user(body):
    """Register a new user"""
    try:
        email = body.get('email')
        password = body.get('password')
        name = body.get('name', '')
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': get_headers(),
                'body': json.dumps({'error': 'Email and password are required'})
            }
        
        # Register the user
        response = cognito_idp.sign_up(
            ClientId=USER_POOL_CLIENT_ID,
            Username=email,
            Password=password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                },
                {
                    'Name': 'name',
                    'Value': name
                }
            ]
        )
        
        # Auto-confirm the user (for development purposes)
        if STAGE == 'dev':
            cognito_idp.admin_confirm_sign_up(
                UserPoolId=USER_POOL_ID,
                Username=email
            )
        
        return {
            'statusCode': 200,
            'headers': get_headers(),
            'body': json.dumps({
                'message': 'User registered successfully',
                'userSub': response['UserSub'],
                'userConfirmed': response['UserConfirmed']
            })
        }
    except cognito_idp.exceptions.UsernameExistsException:
        return {
            'statusCode': 400,
            'headers': get_headers(),
            'body': json.dumps({'error': 'User already exists'})
        }
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_headers(),
            'body': json.dumps({'error': str(e)})
        }

def login_user(body):
    """Login a user"""
    try:
        email = body.get('email')
        password = body.get('password')
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': get_headers(),
                'body': json.dumps({'error': 'Email and password are required'})
            }
        
        # Authenticate the user
        response = cognito_idp.initiate_auth(
            ClientId=USER_POOL_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )
        
        # Get user attributes
        user_info = cognito_idp.get_user(
            AccessToken=response['AuthenticationResult']['AccessToken']
        )
        
        # Extract user attributes
        user_attributes = {}
        for attr in user_info['UserAttributes']:
            user_attributes[attr['Name']] = attr['Value']
        
        return {
            'statusCode': 200,
            'headers': get_headers(),
            'body': json.dumps({
                'message': 'Login successful',
                'idToken': response['AuthenticationResult']['IdToken'],
                'accessToken': response['AuthenticationResult']['AccessToken'],
                'refreshToken': response['AuthenticationResult']['RefreshToken'],
                'expiresIn': response['AuthenticationResult']['ExpiresIn'],
                'user': {
                    'email': user_attributes.get('email', ''),
                    'name': user_attributes.get('name', ''),
                    'sub': user_attributes.get('sub', '')
                }
            })
        }
    except cognito_idp.exceptions.NotAuthorizedException:
        return {
            'statusCode': 401,
            'headers': get_headers(),
            'body': json.dumps({'error': 'Incorrect username or password'})
        }
    except cognito_idp.exceptions.UserNotFoundException:
        return {
            'statusCode': 404,
            'headers': get_headers(),
            'body': json.dumps({'error': 'User not found'})
        }
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_headers(),
            'body': json.dumps({'error': str(e)})
        }

def forgot_password(body):
    """Initiate forgot password flow"""
    try:
        email = body.get('email')
        
        if not email:
            return {
                'statusCode': 400,
                'headers': get_headers(),
                'body': json.dumps({'error': 'Email is required'})
            }
        
        # Initiate forgot password flow
        cognito_idp.forgot_password(
            ClientId=USER_POOL_CLIENT_ID,
            Username=email
        )
        
        return {
            'statusCode': 200,
            'headers': get_headers(),
            'body': json.dumps({
                'message': 'Password reset code sent to email'
            })
        }
    except cognito_idp.exceptions.UserNotFoundException:
        return {
            'statusCode': 404,
            'headers': get_headers(),
            'body': json.dumps({'error': 'User not found'})
        }
    except Exception as e:
        logger.error(f"Error initiating forgot password: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_headers(),
            'body': json.dumps({'error': str(e)})
        }

def reset_password(body):
    """Reset password with confirmation code"""
    try:
        email = body.get('email')
        code = body.get('code')
        new_password = body.get('password')
        
        if not email or not code or not new_password:
            return {
                'statusCode': 400,
                'headers': get_headers(),
                'body': json.dumps({'error': 'Email, code, and password are required'})
            }
        
        # Confirm forgot password
        cognito_idp.confirm_forgot_password(
            ClientId=USER_POOL_CLIENT_ID,
            Username=email,
            ConfirmationCode=code,
            Password=new_password
        )
        
        return {
            'statusCode': 200,
            'headers': get_headers(),
            'body': json.dumps({
                'message': 'Password reset successful'
            })
        }
    except cognito_idp.exceptions.CodeMismatchException:
        return {
            'statusCode': 400,
            'headers': get_headers(),
            'body': json.dumps({'error': 'Invalid verification code'})
        }
    except cognito_idp.exceptions.UserNotFoundException:
        return {
            'statusCode': 404,
            'headers': get_headers(),
            'body': json.dumps({'error': 'User not found'})
        }
    except Exception as e:
        logger.error(f"Error resetting password: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_headers(),
            'body': json.dumps({'error': str(e)})
        }

def get_headers():
    """Get common headers for responses"""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    }
