"""
Builder Agent - Creates and manages code, configurations, and other artifacts based on requests.
"""

import logging
import time
import threading
import json
import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import uuid

class BuilderAgent:
    def __init__(self):
        self.name = "Builder Agent"
        self.status = "active"
        self.running = False
        self.build_queue = []
        self.current_build = None
        self.build_history = []
        self.max_history = 50
        self.log_file = Path("logs/builder.log")
        self.config_file = Path("config/builder_config.json")
        self.build_dir = Path("projects/builds")
        self.template_dir = Path("templates")
        
        # Create log directory if it doesn't exist
        os.makedirs(self.log_file.parent, exist_ok=True)
        os.makedirs(self.build_dir, exist_ok=True)
        
        # Load configuration
        self.load_config()
        
        # Set up logging
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.name)
        self.logger.info(f"{self.name} initialized")
        
        # Thread for processing builds
        self._thread = None
        
        # Event bus reference (will be set by orchestrator)
        self.event_bus = None

    def load_config(self):
        """Load builder configuration from config file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                    self.logger.info(f"Loaded builder configuration")
            else:
                # Create default configuration if file doesn't exist
                self.config = {
                    "max_concurrent_builds": 1,
                    "build_timeout": 300,  # 5 minutes
                    "templates": {
                        "python_agent": "templates/python_agent.py",
                        "javascript_module": "templates/javascript_module.js",
                        "config_file": "templates/config.json"
                    },
                    "build_types": ["agent", "module", "config", "custom"]
                }
                os.makedirs(self.config_file.parent, exist_ok=True)
                with open(self.config_file, 'w') as f:
                    json.dump(self.config, f, indent=2)
                self.logger.info("Created default builder configuration")
        except Exception as e:
            self.logger.error(f"Error loading builder configuration: {e}")
            self.config = {
                "max_concurrent_builds": 1,
                "build_timeout": 300,
                "templates": {},
                "build_types": ["agent", "module", "config", "custom"]
            }

    def queue_build(self, build_type, name, description, parameters=None, requester=None):
        """Add a build request to the queue"""
        build_id = str(uuid.uuid4())
        build_request = {
            "id": build_id,
            "type": build_type,
            "name": name,
            "description": description,
            "parameters": parameters or {},
            "requester": requester or "unknown",
            "status": "queued",
            "queued_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "output_path": None,
            "error": None
        }
        
        self.build_queue.append(build_request)
        self.logger.info(f"Queued build request: {build_id} - {name} ({build_type})")
        
        return build_id

    def process_builds(self):
        """Process builds from the queue"""
        self.logger.info("Starting build processing")
        self.running = True
        
        while self.running:
            # Check if we can start a new build
            if not self.current_build and self.build_queue:
                # Get the next build from the queue
                build = self.build_queue.pop(0)
                self.current_build = build
                
                # Update status
                build["status"] = "in_progress"
                build["started_at"] = datetime.now().isoformat()
                
                self.logger.info(f"Starting build: {build['id']} - {build['name']} ({build['type']})")
                
                try:
                    # Process the build based on type
                    if build["type"] == "agent":
                        self.build_agent(build)
                    elif build["type"] == "module":
                        self.build_module(build)
                    elif build["type"] == "config":
                        self.build_config(build)
                    elif build["type"] == "custom":
                        self.build_custom(build)
                    else:
                        raise ValueError(f"Unknown build type: {build['type']}")
                    
                    # Update status
                    build["status"] = "completed"
                    build["completed_at"] = datetime.now().isoformat()
                    
                    self.logger.info(f"Completed build: {build['id']} - {build['name']}")
                    
                    # Emit event if event bus is available
                    if self.event_bus:
                        self.event_bus.emit("BUILD_COMPLETE", {
                            "build": build,
                            "source_agent": self.name
                        })
                except Exception as e:
                    # Update status
                    build["status"] = "failed"
                    build["error"] = str(e)
                    build["completed_at"] = datetime.now().isoformat()
                    
                    self.logger.error(f"Build failed: {build['id']} - {build['name']}: {e}")
                    
                    # Emit event if event bus is available
                    if self.event_bus:
                        self.event_bus.emit("BUILD_FAILED", {
                            "build": build,
                            "error": str(e),
                            "source_agent": self.name
                        })
                
                # Add to history
                self.build_history.insert(0, build)
                
                # Trim history if needed
                if len(self.build_history) > self.max_history:
                    self.build_history = self.build_history[:self.max_history]
                
                # Clear current build
                self.current_build = None
            
            # Sleep for a bit
            time.sleep(1)

    def build_agent(self, build):
        """Build an agent from template"""
        # Get parameters
        agent_name = build["name"]
        agent_class = build["parameters"].get("class_name", agent_name.replace(" ", ""))
        category = build["parameters"].get("category", "custom")
        description = build["description"]
        
        # Create directory if it doesn't exist
        agent_dir = Path(f"agents/{category}")
        os.makedirs(agent_dir, exist_ok=True)
        
        # Create file path
        file_name = agent_name.lower().replace(" ", "_") + "_agent.py"
        file_path = agent_dir / file_name
        
        # Check if template exists
        template_path = Path(self.config["templates"].get("python_agent", "templates/python_agent.py"))
        if template_path.exists():
            # Read template
            with open(template_path, 'r') as f:
                template = f.read()
            
            # Replace placeholders
            template = template.replace("{{AGENT_NAME}}", agent_name)
            template = template.replace("{{AGENT_CLASS}}", agent_class)
            template = template.replace("{{DESCRIPTION}}", description)
            template = template.replace("{{CATEGORY}}", category)
            template = template.replace("{{DATE}}", datetime.now().strftime("%Y-%m-%d"))
            
            # Write file
            with open(file_path, 'w') as f:
                f.write(template)
            
            # Update build with output path
            build["output_path"] = str(file_path)
            
            # Update agent registry
            self.update_agent_registry(agent_name, description, category, file_name.replace(".py", ""), agent_class)
            
            self.logger.info(f"Built agent: {agent_name} in {file_path}")
        else:
            raise FileNotFoundError(f"Agent template not found: {template_path}")

    def build_module(self, build):
        """Build a JavaScript module from template"""
        # Get parameters
        module_name = build["name"]
        description = build["description"]
        
        # Create directory if it doesn't exist
        module_dir = Path("src/modules")
        os.makedirs(module_dir, exist_ok=True)
        
        # Create file path
        file_name = module_name.lower().replace(" ", "_") + ".js"
        file_path = module_dir / file_name
        
        # Check if template exists
        template_path = Path(self.config["templates"].get("javascript_module", "templates/javascript_module.js"))
        if template_path.exists():
            # Read template
            with open(template_path, 'r') as f:
                template = f.read()
            
            # Replace placeholders
            template = template.replace("{{MODULE_NAME}}", module_name)
            template = template.replace("{{DESCRIPTION}}", description)
            template = template.replace("{{DATE}}", datetime.now().strftime("%Y-%m-%d"))
            
            # Write file
            with open(file_path, 'w') as f:
                f.write(template)
            
            # Update build with output path
            build["output_path"] = str(file_path)
            
            self.logger.info(f"Built module: {module_name} in {file_path}")
        else:
            raise FileNotFoundError(f"Module template not found: {template_path}")

    def build_config(self, build):
        """Build a configuration file from template"""
        # Get parameters
        config_name = build["name"]
        config_data = build["parameters"].get("config_data", {})
        
        # Create directory if it doesn't exist
        config_dir = Path("config")
        os.makedirs(config_dir, exist_ok=True)
        
        # Create file path
        file_name = config_name.lower().replace(" ", "_") + ".json"
        file_path = config_dir / file_name
        
        # Write config file
        with open(file_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Update build with output path
        build["output_path"] = str(file_path)
        
        self.logger.info(f"Built config: {config_name} in {file_path}")

    def build_custom(self, build):
        """Build a custom artifact based on parameters"""
        # Get parameters
        file_path = build["parameters"].get("file_path")
        file_content = build["parameters"].get("file_content")
        
        if not file_path or not file_content:
            raise ValueError("Custom build requires file_path and file_content parameters")
        
        # Create directory if it doesn't exist
        file_path = Path(file_path)
        os.makedirs(file_path.parent, exist_ok=True)
        
        # Write file
        with open(file_path, 'w') as f:
            f.write(file_content)
        
        # Update build with output path
        build["output_path"] = str(file_path)
        
        self.logger.info(f"Built custom file: {file_path}")

    def update_agent_registry(self, agent_name, description, category, module_name, class_name):
        """Update the agent registry with a new agent"""
        try:
            # Load the registry
            registry_path = Path("config/agent_registry.json")
            if registry_path.exists():
                with open(registry_path, 'r') as f:
                    registry = json.load(f)
            else:
                registry = {}
            
            # Create category if it doesn't exist
            if category not in registry:
                registry[category] = []
            
            # Create agent entry
            agent_entry = {
                "name": agent_name,
                "desc": description,
                "status": "active",
                "interface": "cli",
                "module": f"agents.{category}.{module_name}",
                "class": class_name
            }
            
            # Add to registry
            registry[category].append(agent_entry)
            
            # Save registry
            with open(registry_path, 'w') as f:
                json.dump(registry, f, indent=2)
            
            self.logger.info(f"Updated agent registry with {agent_name}")
            
            # Also update the execution registry
            exec_registry_path = Path("agent_registry_EXEC.json")
            if exec_registry_path.exists():
                with open(exec_registry_path, 'r') as f:
                    exec_registry = json.load(f)
            else:
                exec_registry = {}
            
            # Create category if it doesn't exist
            if category not in exec_registry:
                exec_registry[category] = []
            
            # Add to registry
            exec_registry[category].append(agent_entry)
            
            # Save registry
            with open(exec_registry_path, 'w') as f:
                json.dump(exec_registry, f, indent=2)
            
            self.logger.info(f"Updated execution registry with {agent_name}")
            
        except Exception as e:
            self.logger.error(f"Error updating agent registry: {e}")

    def get_build_status(self, build_id):
        """Get the status of a build"""
        # Check current build
        if self.current_build and self.current_build["id"] == build_id:
            return self.current_build
        
        # Check queue
        for build in self.build_queue:
            if build["id"] == build_id:
                return build
        
        # Check history
        for build in self.build_history:
            if build["id"] == build_id:
                return build
        
        return None

    def start(self):
        """Start the builder agent"""
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.process_builds, daemon=True)
            self._thread.start()
            self.logger.info("Builder agent started")
            return True
        return False

    def stop(self):
        """Stop the builder agent"""
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
            self.logger.info("Builder agent stopped")
            return True
        return False

    def heartbeat(self):
        """Check if the agent is running properly"""
        if self._thread and self._thread.is_alive():
            self.logger.debug("Heartbeat check: OK")
            return True
        self.logger.warning("Heartbeat check: Failed - thread not running")
        return False

    def run(self):
        """Run the agent (for CLI execution)"""
        self.start()
        return {
            "status": "running", 
            "queue_length": len(self.build_queue),
            "current_build": self.current_build["id"] if self.current_build else None,
            "history_count": len(self.build_history)
        }

    def handle_event(self, event):
        """Handle events from the event bus"""
        event_type = event.get("type", "")
        data = event.get("data", {})
        
        if event_type == "BUILD_REQUEST":
            # Queue a new build
            if all(k in data for k in ["type", "name", "description"]):
                build_id = self.queue_build(
                    data["type"],
                    data["name"],
                    data["description"],
                    data.get("parameters"),
                    data.get("requester", event.get("source_agent"))
                )
                return build_id
        
        elif event_type == "CHECK_BUILD_STATUS":
            # Check the status of a build
            if "build_id" in data:
                status = self.get_build_status(data["build_id"])
                
                # Emit the result if event bus is available
                if self.event_bus:
                    self.event_bus.emit("BUILD_STATUS", {
                        "build": status,
                        "source_agent": self.name,
                        "request_id": data.get("request_id")
                    })
                
                return status is not None
        
        return False

    def diagnose(self):
        """Return diagnostic information about the agent"""
        return {
            "name": self.name,
            "status": "running" if self.heartbeat() else "stopped",
            "queue_length": len(self.build_queue),
            "current_build": self.current_build,
            "history_count": len(self.build_history),
            "thread_alive": self._thread.is_alive() if self._thread else False
        }
