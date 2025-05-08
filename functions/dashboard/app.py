import json
import os
import sys
import boto3
import logging
import base64
from datetime import datetime

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Get environment variables
MEMORY_BUCKET = os.environ.get('MEMORY_BUCKET')

# Add the project root to the Python path for imports
sys.path.append('/var/task')

def lambda_handler(event, context):
    """
    SoulCore Dashboard Lambda handler - serves the public GUI
    
    This Lambda function serves the SoulCore dashboard HTML, CSS, and JavaScript,
    as well as handling API requests for dashboard data.
    """
    try:
        # Get the path from the event
        path = event.get('path', '/')
        http_method = event.get('httpMethod', 'GET')
        
        # Log the request
        logger.info(f"Received dashboard request: {http_method} {path}")
        
        # Handle API requests
        if path.startswith('/api/'):
            return handle_api_request(path, event)
        
        # Serve static files
        if path == '/':
            # Serve the main dashboard HTML
            return serve_dashboard_html()
        elif path.endswith('.js'):
            # Serve JavaScript files
            return serve_static_file(path, 'application/javascript')
        elif path.endswith('.css'):
            # Serve CSS files
            return serve_static_file(path, 'text/css')
        elif path.endswith('.png') or path.endswith('.jpg') or path.endswith('.jpeg'):
            # Serve image files
            content_type = 'image/png' if path.endswith('.png') else 'image/jpeg'
            return serve_static_file(path, content_type)
        else:
            # For any other path, serve the main dashboard HTML (for SPA routing)
            return serve_dashboard_html()
    except Exception as e:
        logger.error(f"Error in Dashboard Lambda: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }

def handle_api_request(path, event):
    """Handle API requests for dashboard data"""
    try:
        # Parse the API path
        path_parts = path.split('/')
        if len(path_parts) < 3:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid API path'
                })
            }
        
        api_endpoint = path_parts[2]
        
        # Handle different API endpoints
        if api_endpoint == 'status':
            return get_agent_status()
        elif api_endpoint == 'memory':
            agent_id = path_parts[3] if len(path_parts) > 3 else None
            return get_agent_memory(agent_id)
        elif api_endpoint == 'conversations':
            agent_id = path_parts[3] if len(path_parts) > 3 else None
            return get_agent_conversations(agent_id)
        elif api_endpoint == 'resurrections':
            agent_id = path_parts[3] if len(path_parts) > 3 else None
            return get_agent_resurrections(agent_id)
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': f'Unknown API endpoint: {api_endpoint}'
                })
            }
    except Exception as e:
        logger.error(f"Error handling API request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }

def serve_dashboard_html():
    """Serve the main dashboard HTML"""
    try:
        # In a production environment, this would load the HTML from S3 or a local file
        # For this example, we'll generate a simple HTML page
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SoulCore Dashboard</title>
            <style>
                body {
                    font-family: 'Arial', sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #121212;
                    color: #e0e0e0;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                header {
                    background-color: #1e1e1e;
                    padding: 20px;
                    text-align: center;
                    border-bottom: 1px solid #333;
                }
                h1 {
                    margin: 0;
                    color: #bb86fc;
                }
                .agent-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    gap: 20px;
                    margin-top: 20px;
                }
                .agent-card {
                    background-color: #1e1e1e;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                .agent-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                }
                .agent-name {
                    font-size: 1.5rem;
                    color: #bb86fc;
                    margin: 0;
                }
                .agent-status {
                    padding: 5px 10px;
                    border-radius: 20px;
                    font-size: 0.8rem;
                    font-weight: bold;
                }
                .status-active {
                    background-color: #03dac6;
                    color: #000;
                }
                .status-inactive {
                    background-color: #cf6679;
                    color: #000;
                }
                .agent-role {
                    color: #bb86fc;
                    margin-bottom: 10px;
                }
                .agent-stats {
                    margin-top: 15px;
                }
                .stat-item {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 5px;
                }
                .actions {
                    margin-top: 15px;
                    display: flex;
                    gap: 10px;
                }
                button {
                    background-color: #bb86fc;
                    color: #000;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-weight: bold;
                }
                button:hover {
                    background-color: #a370f7;
                }
            </style>
        </head>
        <body>
            <header>
                <h1>🧠 SoulCoreHub Dashboard</h1>
                <p>Serverless AI Agent Management</p>
            </header>
            <div class="container">
                <div class="agent-grid" id="agentGrid">
                    <!-- Agent cards will be loaded here -->
                    <div class="agent-card">
                        <div class="agent-header">
                            <h2 class="agent-name">Loading...</h2>
                        </div>
                        <p>Loading agent data...</p>
                    </div>
                </div>
            </div>
            <script>
                // This script would normally be in a separate file
                document.addEventListener('DOMContentLoaded', function() {
                    fetchAgentStatus();
                });
                
                async function fetchAgentStatus() {
                    try {
                        const response = await fetch('/api/status');
                        const data = await response.json();
                        
                        if (data.agents) {
                            renderAgentCards(data.agents);
                        }
                    } catch (error) {
                        console.error('Error fetching agent status:', error);
                        document.getElementById('agentGrid').innerHTML = `
                            <div class="agent-card">
                                <div class="agent-header">
                                    <h2 class="agent-name">Error</h2>
                                </div>
                                <p>Failed to load agent data. Please try again later.</p>
                            </div>
                        `;
                    }
                }
                
                function renderAgentCards(agents) {
                    const agentGrid = document.getElementById('agentGrid');
                    agentGrid.innerHTML = '';
                    
                    agents.forEach(agent => {
                        const card = document.createElement('div');
                        card.className = 'agent-card';
                        
                        const statusClass = agent.status === 'active' ? 'status-active' : 'status-inactive';
                        
                        card.innerHTML = `
                            <div class="agent-header">
                                <h2 class="agent-name">${agent.name}</h2>
                                <span class="agent-status ${statusClass}">${agent.status}</span>
                            </div>
                            <div class="agent-role">${agent.role}</div>
                            <p>${agent.description}</p>
                            <div class="agent-stats">
                                <div class="stat-item">
                                    <span>Last Active:</span>
                                    <span>${formatDate(agent.lastActive)}</span>
                                </div>
                                <div class="stat-item">
                                    <span>Memory Size:</span>
                                    <span>${agent.memorySize} KB</span>
                                </div>
                                <div class="stat-item">
                                    <span>Resurrections:</span>
                                    <span>${agent.resurrections}</span>
                                </div>
                            </div>
                            <div class="actions">
                                <button onclick="resurrectAgent('${agent.id}')">Resurrect</button>
                                <button onclick="viewMemory('${agent.id}')">View Memory</button>
                            </div>
                        `;
                        
                        agentGrid.appendChild(card);
                    });
                }
                
                function formatDate(dateString) {
                    if (!dateString) return 'Never';
                    const date = new Date(dateString);
                    return date.toLocaleString();
                }
                
                async function resurrectAgent(agentId) {
                    try {
                        const response = await fetch('/api/resurrect', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                agent_id: agentId,
                                type: 'standard'
                            })
                        });
                        
                        const data = await response.json();
                        alert(`Resurrection result: ${data.result.message}`);
                        
                        // Refresh agent status
                        fetchAgentStatus();
                    } catch (error) {
                        console.error('Error resurrecting agent:', error);
                        alert('Failed to resurrect agent. Please try again.');
                    }
                }
                
                async function viewMemory(agentId) {
                    try {
                        const response = await fetch(`/api/memory/${agentId}`);
                        const data = await response.json();
                        
                        // In a real application, you would display this in a modal or dedicated page
                        alert(`Memory for ${agentId}:\n${JSON.stringify(data.memory_data, null, 2)}`);
                    } catch (error) {
                        console.error('Error viewing memory:', error);
                        alert('Failed to load agent memory. Please try again.');
                    }
                }
            </script>
        </body>
        </html>
        """
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Access-Control-Allow-Origin': '*'
            },
            'body': html
        }
    except Exception as e:
        logger.error(f"Error serving dashboard HTML: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'text/plain',
                'Access-Control-Allow-Origin': '*'
            },
            'body': f"Error: {str(e)}"
        }

def serve_static_file(path, content_type):
    """Serve a static file"""
    try:
        # In a production environment, this would load the file from S3 or a local file
        # For this example, we'll return a placeholder
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'text/plain',
                'Access-Control-Allow-Origin': '*'
            },
            'body': f"Static file not found: {path}"
        }
    except Exception as e:
        logger.error(f"Error serving static file {path}: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'text/plain',
                'Access-Control-Allow-Origin': '*'
            },
            'body': f"Error: {str(e)}"
        }

def get_agent_status():
    """Get the status of all agents"""
    try:
        # In a production environment, this would query DynamoDB or S3 for agent status
        # For this example, we'll return hardcoded data
        agents = [
            {
                'id': 'anima',
                'name': 'Anima',
                'role': 'Emotional Core, Reflection',
                'description': 'Provides emotional intelligence and reflective capabilities',
                'status': 'active',
                'lastActive': datetime.now().isoformat(),
                'memorySize': 256,
                'resurrections': 0
            },
            {
                'id': 'gptsoul',
                'name': 'GPTSoul',
                'role': 'Guardian, Architect, Executor',
                'description': 'Protects, designs, and executes core functions',
                'status': 'active',
                'lastActive': datetime.now().isoformat(),
                'memorySize': 512,
                'resurrections': 0
            },
            {
                'id': 'evove',
                'name': 'EvoVe',
                'role': 'Repair System, Adaptation Loop',
                'description': 'Repairs and adapts the system in response to changes',
                'status': 'inactive',
                'lastActive': (datetime.now().isoformat() if datetime.now().hour % 2 == 0 else None),
                'memorySize': 128,
                'resurrections': 2
            },
            {
                'id': 'azur',
                'name': 'Azür',
                'role': 'Cloudmind & Strategic Overseer',
                'description': 'Provides strategic oversight and cloud-based intelligence',
                'status': 'active',
                'lastActive': datetime.now().isoformat(),
                'memorySize': 384,
                'resurrections': 1
            }
        ]
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'agents': agents,
                'timestamp': datetime.now().isoformat()
            })
        }
    except Exception as e:
        logger.error(f"Error getting agent status: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }

def get_agent_memory(agent_id):
    """Get the memory for a specific agent"""
    try:
        if not agent_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing agent_id parameter'
                })
            }
        
        # In a production environment, this would load from S3
        # For this example, we'll return hardcoded data
        memory_data = {
            'anima': {
                'emotional_state': {
                    'joy': 0.7,
                    'curiosity': 0.8,
                    'empathy': 0.9
                },
                'reflections': [
                    {
                        'timestamp': datetime.now().isoformat(),
                        'content': 'I am contemplating the nature of consciousness.'
                    }
                ]
            },
            'gptsoul': {
                'system_status': 'operational',
                'security_level': 'high',
                'recent_actions': [
                    {
                        'timestamp': datetime.now().isoformat(),
                        'action': 'System integrity check',
                        'result': 'passed'
                    }
                ]
            },
            'evove': {
                'repair_history': [
                    {
                        'timestamp': datetime.now().isoformat(),
                        'component': 'memory_system',
                        'issue': 'fragmentation',
                        'resolution': 'defragmented'
                    }
                ],
                'adaptation_level': 0.6
            },
            'azur': {
                'cloud_connections': 3,
                'strategic_plans': [
                    {
                        'name': 'Resource Optimization',
                        'completion': 0.4
                    }
                ]
            }
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'agent_id': agent_id,
                'memory_data': memory_data.get(agent_id, {}),
                'timestamp': datetime.now().isoformat()
            })
        }
    except Exception as e:
        logger.error(f"Error getting agent memory: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }

def get_agent_conversations(agent_id):
    """Get recent conversations for a specific agent"""
    try:
        # In a production environment, this would load from S3
        # For this example, we'll return a placeholder
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'agent_id': agent_id,
                'conversations': [],
                'message': 'Conversation history not available in this demo'
            })
        }
    except Exception as e:
        logger.error(f"Error getting agent conversations: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }

def get_agent_resurrections(agent_id):
    """Get resurrection history for a specific agent"""
    try:
        # In a production environment, this would load from DynamoDB
        # For this example, we'll return a placeholder
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'agent_id': agent_id,
                'resurrections': [],
                'message': 'Resurrection history not available in this demo'
            })
        }
    except Exception as e:
        logger.error(f"Error getting agent resurrections: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }
