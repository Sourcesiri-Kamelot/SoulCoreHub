#!/usr/bin/env python3
"""
Repair Operations Module - Self-healing capabilities for EvoVe
Enables automatic detection and repair of system issues
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path

class RepairOperations:
    """Self-healing operations for the SoulCore system"""
    
    def __init__(self, mcp_bridge=None):
        """
        Initialize the Repair Operations
        
        Args:
            mcp_bridge: MCP Bridge for communication
        """
        self.mcp_bridge = mcp_bridge
        self.repair_history = []
        logging.info("Repair Operations initialized")
    
    def execute_command(self, command, cwd=None):
        """
        Execute a shell command
        
        Args:
            command (str): Command to execute
            cwd (str): Working directory
            
        Returns:
            dict: Result with output or error
        """
        if self.mcp_bridge:
            return self.mcp_bridge.execute_command(command, cwd)
        
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd
            )
            
            stdout, stderr = process.communicate()
            exit_code = process.returncode
            
            return {
                "command": command,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
                "success": exit_code == 0
            }
        except Exception as e:
            logging.error(f"Error executing command: {str(e)}")
            return {"error": str(e)}
    
    def ensure_directory_exists(self, path):
        """
        Ensure a directory exists, creating it if necessary
        
        Args:
            path (str): Path to the directory
            
        Returns:
            bool: True if directory exists or was created, False otherwise
        """
        try:
            path = os.path.expanduser(path)
            if not os.path.exists(path):
                os.makedirs(path)
                logging.info(f"Created directory: {path}")
            return True
        except Exception as e:
            logging.error(f"Error creating directory {path}: {str(e)}")
            return False
    
    def ensure_file_permissions(self, path, executable=True):
        """
        Ensure a file has the correct permissions
        
        Args:
            path (str): Path to the file
            executable (bool): Whether the file should be executable
            
        Returns:
            bool: True if permissions were set correctly, False otherwise
        """
        try:
            path = os.path.expanduser(path)
            if not os.path.exists(path):
                logging.warning(f"File not found: {path}")
                return False
                
            if executable:
                # Make file executable
                os.chmod(path, 0o755)  # rwxr-xr-x
            else:
                # Make file readable/writable but not executable
                os.chmod(path, 0o644)  # rw-r--r--
                
            logging.info(f"Set permissions for {path}")
            return True
        except Exception as e:
            logging.error(f"Error setting permissions for {path}: {str(e)}")
            return False
    
    def repair_mcp_server(self):
        """
        Repair the MCP server if it's not running
        
        Returns:
            bool: True if repair was successful, False otherwise
        """
        try:
            # Check if MCP server is running
            result = self.execute_command("pgrep -f 'python.*mcp_main.py'")
            
            if result.get("success", False) and result.get("stdout", "").strip():
                logging.info("MCP server is already running")
                return True
                
            logging.warning("MCP server is not running, attempting to start it")
            
            # Ensure MCP directory exists
            mcp_dir = Path(__file__).parent.parent / "mcp"
            if not mcp_dir.exists():
                logging.error(f"MCP directory not found: {mcp_dir}")
                return False
                
            # Start MCP server in background
            cmd = f"cd {mcp_dir} && python mcp_main.py > /dev/null 2>&1 &"
            result = self.execute_command(cmd)
            
            if result.get("success", False):
                logging.info("Started MCP server")
                return True
            else:
                logging.error(f"Failed to start MCP server: {result.get('stderr', '')}")
                return False
                
        except Exception as e:
            logging.error(f"Error repairing MCP server: {str(e)}")
            return False
    
    def repair_permissions(self):
        """
        Repair file permissions for key components
        
        Returns:
            bool: True if repair was successful, False otherwise
        """
        try:
            # Run the maintain_permissions.sh script
            script_path = Path(__file__).parent.parent / "maintain_permissions.sh"
            if script_path.exists():
                result = self.execute_command(f"bash {script_path}")
                
                if result.get("success", False):
                    logging.info("Repaired file permissions using maintain_permissions.sh")
                    return True
                else:
                    logging.error(f"Failed to repair permissions: {result.get('stderr', '')}")
            
            # Manual permission repair for key files
            success = True
            
            # MCP files
            mcp_dir = Path(__file__).parent.parent / "mcp"
            if mcp_dir.exists():
                for py_file in mcp_dir.glob("*.py"):
                    if not self.ensure_file_permissions(py_file):
                        success = False
            
            # Script files
            scripts_dir = Path(__file__).parent.parent / "scripts"
            if scripts_dir.exists():
                for sh_file in scripts_dir.glob("*.sh"):
                    if not self.ensure_file_permissions(sh_file):
                        success = False
            
            # Main Python files
            main_dir = Path(__file__).parent.parent
            for py_file in main_dir.glob("*.py"):
                if not self.ensure_file_permissions(py_file):
                    success = False
            
            return success
            
        except Exception as e:
            logging.error(f"Error repairing permissions: {str(e)}")
            return False
    
    def repair_directory_structure(self):
        """
        Repair the directory structure
        
        Returns:
            bool: True if repair was successful, False otherwise
        """
        try:
            # Ensure key directories exist
            directories = [
                "mcp",
                "scripts",
                "logs",
                "data",
                "modules",
                "evove",
                "anima",
                "voices",
                "gallery"
            ]
            
            success = True
            for directory in directories:
                path = Path(__file__).parent.parent / directory
                if not self.ensure_directory_exists(path):
                    success = False
            
            return success
            
        except Exception as e:
            logging.error(f"Error repairing directory structure: {str(e)}")
            return False
    
    def run_health_check(self):
        """
        Run a comprehensive health check and repair
        
        Returns:
            dict: Health check results
        """
        results = {
            "directory_structure": self.repair_directory_structure(),
            "permissions": self.repair_permissions(),
            "mcp_server": self.repair_mcp_server()
        }
        
        # Log the results
        for check, status in results.items():
            if status:
                logging.info(f"Health check passed: {check}")
            else:
                logging.warning(f"Health check failed: {check}")
        
        return results

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    repair_ops = RepairOperations()
    results = repair_ops.run_health_check()
    
    print("Health check results:")
    for check, status in results.items():
        print(f"- {check}: {'PASS' if status else 'FAIL'}")
