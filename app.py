#!/usr/bin/env python3
"""
Flask API for SoulCoreHub RAG + MCP System
Provides endpoints for the Soul Command Center
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
import json
import os
import logging
from neural_routing import NeuralRouter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)
logger = logging.getLogger("soul_command_center_api")

app = Flask(__name__, static_folder='static')
router = NeuralRouter()

# MCP server status (initially all enabled)
mcp_status = {port: True for port in range(8701, 8708)}

@app.route('/')
def index():
    """Serve the Soul Command Center HTML"""
    return render_template('soul_command_center.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.route('/api/query', methods=['POST'])
def query():
    """Route a query through the Neural Router"""
    data = request.json
    query_text = data.get('query')
    force_port = data.get('force_port')
    
    if not query_text:
        return jsonify({"error": "No query provided"}), 400
    
    # Convert force_port to int if it's not None
    if force_port is not None:
        try:
            force_port = int(force_port)
        except ValueError:
            return jsonify({"error": "Invalid port number"}), 400
    
    # Check if the forced port is disabled
    if force_port is not None and not mcp_status.get(force_port, False):
        return jsonify({"error": f"MCP server on port {force_port} is disabled"}), 400
    
    # Route the query
    try:
        result = router.route_query(query_text, force_port)
        
        # Check if the selected port is disabled
        selected_port = result.get("metadata", {}).get("port")
        if selected_port is not None and not mcp_status.get(selected_port, False):
            return jsonify({"error": f"MCP server on port {selected_port} is disabled"}), 400
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error routing query: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/toggle_mcp', methods=['POST'])
def toggle_mcp():
    """Toggle an MCP server on or off"""
    data = request.json
    port = data.get('port')
    
    try:
        port = int(port)
        if port not in range(8701, 8708):
            return jsonify({"error": "Invalid port number"}), 400
        
        # Toggle the status
        mcp_status[port] = not mcp_status[port]
        
        return jsonify({"port": port, "enabled": mcp_status[port]})
    except ValueError:
        return jsonify({"error": "Invalid port number"}), 400
    except Exception as e:
        logger.error(f"Error toggling MCP server: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/mcp_status', methods=['GET'])
def get_mcp_status():
    """Get the status of all MCP servers"""
    return jsonify(mcp_status)

@app.route('/api/feedback', methods=['POST'])
def add_feedback():
    """Add feedback for a routing decision"""
    data = request.json
    query = data.get('query')
    port = data.get('port')
    feedback_type = data.get('feedback')
    
    if not query or not port or not feedback_type:
        return jsonify({"error": "Missing required parameters"}), 400
    
    try:
        port = int(port)
        success = router.add_feedback(query, port, feedback_type)
        
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Failed to add feedback"}), 400
    except ValueError:
        return jsonify({"error": "Invalid port number"}), 400
    except Exception as e:
        logger.error(f"Error adding feedback: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/memory', methods=['GET'])
def get_memory():
    """Get the MCP memory log"""
    try:
        with open('mcp_memory.json', 'r') as f:
            memory = json.load(f)
        return jsonify(memory)
    except FileNotFoundError:
        return jsonify([])
    except Exception as e:
        logger.error(f"Error loading memory: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/feedback_data', methods=['GET'])
def get_feedback_data():
    """Get the routing feedback data"""
    try:
        with open('routing_feedback.json', 'r') as f:
            feedback = json.load(f)
        return jsonify(feedback)
    except FileNotFoundError:
        return jsonify([])
    except Exception as e:
        logger.error(f"Error loading feedback data: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Create empty files if they don't exist
    if not os.path.exists('mcp_memory.json'):
        with open('mcp_memory.json', 'w') as f:
            json.dump([], f)
    
    if not os.path.exists('routing_feedback.json'):
        with open('routing_feedback.json', 'w') as f:
            json.dump([], f)
    
    app.run(debug=True, port=5000)
