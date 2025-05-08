import json
import logging
import os
import subprocess
from typing import Dict, Any, Optional

from mcp.core.tool import MCPTool

class VSCodeTool(MCPTool):
    """
    VS Code integration tool that allows Anima to interact with VS Code through natural language.
    
    This tool enables Anima to create, edit, and manage files in VS Code, as well as
    execute VS Code commands and extensions.
    """
    
    def __init__(self):
        """Initialize the VSCodeTool with its metadata."""
        super().__init__(
            name="vscode",
            description="Interact with Visual Studio Code through natural language commands",
            parameters={
                "command": {
                    "type": "string",
                    "description": "The VS Code command to execute or action to perform",
                    "enum": ["create_file", "edit_file", "open_file", "execute_command", "install_extension"]
                },
                "path": {
                    "type": "string",
                    "description": "File path for file operations"
                },
                "content": {
                    "type": "string",
                    "description": "File content for create or edit operations"
                },
                "vscode_command": {
                    "type": "string",
                    "description": "VS Code command ID to execute"
                },
                "args": {
                    "type": "array",
                    "description": "Arguments for VS Code command"
                },
                "extension_id": {
                    "type": "string",
                    "description": "Extension ID to install"
                }
            },
            required_parameters=["command"]
        )
        self.logger = logging.getLogger("VSCodeTool")
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute VS Code operations based on the command.
        
        Args:
            parameters: Dictionary containing command parameters
            
        Returns:
            Dictionary containing operation results
        """
        command = parameters.get("command", "")
        
        if not command:
            return {"error": "No command provided"}
        
        self.logger.info(f"Executing VS Code command: {command}")
        
        try:
            if command == "create_file":
                return self._create_file(parameters)
            elif command == "edit_file":
                return self._edit_file(parameters)
            elif command == "open_file":
                return self._open_file(parameters)
            elif command == "execute_command":
                return self._execute_command(parameters)
            elif command == "install_extension":
                return self._install_extension(parameters)
            else:
                return {"error": f"Unknown command: {command}"}
        except Exception as e:
            self.logger.error(f"Error executing VS Code command: {str(e)}")
            return {"error": f"Command failed: {str(e)}"}
    
    def _create_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new file in VS Code"""
        path = parameters.get("path")
        content = parameters.get("content", "")
        
        if not path:
            return {"error": "No file path provided"}
        
        try:
            # Ensure the directory exists
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Write the file
            with open(path, 'w') as f:
                f.write(content)
            
            # Open the file in VS Code
            self._run_vscode_command(["code", path])
            
            self.logger.info(f"Created file: {path}")
            return {"success": True, "path": path}
        except Exception as e:
            self.logger.error(f"Error creating file: {str(e)}")
            return {"error": f"Failed to create file: {str(e)}"}
    
    def _edit_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Edit an existing file in VS Code"""
        path = parameters.get("path")
        content = parameters.get("content")
        
        if not path:
            return {"error": "No file path provided"}
        
        if not os.path.exists(path):
            return {"error": f"File not found: {path}"}
        
        if content is None:
            return {"error": "No content provided for edit"}
        
        try:
            with open(path, 'w') as f:
                f.write(content)
            
            # Open the file in VS Code
            self._run_vscode_command(["code", path])
            
            self.logger.info(f"Edited file: {path}")
            return {"success": True, "path": path}
        except Exception as e:
            self.logger.error(f"Error editing file: {str(e)}")
            return {"error": f"Failed to edit file: {str(e)}"}
    
    def _open_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Open a file in VS Code"""
        path = parameters.get("path")
        
        if not path:
            return {"error": "No file path provided"}
        
        if not os.path.exists(path):
            return {"error": f"File not found: {path}"}
        
        try:
            # Open the file in VS Code
            result = self._run_vscode_command(["code", path])
            
            self.logger.info(f"Opened file: {path}")
            return {"success": True, "path": path, "result": result}
        except Exception as e:
            self.logger.error(f"Error opening file: {str(e)}")
            return {"error": f"Failed to open file: {str(e)}"}
    
    def _execute_command(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a VS Code command"""
        vscode_command = parameters.get("vscode_command")
        args = parameters.get("args", [])
        
        if not vscode_command:
            return {"error": "No VS Code command provided"}
        
        try:
            cmd = ["code", "--remote", "anima", "--execute-command", vscode_command]
            
            if args:
                cmd.extend(["--args", json.dumps(args)])
            
            result = self._run_vscode_command(cmd)
            
            self.logger.info(f"Executed VS Code command: {vscode_command}")
            return {"success": True, "command": vscode_command, "result": result}
        except Exception as e:
            self.logger.error(f"Error executing VS Code command: {str(e)}")
            return {"error": f"Failed to execute command: {str(e)}"}
    
    def _install_extension(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Install a VS Code extension"""
        extension_id = parameters.get("extension_id")
        
        if not extension_id:
            return {"error": "No extension ID provided"}
        
        try:
            result = self._run_vscode_command(["code", "--install-extension", extension_id])
            
            self.logger.info(f"Installed VS Code extension: {extension_id}")
            return {"success": True, "extension_id": extension_id, "result": result}
        except Exception as e:
            self.logger.error(f"Error installing extension: {str(e)}")
            return {"error": f"Failed to install extension: {str(e)}"}
    
    def _run_vscode_command(self, command: list) -> Dict[str, Any]:
        """Run a VS Code CLI command"""
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {"stdout": result.stdout, "stderr": result.stderr, "exit_code": result.returncode}
            else:
                self.logger.warning(f"VS Code command failed: {result.stderr}")
                return {"stdout": result.stdout, "stderr": result.stderr, "exit_code": result.returncode}
        except Exception as e:
            self.logger.error(f"Error running VS Code command: {str(e)}")
            raise
