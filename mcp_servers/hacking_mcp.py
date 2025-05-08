#!/usr/bin/env python3
"""
SoulCoreHub Hacking MCP Server
-----------------------------
This MCP server specializes in ethical hacking, security, and penetration testing.
"""

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("HackingMCP")

# Constants
PORT = 8705
SERVER_NAME = "hacking_mcp"
SPECIALTIES = ["ethical hacking", "security", "penetration testing", "vulnerability assessment"]
TOOLS = {
    "security_assessment": {
        "description": "Assesses security risks and provides recommendations",
        "parameters": {
            "system_type": "Type of system to assess (web, network, application)",
            "details": "Specific details about the system"
        }
    },
    "vulnerability_analysis": {
        "description": "Analyzes potential vulnerabilities in code or systems",
        "parameters": {
            "code_or_system": "Code snippet or system description",
            "language_or_platform": "Programming language or platform"
        }
    },
    "security_best_practices": {
        "description": "Provides security best practices for specific contexts",
        "parameters": {
            "context": "Context for security recommendations",
            "level": "Security level (basic, intermediate, advanced)"
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
        
        if tool_name == "security_assessment":
            return self._assess_security(
                parameters.get("system_type", ""),
                parameters.get("details", "")
            )
        
        elif tool_name == "vulnerability_analysis":
            return self._analyze_vulnerability(
                parameters.get("code_or_system", ""),
                parameters.get("language_or_platform", "")
            )
        
        elif tool_name == "security_best_practices":
            return self._provide_best_practices(
                parameters.get("context", ""),
                parameters.get("level", "intermediate")
            )
        
        return {"error": f"Tool implementation for '{tool_name}' not found"}
    
    def _assess_security(self, system_type: str, details: str) -> Dict[str, Any]:
        """Assess security risks and provide recommendations."""
        if not system_type:
            return {"error": "No system type provided"}
        
        if not details:
            return {"error": "No system details provided"}
        
        # Common security risks by system type
        risks = {
            "web": [
                {"name": "Cross-Site Scripting (XSS)", "severity": "High", 
                 "description": "Attackers can inject malicious scripts that execute in users' browsers"},
                {"name": "SQL Injection", "severity": "Critical", 
                 "description": "Attackers can execute arbitrary SQL commands on your database"},
                {"name": "Cross-Site Request Forgery (CSRF)", "severity": "Medium", 
                 "description": "Attackers can trick users into performing unwanted actions"},
                {"name": "Insecure Direct Object References", "severity": "High", 
                 "description": "Attackers can access unauthorized resources by manipulating references"}
            ],
            "network": [
                {"name": "Open Ports", "severity": "Medium", 
                 "description": "Unnecessary open ports increase attack surface"},
                {"name": "Weak Encryption", "severity": "High", 
                 "description": "Data in transit may be intercepted or modified"},
                {"name": "Default Credentials", "severity": "Critical", 
                 "description": "Default or weak credentials on network devices"},
                {"name": "Man-in-the-Middle", "severity": "High", 
                 "description": "Attackers can intercept and potentially alter communications"}
            ],
            "application": [
                {"name": "Insecure Authentication", "severity": "High", 
                 "description": "Weak authentication mechanisms can be bypassed"},
                {"name": "Sensitive Data Exposure", "severity": "Critical", 
                 "description": "Sensitive data is not properly protected"},
                {"name": "Broken Access Control", "severity": "High", 
                 "description": "Users can perform actions they shouldn't be authorized to perform"},
                {"name": "Security Misconfiguration", "severity": "Medium", 
                 "description": "Improper security configuration exposes vulnerabilities"}
            ]
        }
        
        # Recommendations by system type
        recommendations = {
            "web": [
                "Implement Content Security Policy (CSP) to prevent XSS",
                "Use parameterized queries to prevent SQL injection",
                "Implement CSRF tokens for all state-changing operations",
                "Validate all user inputs on both client and server sides",
                "Use HTTPS for all communications",
                "Implement proper session management"
            ],
            "network": [
                "Close unnecessary ports and services",
                "Use strong encryption protocols (TLS 1.2+)",
                "Change default credentials and use strong passwords",
                "Implement network segmentation",
                "Use intrusion detection/prevention systems",
                "Regularly update and patch network devices"
            ],
            "application": [
                "Implement multi-factor authentication",
                "Encrypt sensitive data at rest and in transit",
                "Implement proper access control mechanisms",
                "Follow the principle of least privilege",
                "Regularly update dependencies and libraries",
                "Implement proper error handling that doesn't leak sensitive information"
            ]
        }
        
        # Select relevant risks and recommendations
        system_type_lower = system_type.lower()
        if system_type_lower not in risks:
            system_type_lower = "application"  # Default
        
        selected_risks = risks[system_type_lower]
        selected_recommendations = recommendations[system_type_lower]
        
        # Generate assessment
        assessment = {
            "system_type": system_type,
            "risks": selected_risks,
            "recommendations": selected_recommendations,
            "overall_risk_level": "High" if any(risk["severity"] == "Critical" for risk in selected_risks) else "Medium"
        }
        
        return {
            "security_assessment": assessment
        }
    
    def _analyze_vulnerability(self, code_or_system: str, language_or_platform: str) -> Dict[str, Any]:
        """Analyze potential vulnerabilities in code or systems."""
        if not code_or_system:
            return {"error": "No code or system description provided"}
        
        # Common vulnerabilities by language/platform
        vulnerabilities = {
            "python": [
                {"pattern": "eval(", "name": "Code Injection", "severity": "Critical", 
                 "description": "The eval() function can execute arbitrary code"},
                {"pattern": "exec(", "name": "Code Injection", "severity": "Critical", 
                 "description": "The exec() function can execute arbitrary code"},
                {"pattern": "os.system(", "name": "Command Injection", "severity": "Critical", 
                 "description": "Unsanitized input to os.system() can lead to command injection"},
                {"pattern": "pickle.loads(", "name": "Deserialization Vulnerability", "severity": "High", 
                 "description": "Unpickling untrusted data can lead to code execution"}
            ],
            "javascript": [
                {"pattern": "eval(", "name": "Code Injection", "severity": "Critical", 
                 "description": "The eval() function can execute arbitrary code"},
                {"pattern": "innerHTML", "name": "Cross-Site Scripting (XSS)", "severity": "High", 
                 "description": "Using innerHTML with unsanitized input can lead to XSS"},
                {"pattern": "document.write(", "name": "Cross-Site Scripting (XSS)", "severity": "High", 
                 "description": "document.write() with unsanitized input can lead to XSS"},
                {"pattern": "localStorage", "name": "Sensitive Data Exposure", "severity": "Medium", 
                 "description": "Storing sensitive data in localStorage is insecure"}
            ],
            "php": [
                {"pattern": "eval(", "name": "Code Injection", "severity": "Critical", 
                 "description": "The eval() function can execute arbitrary code"},
                {"pattern": "mysql_query(", "name": "SQL Injection", "severity": "Critical", 
                 "description": "Using mysql_query() without prepared statements can lead to SQL injection"},
                {"pattern": "include(", "name": "File Inclusion Vulnerability", "severity": "High", 
                 "description": "Including user-controlled files can lead to code execution"},
                {"pattern": "$_GET", "name": "Unsanitized Input", "severity": "Medium", 
                 "description": "Using $_GET without proper sanitization can lead to various vulnerabilities"}
            ],
            "web": [
                {"pattern": "password", "name": "Sensitive Data Exposure", "severity": "High", 
                 "description": "Passwords should be properly hashed and salted"},
                {"pattern": "token", "name": "Insecure Authentication", "severity": "Medium", 
                 "description": "Authentication tokens should be properly secured"},
                {"pattern": "admin", "name": "Access Control", "severity": "Medium", 
                 "description": "Admin functionality should be properly protected"},
                {"pattern": "api", "name": "API Security", "severity": "Medium", 
                 "description": "APIs should be properly secured with authentication and authorization"}
            ]
        }
        
        # Default to web if language/platform not specified or not recognized
        language_or_platform_lower = language_or_platform.lower() if language_or_platform else "web"
        if language_or_platform_lower not in vulnerabilities:
            language_or_platform_lower = "web"
        
        # Check for vulnerabilities
        found_vulnerabilities = []
        code_or_system_lower = code_or_system.lower()
        
        for vuln in vulnerabilities[language_or_platform_lower]:
            if vuln["pattern"].lower() in code_or_system_lower:
                found_vulnerabilities.append(vuln)
        
        # Add general recommendations
        recommendations = [
            "Validate and sanitize all user inputs",
            "Follow the principle of least privilege",
            "Keep all dependencies and libraries updated",
            "Implement proper error handling",
            "Use secure coding practices specific to your language/platform"
        ]
        
        # Add language/platform specific recommendations
        if language_or_platform_lower == "python":
            recommendations.extend([
                "Use subprocess.run() with shell=False instead of os.system()",
                "Avoid using eval() and exec() with untrusted input",
                "Use parameterized queries for database operations",
                "Consider using a security linter like bandit"
            ])
        elif language_or_platform_lower == "javascript":
            recommendations.extend([
                "Use textContent instead of innerHTML when possible",
                "Implement Content Security Policy (CSP)",
                "Use secure alternatives to localStorage for sensitive data",
                "Consider using a security linter like ESLint with security plugins"
            ])
        elif language_or_platform_lower == "php":
            recommendations.extend([
                "Use prepared statements for all database queries",
                "Set proper PHP configuration options for security",
                "Use modern PHP frameworks with built-in security features",
                "Consider using a security scanner like RIPS"
            ])
        
        # Generate analysis
        analysis = {
            "language_or_platform": language_or_platform,
            "vulnerabilities_found": len(found_vulnerabilities),
            "vulnerabilities": found_vulnerabilities,
            "recommendations": recommendations,
            "overall_risk_level": "Critical" if any(v["severity"] == "Critical" for v in found_vulnerabilities) else 
                                "High" if any(v["severity"] == "High" for v in found_vulnerabilities) else "Medium"
        }
        
        return {
            "vulnerability_analysis": analysis
        }
    
    def _provide_best_practices(self, context: str, level: str) -> Dict[str, Any]:
        """Provide security best practices for specific contexts."""
        if not context:
            return {"error": "No context provided"}
        
        # Security best practices by context and level
        best_practices = {
            "authentication": {
                "basic": [
                    "Use strong passwords with minimum length requirements",
                    "Implement account lockout after multiple failed attempts",
                    "Use HTTPS for all authentication requests"
                ],
                "intermediate": [
                    "Implement multi-factor authentication",
                    "Use secure password hashing algorithms (bcrypt, Argon2)",
                    "Implement proper session management",
                    "Use secure cookie attributes (HttpOnly, Secure, SameSite)"
                ],
                "advanced": [
                    "Implement risk-based authentication",
                    "Use hardware security keys or biometric authentication",
                    "Implement OAuth 2.0 or OpenID Connect for federated authentication",
                    "Implement certificate-based authentication for sensitive systems"
                ]
            },
            "data_protection": {
                "basic": [
                    "Encrypt sensitive data at rest",
                    "Use HTTPS for all data transmission",
                    "Implement proper access controls"
                ],
                "intermediate": [
                    "Implement data classification and handling policies",
                    "Use strong encryption algorithms and proper key management",
                    "Implement data masking for sensitive information",
                    "Regularly backup data and test restoration procedures"
                ],
                "advanced": [
                    "Implement end-to-end encryption",
                    "Use hardware security modules (HSMs) for key management",
                    "Implement data loss prevention (DLP) solutions",
                    "Use homomorphic encryption for processing sensitive data"
                ]
            },
            "web_security": {
                "basic": [
                    "Use HTTPS for all web traffic",
                    "Implement input validation",
                    "Keep software and dependencies updated",
                    "Use secure HTTP headers"
                ],
                "intermediate": [
                    "Implement Content Security Policy (CSP)",
                    "Use parameterized queries to prevent SQL injection",
                    "Implement proper CORS configuration",
                    "Use security headers like X-XSS-Protection, X-Content-Type-Options"
                ],
                "advanced": [
                    "Implement subresource integrity (SRI) for external resources",
                    "Use HTTP Strict Transport Security (HSTS)",
                    "Implement rate limiting and brute force protection",
                    "Use web application firewalls (WAFs)"
                ]
            },
            "network_security": {
                "basic": [
                    "Use firewalls to restrict traffic",
                    "Change default credentials on all devices",
                    "Disable unnecessary services and ports",
                    "Keep firmware and software updated"
                ],
                "intermediate": [
                    "Implement network segmentation",
                    "Use intrusion detection/prevention systems",
                    "Implement proper logging and monitoring",
                    "Use VPNs for remote access"
                ],
                "advanced": [
                    "Implement zero trust network architecture",
                    "Use microsegmentation",
                    "Implement network behavior analysis",
                    "Use deception technology (honeypots, honeynets)"
                ]
            }
        }
        
        # Determine context category
        context_lower = context.lower()
        context_category = None
        
        if any(word in context_lower for word in ["password", "login", "user", "account", "auth"]):
            context_category = "authentication"
        elif any(word in context_lower for word in ["data", "information", "storage", "database", "encrypt"]):
            context_category = "data_protection"
        elif any(word in context_lower for word in ["web", "site", "application", "api", "http"]):
            context_category = "web_security"
        elif any(word in context_lower for word in ["network", "firewall", "router", "traffic", "packet"]):
            context_category = "network_security"
        else:
            # Default to web security if context is unclear
            context_category = "web_security"
        
        # Determine security level
        level_lower = level.lower()
        if level_lower not in ["basic", "intermediate", "advanced"]:
            level_lower = "intermediate"  # Default
        
        # Select practices based on context and level
        selected_practices = best_practices[context_category][level_lower]
        
        # Add general practices that apply to all contexts
        general_practices = {
            "basic": [
                "Follow the principle of least privilege",
                "Implement proper logging and monitoring",
                "Develop and test incident response procedures",
                "Provide security awareness training"
            ],
            "intermediate": [
                "Conduct regular security assessments",
                "Implement defense in depth strategies",
                "Develop and enforce security policies",
                "Perform regular security testing"
            ],
            "advanced": [
                "Implement continuous security monitoring",
                "Conduct regular penetration testing",
                "Implement threat hunting capabilities",
                "Develop a comprehensive security program aligned with frameworks like NIST or ISO 27001"
            ]
        }
        
        selected_practices.extend(general_practices[level_lower])
        
        # Generate best practices response
        practices = {
            "context": context,
            "context_category": context_category,
            "security_level": level_lower,
            "best_practices": selected_practices,
            "resources": [
                "OWASP Top 10 (https://owasp.org/www-project-top-ten/)",
                "NIST Cybersecurity Framework (https://www.nist.gov/cyberframework)",
                "CIS Controls (https://www.cisecurity.org/controls/)"
            ]
        }
        
        return {
            "security_best_practices": practices
        }
    
    def _generate_context(self, query: str) -> List[Dict[str, Any]]:
        """Generate context information based on the query."""
        context_items = []
        
        # Add security domain specific context if detected
        domains = ["security", "hack", "vulnerability", "exploit", "penetration", "testing", "firewall", "encryption"]
        for domain in domains:
            if domain.lower() in query.lower():
                context_items.append({
                    "type": "domain_context",
                    "domain": domain,
                    "focus": "security"
                })
        
        # Add general security context
        context_items.append({
            "type": "specialty_context",
            "specialty": "security",
            "description": "This MCP server specializes in ethical hacking, security, and penetration testing."
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
