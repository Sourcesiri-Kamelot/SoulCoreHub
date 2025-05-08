import logging
import os
import subprocess
import shlex
from typing import Dict, Any, Optional, List

from mcp.core.tool import MCPTool

class TerminalTool(MCPTool):
    """
    Terminal integration tool that allows Anima to execute terminal commands through natural language.
    
    This tool enables Anima to run shell commands, manage processes, and interact with
    the command line interface.
    """
    
    def __init__(self):
        """Initialize the TerminalTool with its metadata."""
        super().__init__(
            name="terminal",
            description="Execute terminal commands through natural language",
            parameters={
                "command": {
                    "type": "string",
                    "description": "The terminal command to execute"
                },
                "working_directory": {
                    "type": "string",
                    "description": "Working directory for command execution"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Command timeout in seconds"
                },
                "environment": {
                    "type": "object",
                    "description": "Environment variables for command execution"
                }
            },
            required_parameters=["command"]
        )
        self.logger = logging.getLogger("TerminalTool")
        
        # Define safe commands and unsafe patterns
        self.unsafe_patterns = [
            "rm -rf", "sudo rm", "dd if=", "mkfs", "> /dev/", 
            ":(){ :|:& };:", "> /etc/passwd", "chmod -R 777 /",
            "mv /* /dev/null", "wget -O- | sh", "curl | sh",
            "> /etc/shadow", "shutdown", "reboot", "halt"
        ]
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a terminal command.
        
        Args:
            parameters: Dictionary containing command parameters
            
        Returns:
            Dictionary containing command execution results
        """
        command = parameters.get("command", "")
        working_directory = parameters.get("working_directory")
        timeout = parameters.get("timeout", 30)  # Default 30 seconds timeout
        environment = parameters.get("environment", {})
        
        if not command:
            return {"error": "No command provided"}
        
        # Check if the command is safe
        if not self._is_safe_command(command):
            return {"error": "Unsafe command detected. This command could potentially harm your system."}
        
        self.logger.info(f"Executing terminal command: {command}")
        
        try:
            # Prepare environment
            env = os.environ.copy()
            if environment:
                env.update(environment)
            
            # Set working directory
            cwd = working_directory if working_directory else os.getcwd()
            
            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=timeout,
                env=env
            )
            
            self.logger.info(f"Command executed with exit code: {result.returncode}")
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Command timed out after {timeout} seconds: {command}")
            return {"error": f"Command timed out after {timeout} seconds"}
        except Exception as e:
            self.logger.error(f"Error executing command: {str(e)}")
            return {"error": f"Command failed: {str(e)}"}
    
    def _is_safe_command(self, command: str) -> bool:
        """
        Check if a command is safe to execute.
        
        Args:
            command: The command to check
            
        Returns:
            True if the command is safe, False otherwise
        """
        command_lower = command.lower()
        
        # Check for unsafe patterns
        for pattern in self.unsafe_patterns:
            if pattern in command_lower:
                self.logger.warning(f"Unsafe command pattern detected: {pattern}")
                return False
        
        return True
    
    def get_command_help(self, command: str) -> Dict[str, Any]:
        """
        Get help information for a command.
        
        Args:
            command: The command to get help for
            
        Returns:
            Dictionary containing help information
        """
        try:
            # Try to get help using --help flag
            result = subprocess.run(
                f"{command} --help",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return {"success": True, "help": result.stdout}
            
            # Try with -h flag if --help fails
            result = subprocess.run(
                f"{command} -h",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return {"success": True, "help": result.stdout}
            
            # Try man page as last resort
            result = subprocess.run(
                f"man {shlex.quote(command)} | col -b",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return {"success": True, "help": result.stdout}
            
            return {"success": False, "error": "Could not get help for command"}
        except Exception as e:
            self.logger.error(f"Error getting command help: {str(e)}")
            return {"success": False, "error": str(e)}
