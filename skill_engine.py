#!/usr/bin/env python3
"""
skill_engine.py - Dynamic skill creation and management system for Anima
Allows Anima to define, store, and execute skills on the fly
"""

import os
import json
import logging
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import importlib.util
import sys
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("logs/skill_engine.log"),
        logging.StreamHandler()
    ]
)

class SkillEngine:
    """Dynamic skill creation and management system"""
    
    def __init__(self, skills_dir="skills", registry_path="skills/skills.json"):
        """
        Initialize the skill engine
        
        Args:
            skills_dir: Directory to store skill files
            registry_path: Path to the skills registry JSON file
        """
        self.skills_dir = Path(skills_dir)
        self.registry_path = Path(registry_path)
        
        # Create directories if they don't exist
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or create the skills registry
        self.load_registry()
        
        # Supported skill types and their file extensions
        self.skill_types = {
            "python": ".py",
            "bash": ".sh",
            "javascript": ".js",
            "java": ".java",
            "go": ".go",
            "rust": ".rs",
            "ruby": ".rb",
            "php": ".php",
            "perl": ".pl",
            "r": ".r",
            "swift": ".swift",
            "kotlin": ".kt",
            "typescript": ".ts",
            "csharp": ".cs",
            "cpp": ".cpp",
            "c": ".c"
        }
        
        # Command to run each skill type
        self.run_commands = {
            "python": ["python3", "{file_path}"],
            "bash": ["bash", "{file_path}"],
            "javascript": ["node", "{file_path}"],
            "java": ["java", "{file_path}"],
            "go": ["go", "run", "{file_path}"],
            "rust": ["rustc", "{file_path}", "-o", "{output_path}", "&&", "{output_path}"],
            "ruby": ["ruby", "{file_path}"],
            "php": ["php", "{file_path}"],
            "perl": ["perl", "{file_path}"],
            "r": ["Rscript", "{file_path}"],
            "swift": ["swift", "{file_path}"],
            "kotlin": ["kotlinc", "{file_path}", "-include-runtime", "-d", "{output_path}.jar", "&&", "java", "-jar", "{output_path}.jar"],
            "typescript": ["ts-node", "{file_path}"],
            "csharp": ["dotnet", "run", "{file_path}"],
            "cpp": ["g++", "{file_path}", "-o", "{output_path}", "&&", "{output_path}"],
            "c": ["gcc", "{file_path}", "-o", "{output_path}", "&&", "{output_path}"]
        }
        
        logging.info(f"Skill Engine initialized with {len(self.registry)} skills")
    
    def load_registry(self):
        """Load the skills registry from JSON file"""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, 'r') as f:
                    self.registry = json.load(f)
                logging.info(f"Loaded {len(self.registry)} skills from registry")
            except Exception as e:
                logging.error(f"Error loading skills registry: {e}")
                self.registry = {}
        else:
            self.registry = {}
            self.save_registry()
    
    def save_registry(self):
        """Save the skills registry to JSON file"""
        try:
            with open(self.registry_path, 'w') as f:
                json.dump(self.registry, f, indent=2)
            logging.info(f"Saved {len(self.registry)} skills to registry")
        except Exception as e:
            logging.error(f"Error saving skills registry: {e}")
    
    def create_skill(self, name, description, skill_type, code, parameters=None, overwrite=False):
        """
        Create a new skill
        
        Args:
            name: Name of the skill (will be used as filename)
            description: Description of what the skill does
            skill_type: Type of skill (python, bash, etc.)
            code: The actual code for the skill
            parameters: List of parameter descriptions
            overwrite: Whether to overwrite an existing skill with the same name
            
        Returns:
            Dictionary with skill information or None if creation failed
        """
        # Validate skill type
        if skill_type not in self.skill_types:
            logging.error(f"Unsupported skill type: {skill_type}")
            return None
        
        # Sanitize the skill name for use as a filename
        safe_name = self._sanitize_filename(name)
        
        # Check if skill already exists
        if safe_name in self.registry and not overwrite:
            logging.error(f"Skill '{safe_name}' already exists. Use overwrite=True to replace it.")
            return None
        
        # Create the skill file
        file_extension = self.skill_types[skill_type]
        file_path = self.skills_dir / f"{safe_name}{file_extension}"
        
        try:
            with open(file_path, 'w') as f:
                f.write(code)
            
            # Make the file executable if it's a script
            if skill_type in ["python", "bash", "ruby", "perl"]:
                os.chmod(file_path, 0o755)
            
            # Create the skill entry
            skill_info = {
                "name": name,
                "description": description,
                "type": skill_type,
                "file_path": str(file_path),
                "parameters": parameters or [],
                "created": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "execution_count": 0,
                "last_executed": None
            }
            
            # Add to registry
            self.registry[safe_name] = skill_info
            self.save_registry()
            
            logging.info(f"Created skill '{name}' of type {skill_type}")
            return skill_info
            
        except Exception as e:
            logging.error(f"Error creating skill '{name}': {e}")
            return None
    
    def update_skill(self, name, description=None, code=None, parameters=None):
        """
        Update an existing skill
        
        Args:
            name: Name of the skill to update
            description: New description (optional)
            code: New code (optional)
            parameters: New parameters (optional)
            
        Returns:
            Updated skill info or None if update failed
        """
        safe_name = self._sanitize_filename(name)
        
        if safe_name not in self.registry:
            logging.error(f"Skill '{safe_name}' not found")
            return None
        
        skill_info = self.registry[safe_name]
        
        try:
            # Update description if provided
            if description is not None:
                skill_info["description"] = description
            
            # Update parameters if provided
            if parameters is not None:
                skill_info["parameters"] = parameters
            
            # Update code if provided
            if code is not None:
                with open(skill_info["file_path"], 'w') as f:
                    f.write(code)
            
            # Update modification timestamp
            skill_info["last_modified"] = datetime.now().isoformat()
            
            # Save registry
            self.save_registry()
            
            logging.info(f"Updated skill '{name}'")
            return skill_info
            
        except Exception as e:
            logging.error(f"Error updating skill '{name}': {e}")
            return None
    
    def delete_skill(self, name):
        """
        Delete a skill
        
        Args:
            name: Name of the skill to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        safe_name = self._sanitize_filename(name)
        
        if safe_name not in self.registry:
            logging.error(f"Skill '{safe_name}' not found")
            return False
        
        try:
            # Get the file path
            file_path = self.registry[safe_name]["file_path"]
            
            # Delete the file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Remove from registry
            del self.registry[safe_name]
            self.save_registry()
            
            logging.info(f"Deleted skill '{name}'")
            return True
            
        except Exception as e:
            logging.error(f"Error deleting skill '{name}': {e}")
            return False
    
    def get_skill(self, name):
        """
        Get information about a skill
        
        Args:
            name: Name of the skill
            
        Returns:
            Skill information dictionary or None if not found
        """
        safe_name = self._sanitize_filename(name)
        
        if safe_name not in self.registry:
            logging.error(f"Skill '{safe_name}' not found")
            return None
        
        skill_info = self.registry[safe_name]
        
        # Add the code to the info
        try:
            with open(skill_info["file_path"], 'r') as f:
                skill_info["code"] = f.read()
        except Exception as e:
            logging.error(f"Error reading skill code: {e}")
            skill_info["code"] = ""
        
        return skill_info
    
    def list_skills(self, skill_type=None):
        """
        List all skills or skills of a specific type
        
        Args:
            skill_type: Optional filter by skill type
            
        Returns:
            List of skill information dictionaries
        """
        skills = []
        
        for name, info in self.registry.items():
            if skill_type is None or info["type"] == skill_type:
                # Don't include the code in the listing
                skill_copy = info.copy()
                skill_copy.pop("code", None)
                skills.append(skill_copy)
        
        return skills
    
    def execute_skill(self, name, args=None):
        """
        Execute a skill
        
        Args:
            name: Name of the skill to execute
            args: Arguments to pass to the skill
            
        Returns:
            Dictionary with execution results
        """
        safe_name = self._sanitize_filename(name)
        
        if safe_name not in self.registry:
            logging.error(f"Skill '{safe_name}' not found")
            return {"success": False, "output": f"Skill '{name}' not found", "error": "Skill not found"}
        
        skill_info = self.registry[safe_name]
        file_path = skill_info["file_path"]
        skill_type = skill_info["type"]
        
        if not os.path.exists(file_path):
            logging.error(f"Skill file not found: {file_path}")
            return {"success": False, "output": "", "error": f"Skill file not found: {file_path}"}
        
        try:
            # Prepare the command
            if skill_type not in self.run_commands:
                return {"success": False, "output": "", "error": f"Unsupported skill type: {skill_type}"}
            
            # Create a temporary directory for output files
            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = os.path.join(temp_dir, safe_name)
                
                # Build the command
                cmd_template = self.run_commands[skill_type]
                cmd = []
                for part in cmd_template:
                    if "{file_path}" in part:
                        cmd.append(part.replace("{file_path}", file_path))
                    elif "{output_path}" in part:
                        cmd.append(part.replace("{output_path}", output_path))
                    else:
                        cmd.append(part)
                
                # Add arguments if provided
                if args:
                    if isinstance(args, list):
                        cmd.extend(args)
                    else:
                        cmd.append(str(args))
                
                # Execute the command
                process = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=False
                )
                
                # Update execution stats
                skill_info["execution_count"] += 1
                skill_info["last_executed"] = datetime.now().isoformat()
                self.save_registry()
                
                return {
                    "success": process.returncode == 0,
                    "output": process.stdout,
                    "error": process.stderr,
                    "return_code": process.returncode
                }
                
        except Exception as e:
            logging.error(f"Error executing skill '{name}': {e}")
            return {"success": False, "output": "", "error": str(e)}
    
    def import_python_skill(self, name):
        """
        Import a Python skill as a module
        
        Args:
            name: Name of the skill to import
            
        Returns:
            Imported module or None if import failed
        """
        safe_name = self._sanitize_filename(name)
        
        if safe_name not in self.registry:
            logging.error(f"Skill '{safe_name}' not found")
            return None
        
        skill_info = self.registry[safe_name]
        
        if skill_info["type"] != "python":
            logging.error(f"Skill '{safe_name}' is not a Python skill")
            return None
        
        file_path = skill_info["file_path"]
        
        try:
            # Import the module
            spec = importlib.util.spec_from_file_location(safe_name, file_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[safe_name] = module
            spec.loader.exec_module(module)
            
            return module
            
        except Exception as e:
            logging.error(f"Error importing Python skill '{name}': {e}")
            return None
    
    def _sanitize_filename(self, name):
        """
        Sanitize a name for use as a filename
        
        Args:
            name: Name to sanitize
            
        Returns:
            Sanitized name
        """
        # Replace spaces with underscores and remove special characters
        safe_name = re.sub(r'[^\w\-_.]', '_', name.lower().replace(' ', '_'))
        return safe_name

# For testing
if __name__ == "__main__":
    engine = SkillEngine()
    
    # Create a test Python skill
    python_skill = engine.create_skill(
        name="hello_world",
        description="A simple Hello World script",
        skill_type="python",
        code='''#!/usr/bin/env python3
import sys

def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "World"
    print(f"Hello, {name}!")

if __name__ == "__main__":
    main()
''',
        parameters=["name: Optional name to greet"]
    )
    
    # Create a test Bash skill
    bash_skill = engine.create_skill(
        name="system_info",
        description="Display system information",
        skill_type="bash",
        code='''#!/bin/bash
echo "System Information:"
echo "==================="
echo "Hostname: $(hostname)"
echo "Kernel: $(uname -r)"
echo "Uptime: $(uptime)"
echo "CPU: $(grep 'model name' /proc/cpuinfo | head -1 | cut -d ':' -f 2 | sed 's/^[ \t]*//')"
echo "Memory: $(free -h | grep Mem | awk '{print $2}')"
''',
        parameters=[]
    )
    
    # List all skills
    skills = engine.list_skills()
    print(f"Available skills: {len(skills)}")
    for skill in skills:
        print(f"- {skill['name']}: {skill['description']} ({skill['type']})")
    
    # Execute the Python skill
    if python_skill:
        print("\nExecuting Python skill:")
        result = engine.execute_skill("hello_world", ["Friend"])
        print(f"Output: {result['output']}")
    
    # Execute the Bash skill
    if bash_skill:
        print("\nExecuting Bash skill:")
        result = engine.execute_skill("system_info")
        print(f"Output: {result['output']}")
