#!/usr/bin/env python3
"""
AWS Secrets Manager Integration for SoulCoreHub

This module provides functions to securely retrieve secrets from AWS Secrets Manager.
"""

import json
import os
import time
import boto3
from botocore.exceptions import ClientError

# Cache for secrets to avoid repeated calls to AWS Secrets Manager
_secrets_cache = {}
_secrets_last_fetched = {}
_SECRETS_CACHE_TTL = 3600  # 1 hour in seconds

def get_secrets(secret_name, use_cache=True):
    """
    Retrieve a secret from AWS Secrets Manager
    
    Args:
        secret_name (str): Name of the secret to retrieve
        use_cache (bool): Whether to use cached secrets if available
        
    Returns:
        dict: Parsed secret value as a dictionary
    """
    # Check cache first if enabled
    now = time.time()
    if use_cache and secret_name in _secrets_cache:
        last_fetched = _secrets_last_fetched.get(secret_name, 0)
        if now - last_fetched < _SECRETS_CACHE_TTL:
            return _secrets_cache[secret_name]
    
    # Get AWS region from environment or use default
    region_name = os.environ.get('AWS_REGION', 'us-east-1')
    
    # Create a Secrets Manager client
    try:
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
    except Exception as e:
        print(f"Error creating AWS Secrets Manager client: {e}")
        return get_secrets_from_env(secret_name)
    
    try:
        # Get the secret value
        response = client.get_secret_value(SecretId=secret_name)
        
        # Parse and return the secret string
        if 'SecretString' in response:
            secret = json.loads(response['SecretString'])
            
            # Update cache
            _secrets_cache[secret_name] = secret
            _secrets_last_fetched[secret_name] = now
            
            return secret
        else:
            # Handle binary secrets if needed
            decoded_binary_secret = base64.b64decode(response['SecretBinary'])
            secret = json.loads(decoded_binary_secret)
            
            # Update cache
            _secrets_cache[secret_name] = secret
            _secrets_last_fetched[secret_name] = now
            
            return secret
            
    except ClientError as e:
        print(f"Error retrieving secret {secret_name}: {e}")
        # Fall back to environment variables
        return get_secrets_from_env(secret_name)
    except Exception as e:
        print(f"Unexpected error retrieving secret {secret_name}: {e}")
        return get_secrets_from_env(secret_name)

def get_secret_value(secret_name, key, default_value=''):
    """
    Get a specific secret value by key
    
    Args:
        secret_name (str): Name of the secret to retrieve
        key (str): Key of the specific secret value to retrieve
        default_value (str): Default value if not found
        
    Returns:
        str: The specific secret value or default
    """
    secrets = get_secrets(secret_name)
    return secrets.get(key, default_value)

def get_secrets_from_env(secret_name):
    """
    Fallback function to get secrets from environment variables
    when AWS Secrets Manager is not available (e.g., local development)
    
    Args:
        secret_name (str): Name of the secret group to emulate
        
    Returns:
        dict: Dictionary of environment variables that match the pattern
    """
    print(f"Falling back to environment variables for {secret_name}")
    
    # Common secret mappings
    common_secrets = {
        'SoulCoreSecrets': [
            'STRIPE_API_KEY',
            'STRIPE_WEBHOOK_SECRET',
            'JWT_SECRET',
            'DATABASE_URL',
            'HUGGINGFACE_API_KEY'
        ],
        'DatabaseSecrets': [
            'DB_HOST',
            'DB_USER',
            'DB_PASSWORD',
            'DB_NAME',
            'DB_PORT'
        ]
    }
    
    result = {}
    
    # If we know the structure of this secret, use that
    if secret_name in common_secrets:
        for key in common_secrets[secret_name]:
            if key in os.environ:
                result[key] = os.environ[key]
    else:
        # Otherwise, try to find environment variables with a matching prefix
        prefix = secret_name.upper().replace('-', '_') + '_'
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Remove the prefix to match AWS Secrets Manager format
                short_key = key[len(prefix):]
                result[short_key] = value
    
    return result

def clear_secrets_cache():
    """Clear the secrets cache"""
    _secrets_cache.clear()
    _secrets_last_fetched.clear()

# For testing
if __name__ == "__main__":
    # Test with a sample secret
    test_secret_name = "SoulCoreSecrets"
    print(f"Testing get_secrets with {test_secret_name}")
    
    try:
        secrets = get_secrets(test_secret_name)
        print(f"Retrieved {len(secrets)} secret values")
        
        # Don't print actual secrets, just the keys
        print(f"Secret keys: {list(secrets.keys())}")
    except Exception as e:
        print(f"Error testing get_secrets: {e}")
