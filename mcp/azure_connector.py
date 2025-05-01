#!/usr/bin/env python3
"""
Azür - Azure Cloud Connector for SoulCore MCP
Translates MCP tool calls into Azure service operations
"""

import os
import json
import logging
import uuid
from datetime import datetime
import requests
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("azure_connector.log"),
        logging.StreamHandler()
    ]
)

class AzureConnector:
    """Azure Cloud Connector for SoulCore MCP"""
    
    def __init__(self, config_path=None):
        """
        Initialize the Azure Connector
        
        Args:
            config_path (str): Path to the Azure configuration file
        """
        self.config = {}
        self.config_path = config_path or str(Path(__file__).parent / "azure_config.json")
        self.load_config()
        
    def load_config(self):
        """Load Azure configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    self.config = json.load(f)
                logging.info(f"Loaded Azure configuration from {self.config_path}")
            else:
                # Create default configuration
                self.config = {
                    "tenant_id": "",
                    "client_id": "",
                    "client_secret": "",
                    "subscription_id": "",
                    "resource_group": "soulcore-resources",
                    "endpoints": {
                        "planner": "https://graph.microsoft.com/v1.0/planner/tasks",
                        "storage": "https://soulcorestorage.blob.core.windows.net",
                        "cognitive": "https://soulcore-cognitive.cognitiveservices.azure.com"
                    }
                }
                self.save_config()
                logging.info(f"Created default Azure configuration at {self.config_path}")
        except Exception as e:
            logging.error(f"Error loading Azure configuration: {str(e)}")
            self.config = {}
    
    def save_config(self):
        """Save Azure configuration"""
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
            logging.info(f"Saved Azure configuration to {self.config_path}")
        except Exception as e:
            logging.error(f"Error saving Azure configuration: {str(e)}")
    
    def get_auth_token(self):
        """
        Get an authentication token for Azure services
        
        Returns:
            str: Authentication token or None if failed
        """
        if not self.config.get("tenant_id") or not self.config.get("client_id") or not self.config.get("client_secret"):
            logging.error("Azure credentials not configured")
            return None
            
        try:
            # In a real implementation, this would use MSAL or similar library
            # For now, we'll just simulate it
            token = f"simulated_token_{uuid.uuid4()}"
            logging.info("Obtained Azure authentication token")
            return token
        except Exception as e:
            logging.error(f"Error getting Azure authentication token: {str(e)}")
            return None
    
    def create_task(self, title, description="", priority="normal", due_date=None):
        """
        Create a task in Microsoft Planner
        
        Args:
            title (str): Task title
            description (str): Task description
            priority (str): Task priority (low, normal, high)
            due_date (str): Due date in ISO format
            
        Returns:
            dict: Task information or error
        """
        token = self.get_auth_token()
        if not token:
            return {"error": "Authentication failed"}
            
        try:
            # In a real implementation, this would make an actual API call
            # For now, we'll just simulate it
            task_id = str(uuid.uuid4())
            logging.info(f"Created Azure Planner task: {title} (ID: {task_id})")
            
            return {
                "id": task_id,
                "title": title,
                "description": description,
                "priority": priority,
                "due_date": due_date,
                "created_at": datetime.now().isoformat(),
                "status": "not_started"
            }
        except Exception as e:
            logging.error(f"Error creating Azure Planner task: {str(e)}")
            return {"error": str(e)}
    
    def upload_blob(self, file_path, container="default", blob_name=None):
        """
        Upload a file to Azure Blob Storage
        
        Args:
            file_path (str): Path to the file to upload
            container (str): Blob container name
            blob_name (str): Name for the blob (defaults to filename)
            
        Returns:
            dict: Blob information or error
        """
        token = self.get_auth_token()
        if not token:
            return {"error": "Authentication failed"}
            
        try:
            # In a real implementation, this would use Azure SDK
            # For now, we'll just simulate it
            if not os.path.exists(file_path):
                return {"error": f"File not found: {file_path}"}
                
            blob_name = blob_name or os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            logging.info(f"Uploaded file to Azure Blob Storage: {blob_name} ({file_size} bytes)")
            
            return {
                "container": container,
                "blob_name": blob_name,
                "size": file_size,
                "url": f"{self.config['endpoints']['storage']}/{container}/{blob_name}",
                "uploaded_at": datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Error uploading to Azure Blob Storage: {str(e)}")
            return {"error": str(e)}
    
    def analyze_text(self, text, analysis_type="sentiment"):
        """
        Analyze text using Azure Cognitive Services
        
        Args:
            text (str): Text to analyze
            analysis_type (str): Type of analysis (sentiment, language, key_phrases)
            
        Returns:
            dict: Analysis results or error
        """
        token = self.get_auth_token()
        if not token:
            return {"error": "Authentication failed"}
            
        try:
            # In a real implementation, this would use Azure SDK
            # For now, we'll just simulate it
            
            if analysis_type == "sentiment":
                # Simulate sentiment analysis
                import random
                sentiment_score = random.uniform(0, 1)
                sentiment = "positive" if sentiment_score > 0.6 else "neutral" if sentiment_score > 0.4 else "negative"
                
                logging.info(f"Analyzed text sentiment: {sentiment} ({sentiment_score:.2f})")
                
                return {
                    "sentiment": sentiment,
                    "score": sentiment_score,
                    "text_length": len(text),
                    "analyzed_at": datetime.now().isoformat()
                }
            elif analysis_type == "language":
                # Simulate language detection
                languages = ["en", "es", "fr", "de", "ja"]
                detected = random.choice(languages)
                confidence = random.uniform(0.7, 0.99)
                
                logging.info(f"Detected language: {detected} ({confidence:.2f})")
                
                return {
                    "language": detected,
                    "confidence": confidence,
                    "analyzed_at": datetime.now().isoformat()
                }
            elif analysis_type == "key_phrases":
                # Simulate key phrase extraction
                words = text.split()
                phrase_count = min(5, max(1, len(words) // 10))
                phrases = []
                
                for _ in range(phrase_count):
                    start = random.randint(0, max(0, len(words) - 3))
                    length = random.randint(1, min(3, len(words) - start))
                    phrase = " ".join(words[start:start+length])
                    phrases.append(phrase)
                
                logging.info(f"Extracted {len(phrases)} key phrases")
                
                return {
                    "phrases": phrases,
                    "count": len(phrases),
                    "analyzed_at": datetime.now().isoformat()
                }
            else:
                return {"error": f"Unsupported analysis type: {analysis_type}"}
        except Exception as e:
            logging.error(f"Error analyzing text with Azure Cognitive Services: {str(e)}")
            return {"error": str(e)}

# Register Azure tools with MCP server
def register_azure_tools(mcp_server):
    """
    Register Azure tools with the MCP server
    
    Args:
        mcp_server: MCP server instance
    """
    azure = AzureConnector()
    
    # Create task tool
    async def azure_create_task(params, metadata=None):
        title = params.get("title", "Untitled Task")
        description = params.get("description", "")
        priority = params.get("priority", "normal")
        due_date = params.get("due_date")
        return azure.create_task(title, description, priority, due_date)
    
    # Upload blob tool
    async def azure_upload_blob(params, metadata=None):
        file_path = params.get("file_path")
        container = params.get("container", "default")
        blob_name = params.get("blob_name")
        if not file_path:
            return {"error": "file_path parameter is required"}
        return azure.upload_blob(file_path, container, blob_name)
    
    # Analyze text tool
    async def azure_analyze_text(params, metadata=None):
        text = params.get("text")
        analysis_type = params.get("type", "sentiment")
        if not text:
            return {"error": "text parameter is required"}
        return azure.analyze_text(text, analysis_type)
    
    # Register the tools
    mcp_server.register_tool(
        "azure_create_task",
        azure_create_task,
        "Create a task in Microsoft Planner",
        "organized"
    )
    
    mcp_server.register_tool(
        "azure_upload_blob",
        azure_upload_blob,
        "Upload a file to Azure Blob Storage",
        "diligent"
    )
    
    mcp_server.register_tool(
        "azure_analyze_text",
        azure_analyze_text,
        "Analyze text using Azure Cognitive Services",
        "analytical"
    )
    
    logging.info("Registered Azure tools with MCP server")

if __name__ == "__main__":
    # Test the Azure connector
    azure = AzureConnector()
    
    # Test creating a task
    task = azure.create_task("Test task", "This is a test task", "high")
    print(f"Created task: {json.dumps(task, indent=2)}")
    
    # Test uploading a blob
    if os.path.exists("test.txt"):
        blob = azure.upload_blob("test.txt")
        print(f"Uploaded blob: {json.dumps(blob, indent=2)}")
    else:
        print("Create a test.txt file to test blob upload")
    
    # Test analyzing text
    analysis = azure.analyze_text("This is a test of the Azure Cognitive Services integration")
    print(f"Text analysis: {json.dumps(analysis, indent=2)}")
