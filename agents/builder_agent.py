
import logging
import os
import json

class BuilderAgent:
    def __init__(self):
        self.name = "Builder Agent"
        self.logger = logging.getLogger(self.name)
        self.config = self.load_config()
        
    def load_config(self):
        """Load builder configuration if available"""
        config_path = "config/builder_config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading builder config: {e}")
        return {"templates": {}, "defaults": {}}

    def handle_input(self, prompt):
        if "build" in prompt.lower() or "app" in prompt.lower() or "create" in prompt.lower():
            # Check if it's a todo app request
            if "todo" in prompt.lower() or "to-do" in prompt.lower() or "to do" in prompt.lower():
                return self.build_todo_app()
            
            return (
                "🛠️ Builder Agent here! I understand you'd like to build something.\n"
                "This is a stub — in a real setup, I'd generate project files, initialize code, and start scaffolding the app.\n"
                "💡 Try: 'Build me a to-do app', or 'Create a REST API'."
            )
        return (
            "⚠️ I'm the Builder Agent, but that doesn't look like a build request. "
            "Try asking me to 'build' or 'create' something."
        )
        
    def build_todo_app(self):
        """Build a simple todo app"""
        return (
            "🛠️ Building Todo App...\n\n"
            "I would create the following files:\n"
            "- index.html (UI interface)\n"
            "- styles.css (styling)\n"
            "- app.js (application logic)\n"
            "- server.js (backend API if needed)\n\n"
            "The app would include features like:\n"
            "- Adding new tasks\n"
            "- Marking tasks as complete\n"
            "- Deleting tasks\n"
            "- Storing tasks in local storage\n\n"
            "In a full implementation, I would generate all these files with working code."
        )
        
    def heartbeat(self):
        """Return health status of the agent"""
        return True
