#!/usr/bin/env python3
"""
SoulCoreHub Logic Core MCP Server
--------------------------------
This MCP server specializes in logical deduction, mathematics, and clean reasoning.
"""

import json
import logging
import math
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LogicCoreMCP")

# Constants
PORT = 8703
SERVER_NAME = "logic_core_mcp"
SPECIALTIES = ["logic", "mathematics", "reasoning", "problem solving", "algorithms", "decision making"]
TOOLS = {
    "logical_analysis": {
        "description": "Analyzes logical statements and arguments",
        "parameters": {
            "statements": "Logical statements to analyze",
            "format": "Output format (simple, detailed)"
        }
    },
    "math_solver": {
        "description": "Solves mathematical problems",
        "parameters": {
            "problem": "Mathematical problem to solve",
            "show_steps": "Whether to show solution steps (true/false)"
        }
    },
    "decision_tree": {
        "description": "Creates a decision tree for a given problem",
        "parameters": {
            "problem": "Problem description",
            "options": "Available options or choices",
            "criteria": "Decision criteria"
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
        
        if tool_name == "logical_analysis":
            return self._analyze_logic(
                parameters.get("statements", ""),
                parameters.get("format", "simple")
            )
        
        elif tool_name == "math_solver":
            return self._solve_math(
                parameters.get("problem", ""),
                parameters.get("show_steps", True)
            )
        
        elif tool_name == "decision_tree":
            return self._create_decision_tree(
                parameters.get("problem", ""),
                parameters.get("options", []),
                parameters.get("criteria", [])
            )
        
        return {"error": f"Tool implementation for '{tool_name}' not found"}
    
    def _analyze_logic(self, statements: str, format: str) -> Dict[str, Any]:
        """Analyze logical statements and arguments."""
        if not statements:
            return {"error": "No statements provided"}
        
        # Split statements by line or semicolon
        statement_list = [s.strip() for s in statements.replace(';', '\n').split('\n') if s.strip()]
        
        # Basic analysis
        analysis = {
            "statements": statement_list,
            "statement_count": len(statement_list),
            "logical_operators": []
        }
        
        # Identify logical operators
        operators = ["if", "then", "and", "or", "not", "all", "some", "none"]
        for statement in statement_list:
            statement_lower = statement.lower()
            found_operators = [op for op in operators if f" {op} " in f" {statement_lower} "]
            if found_operators:
                analysis["logical_operators"].extend(found_operators)
        
        analysis["logical_operators"] = list(set(analysis["logical_operators"]))
        
        # Detailed analysis if requested
        if format.lower() == "detailed":
            analysis["structure"] = []
            
            for statement in statement_list:
                statement_lower = statement.lower()
                
                # Check for conditional statements
                if "if" in statement_lower and "then" in statement_lower:
                    parts = statement_lower.split("then", 1)
                    condition = parts[0].replace("if", "", 1).strip()
                    consequence = parts[1].strip()
                    analysis["structure"].append({
                        "type": "conditional",
                        "condition": condition,
                        "consequence": consequence
                    })
                
                # Check for universal statements
                elif "all" in statement_lower:
                    analysis["structure"].append({
                        "type": "universal",
                        "statement": statement
                    })
                
                # Check for existential statements
                elif "some" in statement_lower:
                    analysis["structure"].append({
                        "type": "existential",
                        "statement": statement
                    })
                
                # Default case
                else:
                    analysis["structure"].append({
                        "type": "simple",
                        "statement": statement
                    })
        
        return {
            "logical_analysis": analysis
        }
    
    def _solve_math(self, problem: str, show_steps: bool) -> Dict[str, Any]:
        """Solve mathematical problems."""
        if not problem:
            return {"error": "No problem provided"}
        
        problem_lower = problem.lower()
        result = {"problem": problem}
        
        # Very basic equation solver
        if "=" in problem and "x" in problem_lower:
            try:
                # Handle simple linear equations like "2x + 3 = 7"
                left, right = problem.split("=", 1)
                left = left.strip()
                right = right.strip()
                
                # Extract coefficient and constant from left side
                if "x" in left:
                    parts = left.split("x", 1)
                    coefficient = parts[0].strip()
                    if not coefficient:
                        coefficient = "1"
                    elif coefficient == "-":
                        coefficient = "-1"
                    
                    coefficient = float(coefficient)
                    
                    constant = 0
                    if "+" in parts[1]:
                        constant = float(parts[1].split("+", 1)[1].strip())
                    elif "-" in parts[1]:
                        constant = -float(parts[1].split("-", 1)[1].strip())
                    
                    # Solve for x
                    right_val = float(right)
                    x_val = (right_val - constant) / coefficient
                    
                    steps = []
                    if show_steps:
                        steps = [
                            f"Original equation: {problem}",
                            f"Subtract {constant} from both sides: {coefficient}x = {right_val - constant}",
                            f"Divide both sides by {coefficient}: x = {x_val}"
                        ]
                    
                    result["solution"] = x_val
                    result["steps"] = steps
                    
                    return {"math_solution": result}
            except Exception as e:
                return {"error": f"Could not solve equation: {str(e)}"}
        
        # Basic arithmetic
        try:
            # Replace common math terms
            problem_eval = problem_lower.replace("^", "**")
            problem_eval = problem_eval.replace("sqrt", "math.sqrt")
            problem_eval = problem_eval.replace("pi", "math.pi")
            problem_eval = problem_eval.replace("sin", "math.sin")
            problem_eval = problem_eval.replace("cos", "math.cos")
            problem_eval = problem_eval.replace("tan", "math.tan")
            problem_eval = problem_eval.replace("log", "math.log10")
            problem_eval = problem_eval.replace("ln", "math.log")
            
            # Safely evaluate the expression
            solution = eval(problem_eval, {"__builtins__": None}, {"math": math})
            
            result["solution"] = solution
            if show_steps:
                result["steps"] = [f"Evaluated expression: {problem} = {solution}"]
            
            return {"math_solution": result}
        except Exception as e:
            return {"error": f"Could not evaluate expression: {str(e)}"}
    
    def _create_decision_tree(self, problem: str, options: List[str], criteria: List[str]) -> Dict[str, Any]:
        """Create a decision tree for a given problem."""
        if not problem:
            return {"error": "No problem provided"}
        
        if not options:
            return {"error": "No options provided"}
        
        if not criteria:
            return {"error": "No criteria provided"}
        
        # Create a simple decision tree
        tree = {
            "problem": problem,
            "nodes": []
        }
        
        # Create root node
        root_node = {
            "id": "root",
            "type": "problem",
            "content": problem,
            "children": []
        }
        
        # Add criteria nodes
        for i, criterion in enumerate(criteria):
            criterion_id = f"criterion_{i}"
            criterion_node = {
                "id": criterion_id,
                "type": "criterion",
                "content": criterion,
                "children": []
            }
            
            # Add option nodes for each criterion
            for j, option in enumerate(options):
                option_id = f"option_{i}_{j}"
                option_node = {
                    "id": option_id,
                    "type": "option",
                    "content": option,
                    "evaluation": f"Evaluation of {option} based on {criterion}"
                }
                criterion_node["children"].append(option_node)
            
            root_node["children"].append(criterion_node)
        
        tree["nodes"].append(root_node)
        
        # Add a simple recommendation
        recommendation = options[0]  # Just a placeholder
        tree["recommendation"] = {
            "option": recommendation,
            "reasoning": f"Based on the criteria, {recommendation} appears to be the best option."
        }
        
        return {
            "decision_tree": tree
        }
    
    def _generate_context(self, query: str) -> List[Dict[str, Any]]:
        """Generate context information based on the query."""
        context_items = []
        
        # Add math/logic specific context if detected
        topics = ["math", "logic", "equation", "problem", "algorithm", "reasoning"]
        for topic in topics:
            if topic.lower() in query.lower():
                context_items.append({
                    "type": "topic_context",
                    "topic": topic,
                    "focus": "logic_core"
                })
        
        # Add general logic context
        context_items.append({
            "type": "specialty_context",
            "specialty": "logic_core",
            "description": "This MCP server specializes in logical deduction, mathematics, and clean reasoning."
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
