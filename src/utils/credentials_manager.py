#!/usr/bin/env python3
"""
Credentials Manager for SoulCoreHub
Securely manages and provides access to all credentials
"""

import os
import json
import base64
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv, set_key, find_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('CredentialsManager')

class CredentialsManager:
    """
    Manages credentials for SoulCoreHub
    Provides secure access to credentials from .env file
    Supports encryption for credential exports
    """
    
    # Define credential categories
    CATEGORIES = {
        'aws': [
            'AWS_ACCESS_KEY_ID', 
            'AWS_SECRET_ACCESS_KEY', 
            'AWS_ACCOUNT_ID',
            'AWS_REGION',
            'AWS_SECONDARY_ACCESS_KEY_ID',
            'AWS_SECONDARY_SECRET_ACCESS_KEY',
            'AWS_SECONDARY_ACCOUNT_ID',
            'AWS_SECONDARY_REGION'
        ],
        'email': [
            'SMTP_SERVER',
            'SMTP_PORT',
            'SMTP_USERNAME',
            'SMTP_PASSWORD',
            'EMAIL_FROM',
            'EMAIL_REPLY_TO'
        ],
        'nvidia': [
            'NVIDIA_NGC_API_KEY',
            'NVIDIA_NGC_ORG',
            'NVIDIA_NGC_TEAM'
        ],
        'git': [
            'GITHUB_TOKEN',
            'GITLAB_TOKEN',
            'CODECOMMIT_USERNAME',
            'CODECOMMIT_PASSWORD'
        ],
        'microsoft': [
            'AZURE_TENANT_ID',
            'AZURE_CLIENT_ID',
            'AZURE_CLIENT_SECRET',
            'MICROSOFT_API_KEY'
        ],
        'api_keys': [
            'NAMECHEAP_API_KEY',
            'COGCACHE_API_KEY',
            'DOCKER_HUB_TOKEN',
            'OPENAI_API_KEY',
            'HUGGINGFACE_API_KEY',
            'ANTHROPIC_API_KEY'
        ],
        'development': [
            'UNREAL_ENGINE_LICENSE',
            'JETBRAINS_LICENSE',
            'VSCODE_SYNC_TOKEN'
        ],
        'blockchain': [
            'ETH_PRIVATE_KEY',
            'ETH_WALLET_ADDRESS',
            'SOLANA_PRIVATE_KEY',
            'SOLANA_WALLET_ADDRESS'
        ],
        'streaming': [
            'TWITCH_CLIENT_ID',
            'TWITCH_CLIENT_SECRET',
            'YOUTUBE_API_KEY'
        ]
    }
    
    def __init__(self, env_file=None):
        """
        Initialize the Credentials Manager
        
        Args:
            env_file (str, optional): Path to .env file
        """
        if env_file is None:
            env_file = find_dotenv()
            if not env_file:
                env_file = os.path.join(os.getcwd(), '.env')
                
        self.env_file = env_file
        load_dotenv(self.env_file)
        logger.info(f"Credentials Manager initialized with env file: {self.env_file}")
    
    def get_credential(self, key, default=None):
        """
        Get a credential by key
        
        Args:
            key (str): Credential key
            default: Default value if credential is not found
            
        Returns:
            str: Credential value or default
        """
        value = os.getenv(key, default)
        return value
    
    def set_credential(self, key, value):
        """
        Set a credential
        
        Args:
            key (str): Credential key
            value (str): Credential value
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            set_key(self.env_file, key, value)
            os.environ[key] = value
            logger.info(f"Credential '{key}' set successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to set credential '{key}': {str(e)}")
            return False
    
    def get_credentials_by_category(self, category):
        """
        Get all credentials for a specific category
        
        Args:
            category (str): Credential category
            
        Returns:
            dict: Dictionary of credentials for the category
        """
        if category not in self.CATEGORIES:
            logger.error(f"Category '{category}' not found")
            return {}
        
        credentials = {}
        for key in self.CATEGORIES[category]:
            value = self.get_credential(key)
            if value is not None:
                credentials[key] = value
        
        return credentials
    
    def list_categories(self):
        """
        List all credential categories
        
        Returns:
            list: List of credential categories
        """
        return list(self.CATEGORIES.keys())
    
    def get_all_credentials(self, mask_sensitive=True):
        """
        Get all credentials
        
        Args:
            mask_sensitive (bool): Whether to mask sensitive values
            
        Returns:
            dict: Dictionary of all credentials by category
        """
        all_credentials = {}
        
        for category, keys in self.CATEGORIES.items():
            category_credentials = {}
            for key in keys:
                value = self.get_credential(key)
                if value is not None:
                    if mask_sensitive and any(sensitive in key.lower() for sensitive in ['key', 'secret', 'password', 'token']):
                        # Mask sensitive values
                        if len(value) > 8:
                            masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:]
                        else:
                            masked_value = '*' * len(value)
                        category_credentials[key] = masked_value
                    else:
                        category_credentials[key] = value
            
            if category_credentials:
                all_credentials[category] = category_credentials
        
        return all_credentials
    
    def _generate_key(self, password, salt=None):
        """
        Generate an encryption key from a password
        
        Args:
            password (str): Password to derive key from
            salt (bytes, optional): Salt for key derivation
            
        Returns:
            tuple: (key, salt)
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def export_credentials(self, categories=None, output_file=None, password=None):
        """
        Export credentials to a file
        
        Args:
            categories (list, optional): List of categories to export
            output_file (str, optional): Path to output file
            password (str, optional): Password to encrypt the export
            
        Returns:
            str: Path to the exported file
        """
        if categories is None:
            categories = self.list_categories()
        
        # Get credentials for specified categories
        export_data = {}
        for category in categories:
            if category in self.CATEGORIES:
                export_data[category] = self.get_credentials_by_category(category)
        
        # Generate output filename if not provided
        if output_file is None:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"soulcorehub_credentials_{timestamp}.json"
        
        # Encrypt if password is provided
        if password:
            try:
                # Generate encryption key
                key, salt = self._generate_key(password)
                fernet = Fernet(key)
                
                # Encrypt data
                encrypted_data = fernet.encrypt(json.dumps(export_data).encode())
                
                # Write encrypted data with salt
                with open(output_file, 'wb') as f:
                    f.write(salt)
                    f.write(encrypted_data)
                
                logger.info(f"Encrypted credentials exported to {output_file}")
            except Exception as e:
                logger.error(f"Failed to encrypt and export credentials: {str(e)}")
                return None
        else:
            # Write unencrypted data
            try:
                with open(output_file, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                logger.info(f"Credentials exported to {output_file}")
            except Exception as e:
                logger.error(f"Failed to export credentials: {str(e)}")
                return None
        
        return output_file
    
    def import_credentials(self, input_file, password=None, overwrite=False):
        """
        Import credentials from a file
        
        Args:
            input_file (str): Path to input file
            password (str, optional): Password to decrypt the import
            overwrite (bool): Whether to overwrite existing credentials
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if file is encrypted (has salt at beginning)
            with open(input_file, 'rb') as f:
                file_data = f.read()
            
            # Try to parse as JSON first (unencrypted)
            try:
                import_data = json.loads(file_data)
                encrypted = False
            except json.JSONDecodeError:
                # File might be encrypted
                if password is None:
                    logger.error("Password required to decrypt the import file")
                    return False
                
                encrypted = True
            
            # Decrypt if encrypted
            if encrypted:
                try:
                    # Extract salt and encrypted data
                    salt = file_data[:16]
                    encrypted_data = file_data[16:]
                    
                    # Generate key from password and salt
                    key, _ = self._generate_key(password, salt)
                    fernet = Fernet(key)
                    
                    # Decrypt data
                    decrypted_data = fernet.decrypt(encrypted_data).decode()
                    import_data = json.loads(decrypted_data)
                except Exception as e:
                    logger.error(f"Failed to decrypt import file: {str(e)}")
                    return False
            
            # Import credentials
            for category, credentials in import_data.items():
                for key, value in credentials.items():
                    if overwrite or self.get_credential(key) is None:
                        self.set_credential(key, value)
            
            logger.info(f"Credentials imported from {input_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to import credentials: {str(e)}")
            return False
    
    def generate_credentials_markdown(self, output_file=None):
        """
        Generate a markdown file with all credentials (masked)
        
        Args:
            output_file (str, optional): Path to output file
            
        Returns:
            str: Path to the generated file
        """
        if output_file is None:
            output_file = "master_credentials.md"
        
        try:
            all_credentials = self.get_all_credentials(mask_sensitive=True)
            
            with open(output_file, 'w') as f:
                f.write("# SoulCoreHub Master Credentials\n\n")
                f.write("This document contains a comprehensive list of all credentials used by SoulCoreHub.\n")
                f.write("Sensitive values are masked for security.\n\n")
                
                for category, credentials in all_credentials.items():
                    f.write(f"## {category.upper()}\n\n")
                    
                    if not credentials:
                        f.write("*No credentials configured for this category*\n\n")
                        continue
                    
                    f.write("| Key | Value | Description |\n")
                    f.write("|-----|-------|-------------|\n")
                    
                    for key, value in credentials.items():
                        # Add a generic description based on the key name
                        description = key.replace('_', ' ').title()
                        f.write(f"| `{key}` | `{value}` | {description} |\n")
                    
                    f.write("\n")
                
                f.write("\n## Security Best Practices\n\n")
                f.write("1. Never commit the `.env` file to version control\n")
                f.write("2. Rotate credentials regularly\n")
                f.write("3. Use the CredentialsManager to access credentials securely\n")
                f.write("4. Export encrypted backups of credentials\n")
                f.write("5. Use least privilege for all credentials\n")
            
            logger.info(f"Credentials markdown generated at {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Failed to generate credentials markdown: {str(e)}")
            return None

if __name__ == "__main__":
    # Example usage
    creds = CredentialsManager()
    categories = creds.list_categories()
    print(f"Available credential categories: {categories}")
    
    # Generate markdown documentation
    creds.generate_credentials_markdown()
