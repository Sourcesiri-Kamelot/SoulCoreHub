#!/usr/bin/env python3
"""
Update API Endpoints Script
This script updates the API endpoints in the frontend code after deployment
"""

import os
import json
import re
import boto3
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("UpdateAPIEndpoints")

def get_api_endpoint():
    """
    Get the API endpoint from CloudFormation outputs
    
    Returns:
        The API endpoint URL or None if not found
    """
    try:
        # Initialize CloudFormation client
        cloudformation = boto3.client('cloudformation')
        
        # Get the stack outputs
        response = cloudformation.describe_stacks(StackName='soulcore-heartbeat-check')
        outputs = response['Stacks'][0]['Outputs']
        
        # Find the API endpoint output
        for output in outputs:
            if output['OutputKey'] == 'SoulCoreApi':
                return output['OutputValue']
        
        logger.warning("API endpoint not found in CloudFormation outputs")
        return None
    except Exception as e:
        logger.error(f"Error getting API endpoint: {e}")
        return None

def update_file(file_path, api_endpoint):
    """
    Update API endpoint in a file
    
    Args:
        file_path: Path to the file
        api_endpoint: The API endpoint URL
        
    Returns:
        True if the file was updated, False otherwise
    """
    try:
        # Read the file
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Define patterns to match API endpoint definitions
        patterns = [
            r'const\s+API_ENDPOINT\s*=\s*[\'"]([^\'"]*)[\'"]',
            r'const\s+apiUrl\s*=\s*[\'"]([^\'"]*)[\'"]',
            r'apiEndpoint:\s*[\'"]([^\'"]*)[\'"]',
            r'baseURL:\s*[\'"]([^\'"]*)[\'"]'
        ]
        
        # Check if any pattern matches
        updated = False
        for pattern in patterns:
            if re.search(pattern, content):
                # Update the API endpoint
                updated_content = re.sub(pattern, lambda m: m.group(0).replace(m.group(1), api_endpoint), content)
                
                # Write the updated content
                with open(file_path, 'w') as f:
                    f.write(updated_content)
                
                logger.info(f"Updated API endpoint in {file_path}")
                updated = True
                break
        
        if not updated:
            logger.warning(f"No API endpoint pattern matched in {file_path}")
        
        return updated
    except Exception as e:
        logger.error(f"Error updating {file_path}: {e}")
        return False

def update_env_file(api_endpoint):
    """
    Update API endpoint in .env file
    
    Args:
        api_endpoint: The API endpoint URL
        
    Returns:
        True if the file was updated, False otherwise
    """
    try:
        env_path = Path('.env')
        
        # Check if .env file exists
        if env_path.exists():
            # Read the file
            with open(env_path, 'r') as f:
                content = f.read()
            
            # Check if API_ENDPOINT is defined
            if re.search(r'^API_ENDPOINT=', content, re.MULTILINE):
                # Update the API endpoint
                updated_content = re.sub(r'^API_ENDPOINT=.*$', f'API_ENDPOINT={api_endpoint}', content, flags=re.MULTILINE)
                
                # Write the updated content
                with open(env_path, 'w') as f:
                    f.write(updated_content)
                
                logger.info(f"Updated API endpoint in .env file")
                return True
            else:
                # Add API_ENDPOINT to the file
                with open(env_path, 'a') as f:
                    f.write(f'\nAPI_ENDPOINT={api_endpoint}\n')
                
                logger.info(f"Added API endpoint to .env file")
                return True
        else:
            # Create .env file
            with open(env_path, 'w') as f:
                f.write(f'API_ENDPOINT={api_endpoint}\n')
            
            logger.info(f"Created .env file with API endpoint")
            return True
    except Exception as e:
        logger.error(f"Error updating .env file: {e}")
        return False

def main():
    """Main function"""
    logger.info("Updating API endpoints in frontend code...")
    
    # Get the API endpoint
    api_endpoint = get_api_endpoint()
    
    if not api_endpoint:
        logger.error("Failed to get API endpoint")
        return
    
    logger.info(f"API endpoint: {api_endpoint}")
    
    # Update .env file
    update_env_file(api_endpoint)
    
    # Find frontend files
    frontend_dirs = ['public', 'anima-interface', 'anima_ui', 'webui', 'soulcore-gui']
    frontend_extensions = ['.html', '.js', '.jsx', '.ts', '.tsx']
    
    updated_files = 0
    
    for directory in frontend_dirs:
        if not os.path.exists(directory):
            continue
        
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in frontend_extensions):
                    file_path = os.path.join(root, file)
                    if update_file(file_path, api_endpoint):
                        updated_files += 1
    
    logger.info(f"Updated API endpoint in {updated_files} files")

if __name__ == "__main__":
    main()
