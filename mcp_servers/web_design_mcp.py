#!/usr/bin/env python3
"""
SoulCoreHub Web Design MCP Server
--------------------------------
This MCP server specializes in web design, HTML, CSS, JavaScript, and UI/UX frameworks.
"""

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WebDesignMCP")

# Constants
PORT = 8702
SERVER_NAME = "web_design_mcp"
SPECIALTIES = ["HTML", "CSS", "JavaScript", "UI/UX", "web design", "frontend", "frameworks"]
TOOLS = {
    "html_template": {
        "description": "Generates HTML templates for specific components",
        "parameters": {
            "component_type": "Type of component (form, navbar, card, etc.)",
            "style": "Design style (minimal, modern, etc.)"
        }
    },
    "css_styling": {
        "description": "Provides CSS styling for HTML elements",
        "parameters": {
            "element": "HTML element to style",
            "style_type": "Type of styling (responsive, animation, etc.)"
        }
    },
    "framework_suggestion": {
        "description": "Suggests frameworks for specific web development needs",
        "parameters": {
            "requirements": "Project requirements",
            "complexity": "Project complexity (simple, medium, complex)"
        }
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
        
        if tool_name == "html_template":
            return self._generate_html_template(
                parameters.get("component_type", ""),
                parameters.get("style", "minimal")
            )
        
        elif tool_name == "css_styling":
            return self._generate_css_styling(
                parameters.get("element", ""),
                parameters.get("style_type", "basic")
            )
        
        elif tool_name == "framework_suggestion":
            return self._suggest_framework(
                parameters.get("requirements", ""),
                parameters.get("complexity", "medium")
            )
        
        return {"error": f"Tool implementation for '{tool_name}' not found"}
    
    def _generate_html_template(self, component_type: str, style: str) -> Dict[str, Any]:
        """Generate HTML template for a specific component."""
        if not component_type:
            return {"error": "No component type provided"}
        
        html_templates = {
            "form": """
<form class="form-{style}">
  <div class="form-group">
    <label for="name">Name</label>
    <input type="text" id="name" name="name" class="form-control" required>
  </div>
  <div class="form-group">
    <label for="email">Email</label>
    <input type="email" id="email" name="email" class="form-control" required>
  </div>
  <button type="submit" class="btn btn-primary">Submit</button>
</form>
""",
            "navbar": """
<nav class="navbar navbar-{style}">
  <div class="container">
    <a class="navbar-brand" href="#">Brand</a>
    <ul class="navbar-nav">
      <li class="nav-item"><a class="nav-link" href="#">Home</a></li>
      <li class="nav-item"><a class="nav-link" href="#">About</a></li>
      <li class="nav-item"><a class="nav-link" href="#">Services</a></li>
      <li class="nav-item"><a class="nav-link" href="#">Contact</a></li>
    </ul>
  </div>
</nav>
""",
            "card": """
<div class="card card-{style}">
  <img src="image.jpg" class="card-img-top" alt="...">
  <div class="card-body">
    <h5 class="card-title">Card title</h5>
    <p class="card-text">Some quick example text to build on the card title and make up the bulk of the card's content.</p>
    <a href="#" class="btn btn-primary">Go somewhere</a>
  </div>
</div>
"""
        }
        
        if component_type.lower() not in html_templates:
            return {
                "error": f"Component type '{component_type}' not found",
                "available_components": list(html_templates.keys())
            }
        
        template = html_templates[component_type.lower()].replace("{style}", style.lower())
        
        return {
            "html_template": {
                "component_type": component_type,
                "style": style,
                "template": template
            }
        }
    
    def _generate_css_styling(self, element: str, style_type: str) -> Dict[str, Any]:
        """Generate CSS styling for HTML elements."""
        if not element:
            return {"error": "No element provided"}
        
        css_styles = {
            "button": {
                "basic": """
.btn {
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  background-color: #007bff;
  color: white;
  cursor: pointer;
}
.btn:hover {
  background-color: #0069d9;
}
""",
                "responsive": """
.btn {
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  background-color: #007bff;
  color: white;
  cursor: pointer;
}
.btn:hover {
  background-color: #0069d9;
}
@media (max-width: 768px) {
  .btn {
    padding: 8px 12px;
    font-size: 0.9em;
  }
}
""",
                "animation": """
.btn {
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}
.btn:hover {
  background-color: #0069d9;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
"""
            },
            "card": {
                "basic": """
.card {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.card-img-top {
  width: 100%;
  height: auto;
}
.card-body {
  padding: 15px;
}
.card-title {
  margin-bottom: 10px;
  font-size: 1.25rem;
}
.card-text {
  color: #6c757d;
}
""",
                "responsive": """
.card {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.card-img-top {
  width: 100%;
  height: auto;
}
.card-body {
  padding: 15px;
}
.card-title {
  margin-bottom: 10px;
  font-size: 1.25rem;
}
.card-text {
  color: #6c757d;
}
@media (max-width: 768px) {
  .card {
    margin-bottom: 15px;
  }
  .card-body {
    padding: 10px;
  }
  .card-title {
    font-size: 1.1rem;
  }
}
"""
            }
        }
        
        if element.lower() not in css_styles:
            return {
                "error": f"Element '{element}' not found",
                "available_elements": list(css_styles.keys())
            }
        
        if style_type.lower() not in css_styles[element.lower()]:
            return {
                "error": f"Style type '{style_type}' not found for element '{element}'",
                "available_styles": list(css_styles[element.lower()].keys())
            }
        
        css = css_styles[element.lower()][style_type.lower()]
        
        return {
            "css_styling": {
                "element": element,
                "style_type": style_type,
                "css": css
            }
        }
    
    def _suggest_framework(self, requirements: str, complexity: str) -> Dict[str, Any]:
        """Suggest frameworks for specific web development needs."""
        if not requirements:
            return {"error": "No requirements provided"}
        
        requirements_lower = requirements.lower()
        suggestions = []
        
        # Frontend frameworks
        if "frontend" in requirements_lower or "ui" in requirements_lower:
            if complexity.lower() == "simple":
                suggestions.append({
                    "name": "Bootstrap",
                    "type": "CSS Framework",
                    "description": "Quick and easy UI components with minimal JavaScript requirements"
                })
            elif complexity.lower() == "medium":
                suggestions.append({
                    "name": "Vue.js",
                    "type": "JavaScript Framework",
                    "description": "Progressive framework for building UIs with a gentle learning curve"
                })
            else:  # complex
                suggestions.append({
                    "name": "React",
                    "type": "JavaScript Library",
                    "description": "Powerful library for building complex, state-driven user interfaces"
                })
        
        # Backend frameworks
        if "backend" in requirements_lower or "server" in requirements_lower:
            if "python" in requirements_lower:
                suggestions.append({
                    "name": "Flask" if complexity.lower() == "simple" else "Django",
                    "type": "Python Framework",
                    "description": "Lightweight microframework" if complexity.lower() == "simple" else "Full-featured framework with admin panel"
                })
            elif "javascript" in requirements_lower or "node" in requirements_lower:
                suggestions.append({
                    "name": "Express.js",
                    "type": "Node.js Framework",
                    "description": "Fast, unopinionated, minimalist web framework for Node.js"
                })
        
        # If no specific matches, provide general suggestions
        if not suggestions:
            suggestions = [
                {
                    "name": "React",
                    "type": "JavaScript Library",
                    "description": "Popular library for building user interfaces"
                },
                {
                    "name": "Vue.js",
                    "type": "JavaScript Framework",
                    "description": "Progressive framework for building UIs"
                },
                {
                    "name": "Angular",
                    "type": "JavaScript Framework",
                    "description": "Platform for building mobile and desktop web applications"
                }
            ]
        
        return {
            "framework_suggestions": {
                "requirements": requirements,
                "complexity": complexity,
                "suggestions": suggestions
            }
        }
    
    def _generate_context(self, query: str) -> List[Dict[str, Any]]:
        """Generate context information based on the query."""
        context_items = []
        
        # Add web technology specific context if detected
        technologies = ["html", "css", "javascript", "react", "vue", "angular", "bootstrap"]
        for tech in technologies:
            if tech.lower() in query.lower():
                context_items.append({
                    "type": "technology_context",
                    "technology": tech,
                    "focus": "web_design"
                })
        
        # Add general web design context
        context_items.append({
            "type": "specialty_context",
            "specialty": "web_design",
            "description": "This MCP server specializes in web design, HTML, CSS, JavaScript, and UI/UX frameworks."
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
