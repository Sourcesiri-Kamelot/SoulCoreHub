import requests
from typing import Dict, Any, Optional, Union
from urllib.parse import urlparse

from .registry import StatelessTool, register_tool


@register_tool("api_call")
class ApiCallTool(StatelessTool):
    """Tool for making HTTP API calls."""
    
    def __init__(self):
        self.name = "api_call"
        self.description = "Make HTTP requests to external APIs"
        self.parameters = {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to make the request to"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                    "description": "HTTP method to use for the request"
                },
                "headers": {
                    "type": "object",
                    "description": "HTTP headers to include in the request"
                },
                "params": {
                    "type": "object",
                    "description": "URL parameters for the request"
                },
                "data": {
                    "type": "object",
                    "description": "Data to send in the request body (for POST, PUT, PATCH)"
                },
                "json_data": {
                    "type": "object",
                    "description": "JSON data to send in the request body (for POST, PUT, PATCH)"
                },
                "timeout": {
                    "type": "number",
                    "description": "Request timeout in seconds"
                }
            },
            "required": ["url", "method"]
        }
        
    def __call__(
        self, 
        url: str, 
        method: str = "GET", 
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: float = 10.0
    ) -> Dict[str, Any]:
        """Make an HTTP request to the specified URL."""
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return {"error": f"Invalid URL '{url}'"}
            
            # Prepare request
            method = method.upper()
            if method not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                return {"error": f"Unsupported HTTP method '{method}'"}
            
            # Make request
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                timeout=timeout
            )
            
            # Try to parse response as JSON
            try:
                json_result = response.json()
                response_data = json_result
            except ValueError:
                # Not JSON, return text
                response_data = response.text
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response_data
            }
        except requests.exceptions.RequestException as e:
            return {"error": f"Error making API request: {str(e)}"}
        except Exception as e:
            return {"error": f"Error: {str(e)}"}
    
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