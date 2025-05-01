# modules/build_queue.py
"""
Build Queue Module
----------------
Manages a queue of build tasks for EvoVe to process.
"""

import logging
import threading
import time
import json
import os
import subprocess
import uuid
from datetime import datetime
from queue import Queue, Empty

logger = logging.getLogger("EvoVe.BuildQueue")

class BuildQueue:
    """Manages a queue of build tasks."""
    
    def __init__(self, evove):
        """Initialize the build queue."""
        self.evove = evove
        self.config = evove.config.get("build_queue", {})
        self.queue_file = self.config.get("queue_file", "data/build_queue.json")
        self.history_file = self.config.get("history_file", "data/build_history.json")
        self.max_history = self.config.get("max_history", 100)
        self.running = False
        self.queue = Queue()
        self.task_list = []
        self.history = []
        self.current_task = None
        self.worker_thread = None
        
        # Load existing queue and history
        self._load_queue()
        self._load_history()
        
    def start(self):
        """Start the build queue."""
        if self.running:
            logger.warning("Build queue is already running")
            return
            
        self.running = True
        logger.info("Starting build queue")
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(self.queue_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        
        # Start worker thread
        self.worker_thread = threading.Thread(target=self._worker_loop)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        
    def stop(self):
        """Stop the build queue."""
        if not self.running:
            logger.warning("Build queue is not running")
            return
            
        self.running = False
        logger.info("Stopping build queue")
        
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
            
        # Save queue and history before stopping
        self._save_queue()
        self._save_history()
    
    def _worker_loop(self):
        """Main worker loop."""
        while self.running:
            try:
                # Get a task from the queue
                try:
                    task = self.queue.get(timeout=1)
                except Empty:
                    continue
                
                # Set as current task
                self.current_task = task
                
                # Process the task
                logger.info(f"Processing build task: {task['name']} (ID: {task['id']})")
                
                # Update task status
                task["status"] = "running"
                task["started_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self._save_queue()
                
                # Execute the task
                result = self._execute_task(task)
                
                # Update task with result
                task["status"] = "completed" if result["success"] else "failed"
                task["completed_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                task["result"] = result
                
                # Move task to history
                self.task_list.remove(task)
                self.history.append(task)
                
                # Trim history if needed
                if len(self.history) > self.max_history:
                    self.history = self.history[-self.max_history:]
                
                # Save queue and history
                self._save_queue()
                self._save_history()
                
                # Clear current task
                self.current_task = None
                
                # Mark task as done
                self.queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in build queue worker: {e}")
                time.sleep(5)  # Sleep on error
    
    def _execute_task(self, task):
        """Execute a build task."""
        task_type = task.get("type")
        parameters = task.get("parameters", {})
        
        result = {
            "success": False,
            "output": "",
            "error": ""
        }
        
        try:
            if task_type == "flask_api":
                result = self._build_flask_api(parameters)
            elif task_type == "vscode_plugin":
                result = self._build_vscode_plugin(parameters)
            elif task_type == "docker_container":
                result = self._build_docker_container(parameters)
            elif task_type == "script":
                result = self._run_script(parameters)
            elif task_type == "command":
                result = self._run_command(parameters)
            else:
                result["error"] = f"Unknown task type: {task_type}"
                
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error executing task {task['id']}: {e}")
            
        return result
    
    def _build_flask_api(self, parameters):
        """Build a Flask API."""
        name = parameters.get("name", "api")
        port = parameters.get("port", 5000)
        endpoints = parameters.get("endpoints", [])
        output_dir = parameters.get("output_dir", f"builds/flask_api_{name}")
        
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Create app.py
            with open(os.path.join(output_dir, "app.py"), 'w') as f:
                f.write(f"""from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({{"message": "Welcome to {name} API"}})

""")
                
                # Add endpoints
                for endpoint in endpoints:
                    route = endpoint.get("route", "/")
                    method = endpoint.get("method", "GET").lower()
                    response = endpoint.get("response", {})
                    
                    f.write(f"""
@app.route('{route}', methods=['{method.upper()}'])
def {method}_{route.replace('/', '_')}():
    if request.method == '{method.upper()}':
        return jsonify({response})
""")
                
                f.write(f"""
if __name__ == '__main__':
    app.run(host='0.0.0.0', port={port}, debug=True)
""")
            
            # Create requirements.txt
            with open(os.path.join(output_dir, "requirements.txt"), 'w') as f:
                f.write("flask>=2.0.0\n")
            
            # Create README.md
            with open(os.path.join(output_dir, "README.md"), 'w') as f:
                f.write(f"""# {name} API

A Flask API built by EvoVe.

## Installation

bash
pip install -r requirements.txt

## Running the API

bash
python app.py

The API will be available at http://localhost:{port}/
""")
            
            return {
                "success": True,
                "output": f"Flask API created in {output_dir}",
                "files": ["app.py", "requirements.txt", "README.md"]
            }
            
        except Exception as e:
            logger.error(f"Error building Flask API: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_vscode_plugin(self, parameters):
        """Build a VS Code plugin."""
        name = parameters.get("name", "evove-plugin")
        display_name = parameters.get("display_name", "EvoVe Plugin")
        description = parameters.get("description", "A VS Code plugin built by EvoVe")
        commands = parameters.get("commands", [])
        output_dir = parameters.get("output_dir", f"builds/vscode_plugin_{name}")
        
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Create package.json
            with open(os.path.join(output_dir, "package.json"), 'w') as f:
                package = {
                    "name": name,
                    "displayName": display_name,
                    "description": description,
                    "version": "0.1.0",
                    "engines": {
                        "vscode": "^1.60.0"
                    },
                    "categories": [
                        "Other"
                    ],
                    "activationEvents": [
                        "onCommand:" + name + ".helloWorld"
                    ],
                    "main": "./extension.js",
                    "contributes": {
                        "commands": [
                            {
                                "command": name + ".helloWorld",
                                "title": "Hello World"
                            }
                        ]
                    },
                    "scripts": {
                        "lint": "eslint .",
                        "pretest": "npm run lint",
                        "test": "node ./test/runTest.js"
                    },
                    "devDependencies": {
                        "@types/vscode": "^1.60.0",
                        "eslint": "^8.1.0",
                        "glob": "^7.1.7",
                        "mocha": "^9.1.3",
                        "typescript": "^4.4.4",
                        "@vscode/test-electron": "^1.6.2"
                    }
                }
                
                # Add custom commands
                for cmd in commands:
                    cmd_name = cmd.get("name", "customCommand")
                    cmd_title = cmd.get("title", "Custom Command")
                    
                    package["activationEvents"].append("onCommand:" + name + "." + cmd_name)
                    package["contributes"]["commands"].append({
                        "command": name + "." + cmd_name,
                        "title": cmd_title
                    })
                
                json.dump(package, f, indent=2)
            
            # Create extension.js
            with open(os.path.join(output_dir, "extension.js"), 'w') as f:
                f.write(f"""const vscode = require('vscode');

/**
 * @param {{context: vscode.ExtensionContext}} context
 */
function activate(context) {{
    console.log('Congratulations, your extension "{display_name}" is now active!');

    let helloWorldCommand = vscode.commands.registerCommand('{name}.helloWorld', function () {{
        vscode.window.showInformationMessage('Hello World from {display_name}!');
    }});

    context.subscriptions.push(helloWorldCommand);
""")
                
                # Add custom commands
                for cmd in commands:
                    cmd_name = cmd.get("name", "customCommand")
                    cmd_action = cmd.get("action", "vscode.window.showInformationMessage('Custom command executed!');")
                    
                    f.write(f"""
    let {cmd_name}Command = vscode.commands.registerCommand('{name}.{cmd_name}', function () {{
        {cmd_action}
    }});

    context.subscriptions.push({cmd_name}Command);
""")
                
                f.write(f"""
}}

function deactivate() {{}}

module.exports = {{
    activate,
    deactivate
}}
""")
            
            # Create README.md
            with open(os.path.join(output_dir, "README.md"), 'w') as f:
                f.write(f"""# {display_name}

{description}

## Features

This extension provides the following commands:

- `Hello World`: Displays a hello world message
""")
                
                # Add custom commands to README
                for cmd in commands:
                    cmd_title = cmd.get("title", "Custom Command")
                    cmd_description = cmd.get("description", "A custom command")
                    
                    f.write(f"- `{cmd_title}`: {cmd_description}\n")
            
            # Create .vscodeignore
            with open(os.path.join(output_dir, ".vscodeignore"), 'w') as f:
                f.write(""".vscode/**
.vscode-test/**
test/**
.gitignore
.yarnrc
vsc-extension-quickstart.md
**/jsconfig.json
**/.eslintrc.json
**/*.map
**/*.ts
""")
            
            return {
                "success": True,
                "output": f"VS Code plugin created in {output_dir}",
                "files": ["package.json", "extension.js", "README.md", ".vscodeignore"]
            }
            
        except Exception as e:
            logger.error(f"Error building VS Code plugin: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_docker_container(self, parameters):
        """Build a Docker container."""
        name = parameters.get("name", "evove-container")
        base_image = parameters.get("base_image", "python:3.9-slim")
        ports = parameters.get("ports", [])
        environment = parameters.get("environment", {})
        commands = parameters.get("commands", [])
        output_dir = parameters.get("output_dir", f"builds/docker_{name}")
        
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Create Dockerfile
            with open(os.path.join(output_dir, "Dockerfile"), 'w') as f:
                f.write(f"""FROM {base_image}

WORKDIR /app

""")
                
                # Add environment variables
                for key, value in environment.items():
                    f.write(f"ENV {key}={value}\n")
                
                f.write("\n")
                
                # Add commands
                for cmd in commands:
                    f.write(f"RUN {cmd}\n")
                
                f.write("""
COPY . .

CMD ["python", "app.py"]
""")
            
            # Create docker-compose.yml
            with open(os.path.join(output_dir, "docker-compose.yml"), 'w') as f:
                f.write(f"""version: '3'

services:
  {name}:
    build: .
    container_name: {name}
""")
                
                # Add ports
                if ports:
                    f.write("    ports:\n")
                    for port in ports:
                        f.write(f"      - \"{port}:{port}\"\n")
                
                # Add environment variables
                if environment:
                    f.write("    environment:\n")
                    for key, value in environment.items():
                  # Add environment variables
                if environment:
                    f.write("    environment:\n")
                    for key, value in environment.items():
                        f.write(f"      - {key}={value}\n")
            
            # Create a sample app.py
            with open(os.path.join(output_dir, "app.py"), 'w') as f:
                f.write("""import os
import time

print("Container started")

# Print environment variables
print("Environment variables:")
for key, value in os.environ.items():
    print(f"  {key}={value}")

# Keep container running
while True:
    print("Container is running...")
    time.sleep(60)
""")
            
            # Create README.md
            with open(os.path.join(output_dir, "README.md"), 'w') as f:
                f.write(f"""# {name} Docker Container

A Docker container built by EvoVe.

## Building the Container

bash
docker build -t {name} .

## Running the Container

bash
docker run -d --name {name}""")
               
               # Add port mappings
               for port in ports:
                   f.write(f" -p {port}:{port}")
               
               # Add environment variables
               for key, value in environment.items():
                   f.write(f" -e {key}={value}")
               
               f.write(f" {name}\n\n\n")
                
                f.write("""## Using Docker Compose

bash
docker-compose up -d
""")
            
            return {
                "success": True,
                "output": f"Docker container created in {output_dir}",
                "files": ["Dockerfile", "docker-compose.yml", "app.py", "README.md"]
            }
            
        except Exception as e:
            logger.error(f"Error building Docker container: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _run_script(self, parameters):
        """Run a script."""
        script_path = parameters.get("path")
        args = parameters.get("args", "")
        
        if not script_path:
            return {
                "success": False,
                "error": "No script path provided"
            }
            
        if not os.path.exists(script_path):
            return {
                "success": False,
                "error": f"Script not found: {script_path}"
            }
            
        try:
            # Run the script
            cmd = f"{script_path} {args}"
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            exit_code = process.returncode
            
            return {
                "success": exit_code == 0,
                "output": stdout,
                "error": stderr,
                "exit_code": exit_code
            }
            
        except Exception as e:
            logger.error(f"Error running script: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _run_command(self, parameters):
        """Run a command."""
        command = parameters.get("command")
        
        if not command:
            return {
                "success": False,
                "error": "No command provided"
            }
            
        try:
            # Run the command
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            exit_code = process.returncode
            
            return {
                "success": exit_code == 0,
                "output": stdout,
                "error": stderr,
                "exit_code": exit_code
            }
            
        except Exception as e:
            logger.error(f"Error running command: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _load_queue(self):
        """Load the task queue from file."""
        if os.path.exists(self.queue_file):
            try:
                with open(self.queue_file, 'r') as f:
                    data = json.load(f)
                    self.task_list = data.get("tasks", [])
                    
                # Add tasks to the queue
                for task in self.task_list:
                    if task["status"] == "pending":
                        self.queue.put(task)
                        
                logger.info(f"Loaded {len(self.task_list)} tasks from queue")
            except Exception as e:
                logger.error(f"Failed to load task queue: {e}")
    
    def _save_queue(self):
        """Save the task queue to file."""
        try:
            os.makedirs(os.path.dirname(self.queue_file), exist_ok=True)
            with open(self.queue_file, 'w') as f:
                json.dump({
                    "tasks": self.task_list,
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save task queue: {e}")
    
    def _load_history(self):
        """Load the task history from file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.history = data.get("tasks", [])
                logger.info(f"Loaded {len(self.history)} tasks from history")
            except Exception as e:
                logger.error(f"Failed to load task history: {e}")
    
    def _save_history(self):
        """Save the task history to file."""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, 'w') as f:
                json.dump({
                    "tasks": self.history,
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save task history: {e}")
    
    def add_task(self, task_type, name, parameters=None, priority=0):
        """Add a task to the queue."""
        if not parameters:
            parameters = {}
            
        task = {
            "id": str(uuid.uuid4()),
            "type": task_type,
            "name": name,
            "parameters": parameters,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.task_list.append(task)
        self.queue.put(task)
        
        # Save queue
        self._save_queue()
        
        logger.info(f"Added task to queue: {name} (ID: {task['id']})")
        return task
    
    def cancel_task(self, task_id):
        """Cancel a pending task."""
        for task in self.task_list:
            if task["id"] == task_id and task["status"] == "pending":
                task["status"] = "cancelled"
                logger.info(f"Cancelled task: {task['name']} (ID: {task_id})")
                
                # Save queue
                self._save_queue()
                
                return True
                
        logger.warning(f"Task not found or not pending: {task_id}")
        return False
    
    def get_queue(self):
        """Get the current task queue."""
        return self.task_list
    
    def get_history(self):
        """Get the task history."""
        return self.history
    
    def get_task(self, task_id):
        """Get a specific task by ID."""
        # Check current tasks
        for task in self.task_list:
            if task["id"] == task_id:
                return task
                
        # Check history
        for task in self.history:
            if task["id"] == task_id:
                return task
                
        return None



