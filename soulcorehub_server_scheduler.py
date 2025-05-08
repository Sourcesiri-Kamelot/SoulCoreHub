"""
SoulCoreHub Server with Scheduler Integration

This module extends the SoulCoreHub server with skill scheduling capabilities.
"""

from flask import Flask, request, jsonify, send_from_directory
import subprocess
import os
import json
from datetime import datetime
import logging

from skill_engine import SkillEngine
from scheduler import AnimaScheduler
from anima_skill_scheduler import AnimaSkillScheduler
from conversation_state import ConversationState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/soulcorehub_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('soulcorehub.server')

class SoulCoreHubServer:
    """SoulCoreHub server with skill scheduling capabilities."""
    
    def __init__(self):
        """Initialize the server."""
        # Initialize the skill engine
        self.skill_engine = SkillEngine()
        
        # Initialize the conversation state
        self.conversation_state = ConversationState()
        
        # Initialize the skill scheduler
        self.skill_scheduler = AnimaSkillScheduler(self.skill_engine, self.conversation_state)
        
        # Optional: log commands to a file
        self.log_path = "logs/webui_command_log.txt"
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        
        logger.info("SoulCoreHub server initialized with scheduler")
    
    def execute_command(self):
        """Execute a command from the web UI."""
        data = request.get_json()
        command = data.get("command")

        if not command:
            return jsonify({"output": "❌ No command provided"}), 400

        try:
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Log the command
            with open(self.log_path, "a") as f:
                f.write(f"[{datetime.now()}] {command}\n")
                f.write(result.stdout + result.stderr + "\n\n")

            return jsonify({
                "output": result.stdout + result.stderr
            })
        except Exception as e:
            return jsonify({"output": f"❌ Exception: {str(e)}"}), 500
    
    def handle_agent_request(self):
        """Handle an agent request from the web UI."""
        data = request.json
        query = data.get("query")
        agent = data.get("agent", "anima")  # default to anima if not specified

        if not query:
            return jsonify({"error": "No query provided", "success": False}), 400

        try:
            # Log the agent request
            with open(self.log_path, "a") as f:
                f.write(f"[{datetime.now()}] Agent request: {agent} - {query}\n")

            # Execute the agent_response_hub.py script
            result = subprocess.run(
                ["python3", "agent_response_hub.py", agent, query],
                capture_output=True,
                text=True,
                timeout=60
            )

            # Log the result
            with open(self.log_path, "a") as f:
                f.write(f"Agent response: {result.stdout.strip()}\n")
                if result.stderr:
                    f.write(f"Agent error: {result.stderr.strip()}\n")
                f.write("\n")

            # Return the result
            if result.returncode == 0:
                try:
                    # Try to parse the output as JSON
                    response_json = json.loads(result.stdout.strip())
                    return jsonify(response_json)
                except:
                    # If parsing fails, return the raw output
                    return jsonify({
                        "output": result.stdout.strip(),
                        "error": result.stderr.strip(),
                        "success": True
                    })
            else:
                return jsonify({
                    "output": result.stdout.strip(),
                    "error": result.stderr.strip(),
                    "success": False
                })
        except subprocess.TimeoutExpired:
            return jsonify({"error": "Request timed out", "success": False}), 504
        except Exception as e:
            return jsonify({"error": str(e), "success": False}), 500
    
    def schedule_skill(self):
        """Schedule a skill for execution."""
        data = request.get_json()
        skill_name = data.get('skill_name')
        schedule = data.get('schedule')
        args = data.get('args', {})
        
        if not skill_name or not schedule:
            return jsonify({
                'success': False,
                'message': 'Skill name and schedule are required'
            })
        
        try:
            # Add args to the schedule config if provided
            if args:
                schedule['args'] = args
                
            job_id = self.skill_scheduler.scheduler.schedule_skill(skill_name, schedule)
            
            return jsonify({
                'success': True,
                'message': f'Skill {skill_name} scheduled successfully',
                'job_id': job_id
            })
        except Exception as e:
            logger.error(f"Error scheduling skill: {str(e)}")
            return jsonify({
                'success': False,
                'message': str(e)
            })
    
    def unschedule_skill(self):
        """Unschedule a skill."""
        data = request.get_json()
        job_id = data.get('job_id')
        
        if not job_id:
            return jsonify({
                'success': False,
                'message': 'Job ID is required'
            })
        
        result = self.skill_scheduler.unschedule_skill(job_id)
        return jsonify(result)
    
    def get_scheduled_skills(self):
        """Get all scheduled skills."""
        scheduled_skills = self.skill_scheduler.list_scheduled_skills()
        return jsonify(scheduled_skills)
    
    def process_schedule_request(self):
        """Process a natural language scheduling request."""
        data = request.get_json()
        request_text = data.get('request')
        
        if not request_text:
            return jsonify({
                'success': False,
                'message': 'Request text is required'
            })
        
        result = self.skill_scheduler.process_scheduling_request(request_text)
        return jsonify(result)
    
    def get_skills(self):
        """Get all available skills."""
        skills = self.skill_engine.list_skills()
        return jsonify(skills)
    
    def execute_skill(self):
        """Execute a skill."""
        data = request.get_json()
        skill_name = data.get('skill_name')
        args = data.get('args', {})
        
        if not skill_name:
            return jsonify({
                'success': False,
                'message': 'Skill name is required'
            })
        
        try:
            result = self.skill_engine.execute_skill(skill_name, args)
            return jsonify({
                'success': True,
                'result': result
            })
        except Exception as e:
            logger.error(f"Error executing skill: {str(e)}")
            return jsonify({
                'success': False,
                'message': str(e)
            })

# Create the Flask app and server instance
app = Flask(__name__)
server = SoulCoreHubServer()

# Define routes
@app.route('/execute-command', methods=['POST'])
def execute_command_route():
    return server.execute_command()

@app.route('/agent', methods=['POST'])
def handle_agent_request_route():
    return server.handle_agent_request()

@app.route('/api/schedule_skill', methods=['POST'])
def schedule_skill_route():
    return server.schedule_skill()

@app.route('/api/unschedule_skill', methods=['POST'])
def unschedule_skill_route():
    return server.unschedule_skill()

@app.route('/api/scheduled_skills', methods=['GET'])
def get_scheduled_skills_route():
    return server.get_scheduled_skills()

@app.route('/api/process_schedule_request', methods=['POST'])
def process_schedule_request_route():
    return server.process_schedule_request()

@app.route('/api/skills', methods=['GET'])
def get_skills_route():
    return server.get_skills()

@app.route('/api/execute_skill', methods=['POST'])
def execute_skill_route():
    return server.execute_skill()

@app.route('/')
def index():
    return "✅ SoulCoreHub Server Running with Scheduler"

@app.route('/dashboard/<path:filename>')
def serve_dashboard_file(filename):
    return send_from_directory('webui', filename)

@app.route('/scheduled-skills')
def scheduled_skills():
    return send_from_directory('webui', 'scheduled_skills.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
