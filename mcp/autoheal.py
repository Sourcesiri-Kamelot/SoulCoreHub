"""
AutoHeal System for SoulCoreHub
Implements self-healing capabilities for failed toolchains
"""

import os
import sys
import json
import logging
import traceback
import importlib
import inspect
import asyncio
import subprocess
import shutil
from typing import Dict, List, Any, Optional, Callable, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolchainError(Exception):
    """Exception for toolchain errors"""
    def __init__(self, message: str, tool_name: str = None, error_type: str = None, 
                traceback_str: str = None):
        super().__init__(message)
        self.tool_name = tool_name
        self.error_type = error_type
        self.traceback_str = traceback_str

class AutoHealSystem:
    """Self-healing system for failed toolchains"""
    
    def __init__(self, logs_dir: str = "logs/autoheal", 
                backup_dir: str = "backups/autoheal"):
        """
        Initialize the AutoHeal system
        
        Args:
            logs_dir: Directory to store healing logs
            backup_dir: Directory to store backups before healing
        """
        self.logs_dir = logs_dir
        self.backup_dir = backup_dir
        self.healing_history = []
        self.error_patterns = self._load_error_patterns()
        self.healing_strategies = self._register_healing_strategies()
        
        # Create directories if they don't exist
        os.makedirs(logs_dir, exist_ok=True)
        os.makedirs(backup_dir, exist_ok=True)
        
        logger.info(f"AutoHeal system initialized")
    
    def _load_error_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
        Load error patterns from configuration
        
        Returns:
            Dictionary of error patterns and their solutions
        """
        # Default patterns
        patterns = {
            "ModuleNotFoundError": {
                "pattern": r"ModuleNotFoundError: No module named '([^']+)'",
                "solution": "install_module",
                "description": "Missing Python module"
            },
            "ImportError": {
                "pattern": r"ImportError: Cannot import name '([^']+)' from '([^']+)'",
                "solution": "fix_import",
                "description": "Invalid import statement"
            },
            "FileNotFoundError": {
                "pattern": r"FileNotFoundError: \[Errno 2\] No such file or directory: '([^']+)'",
                "solution": "create_file",
                "description": "Missing file"
            },
            "PermissionError": {
                "pattern": r"PermissionError: \[Errno 13\] Permission denied: '([^']+)'",
                "solution": "fix_permissions",
                "description": "Permission denied"
            },
            "SyntaxError": {
                "pattern": r"SyntaxError: (.*) \(([^,]+), line (\d+)\)",
                "solution": "fix_syntax",
                "description": "Syntax error in code"
            },
            "JSONDecodeError": {
                "pattern": r"JSONDecodeError: (.*) at line (\d+) column (\d+)",
                "solution": "fix_json",
                "description": "Invalid JSON format"
            },
            "ConnectionError": {
                "pattern": r"ConnectionError: (.*)",
                "solution": "fix_connection",
                "description": "Connection failed"
            },
            "WebSocketConnectionError": {
                "pattern": r"WebSocketConnectionError: (.*)",
                "solution": "restart_websocket",
                "description": "WebSocket connection failed"
            }
        }
        
        # Try to load custom patterns from file
        patterns_path = "config/autoheal_patterns.json"
        if os.path.exists(patterns_path):
            try:
                with open(patterns_path, 'r') as f:
                    custom_patterns = json.load(f)
                patterns.update(custom_patterns)
                logger.info(f"Loaded {len(custom_patterns)} custom error patterns")
            except Exception as e:
                logger.error(f"Error loading custom error patterns: {e}")
        
        return patterns
    
    def _register_healing_strategies(self) -> Dict[str, Callable]:
        """
        Register healing strategies
        
        Returns:
            Dictionary of strategy names and their functions
        """
        return {
            "install_module": self._heal_install_module,
            "fix_import": self._heal_fix_import,
            "create_file": self._heal_create_file,
            "fix_permissions": self._heal_fix_permissions,
            "fix_syntax": self._heal_fix_syntax,
            "fix_json": self._heal_fix_json,
            "fix_connection": self._heal_fix_connection,
            "restart_websocket": self._heal_restart_websocket,
            "restart_service": self._heal_restart_service
        }
    
    async def monitor_execution(self, func: Callable, *args, **kwargs) -> Tuple[Any, Optional[Exception]]:
        """
        Monitor the execution of a function and catch errors
        
        Args:
            func: Function to monitor
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            Tuple of (result, exception)
        """
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            return result, None
        except Exception as e:
            logger.error(f"Error in monitored function: {e}")
            return None, e
    
    async def diagnose_error(self, error: Exception) -> Dict[str, Any]:
        """
        Diagnose an error and identify potential solutions
        
        Args:
            error: The exception to diagnose
            
        Returns:
            Diagnosis information
        """
        error_type = type(error).__name__
        error_message = str(error)
        traceback_str = traceback.format_exc()
        
        logger.info(f"Diagnosing error: {error_type} - {error_message}")
        
        # Check for known error patterns
        matched_pattern = None
        match_data = None
        
        for pattern_name, pattern_info in self.error_patterns.items():
            import re
            match = re.search(pattern_info["pattern"], traceback_str)
            if match:
                matched_pattern = pattern_name
                match_data = match.groups()
                break
        
        diagnosis = {
            "error_type": error_type,
            "error_message": error_message,
            "traceback": traceback_str,
            "timestamp": datetime.now().isoformat(),
            "matched_pattern": matched_pattern,
            "match_data": match_data,
            "recommended_solution": self.error_patterns.get(matched_pattern, {}).get("solution") if matched_pattern else None,
            "solution_description": self.error_patterns.get(matched_pattern, {}).get("description") if matched_pattern else None
        }
        
        # Log the diagnosis
        log_file = os.path.join(self.logs_dir, f"diagnosis_{int(datetime.now().timestamp())}.json")
        with open(log_file, 'w') as f:
            json.dump(diagnosis, f, indent=2)
        
        return diagnosis
    
    async def heal(self, diagnosis: Dict[str, Any], auto_approve: bool = False) -> Dict[str, Any]:
        """
        Attempt to heal a diagnosed error
        
        Args:
            diagnosis: Diagnosis information
            auto_approve: Whether to automatically approve healing actions
            
        Returns:
            Healing result information
        """
        solution = diagnosis.get("recommended_solution")
        if not solution or solution not in self.healing_strategies:
            return {
                "success": False,
                "message": f"No healing strategy available for this error",
                "diagnosis": diagnosis
            }
        
        # Create backup before healing
        backup_path = self._create_backup()
        
        # Execute healing strategy
        strategy = self.healing_strategies[solution]
        try:
            if not auto_approve:
                logger.info(f"Would execute healing strategy: {solution}")
                return {
                    "success": False,
                    "message": f"Healing strategy {solution} requires approval",
                    "diagnosis": diagnosis,
                    "backup_path": backup_path,
                    "needs_approval": True
                }
            
            logger.info(f"Executing healing strategy: {solution}")
            result = await strategy(diagnosis)
            
            # Record healing action
            self.healing_history.append({
                "timestamp": datetime.now().isoformat(),
                "diagnosis": diagnosis,
                "solution": solution,
                "result": result,
                "backup_path": backup_path
            })
            
            return {
                "success": result.get("success", False),
                "message": result.get("message", ""),
                "diagnosis": diagnosis,
                "solution": solution,
                "backup_path": backup_path
            }
            
        except Exception as e:
            logger.error(f"Error during healing: {e}")
            return {
                "success": False,
                "message": f"Error during healing: {str(e)}",
                "diagnosis": diagnosis,
                "backup_path": backup_path
            }
    
    def _create_backup(self) -> str:
        """
        Create a backup before healing
        
        Returns:
            Path to the backup directory
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}")
        
        try:
            # Create backup of key directories
            os.makedirs(backup_path, exist_ok=True)
            
            # Backup Python files
            python_backup_dir = os.path.join(backup_path, "python_files")
            os.makedirs(python_backup_dir, exist_ok=True)
            
            for root, _, files in os.walk("."):
                for file in files:
                    if file.endswith(".py"):
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, ".")
                        dst_path = os.path.join(python_backup_dir, rel_path)
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        shutil.copy2(src_path, dst_path)
            
            # Backup config files
            config_backup_dir = os.path.join(backup_path, "config_files")
            os.makedirs(config_backup_dir, exist_ok=True)
            
            if os.path.exists("config"):
                for root, _, files in os.walk("config"):
                    for file in files:
                        if file.endswith((".json", ".yaml", ".yml", ".toml")):
                            src_path = os.path.join(root, file)
                            rel_path = os.path.relpath(src_path, "config")
                            dst_path = os.path.join(config_backup_dir, rel_path)
                            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                            shutil.copy2(src_path, dst_path)
            
            logger.info(f"Created backup at {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    async def restore_backup(self, backup_path: str) -> Dict[str, Any]:
        """
        Restore from a backup
        
        Args:
            backup_path: Path to the backup directory
            
        Returns:
            Restoration result
        """
        if not os.path.exists(backup_path):
            return {
                "success": False,
                "message": f"Backup path {backup_path} does not exist"
            }
        
        try:
            # Restore Python files
            python_backup_dir = os.path.join(backup_path, "python_files")
            if os.path.exists(python_backup_dir):
                for root, _, files in os.walk(python_backup_dir):
                    for file in files:
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, python_backup_dir)
                        dst_path = os.path.join(".", rel_path)
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        shutil.copy2(src_path, dst_path)
            
            # Restore config files
            config_backup_dir = os.path.join(backup_path, "config_files")
            if os.path.exists(config_backup_dir):
                for root, _, files in os.walk(config_backup_dir):
                    for file in files:
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, config_backup_dir)
                        dst_path = os.path.join("config", rel_path)
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        shutil.copy2(src_path, dst_path)
            
            return {
                "success": True,
                "message": f"Successfully restored from backup {backup_path}"
            }
            
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return {
                "success": False,
                "message": f"Error restoring backup: {str(e)}"
            }
    
    # Healing strategies
    
    async def _heal_install_module(self, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """Heal by installing a missing module"""
        if not diagnosis.get("match_data"):
            return {"success": False, "message": "No module name found in error"}
        
        module_name = diagnosis["match_data"][0]
        logger.info(f"Installing missing module: {module_name}")
        
        try:
            # Run pip install
            process = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "pip", "install", module_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "message": f"Successfully installed module {module_name}",
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode()
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to install module {module_name}",
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode()
                }
        except Exception as e:
            return {"success": False, "message": f"Error installing module: {str(e)}"}
    
    async def _heal_fix_import(self, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """Heal by fixing an import statement"""
        if not diagnosis.get("match_data") or len(diagnosis["match_data"]) < 2:
            return {"success": False, "message": "Insufficient import information in error"}
        
        name = diagnosis["match_data"][0]
        module = diagnosis["match_data"][1]
        
        # Try to find the module file
        module_path = module.replace(".", "/") + ".py"
        if not os.path.exists(module_path):
            return {"success": False, "message": f"Module file {module_path} not found"}
        
        try:
            # Read the module file
            with open(module_path, 'r') as f:
                content = f.read()
            
            # Check if the name is defined in the module
            if f"def {name}" in content or f"class {name}" in content:
                return {
                    "success": False,
                    "message": f"Name {name} exists in {module} but might not be exported"
                }
            
            # Suggest adding the name to __all__
            if "__all__" in content:
                return {
                    "success": False,
                    "message": f"Consider adding '{name}' to __all__ in {module_path}"
                }
            
            return {
                "success": False,
                "message": f"Could not automatically fix import. The name '{name}' might not exist in {module}"
            }
        except Exception as e:
            return {"success": False, "message": f"Error fixing import: {str(e)}"}
    
    async def _heal_create_file(self, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """Heal by creating a missing file"""
        if not diagnosis.get("match_data"):
            return {"success": False, "message": "No file path found in error"}
        
        file_path = diagnosis["match_data"][0]
        
        # Check if it's a directory
        if file_path.endswith("/") or file_path.endswith("\\"):
            try:
                os.makedirs(file_path, exist_ok=True)
                return {
                    "success": True,
                    "message": f"Created directory {file_path}"
                }
            except Exception as e:
                return {"success": False, "message": f"Error creating directory: {str(e)}"}
        
        # It's a file
        try:
            # Create parent directory if needed
            parent_dir = os.path.dirname(file_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
            
            # Create empty file
            with open(file_path, 'w') as f:
                pass
            
            return {
                "success": True,
                "message": f"Created empty file {file_path}"
            }
        except Exception as e:
            return {"success": False, "message": f"Error creating file: {str(e)}"}
    
    async def _heal_fix_permissions(self, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """Heal by fixing file permissions"""
        if not diagnosis.get("match_data"):
            return {"success": False, "message": "No file path found in error"}
        
        file_path = diagnosis["match_data"][0]
        
        try:
            # Make file executable
            os.chmod(file_path, 0o755)
            return {
                "success": True,
                "message": f"Fixed permissions for {file_path}"
            }
        except Exception as e:
            return {"success": False, "message": f"Error fixing permissions: {str(e)}"}
    
    async def _heal_fix_syntax(self, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """Heal by fixing syntax errors"""
        if not diagnosis.get("match_data") or len(diagnosis["match_data"]) < 3:
            return {"success": False, "message": "Insufficient syntax error information"}
        
        error_msg = diagnosis["match_data"][0]
        file_path = diagnosis["match_data"][1]
        line_num = int(diagnosis["match_data"][2])
        
        try:
            # Read the file
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Get the problematic line
            if 0 <= line_num - 1 < len(lines):
                problem_line = lines[line_num - 1]
                
                # Simple fixes for common syntax errors
                fixed_line = problem_line
                
                # Missing closing parenthesis/bracket/brace
                if "unexpected EOF" in error_msg or "expected" in error_msg:
                    if "(" in problem_line and ")" not in problem_line:
                        fixed_line = problem_line.rstrip() + ")\n"
                    elif "[" in problem_line and "]" not in problem_line:
                        fixed_line = problem_line.rstrip() + "]\n"
                    elif "{" in problem_line and "}" not in problem_line:
                        fixed_line = problem_line.rstrip() + "}\n"
                
                # Missing colon in if/for/while/def
                if "expected ':'" in error_msg:
                    fixed_line = problem_line.rstrip() + ":\n"
                
                # Apply the fix if we changed something
                if fixed_line != problem_line:
                    lines[line_num - 1] = fixed_line
                    with open(file_path, 'w') as f:
                        f.writelines(lines)
                    
                    return {
                        "success": True,
                        "message": f"Fixed syntax error in {file_path} line {line_num}",
                        "original_line": problem_line,
                        "fixed_line": fixed_line
                    }
            
            return {
                "success": False,
                "message": f"Could not automatically fix syntax error in {file_path} line {line_num}"
            }
        except Exception as e:
            return {"success": False, "message": f"Error fixing syntax: {str(e)}"}
    
    async def _heal_fix_json(self, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """Heal by fixing JSON format errors"""
        # This would require knowing which file has the JSON error
        # For now, just return a message
        return {
            "success": False,
            "message": "JSON format errors require manual inspection"
        }
    
    async def _heal_fix_connection(self, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """Heal by fixing connection errors"""
        # Check if it's a connection to a local service
        traceback_str = diagnosis.get("traceback", "")
        
        if "localhost" in traceback_str or "127.0.0.1" in traceback_str:
            # It might be a local service that needs to be started
            if "8765" in traceback_str:  # MCP server port
                return await self._heal_restart_service("mcp_server")
        
        return {
            "success": False,
            "message": "Connection errors may require checking network or service status"
        }
    
    async def _heal_restart_websocket(self, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """Heal by restarting WebSocket connections"""
        # This is a specific case of restarting a service
        return await self._heal_restart_service("mcp_server")
    
    async def _heal_restart_service(self, service_name: str) -> Dict[str, Any]:
        """Heal by restarting a service"""
        if service_name == "mcp_server":
            # Kill any existing MCP server processes
            try:
                subprocess.run(["pkill", "-f", "python.*mcp_main.py"], check=False)
                await asyncio.sleep(1)  # Give it time to shut down
                
                # Start a new MCP server
                subprocess.Popen(
                    [sys.executable, "mcp/mcp_main.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                await asyncio.sleep(2)  # Give it time to start
                
                # Check if it's running
                result = subprocess.run(["pgrep", "-f", "python.*mcp_main.py"], capture_output=True)
                if result.returncode == 0:
                    return {
                        "success": True,
                        "message": "Successfully restarted MCP server"
                    }
                else:
                    return {
                        "success": False,
                        "message": "Failed to restart MCP server"
                    }
            except Exception as e:
                return {"success": False, "message": f"Error restarting service: {str(e)}"}
        
        return {
            "success": False,
            "message": f"Don't know how to restart service: {service_name}"
        }
