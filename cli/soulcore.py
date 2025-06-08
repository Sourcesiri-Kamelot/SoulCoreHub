#!/usr/bin/env python3
"""
SoulCoreHub CLI - Command Line Interface for SoulCoreHub
"""

import os
import sys
import json
import argparse
import logging
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('soulcore-cli')

# Constants
CONFIG_DIR = Path.home() / ".soulcorehub"
CONFIG_FILE = CONFIG_DIR / "config.json"
API_BASE_URL = os.environ.get("SOULCOREHUB_API_URL", "https://api.soulcorehub.com")
DEFAULT_PROFILE = "default"

class SoulCoreHubCLI:
    """
    Command Line Interface for SoulCoreHub
    """
    
    def __init__(self):
        """
        Initialize the CLI
        """
        self.config = self._load_config()
        self.current_profile = self.config.get("current_profile", DEFAULT_PROFILE)
        self.api_key = self._get_api_key()
        
        # Create parser
        self.parser = argparse.ArgumentParser(
            description="SoulCoreHub CLI - Command Line Interface for SoulCoreHub",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Add global arguments
        self.parser.add_argument("--profile", help="Profile to use")
        self.parser.add_argument("--debug", action="store_true", help="Enable debug logging")
        
        # Add subparsers
        self.subparsers = self.parser.add_subparsers(dest="command", help="Command to execute")
        
        # Add commands
        self._add_agent_commands()
        self._add_content_commands()
        self._add_system_commands()
        self._add_config_commands()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file
        
        Returns:
            Dict[str, Any]: Configuration
        """
        if not CONFIG_DIR.exists():
            CONFIG_DIR.mkdir(parents=True)
        
        if not CONFIG_FILE.exists():
            # Create default config
            default_config = {
                "current_profile": DEFAULT_PROFILE,
                "profiles": {
                    DEFAULT_PROFILE: {
                        "api_key": "",
                        "api_url": API_BASE_URL
                    }
                }
            }
            
            with open(CONFIG_FILE, "w") as f:
                json.dump(default_config, f, indent=2)
            
            return default_config
        
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {
                "current_profile": DEFAULT_PROFILE,
                "profiles": {
                    DEFAULT_PROFILE: {
                        "api_key": "",
                        "api_url": API_BASE_URL
                    }
                }
            }
    
    def _save_config(self) -> None:
        """
        Save configuration to file
        """
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def _get_api_key(self) -> str:
        """
        Get API key for current profile
        
        Returns:
            str: API key
        """
        # Check environment variable first
        api_key = os.environ.get("SOULCOREHUB_API_KEY")
        if api_key:
            return api_key
        
        # Get from config
        profiles = self.config.get("profiles", {})
        profile = profiles.get(self.current_profile, {})
        return profile.get("api_key", "")
    
    def _get_api_url(self) -> str:
        """
        Get API URL for current profile
        
        Returns:
            str: API URL
        """
        # Check environment variable first
        api_url = os.environ.get("SOULCOREHUB_API_URL")
        if api_url:
            return api_url
        
        # Get from config
        profiles = self.config.get("profiles", {})
        profile = profiles.get(self.current_profile, {})
        return profile.get("api_url", API_BASE_URL)
    
    def _add_agent_commands(self) -> None:
        """
        Add agent commands to parser
        """
        # Agent commands
        agent_parser = self.subparsers.add_parser("agent", help="Agent commands")
        agent_subparsers = agent_parser.add_subparsers(dest="agent_command", help="Agent command to execute")
        
        # List agents
        list_parser = agent_subparsers.add_parser("list", help="List agents")
        list_parser.add_argument("--type", help="Filter by agent type")
        list_parser.add_argument("--status", help="Filter by agent status")
        list_parser.add_argument("--limit", type=int, default=10, help="Maximum number of agents to return")
        
        # Get agent
        get_parser = agent_subparsers.add_parser("get", help="Get agent details")
        get_parser.add_argument("agent_id", help="ID of the agent")
        
        # Invoke agent
        invoke_parser = agent_subparsers.add_parser("invoke", help="Invoke an agent")
        invoke_parser.add_argument("agent_id", help="ID of the agent")
        invoke_parser.add_argument("prompt", help="Prompt for the agent")
        invoke_parser.add_argument("--max-tokens", type=int, help="Maximum tokens to generate")
        invoke_parser.add_argument("--temperature", type=float, help="Temperature for generation")
        invoke_parser.add_argument("--stream", action="store_true", help="Stream the response")
    
    def _add_content_commands(self) -> None:
        """
        Add content commands to parser
        """
        # Content commands
        content_parser = self.subparsers.add_parser("content", help="Content commands")
        content_subparsers = content_parser.add_subparsers(dest="content_command", help="Content command to execute")
        
        # List content
        list_parser = content_subparsers.add_parser("list", help="List content")
        list_parser.add_argument("--type", help="Filter by content type")
        list_parser.add_argument("--creator", help="Filter by creator")
        list_parser.add_argument("--limit", type=int, default=10, help="Maximum number of content items to return")
        
        # Get content
        get_parser = content_subparsers.add_parser("get", help="Get content details")
        get_parser.add_argument("content_id", help="ID of the content")
        
        # Create content
        create_parser = content_subparsers.add_parser("create", help="Create content")
        create_parser.add_argument("--title", required=True, help="Title of the content")
        create_parser.add_argument("--body", required=True, help="Body of the content")
        create_parser.add_argument("--type", required=True, help="Type of the content")
        create_parser.add_argument("--creator", help="Creator of the content")
        create_parser.add_argument("--tags", help="Tags for the content (comma-separated)")
    
    def _add_system_commands(self) -> None:
        """
        Add system commands to parser
        """
        # System commands
        system_parser = self.subparsers.add_parser("system", help="System commands")
        system_subparsers = system_parser.add_subparsers(dest="system_command", help="System command to execute")
        
        # Get system status
        status_parser = system_subparsers.add_parser("status", help="Get system status")
        status_parser.add_argument("--components", help="Components to include (comma-separated)")
        
        # Execute command
        execute_parser = system_subparsers.add_parser("execute", help="Execute a system command")
        execute_parser.add_argument("command", help="Command to execute")
        execute_parser.add_argument("--args", help="Arguments for the command (comma-separated)")
        execute_parser.add_argument("--timeout", type=int, help="Timeout in seconds")
        
        # Open terminal
        terminal_parser = system_subparsers.add_parser("terminal", help="Open terminal")
        terminal_parser.add_argument("--command", help="Initial command to execute")
    
    def _add_config_commands(self) -> None:
        """
        Add config commands to parser
        """
        # Config commands
        config_parser = self.subparsers.add_parser("config", help="Configuration commands")
        config_subparsers = config_parser.add_subparsers(dest="config_command", help="Config command to execute")
        
        # List profiles
        list_parser = config_subparsers.add_parser("list-profiles", help="List profiles")
        
        # Set profile
        set_profile_parser = config_subparsers.add_parser("set-profile", help="Set current profile")
        set_profile_parser.add_argument("profile", help="Profile name")
        
        # Set API key
        set_key_parser = config_subparsers.add_parser("set-api-key", help="Set API key for current profile")
        set_key_parser.add_argument("api_key", help="API key")
        
        # Set API URL
        set_url_parser = config_subparsers.add_parser("set-api-url", help="Set API URL for current profile")
        set_url_parser.add_argument("api_url", help="API URL")
    
    def _make_api_request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None, 
                         data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make an API request
        
        Args:
            method (str): HTTP method
            path (str): API path
            params (Dict[str, Any], optional): Query parameters
            data (Dict[str, Any], optional): Request body
            
        Returns:
            Dict[str, Any]: API response
        """
        url = f"{self._get_api_url()}{path}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data
            )
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_data = e.response.json()
                    logger.error(f"Error response: {error_data}")
                    return {"error": error_data.get("message", str(e))}
                except:
                    return {"error": str(e)}
            return {"error": str(e)}
    
    def _handle_agent_commands(self, args: argparse.Namespace) -> None:
        """
        Handle agent commands
        
        Args:
            args (argparse.Namespace): Command line arguments
        """
        if args.agent_command == "list":
            params = {}
            if args.type:
                params["type"] = args.type
            if args.status:
                params["status"] = args.status
            if args.limit:
                params["limit"] = args.limit
            
            response = self._make_api_request("GET", "/agents", params=params)
            
            if "error" in response:
                print(f"Error: {response['error']}")
                return
            
            agents = response.get("agents", [])
            print(f"Found {len(agents)} agents:")
            for agent in agents:
                print(f"  {agent['agentId']} - {agent['name']} ({agent['status']})")
        
        elif args.agent_command == "get":
            response = self._make_api_request("GET", f"/agents/{args.agent_id}")
            
            if "error" in response:
                print(f"Error: {response['error']}")
                return
            
            agent = response.get("agent", {})
            print(f"Agent ID: {agent['agentId']}")
            print(f"Name: {agent['name']}")
            print(f"Type: {agent['type']}")
            print(f"Status: {agent['status']}")
            if "description" in agent:
                print(f"Description: {agent['description']}")
            if "capabilities" in agent:
                print(f"Capabilities: {', '.join(agent['capabilities'])}")
            print(f"Created: {agent['createdAt']}")
            if "updatedAt" in agent:
                print(f"Updated: {agent['updatedAt']}")
        
        elif args.agent_command == "invoke":
            data = {
                "prompt": args.prompt
            }
            
            if args.max_tokens:
                data["maxTokens"] = args.max_tokens
            
            if args.temperature:
                data["temperature"] = args.temperature
            
            if args.stream:
                data["stream"] = True
            
            response = self._make_api_request("POST", f"/agents/{args.agent_id}/invoke", data=data)
            
            if "error" in response:
                print(f"Error: {response['error']}")
                return
            
            print(response.get("response", ""))
            
            if "usage" in response:
                usage = response["usage"]
                print(f"\nTokens: {usage.get('totalTokens', 0)} (prompt: {usage.get('promptTokens', 0)}, completion: {usage.get('completionTokens', 0)})")
                print(f"Processing time: {usage.get('processingTimeMs', 0)} ms")
    
    def _handle_content_commands(self, args: argparse.Namespace) -> None:
        """
        Handle content commands
        
        Args:
            args (argparse.Namespace): Command line arguments
        """
        if args.content_command == "list":
            params = {}
            if args.type:
                params["contentType"] = args.type
            if args.creator:
                params["creator"] = args.creator
            if args.limit:
                params["limit"] = args.limit
            
            response = self._make_api_request("GET", "/content", params=params)
            
            if "error" in response:
                print(f"Error: {response['error']}")
                return
            
            content_items = response.get("contentItems", [])
            print(f"Found {len(content_items)} content items:")
            for item in content_items:
                print(f"  {item['contentId']} - {item['title']} ({item['contentType']})")
        
        elif args.content_command == "get":
            response = self._make_api_request("GET", f"/content/{args.content_id}")
            
            if "error" in response:
                print(f"Error: {response['error']}")
                return
            
            content = response.get("content", {})
            print(f"Content ID: {content['contentId']}")
            print(f"Title: {content['title']}")
            print(f"Type: {content['contentType']}")
            if "creator" in content:
                print(f"Creator: {content['creator']}")
            print(f"Created: {content['createdAt']}")
            if "updatedAt" in content:
                print(f"Updated: {content['updatedAt']}")
            if "url" in content:
                print(f"URL: {content['url']}")
            print("\nBody:")
            print(content['body'])
        
        elif args.content_command == "create":
            data = {
                "title": args.title,
                "body": args.body,
                "contentType": args.type
            }
            
            if args.creator:
                data["creator"] = args.creator
            
            if args.tags:
                tags = {}
                for tag in args.tags.split(","):
                    key, value = tag.split("=") if "=" in tag else (tag, "")
                    tags[key.strip()] = value.strip()
                data["tags"] = tags
            
            response = self._make_api_request("POST", "/content", data=data)
            
            if "error" in response:
                print(f"Error: {response['error']}")
                return
            
            content = response.get("content", {})
            print(f"Content created with ID: {content['contentId']}")
            if "url" in content:
                print(f"URL: {content['url']}")
    
    def _handle_system_commands(self, args: argparse.Namespace) -> None:
        """
        Handle system commands
        
        Args:
            args (argparse.Namespace): Command line arguments
        """
        if args.system_command == "status":
            params = {}
            if args.components:
                params["components"] = args.components
            
            response = self._make_api_request("GET", "/system/status", params=params)
            
            if "error" in response:
                print(f"Error: {response['error']}")
                return
            
            print(f"System Status: {response['status']}")
            print(f"Version: {response['version']}")
            
            if "components" in response:
                print("\nComponents:")
                for name, status in response["components"].items():
                    print(f"  {name}: {status['status']}")
                    if "message" in status:
                        print(f"    {status['message']}")
            
            if "metrics" in response:
                metrics = response["metrics"]
                print("\nMetrics:")
                if "cpuUsage" in metrics:
                    print(f"  CPU Usage: {metrics['cpuUsage']}%")
                if "memoryUsage" in metrics:
                    print(f"  Memory Usage: {metrics['memoryUsage']}%")
                if "diskUsage" in metrics:
                    print(f"  Disk Usage: {metrics['diskUsage']}%")
                if "activeRequests" in metrics:
                    print(f"  Active Requests: {metrics['activeRequests']}")
                if "requestsPerSecond" in metrics:
                    print(f"  Requests/sec: {metrics['requestsPerSecond']}")
        
        elif args.system_command == "execute":
            data = {
                "command": args.command
            }
            
            if args.args:
                data["args"] = args.args.split(",")
            
            if args.timeout:
                data["timeout"] = args.timeout
            
            response = self._make_api_request("POST", "/system/command", data=data)
            
            if "error" in response:
                print(f"Error: {response['error']}")
                return
            
            print(response.get("output", ""))
            
            if "error" in response and response["error"]:
                print(f"\nError: {response['error']}")
            
            print(f"\nExit Code: {response.get('exitCode', 0)}")
            if "executionTime" in response:
                print(f"Execution Time: {response['executionTime']} ms")
        
        elif args.system_command == "terminal":
            # Open terminal UI
            try:
                # Check if we're in a GUI environment
                if os.environ.get("DISPLAY") or sys.platform == "darwin" or sys.platform == "win32":
                    # Open terminal in a new window
                    if sys.platform == "darwin":  # macOS
                        cmd = ["open", "-a", "Terminal", "python", "-m", "soulcorehub.terminal"]
                    elif sys.platform == "win32":  # Windows
                        cmd = ["start", "cmd", "/k", "python", "-m", "soulcorehub.terminal"]
                    else:  # Linux
                        cmd = ["x-terminal-emulator", "-e", "python", "-m", "soulcorehub.terminal"]
                    
                    if args.command:
                        cmd.extend(["--command", args.command])
                    
                    subprocess.Popen(cmd, shell=(sys.platform == "win32"))
                else:
                    # Run terminal in current console
                    from soulcorehub.terminal import run_terminal
                    run_terminal(initial_command=args.command)
            except Exception as e:
                print(f"Failed to open terminal: {e}")
                print("Please install the terminal package with: pip install soulcorehub-terminal")
    
    def _handle_config_commands(self, args: argparse.Namespace) -> None:
        """
        Handle config commands
        
        Args:
            args (argparse.Namespace): Command line arguments
        """
        if args.config_command == "list-profiles":
            profiles = self.config.get("profiles", {})
            current_profile = self.config.get("current_profile", DEFAULT_PROFILE)
            
            print("Available profiles:")
            for profile_name, profile in profiles.items():
                current = " (current)" if profile_name == current_profile else ""
                print(f"  {profile_name}{current}")
                print(f"    API URL: {profile.get('api_url', API_BASE_URL)}")
                api_key = profile.get('api_key', '')
                if api_key:
                    masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "****"
                    print(f"    API Key: {masked_key}")
                else:
                    print("    API Key: Not set")
        
        elif args.config_command == "set-profile":
            profiles = self.config.get("profiles", {})
            
            if args.profile not in profiles:
                profiles[args.profile] = {
                    "api_key": "",
                    "api_url": API_BASE_URL
                }
                self.config["profiles"] = profiles
            
            self.config["current_profile"] = args.profile
            self.current_profile = args.profile
            self._save_config()
            
            print(f"Current profile set to: {args.profile}")
        
        elif args.config_command == "set-api-key":
            profiles = self.config.get("profiles", {})
            profile = profiles.get(self.current_profile, {})
            profile["api_key"] = args.api_key
            profiles[self.current_profile] = profile
            self.config["profiles"] = profiles
            self._save_config()
            
            print(f"API key set for profile: {self.current_profile}")
        
        elif args.config_command == "set-api-url":
            profiles = self.config.get("profiles", {})
            profile = profiles.get(self.current_profile, {})
            profile["api_url"] = args.api_url
            profiles[self.current_profile] = profile
            self.config["profiles"] = profiles
            self._save_config()
            
            print(f"API URL set for profile: {self.current_profile}")
    
    def run(self) -> None:
        """
        Run the CLI
        """
        args = self.parser.parse_args()
        
        # Set debug logging if requested
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Set profile if specified
        if args.profile:
            self.current_profile = args.profile
        
        # Handle commands
        if args.command == "agent":
            self._handle_agent_commands(args)
        elif args.command == "content":
            self._handle_content_commands(args)
        elif args.command == "system":
            self._handle_system_commands(args)
        elif args.command == "config":
            self._handle_config_commands(args)
        else:
            self.parser.print_help()

def main():
    """
    Main entry point
    """
    try:
        cli = SoulCoreHubCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
