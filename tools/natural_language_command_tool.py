import json
import logging
import re
from typing import Dict, Any, List, Optional, Tuple

from mcp.core.tool import MCPTool

class NaturalLanguageCommandTool(MCPTool):
    """
    Natural Language Command Tool that parses natural language into structured commands.
    
    This tool enables Anima to understand natural language instructions and convert them
    into structured commands that can be executed by other tools.
    """
    
    def __init__(self):
        """Initialize the NaturalLanguageCommandTool with its metadata."""
        super().__init__(
            name="nlcommand",
            description="Parse natural language into structured commands",
            parameters={
                "text": {
                    "type": "string",
                    "description": "The natural language command to parse"
                },
                "context": {
                    "type": "object",
                    "description": "Additional context for command parsing"
                }
            },
            required_parameters=["text"]
        )
        self.logger = logging.getLogger("NaturalLanguageCommandTool")
        
        # Define command patterns
        self.command_patterns = [
            {
                "pattern": r"create (?:a )?(?:new )?file (?:called |named )?(?P<file_path>[^\s]+)(?: with (?:content|the following))?",
                "tool": "vscode",
                "command": "create_file",
                "parameters": {
                    "path": "file_path"
                }
            },
            {
                "pattern": r"edit (?:the )?file (?P<file_path>[^\s]+)",
                "tool": "vscode",
                "command": "edit_file",
                "parameters": {
                    "path": "file_path"
                }
            },
            {
                "pattern": r"open (?:the )?file (?P<file_path>[^\s]+)",
                "tool": "vscode",
                "command": "open_file",
                "parameters": {
                    "path": "file_path"
                }
            },
            {
                "pattern": r"run (?:the )?command (?P<command>.+)",
                "tool": "terminal",
                "command": "command",
                "parameters": {
                    "command": "command"
                }
            },
            {
                "pattern": r"create (?:a )?(?:new )?(?P<project_type>\w+) project (?:called |named )?(?P<project_name>[^\s]+)",
                "tool": "builder",
                "command": "create_project",
                "parameters": {
                    "action": "create_project",
                    "project_type": "project_type",
                    "project_name": "project_name"
                }
            },
            {
                "pattern": r"install (?:the )?(?:dependency|package|module) (?P<dependency>[^\s]+)",
                "tool": "builder",
                "command": "install_dependencies",
                "parameters": {
                    "action": "install_dependencies",
                    "dependencies": ["dependency"]
                }
            }
        ]
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse natural language into structured commands.
        
        Args:
            parameters: Dictionary containing the natural language text
            
        Returns:
            Dictionary containing the parsed command
        """
        text = parameters.get("text", "")
        context = parameters.get("context", {})
        
        if not text:
            return {"error": "No text provided"}
        
        self.logger.info(f"Parsing natural language command: {text}")
        
        try:
            # Parse the command
            parsed_command = self._parse_command(text, context)
            
            if parsed_command:
                return {
                    "success": True,
                    "parsed_command": parsed_command
                }
            else:
                return {
                    "success": False,
                    "error": "Could not parse command",
                    "text": text
                }
        except Exception as e:
            self.logger.error(f"Error parsing command: {str(e)}")
            return {"error": f"Failed to parse command: {str(e)}"}
    
    def _parse_command(self, text: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse a natural language command into a structured command.
        
        Args:
            text: The natural language command
            context: Additional context for command parsing
            
        Returns:
            Structured command or None if parsing failed
        """
        # Try to match the command against known patterns
        for pattern in self.command_patterns:
            match = re.search(pattern["pattern"], text, re.IGNORECASE)
            if match:
                # Extract parameters from the match
                params = {}
                for param_name, match_name in pattern["parameters"].items():
                    if match_name in match.groupdict():
                        params[param_name] = match.group(match_name)
                
                # Extract file content if present
                if "create file" in text.lower() or "edit file" in text.lower():
                    content_match = re.search(r"with content[:\s]+(.+?)(?:$|(?=\s+and\s+))", text, re.DOTALL | re.IGNORECASE)
                    if content_match:
                        params["content"] = content_match.group(1).strip()
                
                # Extract project description if present
                if "create" in text.lower() and "project" in text.lower():
                    desc_match = re.search(r"with description[:\s]+(.+?)(?:$|(?=\s+and\s+))", text, re.DOTALL | re.IGNORECASE)
                    if desc_match:
                        params["project_description"] = desc_match.group(1).strip()
                
                # Build the command
                command = {
                    "tool": pattern["tool"],
                    "command": pattern["command"],
                    "parameters": params
                }
                
                return command
        
        # If no pattern matched, try to extract a command using heuristics
        return self._extract_command_heuristically(text, context)
    
    def _extract_command_heuristically(self, text: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract a command using heuristics when no pattern matches.
        
        Args:
            text: The natural language command
            context: Additional context for command parsing
            
        Returns:
            Structured command or None if extraction failed
        """
        text_lower = text.lower()
        
        # Check for file operations
        if "file" in text_lower:
            if "create" in text_lower or "new" in text_lower:
                # Extract file path
                file_path = self._extract_file_path(text)
                if file_path:
                    return {
                        "tool": "vscode",
                        "command": "create_file",
                        "parameters": {
                            "path": file_path,
                            "content": self._extract_content(text)
                        }
                    }
            elif "edit" in text_lower or "modify" in text_lower:
                # Extract file path
                file_path = self._extract_file_path(text)
                if file_path:
                    return {
                        "tool": "vscode",
                        "command": "edit_file",
                        "parameters": {
                            "path": file_path,
                            "content": self._extract_content(text)
                        }
                    }
        
        # Check for terminal commands
        if "run" in text_lower or "execute" in text_lower:
            # Extract command
            command_match = re.search(r"run\s+(?:the\s+)?(?:command\s+)?['\"]?([^'\"]+)['\"]?", text_lower)
            if command_match:
                return {
                    "tool": "terminal",
                    "command": "command",
                    "parameters": {
                        "command": command_match.group(1).strip()
                    }
                }
        
        # Check for project creation
        if "create" in text_lower and "project" in text_lower:
            project_type_match = re.search(r"create\s+(?:a\s+)?(?:new\s+)?(\w+)\s+project", text_lower)
            project_name_match = re.search(r"project\s+(?:called|named)\s+([^\s]+)", text_lower)
            
            if project_type_match and project_name_match:
                return {
                    "tool": "builder",
                    "command": "create_project",
                    "parameters": {
                        "action": "create_project",
                        "project_type": project_type_match.group(1),
                        "project_name": project_name_match.group(1),
                        "project_description": self._extract_description(text)
                    }
                }
        
        # No command could be extracted
        return None
    
    def _extract_file_path(self, text: str) -> Optional[str]:
        """Extract a file path from text"""
        # Try different patterns to extract file path
        patterns = [
            r"file\s+(?:called|named)\s+([^\s]+)",
            r"file\s+([^\s]+)",
            r"(?:called|named)\s+([^\s]+\.[\w]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_content(self, text: str) -> str:
        """Extract content from text"""
        # Try to extract content after "with content" or similar phrases
        content_patterns = [
            r"with\s+content[:\s]+(.+?)(?:$|(?=\s+and\s+))",
            r"content[:\s]+(.+?)(?:$|(?=\s+and\s+))",
            r"containing[:\s]+(.+?)(?:$|(?=\s+and\s+))"
        ]
        
        for pattern in content_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_description(self, text: str) -> str:
        """Extract description from text"""
        # Try to extract description after "with description" or similar phrases
        desc_patterns = [
            r"with\s+description[:\s]+(.+?)(?:$|(?=\s+and\s+))",
            r"description[:\s]+(.+?)(?:$|(?=\s+and\s+))",
            r"described\s+as[:\s]+(.+?)(?:$|(?=\s+and\s+))"
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
