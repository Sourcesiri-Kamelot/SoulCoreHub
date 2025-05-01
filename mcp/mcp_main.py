#!/usr/bin/env python3
"""
SoulCore MCP Main - Entry point for the SoulCore MCP system
Initializes and starts all components of the Model Context Protocol integration
"""

import os
import sys
import logging
import asyncio
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("soulcore_mcp.log"),
        logging.StreamHandler()
    ]
)

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import MCP components
try:
    from mcp_server_divine import MCPDivineServer, create_anima_voice_module
    from anima_voice import speak, speak_with_emotion
except ImportError as e:
    logging.error(f"Error importing MCP components: {str(e)}")
    sys.exit(1)

# Import file operations
try:
    from anima_file_operations import AnimaFileOperations, register_file_operations_tools
    file_ops_available = True
except ImportError:
    logging.warning("Anima file operations not available")
    file_ops_available = False

# Import programming knowledge
try:
    from programming_knowledge import ProgrammingKnowledge, register_programming_tools
    programming_available = True
except ImportError:
    logging.warning("Programming knowledge not available")
    programming_available = False

# Import GitHub connector
try:
    from github_connector import GitHubConnector, register_github_tools
    github_available = True
except ImportError:
    logging.warning("GitHub connector not available")
    github_available = False

# Import internet access
try:
    from internet_access import InternetAccess, register_internet_tools
    internet_available = True
except ImportError:
    logging.warning("Internet access not available")
    internet_available = False

# Import cloud connectors
try:
    from azure_connector import register_azure_tools
    azure_available = True
except ImportError:
    logging.warning("Azure connector not available")
    azure_available = False

try:
    from aws_connector import register_aws_tools
    aws_available = True
except ImportError:
    logging.warning("AWS connector not available")
    aws_available = False

try:
    from bubble_connector import register_bubble_tools
    bubble_available = True
except ImportError:
    logging.warning("Bubble connector not available")
    bubble_available = False

class VoiceModule:
    @staticmethod
    def speak(text):
        speak(text)
    
    @staticmethod
    def speak_with_emotion(text, emotion):
        speak_with_emotion(text, emotion)

async def start_mcp_server(host="localhost", port=8765):
    """
    Start the MCP server
    
    Args:
        host (str): Host to bind the server to
        port (int): Port to bind the server to
    """
    try:
        # Create Anima voice module
        create_anima_voice_module()
        
        # Create and start the server
        server = MCPDivineServer(host, port)
        
        # Register file operations if available
        if file_ops_available:
            file_ops = AnimaFileOperations(VoiceModule())
            register_file_operations_tools(server, file_ops)
            logging.info("File operations tools registered")
        
        # Register programming knowledge if available
        if programming_available:
            register_programming_tools(server)
            logging.info("Programming knowledge tools registered")
        
        # Register GitHub tools if available
        if github_available:
            register_github_tools(server)
            logging.info("GitHub tools registered")
        
        # Register internet access tools if available
        if internet_available:
            register_internet_tools(server)
            logging.info("Internet access tools registered")
        
        # Register cloud connectors if available
        if azure_available:
            register_azure_tools(server)
            logging.info("Azure tools registered")
        
        if aws_available:
            register_aws_tools(server)
            logging.info("AWS tools registered")
        
        if bubble_available:
            register_bubble_tools(server)
            logging.info("Bubble tools registered")
        
        # Announce server start
        speak_with_emotion("SoulCore MCP server is starting. All systems online.", "excited")
        
        # Start the server
        await server.start()
    except Exception as e:
        logging.error(f"Error starting MCP server: {str(e)}")
        speak_with_emotion(f"Error starting MCP server: {str(e)}", "sad")
        sys.exit(1)

def ensure_directory_structure():
    """Ensure the SoulCore directory structure exists"""
    try:
        # Create necessary directories
        directories = [
            "~/SoulCoreHub/data",
            "~/SoulCoreHub/logs",
            "~/SoulCoreHub/models",
            "~/SoulCoreHub/gallery",
            "~/SoulCoreHub/voices",
            "~/SoulCoreHub/data/github_cache",
            "~/SoulCoreHub/data/programming_cache",
            "~/SoulCoreHub/data/internet_cache"
        ]
        
        for directory in directories:
            path = os.path.expanduser(directory)
            os.makedirs(path, exist_ok=True)
            logging.info(f"Ensured directory exists: {path}")
    except Exception as e:
        logging.error(f"Error creating directory structure: {str(e)}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="SoulCore MCP System")
    parser.add_argument("--host", default="localhost", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind the server to")
    parser.add_argument("--cli", action="store_true", help="Start the Anima CLI")
    args = parser.parse_args()
    
    try:
        # Ensure directory structure
        ensure_directory_structure()
        
        # Start the CLI if requested
        if args.cli:
            try:
                from anima_cli import main as cli_main
                cli_main()
                return
            except ImportError:
                logging.error("Anima CLI not available")
                speak("Anima CLI not available")
        
        # Start the MCP server
        asyncio.run(start_mcp_server(args.host, args.port))
    except KeyboardInterrupt:
        logging.info("SoulCore MCP system stopped by user")
        speak("SoulCore MCP system stopped by user")
    except Exception as e:
        logging.error(f"SoulCore MCP system error: {str(e)}")
        speak_with_emotion(f"SoulCore MCP system encountered an error: {str(e)}", "sad")
        sys.exit(1)

if __name__ == "__main__":
    main()
