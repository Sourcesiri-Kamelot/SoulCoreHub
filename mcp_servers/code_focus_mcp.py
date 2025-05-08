#!/usr/bin/env python3
"""
SoulCoreHub Code Focus MCP Server
---------------------------------
This MCP server specializes in coding, CLI operations, and debugging.
"""

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CodeFocusMCP")

# Constants
PORT = 8701
SERVER_NAME = "code_focus_mcp"
SPECIALTIES = ["coding", "programming", "debugging", "CLI", "terminal", "shell", "git"]
TOOLS = {
    "code_analysis": {
        "description": "Analyzes code structure and provides insights",
        "parameters": {"code": "The code to analyze", "language": "Programming language"}
    },
    "debug_assistance": {
        "description": "Helps debug code issues and errors",
        "parameters": {"code": "The code with issues", "error": "Error message", "language": "Language"}
    },
    "cli_command": {
        "description": "Suggests CLI commands for specific tasks",
        "parameters": {"task": "Description of the task", "os": "Operating system"}
    }
}

class MCPHandler(BaseHTTPRequestHandler):
    """Handler for MCP server requests."""
    
    def _set_headers(self, content_type="application/json"):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests - primarily for server info and health checks."""
        if self.path == "/":
            self._set_headers()
            server_info = {
                "name": SERVER_NAME,
                "status": "active",
                "specialties": SPECIALTIES,
                "tools": list(TOOLS.keys()),
                "version": "1.0.0"
            }
            self.wfile.write(json.dumps(server_info).encode())
        elif self.path == "/health":
            self._set_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests for tool invocation."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            request = json.loads(post_data.decode('utf-8'))
            
            if self.path == "/invoke":
                tool_name = request.get("tool")
                parameters = request.get("parameters", {})
                
                if tool_name not in TOOLS:
                    self._set_headers()
                    self.wfile.write(json.dumps({
                        "error": f"Tool '{tool_name}' not found",
                        "available_tools": list(TOOLS.keys())
                    }).encode())
                    return
                
                # Process the tool request
                result = self._process_tool(tool_name, parameters)
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            
            elif self.path == "/context":
                # Process context request
                query = request.get("query", "")
                context = self._generate_context(query)
                self._set_headers()
                self.wfile.write(json.dumps({"context": context}).encode())
            
            else:
                self.send_response(404)
                self.end_headers()
        
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
    
    def _process_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process a tool invocation request."""
        logger.info(f"Processing tool: {tool_name} with parameters: {parameters}")
        
        if tool_name == "code_analysis":
            return self._analyze_code(parameters.get("code", ""), parameters.get("language", ""))
        elif tool_name == "debug_assistance":
            return self._debug_code(parameters.get("code", ""), parameters.get("error", ""), parameters.get("language", ""))
        elif tool_name == "cli_command":
            return self._suggest_cli_command(parameters.get("task", ""), parameters.get("os", "linux"))
        
        return {"error": f"Tool implementation for '{tool_name}' not found"}
    
    def _analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code structure and provide insights."""
        if not code:
            return {"error": "No code provided"}
        
        lines = code.split("\n")
        line_count = len(lines)
        
        return {
            "analysis": {
                "language": language,
                "line_count": line_count,
                "complexity_estimate": "medium" if line_count > 50 else "low",
                "suggestions": [
                    "Consider adding more comments" if line_count > 20 else "Code length looks reasonable"
                ]
            }
        }
    
    def _debug_code(self, code: str, error: str, language: str) -> Dict[str, Any]:
        """Help debug code issues."""
        if not code:
            return {"error": "No code provided"}
        
        suggestions = ["Check for typos", "Verify all variables are defined before use", 
                      "Ensure proper syntax for the language"]
        
        return {
            "debug_suggestions": {
                "error_type": error[:50] if error else "Unknown",
                "suggestions": suggestions,
                "general_advice": "Use console.log() or print() statements to trace variable values"
            }
        }
    
    def _suggest_cli_command(self, task: str, os: str) -> Dict[str, Any]:
        """Suggest CLI commands for specific tasks."""
        if not task:
            return {"error": "No task provided"}
        
        # Basic command suggestions
        commands = [
            {"category": "file", "command": "ls -la" if os != "windows" else "dir", 
             "description": "List files with details"},
            {"category": "search", "command": "grep -r 'pattern' ." if os != "windows" else "findstr /s /i 'pattern' *.*", 
             "description": "Search for text in files"}
        ]
        
        return {
            "cli_suggestions": {
                "os": os,
                "task": task,
                "commands": commands
            }
        }
    
    def _generate_context(self, query: str) -> List[Dict[str, Any]]:
        """Generate context information based on the query."""
        context_items = []
        
        # Add programming language specific context if detected
        languages = ["python", "javascript", "java", "c++", "ruby", "php"]
        for lang in languages:
            if lang.lower() in query.lower():
                context_items.append({
                    "type": "language_context",
                    "language": lang,
                    "focus": "code"
                })
                break
        
        # Add general coding context
        context_items.append({
            "type": "specialty_context",
            "specialty": "coding",
            "description": "This MCP server specializes in coding, CLI operations, and debugging."
        })
        
        return context_items

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    pass

def run_server():
    """Run the MCP server."""
    server_address = ('', PORT)
    httpd = ThreadedHTTPServer(server_address, MCPHandler)
    logger.info(f"Starting {SERVER_NAME} on port {PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
