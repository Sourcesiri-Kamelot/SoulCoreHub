import os
import json
import subprocess
from pathlib import Path

from .registry import StatelessTool, register_tool


@register_tool("list_directory")
class ListDirectoryTool(StatelessTool):
    """Tool for listing contents of a directory."""
    
    def __init__(self):
        self.name = "list_directory"
        self.description = "List the contents of a directory, showing files and subdirectories"
        self.parameters = {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the directory to list. "
                                  "Defaults to current directory if not provided."
                },
                "show_hidden": {
                    "type": "boolean",
                    "description": "Whether to show hidden files (starting with .)"
                }
            },
            "required": []
        }
        
    def __call__(self, path: str = ".", show_hidden: bool = False) -> str:
        """List the contents of a directory."""
        try:
            path = os.path.expanduser(path)
            if not os.path.exists(path):
                return f"Error: Path '{path}' does not exist"
            
            if not os.path.isdir(path):
                return f"Error: Path '{path}' is not a directory"
            
            items = []
            for item in os.listdir(path):
                if not show_hidden and item.startswith('.'):
                    continue
                    
                item_path = os.path.join(path, item)
                item_type = "directory" if os.path.isdir(item_path) else "file"
                size = os.path.getsize(item_path) if os.path.isfile(item_path) else None
                
                items.append({
                    "name": item,
                    "type": item_type,
                    "size": size
                })
            
            return json.dumps({"path": path, "items": items}, indent=2)
        except Exception as e:
            return f"Error listing directory: {str(e)}"
    
    def to_dict(self):
        """Convert tool to dictionary format for LLM function calling."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


@register_tool("directory_tree")
class DirectoryTreeTool(StatelessTool):
    """Tool for displaying directory structure as a tree."""
    
    def __init__(self):
        self.name = "directory_tree"
        self.description = "Display the directory structure as a tree, " \
                          "showing the hierarchy of files and directories"
        self.parameters = {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the root directory. " \
                                  "Defaults to current directory if not provided."
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum depth of subdirectories to display"
                },
                "show_hidden": {
                    "type": "boolean",
                    "description": "Whether to show hidden files (starting with .)"
                }
            },
            "required": []
        }
        
    def __call__(self, path: str = ".", max_depth: int = 3, show_hidden: bool = False) -> str:
        """Display the directory structure as a tree."""
        try:
            path = os.path.expanduser(path)
            if not os.path.exists(path):
                return f"Error: Path '{path}' does not exist"
            
            if not os.path.isdir(path):
                return f"Error: Path '{path}' is not a directory"
            
            # Try to use external 'tree' command if available
            try:
                cmd = ["tree", path, "-L", str(max_depth)]
                if not show_hidden:
                    cmd.append("-I")
                    cmd.append(".*")
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout
            except (subprocess.SubprocessError, FileNotFoundError):
                # If 'tree' command fails or is not available, fall back to custom implementation
                pass
                
            # Custom tree implementation
            result = [f"Directory tree for {path}:"]
            
            def add_to_tree(directory: Path, prefix: str = "", depth: int = 0):
                if depth > max_depth:
                    return
                
                try:
                    entries = sorted(directory.iterdir(), 
                                   key=lambda x: (x.is_file(), x.name))
                    
                    for i, entry in enumerate(entries):
                        if not show_hidden and entry.name.startswith('.'):
                            continue
                            
                        is_last = i == len(entries) - 1
                        result.append(f"{prefix}{'└── ' if is_last else '├── '}{entry.name}")
                        
                        if entry.is_dir():
                            add_to_tree(
                                entry,
                                prefix + ('    ' if is_last else '│   '),
                                depth + 1
                            )
                except PermissionError:
                    result.append(f"{prefix}└── [Permission denied]")
            
            add_to_tree(Path(path))
            return "\n".join(result)
        except Exception as e:
            return f"Error creating directory tree: {str(e)}"
    
    def to_dict(self):
        """Convert tool to dictionary format for LLM function calling."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        } 