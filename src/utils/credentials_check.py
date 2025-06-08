"""
SoulCoreHub Credentials Check Utility
------------------------------------
Validates that all required credentials are present in the .env file
and prompts the user to enter any missing credentials.
"""

import os
import sys
from dotenv import load_dotenv, set_key

def check_credentials():
    """
    Check if all required credentials are present in the .env file.
    Prompt the user to enter any missing credentials.
    """
    # Load environment variables
    load_dotenv()
    
    # Define required credentials
    required_credentials = {
        'SMTP_SERVER': 'SMTP server address',
        'SMTP_PORT': 'SMTP port',
        'SMTP_USERNAME': 'SMTP username',
        'SMTP_PASSWORD': 'SMTP password',
        'DEFAULT_SENDER': 'Default sender email address',
        'EMAIL_BUCKET': 'S3 bucket for email storage',
        'AWS_ACCESS_KEY_ID': 'AWS access key ID',
        'AWS_SECRET_ACCESS_KEY': 'AWS secret access key'
    }
    
    # Check for missing credentials
    missing_credentials = {}
    for key, description in required_credentials.items():
        if not os.getenv(key):
            missing_credentials[key] = description
    
    # If no credentials are missing, return True
    if not missing_credentials:
        print("✅ All required credentials are present.")
        return True
    
    # Prompt the user to enter missing credentials
    print("\n⚠️ Some required credentials are missing from your .env file.")
    print("Please enter the following credentials:\n")
    
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
    
    for key, description in missing_credentials.items():
        value = input(f"{description} ({key}): ")
        if value:
            # Update .env file
            set_key(env_path, key, value)
            os.environ[key] = value
        else:
            print(f"⚠️ Warning: {key} is required for full functionality.")
    
    # Reload environment variables
    load_dotenv()
    
    # Check if all required credentials are now present
    for key in missing_credentials.keys():
        if not os.getenv(key):
            print(f"\n❌ Error: {key} is still missing. Some features may not work correctly.")
            return False
    
    print("\n✅ All credentials have been updated successfully.")
    return True

def test_smtp_connection():
    """
    Test the SMTP connection using the credentials in the .env file.
    """
    import smtplib
    
    # Load environment variables
    load_dotenv()
    
    # Get SMTP credentials
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    if not all([smtp_server, smtp_port, smtp_username, smtp_password]):
        print("❌ SMTP credentials are missing. Cannot test connection.")
        return False
    
    try:
        # Create SMTP connection
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        
        # Login
        server.login(smtp_username, smtp_password)
        
        # Close connection
        server.quit()
        
        print("✅ SMTP connection test successful.")
        return True
    except Exception as e:
        print(f"❌ SMTP connection test failed: {e}")
        return False

def test_aws_connection():
    """
    Test the AWS connection using the credentials in the .env file.
    """
    import boto3
    from botocore.exceptions import ClientError
    
    # Load environment variables
    load_dotenv()
    
    # Get AWS credentials
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    if not all([aws_access_key_id, aws_secret_access_key]):
        print("❌ AWS credentials are missing. Cannot test connection.")
        return False
    
    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        
        # List buckets
        response = s3_client.list_buckets()
        
        print(f"✅ AWS connection test successful. Found {len(response['Buckets'])} buckets.")
        return True
    except ClientError as e:
        print(f"❌ AWS connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("SoulCoreHub Credentials Check")
    print("=============================\n")
    
    # Check credentials
    if check_credentials():
        # Test connections
        print("\nTesting connections...")
        test_smtp_connection()
        test_aws_connection()
    else:
        print("\nPlease update your credentials and run this script again.")
