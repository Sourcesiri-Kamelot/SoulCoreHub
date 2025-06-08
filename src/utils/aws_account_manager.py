#!/usr/bin/env python3
"""
AWS Account Manager for SoulCoreHub
Manages multiple AWS accounts and provides seamless switching between them
"""

import os
import boto3
import json
import logging
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AWSAccountManager')

class AWSAccountManager:
    """
    Manages multiple AWS accounts and provides methods to switch between them
    and create appropriate clients for different AWS services.
    """
    
    def __init__(self, default_profile='default', default_region='us-east-1'):
        """
        Initialize the AWS Account Manager
        
        Args:
            default_profile (str): Default AWS profile to use
            default_region (str): Default AWS region to use
        """
        load_dotenv()  # Load environment variables from .env file
        
        self.default_profile = default_profile
        self.default_region = default_region
        self.current_profile = default_profile
        self.current_region = default_region
        
        # Load account configurations
        self.accounts = self._load_account_configs()
        
        # Initialize session with default profile
        self.session = boto3.Session(
            profile_name=self.current_profile,
            region_name=self.current_region
        )
        
        logger.info(f"AWS Account Manager initialized with profile: {self.current_profile}")
    
    def _load_account_configs(self):
        """
        Load AWS account configurations from environment variables
        
        Returns:
            dict: Dictionary of account configurations
        """
        accounts = {
            'default': {
                'account_id': os.getenv('AWS_ACCOUNT_ID'),
                'access_key': os.getenv('AWS_ACCESS_KEY_ID'),
                'secret_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
                'region': os.getenv('AWS_REGION', self.default_region)
            }
        }
        
        # Load secondary account if available
        if os.getenv('AWS_SECONDARY_ACCOUNT_ID'):
            accounts['secondary'] = {
                'account_id': os.getenv('AWS_SECONDARY_ACCOUNT_ID'),
                'access_key': os.getenv('AWS_SECONDARY_ACCESS_KEY_ID'),
                'secret_key': os.getenv('AWS_SECONDARY_SECRET_ACCESS_KEY'),
                'region': os.getenv('AWS_SECONDARY_REGION', self.default_region)
            }
        
        return accounts
    
    def switch_account(self, account_name):
        """
        Switch to a different AWS account
        
        Args:
            account_name (str): Name of the account to switch to
            
        Returns:
            bool: True if switch was successful, False otherwise
        """
        if account_name not in self.accounts:
            logger.error(f"Account '{account_name}' not found in configurations")
            return False
        
        account = self.accounts[account_name]
        
        # Create new session with account credentials
        try:
            self.session = boto3.Session(
                aws_access_key_id=account['access_key'],
                aws_secret_access_key=account['secret_key'],
                region_name=account['region']
            )
            self.current_profile = account_name
            self.current_region = account['region']
            
            logger.info(f"Switched to account: {account_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to switch to account '{account_name}': {str(e)}")
            return False
    
    def get_client(self, service_name, region=None):
        """
        Get a boto3 client for the specified service
        
        Args:
            service_name (str): Name of the AWS service
            region (str, optional): AWS region for the client
            
        Returns:
            boto3.client: Boto3 client for the specified service
        """
        if region is None:
            region = self.current_region
        
        try:
            return self.session.client(service_name, region_name=region)
        except Exception as e:
            logger.error(f"Failed to create client for service '{service_name}': {str(e)}")
            return None
    
    def get_resource(self, service_name, region=None):
        """
        Get a boto3 resource for the specified service
        
        Args:
            service_name (str): Name of the AWS service
            region (str, optional): AWS region for the resource
            
        Returns:
            boto3.resource: Boto3 resource for the specified service
        """
        if region is None:
            region = self.current_region
        
        try:
            return self.session.resource(service_name, region_name=region)
        except Exception as e:
            logger.error(f"Failed to create resource for service '{service_name}': {str(e)}")
            return None
    
    def assume_role(self, role_arn, session_name="SoulCoreHubSession"):
        """
        Assume an IAM role
        
        Args:
            role_arn (str): ARN of the role to assume
            session_name (str): Name for the assumed role session
            
        Returns:
            boto3.Session: New session with the assumed role
        """
        try:
            sts_client = self.session.client('sts')
            response = sts_client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=session_name
            )
            
            credentials = response['Credentials']
            
            # Create new session with assumed role credentials
            new_session = boto3.Session(
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken'],
                region_name=self.current_region
            )
            
            logger.info(f"Successfully assumed role: {role_arn}")
            return new_session
        except Exception as e:
            logger.error(f"Failed to assume role '{role_arn}': {str(e)}")
            return None
    
    def get_account_info(self):
        """
        Get information about the current AWS account
        
        Returns:
            dict: Account information
        """
        try:
            sts_client = self.session.client('sts')
            response = sts_client.get_caller_identity()
            
            return {
                'account_id': response['Account'],
                'user_id': response['UserId'],
                'arn': response['Arn'],
                'profile': self.current_profile,
                'region': self.current_region
            }
        except Exception as e:
            logger.error(f"Failed to get account info: {str(e)}")
            return None
    
    def list_resources(self, service_name, method_name, **kwargs):
        """
        List resources for a specific AWS service
        
        Args:
            service_name (str): Name of the AWS service
            method_name (str): Name of the method to call
            **kwargs: Additional arguments to pass to the method
            
        Returns:
            list: List of resources
        """
        try:
            client = self.get_client(service_name)
            method = getattr(client, method_name)
            response = method(**kwargs)
            
            # Most AWS list methods return a list under a key that's the plural of the resource
            # Try to find that key, otherwise return the whole response
            for key in response:
                if isinstance(response[key], list):
                    return response[key]
            
            return response
        except Exception as e:
            logger.error(f"Failed to list resources for service '{service_name}': {str(e)}")
            return []

if __name__ == "__main__":
    # Example usage
    aws_manager = AWSAccountManager()
    account_info = aws_manager.get_account_info()
    print(f"Current account: {json.dumps(account_info, indent=2)}")
