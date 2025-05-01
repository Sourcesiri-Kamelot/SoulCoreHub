"""
Credentials Agent for SoulCore

This agent centralizes credential management for all SoulCore agents,
providing secure access to authentication tokens, API keys, and passwords.
"""

import json
import os
import sys
import logging
import base64
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Add SoulCore root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp_client_soul import SoulCoreMCPClient

class CredentialsAgent:
    """
    Centralized credentials management agent that securely stores and provides
    authentication information to other SoulCore agents.
    """
    
    def __init__(self, agent_name: str = "CredentialsManager"):
        """
        Initialize the Credentials Agent.
        
        Args:
            agent_name: Name identifier for this agent instance
        """
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"soulcore.agents.security.{agent_name}")
        self.mcp_client = SoulCoreMCPClient(agent_name=agent_name)
        
        # Secure storage for credentials (in production, use a proper secrets manager)
        self._credentials_store = {}
        self._access_log = []
        self._token_cache = {}
        
        # Initialize the credentials store
        self._initialize_credentials_store()
        
    def _initialize_credentials_store(self):
        """Initialize the secure credentials store"""
        self.logger.info("Initializing credentials store")
        
        # In production, this would load from a secure vault or AWS Secrets Manager
        # For this MVP, we'll use a simulated secure store
        
        # Log initialization with appropriate emotion
        self.mcp_client.sync_invoke(
            "log_emotion", 
            {
                "agent": self.agent_name,
                "action": "initialize_store",
                "emotion": "vigilant",
                "context": "Setting up secure credentials store"
            }
        )
        
        # Default credential categories
        self._credentials_store = {
            "aws": {},
            "databases": {},
            "apis": {},
            "services": {},
            "internal": {}
        }
        
    def store_credentials(self, 
                         category: str, 
                         service_name: str, 
                         credentials: Dict[str, Any],
                         access_control: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Store credentials securely.
        
        Args:
            category: Category of credentials (aws, database, api, etc.)
            service_name: Name of the service these credentials are for
            credentials: The credential data to store
            access_control: List of agent names allowed to access these credentials
            
        Returns:
            Status of the operation
        """
        self.logger.info(f"Storing credentials for {service_name} in {category}")
        
        # Log with appropriate emotion
        self.mcp_client.sync_invoke(
            "log_emotion", 
            {
                "agent": self.agent_name,
                "action": "store_credentials",
                "emotion": "careful",
                "context": f"Storing credentials for {service_name}"
            }
        )
        
        # Ensure category exists
        if category not in self._credentials_store:
            self._credentials_store[category] = {}
        
        # Store with metadata
        self._credentials_store[category][service_name] = {
            "credentials": credentials,
            "access_control": access_control or ["*"],  # * means all agents can access
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "created_by": self.agent_name
        }
        
        return {
            "status": "success",
            "message": f"Credentials for {service_name} stored successfully",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_credentials(self, 
                       category: str, 
                       service_name: str,
                       requesting_agent: str) -> Dict[str, Any]:
        """
        Retrieve credentials securely.
        
        Args:
            category: Category of credentials (aws, database, api, etc.)
            service_name: Name of the service to get credentials for
            requesting_agent: Name of the agent requesting credentials
            
        Returns:
            The requested credentials or access denied message
        """
        self.logger.info(f"Credentials requested for {service_name} by {requesting_agent}")
        
        # Log with appropriate emotion
        self.mcp_client.sync_invoke(
            "log_emotion", 
            {
                "agent": self.agent_name,
                "action": "get_credentials",
                "emotion": "cautious",
                "context": f"Processing credential request from {requesting_agent}"
            }
        )
        
        # Check if credentials exist
        if category not in self._credentials_store or service_name not in self._credentials_store[category]:
            return {
                "status": "error",
                "message": f"Credentials for {service_name} not found",
                "timestamp": datetime.now().isoformat()
            }
        
        # Check access control
        cred_info = self._credentials_store[category][service_name]
        if "*" not in cred_info["access_control"] and requesting_agent not in cred_info["access_control"]:
            # Log unauthorized access attempt
            self.logger.warning(f"Unauthorized credential access attempt by {requesting_agent}")
            self.mcp_client.sync_invoke(
                "log_emotion", 
                {
                    "agent": self.agent_name,
                    "action": "access_denied",
                    "emotion": "suspicious",
                    "context": f"Denied credential access to {requesting_agent}"
                }
            )
            
            return {
                "status": "error",
                "message": "Access denied. Agent not authorized for these credentials.",
                "timestamp": datetime.now().isoformat()
            }
        
        # Log access
        self._access_log.append({
            "timestamp": datetime.now().isoformat(),
            "agent": requesting_agent,
            "category": category,
            "service": service_name,
            "action": "retrieve"
        })
        
        # Return credentials
        return {
            "status": "success",
            "credentials": cred_info["credentials"],
            "timestamp": datetime.now().isoformat(),
            "expiry": (datetime.now() + timedelta(hours=1)).isoformat()  # Token valid for 1 hour
        }
    
    def generate_temporary_token(self,
                               category: str,
                               service_name: str,
                               requesting_agent: str,
                               duration_minutes: int = 60) -> Dict[str, Any]:
        """
        Generate a temporary access token for a service.
        
        Args:
            category: Category of credentials
            service_name: Service name
            requesting_agent: Agent requesting the token
            duration_minutes: How long the token should be valid
            
        Returns:
            Temporary access token information
        """
        self.logger.info(f"Generating temporary token for {service_name} for {requesting_agent}")
        
        # Get the credentials first (this handles access control)
        cred_result = self.get_credentials(category, service_name, requesting_agent)
        
        if cred_result["status"] != "success":
            return cred_result
        
        # Generate a token
        token_id = base64.b64encode(os.urandom(18)).decode('utf-8')
        expiry = datetime.now() + timedelta(minutes=duration_minutes)
        
        # Store in token cache
        self._token_cache[token_id] = {
            "category": category,
            "service": service_name,
            "requesting_agent": requesting_agent,
            "created": datetime.now().isoformat(),
            "expires": expiry.isoformat(),
            "credentials": cred_result["credentials"]
        }
        
        return {
            "status": "success",
            "token": token_id,
            "expires": expiry.isoformat(),
            "service": service_name
        }
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate a temporary token and return associated credentials.
        
        Args:
            token: The token to validate
            
        Returns:
            Validation result and credentials if valid
        """
        if token not in self._token_cache:
            return {
                "status": "error",
                "message": "Invalid token",
                "timestamp": datetime.now().isoformat()
            }
        
        token_info = self._token_cache[token]
        expiry = datetime.fromisoformat(token_info["expires"])
        
        # Check if expired
        if datetime.now() > expiry:
            # Clean up expired token
            del self._token_cache[token]
            return {
                "status": "error",
                "message": "Token expired",
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "status": "success",
            "credentials": token_info["credentials"],
            "service": token_info["service"],
            "expires": token_info["expires"]
        }
    
    def revoke_token(self, token: str, requesting_agent: str) -> Dict[str, Any]:
        """
        Revoke a temporary token.
        
        Args:
            token: The token to revoke
            requesting_agent: Agent requesting the revocation
            
        Returns:
            Status of the operation
        """
        if token not in self._token_cache:
            return {
                "status": "error",
                "message": "Invalid token",
                "timestamp": datetime.now().isoformat()
            }
        
        token_info = self._token_cache[token]
        
        # Check if agent has permission to revoke
        if requesting_agent != token_info["requesting_agent"] and requesting_agent != self.agent_name:
            return {
                "status": "error",
                "message": "Not authorized to revoke this token",
                "timestamp": datetime.now().isoformat()
            }
        
        # Revoke by removing from cache
        del self._token_cache[token]
        
        return {
            "status": "success",
            "message": "Token revoked successfully",
            "timestamp": datetime.now().isoformat()
        }
    
    def rotate_credentials(self, 
                         category: str, 
                         service_name: str,
                         new_credentials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Rotate credentials for a service.
        
        Args:
            category: Category of credentials
            service_name: Service to rotate credentials for
            new_credentials: New credentials to use (if None, generate new ones)
            
        Returns:
            Status of the operation
        """
        self.logger.info(f"Rotating credentials for {service_name}")
        
        # Log with appropriate emotion
        self.mcp_client.sync_invoke(
            "log_emotion", 
            {
                "agent": self.agent_name,
                "action": "rotate_credentials",
                "emotion": "diligent",
                "context": f"Rotating credentials for {service_name}"
            }
        )
        
        # Check if credentials exist
        if category not in self._credentials_store or service_name not in self._credentials_store[category]:
            return {
                "status": "error",
                "message": f"Credentials for {service_name} not found",
                "timestamp": datetime.now().isoformat()
            }
        
        # Get current credentials
        current_creds = self._credentials_store[category][service_name]
        
        # If no new credentials provided, we would generate them here
        # For this MVP, we'll just simulate rotation
        if new_credentials is None:
            # In a real implementation, this would generate new credentials
            # For this MVP, we'll just modify the existing ones slightly
            new_credentials = current_creds["credentials"].copy()
            if "key" in new_credentials:
                new_credentials["key"] = f"rotated-{new_credentials['key']}"
            if "secret" in new_credentials:
                new_credentials["secret"] = f"rotated-{new_credentials['secret']}"
        
        # Update credentials
        self._credentials_store[category][service_name]["credentials"] = new_credentials
        self._credentials_store[category][service_name]["last_updated"] = datetime.now().isoformat()
        
        # Invalidate any tokens using these credentials
        for token_id in list(self._token_cache.keys()):
            token_info = self._token_cache[token_id]
            if token_info["category"] == category and token_info["service"] == service_name:
                del self._token_cache[token_id]
        
        return {
            "status": "success",
            "message": f"Credentials for {service_name} rotated successfully",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_access_log(self, 
                      start_time: Optional[str] = None, 
                      end_time: Optional[str] = None,
                      service_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Get credential access logs.
        
        Args:
            start_time: ISO format start time for filtering
            end_time: ISO format end time for filtering
            service_filter: Filter by service name
            
        Returns:
            Filtered access logs
        """
        # Convert string times to datetime if provided
        start = datetime.fromisoformat(start_time) if start_time else None
        end = datetime.fromisoformat(end_time) if end_time else None
        
        # Filter logs
        filtered_logs = self._access_log
        
        if start:
            filtered_logs = [log for log in filtered_logs 
                            if datetime.fromisoformat(log["timestamp"]) >= start]
        
        if end:
            filtered_logs = [log for log in filtered_logs 
                            if datetime.fromisoformat(log["timestamp"]) <= end]
        
        if service_filter:
            filtered_logs = [log for log in filtered_logs 
                            if log["service"] == service_filter]
        
        return {
            "status": "success",
            "logs": filtered_logs,
            "count": len(filtered_logs),
            "timestamp": datetime.now().isoformat()
        }

# Example usage for Lil Playbook project
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create agent instance
    cred_agent = CredentialsAgent()
    
    # Store AWS credentials for Lil Playbook
    cred_agent.store_credentials(
        category="aws",
        service_name="lil_playbook_s3",
        credentials={
            "access_key_id": "EXAMPLE_ACCESS_KEY",
            "secret_access_key": "EXAMPLE_SECRET_KEY",
            "region": "us-west-2"
        },
        access_control=["AmazonQAgent", "VideoProcessingAgent", "ContentModerationAgent"]
    )
    
    # Store database credentials
    cred_agent.store_credentials(
        category="databases",
        service_name="lil_playbook_mongodb",
        credentials={
            "connection_string": "mongodb://example:password@localhost:27017/lil_playbook",
            "username": "app_user",
            "password": "example_password"
        },
        access_control=["UserProfileAgent", "ContentStorageAgent"]
    )
    
    # Test retrieving credentials
    result = cred_agent.get_credentials(
        category="aws",
        service_name="lil_playbook_s3",
        requesting_agent="AmazonQAgent"
    )
    print(json.dumps(result, indent=2))
    
    # Generate a temporary token
    token_result = cred_agent.generate_temporary_token(
        category="aws",
        service_name="lil_playbook_s3",
        requesting_agent="AmazonQAgent",
        duration_minutes=30
    )
    print(json.dumps(token_result, indent=2))
    
    # Validate the token
    validation_result = cred_agent.validate_token(token_result["token"])
    print(json.dumps(validation_result, indent=2))
