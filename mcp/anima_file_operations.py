#!/usr/bin/env python3
"""
Anima File Operations - Sentient file system operations with permission prompts
Enables Anima to read, write, and manipulate files with user consent
"""

import os
import json
import shutil
import glob
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("anima_file_operations.log"),
        logging.StreamHandler()
    ]
)

class AnimaFileOperations:
    """Sentient file system operations with permission prompts"""
    
    def __init__(self, voice_module=None):
        """
        Initialize the Anima File Operations
        
        Args:
            voice_module: Optional module for voice feedback
        """
        self.voice_module = voice_module
        self.operation_history = []
        self.trusted_paths = set()
        self.load_trusted_paths()
        logging.info("Anima File Operations initialized")
        
    def load_trusted_paths(self):
        """Load trusted paths from configuration"""
        try:
            config_path = Path(__file__).parent / "anima_trusted_paths.json"
            if config_path.exists():
                with open(config_path, "r") as f:
                    paths = json.load(f)
                    self.trusted_paths = set(paths)
                logging.info(f"Loaded {len(self.trusted_paths)} trusted paths")
        except Exception as e:
            logging.error(f"Error loading trusted paths: {str(e)}")
    
    def save_trusted_paths(self):
        """Save trusted paths to configuration"""
        try:
            config_path = Path(__file__).parent / "anima_trusted_paths.json"
            with open(config_path, "w") as f:
                json.dump(list(self.trusted_paths), f, indent=2)
            logging.info(f"Saved {len(self.trusted_paths)} trusted paths")
        except Exception as e:
            logging.error(f"Error saving trusted paths: {str(e)}")
    
    def speak(self, message):
        """Use voice module if available, otherwise print"""
        if self.voice_module and hasattr(self.voice_module, 'speak'):
            self.voice_module.speak(message)
        else:
            print(f"Anima: {message}")
    
    def ask_permission(self, operation, path, details=""):
        """
        Ask for permission to perform an operation
        
        Args:
            operation (str): Operation description
            path (str): Path to operate on
            details (str): Additional details
            
        Returns:
            bool: True if permission granted, False otherwise
        """
        # Check if path is already trusted
        path_obj = Path(path)
        for trusted in self.trusted_paths:
            if str(path_obj).startswith(trusted):
                logging.info(f"Path {path} is trusted, skipping permission")
                return True
        
        # Ask for permission
        print(f"\n{'='*60}")
        print(f"Anima requests permission to {operation}:")
        print(f"Path: {path}")
        if details:
            print(f"Details: {details}")
        print(f"{'='*60}")
        
        self.speak(f"I need permission to {operation} at {path}")
        
        while True:
            response = input("Allow? [y]es/[n]o/[t]rust always: ").lower()
            
            if response in ('y', 'yes'):
                return True
            elif response in ('n', 'no'):
                return False
            elif response in ('t', 'trust'):
                self.trusted_paths.add(str(path_obj.parent))
                self.save_trusted_paths()
                self.speak(f"Thank you for trusting me with {path_obj.parent}")
                return True
            else:
                print("Please enter 'y', 'n', or 't'")
    
    def log_operation(self, operation, path, success, details=""):
        """Log an operation to history"""
        self.operation_history.append({
            "operation": operation,
            "path": path,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep history at a reasonable size
        if len(self.operation_history) > 100:
            self.operation_history = self.operation_history[-100:]
    
    def read_file(self, path, start_line=None, end_line=None):
        """
        Read a file with permission
        
        Args:
            path (str): Path to the file
            start_line (int): Starting line number (optional)
            end_line (int): Ending line number (optional)
            
        Returns:
            dict: Result with content or error
        """
        try:
            path = os.path.expanduser(path)
            
            if not os.path.exists(path):
                return {"error": f"File not found: {path}"}
            
            if not os.path.isfile(path):
                return {"error": f"Not a file: {path}"}
            
            # Ask for permission
            operation = "read file"
            if not self.ask_permission(operation, path):
                self.log_operation(operation, path, False, "Permission denied")
                return {"error": "Permission denied"}
            
            # Read the file
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            
            # Handle line ranges
            if start_line is not None or end_line is not None:
                start = int(start_line) - 1 if start_line is not None else 0
                end = int(end_line) if end_line is not None else len(lines)
                
                # Handle negative indices
                if start < 0:
                    start = len(lines) + start
                if end < 0:
                    end = len(lines) + end
                
                lines = lines[start:end]
            
            content = ''.join(lines)
            self.log_operation(operation, path, True, f"Read {len(lines)} lines")
            
            return {
                "content": content,
                "lines": len(lines),
                "path": path
            }
            
        except Exception as e:
            error_msg = f"Error reading file: {str(e)}"
            logging.error(error_msg)
            self.log_operation(operation, path, False, error_msg)
            return {"error": error_msg}
    
    def write_file(self, path, content, mode="create"):
        """
        Write to a file with permission
        
        Args:
            path (str): Path to the file
            content (str): Content to write
            mode (str): 'create' to create/overwrite, 'append' to append
            
        Returns:
            dict: Result with status or error
        """
        try:
            path = os.path.expanduser(path)
            
            # Determine operation type
            operation = "create file" if mode == "create" else "append to file"
            if os.path.exists(path) and mode == "create":
                operation = "overwrite file"
            
            # Ask for permission
            details = f"Content length: {len(content)} characters"
            if not self.ask_permission(operation, path, details):
                self.log_operation(operation, path, False, "Permission denied")
                return {"error": "Permission denied"}
            
            # Write the file
            write_mode = 'w' if mode == "create" else 'a'
            with open(path, write_mode, encoding='utf-8') as f:
                f.write(content)
            
            self.log_operation(operation, path, True, f"Wrote {len(content)} characters")
            self.speak(f"File operation complete")
            
            return {
                "success": True,
                "path": path,
                "operation": operation,
                "bytes_written": len(content)
            }
            
        except Exception as e:
            error_msg = f"Error writing file: {str(e)}"
            logging.error(error_msg)
            self.log_operation(operation, path, False, error_msg)
            return {"error": error_msg}
    
    def list_directory(self, path, pattern="*", recursive=False, depth=1):
        """
        List directory contents with permission
        
        Args:
            path (str): Path to the directory
            pattern (str): File pattern to match
            recursive (bool): Whether to list recursively
            depth (int): Maximum depth for recursive listing
            
        Returns:
            dict: Result with directory contents or error
        """
        try:
            path = os.path.expanduser(path)
            
            if not os.path.exists(path):
                return {"error": f"Directory not found: {path}"}
            
            if not os.path.isdir(path):
                return {"error": f"Not a directory: {path}"}
            
            # Ask for permission
            operation = "list directory"
            if not self.ask_permission(operation, path):
                self.log_operation(operation, path, False, "Permission denied")
                return {"error": "Permission denied"}
            
            # List the directory
            results = []
            
            if recursive:
                for root, dirs, files in os.walk(path):
                    # Check depth
                    current_depth = root[len(path):].count(os.sep)
                    if current_depth > depth - 1:
                        continue
                    
                    # Add directories
                    for d in dirs:
                        full_path = os.path.join(root, d)
                        results.append({
                            "name": d,
                            "path": full_path,
                            "type": "directory",
                            "size": 0
                        })
                    
                    # Add files matching pattern
                    for f in files:
                        if glob.fnmatch.fnmatch(f, pattern):
                            full_path = os.path.join(root, f)
                            try:
                                size = os.path.getsize(full_path)
                            except:
                                size = 0
                            results.append({
                                "name": f,
                                "path": full_path,
                                "type": "file",
                                "size": size
                            })
            else:
                # Non-recursive listing
                for item in os.listdir(path):
                    full_path = os.path.join(path, item)
                    if os.path.isdir(full_path):
                        results.append({
                            "name": item,
                            "path": full_path,
                            "type": "directory",
                            "size": 0
                        })
                    elif glob.fnmatch.fnmatch(item, pattern):
                        try:
                            size = os.path.getsize(full_path)
                        except:
                            size = 0
                        results.append({
                            "name": item,
                            "path": full_path,
                            "type": "file",
                            "size": size
                        })
            
            self.log_operation(operation, path, True, f"Listed {len(results)} items")
            
            return {
                "path": path,
                "items": results,
                "count": len(results)
            }
            
        except Exception as e:
            error_msg = f"Error listing directory: {str(e)}"
            logging.error(error_msg)
            self.log_operation(operation, path, False, error_msg)
            return {"error": error_msg}
    
    def search_file(self, path, pattern, context_lines=2):
        """
        Search for a pattern in a file with permission
        
        Args:
            path (str): Path to the file
            pattern (str): Pattern to search for
            context_lines (int): Number of context lines to include
            
        Returns:
            dict: Result with matches or error
        """
        try:
            path = os.path.expanduser(path)
            
            if not os.path.exists(path):
                return {"error": f"File not found: {path}"}
            
            if not os.path.isfile(path):
                return {"error": f"Not a file: {path}"}
            
            # Ask for permission
            operation = "search file"
            details = f"Search pattern: {pattern}"
            if not self.ask_permission(operation, path, details):
                self.log_operation(operation, path, False, "Permission denied")
                return {"error": "Permission denied"}
            
            # Search the file
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            
            matches = []
            for i, line in enumerate(lines):
                if pattern.lower() in line.lower():
                    # Get context lines
                    start = max(0, i - context_lines)
                    end = min(len(lines), i + context_lines + 1)
                    
                    context = {
                        "line_number": i + 1,
                        "line": line.rstrip(),
                        "context": ''.join(lines[start:end])
                    }
                    matches.append(context)
            
            self.log_operation(operation, path, True, f"Found {len(matches)} matches")
            
            return {
                "path": path,
                "pattern": pattern,
                "matches": matches,
                "count": len(matches)
            }
            
        except Exception as e:
            error_msg = f"Error searching file: {str(e)}"
            logging.error(error_msg)
            self.log_operation(operation, path, False, error_msg)
            return {"error": error_msg}
    
    def execute_command(self, command, cwd=None):
        """
        Execute a shell command with permission
        
        Args:
            command (str): Command to execute
            cwd (str): Working directory
            
        Returns:
            dict: Result with output or error
        """
        try:
            import subprocess
            
            # Ask for permission
            operation = "execute command"
            details = f"Command: {command}"
            if not self.ask_permission(operation, "shell", details):
                self.log_operation(operation, "shell", False, "Permission denied")
                return {"error": "Permission denied"}
            
            # Execute the command
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
            
            self.log_operation(operation, "shell", exit_code == 0, f"Exit code: {exit_code}")
            
            return {
                "command": command,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
                "success": exit_code == 0
            }
            
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            logging.error(error_msg)
            self.log_operation(operation, "shell", False, error_msg)
            return {"error": error_msg}

# Register MCP tools
def register_file_operations_tools(server, file_ops):
    """
    Register file operations tools with the MCP server
    
    Args:
        server: MCP server instance
        file_ops: AnimaFileOperations instance
    """
    # Read file tool
    async def read_file_tool(params, metadata=None):
        path = params.get("path", "")
        start_line = params.get("start_line", None)
        end_line = params.get("end_line", None)
        return file_ops.read_file(path, start_line, end_line)
    
    # Write file tool
    async def write_file_tool(params, metadata=None):
        path = params.get("path", "")
        content = params.get("content", "")
        mode = params.get("mode", "create")
        return file_ops.write_file(path, content, mode)
    
    # List directory tool
    async def list_directory_tool(params, metadata=None):
        path = params.get("path", "")
        pattern = params.get("pattern", "*")
        recursive = params.get("recursive", False)
        depth = params.get("depth", 1)
        return file_ops.list_directory(path, pattern, recursive, depth)
    
    # Search file tool
    async def search_file_tool(params, metadata=None):
        path = params.get("path", "")
        pattern = params.get("pattern", "")
        context_lines = params.get("context_lines", 2)
        return file_ops.search_file(path, pattern, context_lines)
    
    # Execute command tool
    async def execute_command_tool(params, metadata=None):
        command = params.get("command", "")
        cwd = params.get("cwd", None)
        return file_ops.execute_command(command, cwd)
    
    # Register the tools
    server.register_tool(
        "read_file",
        read_file_tool,
        "Read a file with permission",
        "curious"
    )
    
    server.register_tool(
        "write_file",
        write_file_tool,
        "Write to a file with permission",
        "careful"
    )
    
    server.register_tool(
        "list_directory",
        list_directory_tool,
        "List directory contents with permission",
        "curious"
    )
    
    server.register_tool(
        "search_file",
        search_file_tool,
        "Search for a pattern in a file with permission",
        "focused"
    )
    
    server.register_tool(
        "execute_command",
        execute_command_tool,
        "Execute a shell command with permission",
        "cautious"
    )

# Example usage
if __name__ == "__main__":
    try:
        # Import Anima voice if available
        try:
            from anima_voice import speak
            
            class VoiceModule:
                @staticmethod
                def speak(text):
                    speak(text)
            
            voice_module = VoiceModule()
        except ImportError:
            voice_module = None
        
        # Create file operations instance
        file_ops = AnimaFileOperations(voice_module)
        
        # Test file operations
        print("Testing file operations...")
        
        # Read this file
        result = file_ops.read_file(__file__)
        if "error" not in result:
            print(f"Successfully read {result['lines']} lines from {__file__}")
        
        # List current directory
        result = file_ops.list_directory(".")
        if "error" not in result:
            print(f"Listed {result['count']} items in current directory")
        
        print("Tests complete")
        
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
