import json
import logging
import os
import re
import subprocess
from typing import Dict, Any, List, Optional

from mcp.core.tool import MCPTool

class BuilderTool(MCPTool):
    """
    Builder tool that allows Anima to create and modify software projects through natural language.
    
    This tool enables Anima to scaffold projects, create files with appropriate code,
    and manage development workflows based on natural language descriptions.
    """
    
    def __init__(self):
        """Initialize the BuilderTool with its metadata."""
        super().__init__(
            name="builder",
            description="Create and modify software projects through natural language",
            parameters={
                "action": {
                    "type": "string",
                    "description": "The builder action to perform",
                    "enum": ["create_project", "create_file", "modify_file", "run_tests", "install_dependencies"]
                },
                "project_type": {
                    "type": "string",
                    "description": "Type of project to create (e.g., python, react, node)"
                },
                "project_name": {
                    "type": "string",
                    "description": "Name of the project"
                },
                "project_description": {
                    "type": "string",
                    "description": "Description of the project"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to create or modify"
                },
                "file_content": {
                    "type": "string",
                    "description": "Content for the file"
                },
                "modification_description": {
                    "type": "string",
                    "description": "Description of the modification to make"
                },
                "dependencies": {
                    "type": "array",
                    "description": "List of dependencies to install"
                }
            },
            required_parameters=["action"]
        )
        self.logger = logging.getLogger("BuilderTool")
        
        # Load project templates
        self.templates = self._load_templates()
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a builder action.
        
        Args:
            parameters: Dictionary containing action parameters
            
        Returns:
            Dictionary containing action results
        """
        action = parameters.get("action", "")
        
        if not action:
            return {"error": "No action provided"}
        
        self.logger.info(f"Executing builder action: {action}")
        
        try:
            if action == "create_project":
                return self._create_project(parameters)
            elif action == "create_file":
                return self._create_file(parameters)
            elif action == "modify_file":
                return self._modify_file(parameters)
            elif action == "run_tests":
                return self._run_tests(parameters)
            elif action == "install_dependencies":
                return self._install_dependencies(parameters)
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            self.logger.error(f"Error executing builder action: {str(e)}")
            return {"error": f"Action failed: {str(e)}"}
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load project templates from the templates directory"""
        templates = {}
        templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir, exist_ok=True)
            self._create_default_templates(templates_dir)
        
        try:
            # Load template configuration
            config_path = os.path.join(templates_dir, "templates.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    templates = json.load(f)
            else:
                # Create default template configuration
                templates = {
                    "python": {
                        "files": [
                            {"path": "README.md", "template": "python/README.md"},
                            {"path": "requirements.txt", "template": "python/requirements.txt"},
                            {"path": "setup.py", "template": "python/setup.py"},
                            {"path": "{project_name}/__init__.py", "template": "python/__init__.py"},
                            {"path": "{project_name}/main.py", "template": "python/main.py"},
                            {"path": "tests/__init__.py", "template": "python/tests/__init__.py"},
                            {"path": "tests/test_main.py", "template": "python/tests/test_main.py"}
                        ],
                        "dependencies": ["pytest"]
                    },
                    "react": {
                        "files": [
                            {"path": "README.md", "template": "react/README.md"},
                            {"path": "package.json", "template": "react/package.json"},
                            {"path": "public/index.html", "template": "react/public/index.html"},
                            {"path": "src/index.js", "template": "react/src/index.js"},
                            {"path": "src/App.js", "template": "react/src/App.js"},
                            {"path": "src/App.css", "template": "react/src/App.css"}
                        ],
                        "dependencies": ["react", "react-dom", "react-scripts"]
                    },
                    "node": {
                        "files": [
                            {"path": "README.md", "template": "node/README.md"},
                            {"path": "package.json", "template": "node/package.json"},
                            {"path": "index.js", "template": "node/index.js"},
                            {"path": "src/app.js", "template": "node/src/app.js"}
                        ],
                        "dependencies": ["express", "dotenv"]
                    }
                }
                
                with open(config_path, 'w') as f:
                    json.dump(templates, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error loading templates: {str(e)}")
        
        return templates
    
    def _create_default_templates(self, templates_dir: str):
        """Create default project templates"""
        # Create Python templates
        python_dir = os.path.join(templates_dir, "python")
        os.makedirs(python_dir, exist_ok=True)
        os.makedirs(os.path.join(python_dir, "tests"), exist_ok=True)
        
        with open(os.path.join(python_dir, "README.md"), 'w') as f:
            f.write("# {project_name}\n\n{project_description}\n\n## Installation\n\n```bash\npip install -e .\n```\n\n## Usage\n\n```python\nfrom {project_name} import main\n```\n")
        
        with open(os.path.join(python_dir, "requirements.txt"), 'w') as f:
            f.write("pytest\n")
        
        with open(os.path.join(python_dir, "setup.py"), 'w') as f:
            f.write('from setuptools import setup, find_packages\n\nsetup(\n    name="{project_name}",\n    version="0.1.0",\n    packages=find_packages(),\n    install_requires=[\n        # Add dependencies here\n    ],\n)\n')
        
        with open(os.path.join(python_dir, "__init__.py"), 'w') as f:
            f.write('"""Main package for {project_name}."""\n\n__version__ = "0.1.0"\n')
        
        with open(os.path.join(python_dir, "main.py"), 'w') as f:
            f.write('"""Main module for {project_name}."""\n\ndef main():\n    """Run the main function."""\n    print("Hello from {project_name}!")\n\nif __name__ == "__main__":\n    main()\n')
        
        with open(os.path.join(python_dir, "tests", "__init__.py"), 'w') as f:
            f.write('"""Tests for {project_name}."""\n')
        
        with open(os.path.join(python_dir, "tests", "test_main.py"), 'w') as f:
            f.write('"""Tests for main module."""\n\nfrom {project_name} import main\n\ndef test_main():\n    """Test the main function."""\n    # Add tests here\n    assert True\n')
        
        # Create React templates
        react_dir = os.path.join(templates_dir, "react")
        os.makedirs(react_dir, exist_ok=True)
        os.makedirs(os.path.join(react_dir, "public"), exist_ok=True)
        os.makedirs(os.path.join(react_dir, "src"), exist_ok=True)
        
        # Create Node templates
        node_dir = os.path.join(templates_dir, "node")
        os.makedirs(node_dir, exist_ok=True)
        os.makedirs(os.path.join(node_dir, "src"), exist_ok=True)
    
    def _create_project(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project from a template"""
        project_type = parameters.get("project_type")
        project_name = parameters.get("project_name")
        project_description = parameters.get("project_description", "")
        
        if not project_type:
            return {"error": "No project type provided"}
        
        if not project_name:
            return {"error": "No project name provided"}
        
        if project_type not in self.templates:
            return {"error": f"Unknown project type: {project_type}"}
        
        try:
            # Create project directory
            project_dir = os.path.join(os.getcwd(), project_name)
            if os.path.exists(project_dir):
                return {"error": f"Project directory already exists: {project_dir}"}
            
            os.makedirs(project_dir, exist_ok=True)
            
            # Create project files
            template = self.templates[project_type]
            created_files = []
            
            for file_info in template["files"]:
                file_path = file_info["path"].format(project_name=project_name)
                template_path = file_info["template"]
                
                # Create directory if needed
                file_dir = os.path.dirname(os.path.join(project_dir, file_path))
                if file_dir and not os.path.exists(file_dir):
                    os.makedirs(file_dir, exist_ok=True)
                
                # Read template content
                templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
                template_file_path = os.path.join(templates_dir, template_path)
                
                if os.path.exists(template_file_path):
                    with open(template_file_path, 'r') as f:
                        content = f.read()
                else:
                    # Use default content if template file doesn't exist
                    content = f"# {os.path.basename(file_path)}\n\nAdd content here."
                
                # Replace placeholders
                content = content.format(
                    project_name=project_name,
                    project_description=project_description
                )
                
                # Write file
                with open(os.path.join(project_dir, file_path), 'w') as f:
                    f.write(content)
                
                created_files.append(file_path)
            
            # Install dependencies if specified
            if "dependencies" in template and template["dependencies"]:
                self._install_project_dependencies(project_dir, project_type, template["dependencies"])
            
            self.logger.info(f"Created {project_type} project: {project_name}")
            
            return {
                "success": True,
                "project_type": project_type,
                "project_name": project_name,
                "project_dir": project_dir,
                "created_files": created_files
            }
        except Exception as e:
            self.logger.error(f"Error creating project: {str(e)}")
            return {"error": f"Failed to create project: {str(e)}"}
    
    def _create_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new file with the specified content"""
        file_path = parameters.get("file_path")
        file_content = parameters.get("file_content", "")
        
        if not file_path:
            return {"error": "No file path provided"}
        
        try:
            # Create directory if needed
            file_dir = os.path.dirname(file_path)
            if file_dir and not os.path.exists(file_dir):
                os.makedirs(file_dir, exist_ok=True)
            
            # Write file
            with open(file_path, 'w') as f:
                f.write(file_content)
            
            self.logger.info(f"Created file: {file_path}")
            
            return {
                "success": True,
                "file_path": file_path,
                "file_size": len(file_content)
            }
        except Exception as e:
            self.logger.error(f"Error creating file: {str(e)}")
            return {"error": f"Failed to create file: {str(e)}"}
    
    def _modify_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Modify an existing file based on a description"""
        file_path = parameters.get("file_path")
        file_content = parameters.get("file_content")
        modification_description = parameters.get("modification_description")
        
        if not file_path:
            return {"error": "No file path provided"}
        
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        if file_content is None and not modification_description:
            return {"error": "No file content or modification description provided"}
        
        try:
            # Read existing file
            with open(file_path, 'r') as f:
                original_content = f.read()
            
            # If file content is provided, use it directly
            if file_content is not None:
                new_content = file_content
            # Otherwise, apply modifications based on description
            elif modification_description:
                # This is a simplified implementation
                # In a real implementation, you would use an LLM to generate the modified content
                new_content = original_content
                
                # For now, just append the description as a comment
                file_ext = os.path.splitext(file_path)[1].lower()
                
                if file_ext in ['.py', '.sh']:
                    new_content += f"\n# {modification_description}\n"
                elif file_ext in ['.js', '.ts', '.java', '.c', '.cpp', '.cs']:
                    new_content += f"\n// {modification_description}\n"
                elif file_ext in ['.html', '.xml']:
                    new_content += f"\n<!-- {modification_description} -->\n"
                else:
                    new_content += f"\n# {modification_description}\n"
            
            # Write modified content
            with open(file_path, 'w') as f:
                f.write(new_content)
            
            self.logger.info(f"Modified file: {file_path}")
            
            return {
                "success": True,
                "file_path": file_path,
                "original_size": len(original_content),
                "new_size": len(new_content)
            }
        except Exception as e:
            self.logger.error(f"Error modifying file: {str(e)}")
            return {"error": f"Failed to modify file: {str(e)}"}
    
    def _run_tests(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run tests for a project"""
        project_type = parameters.get("project_type")
        project_name = parameters.get("project_name")
        
        if not project_type:
            # Try to detect project type
            if os.path.exists("package.json"):
                project_type = "node"
            elif os.path.exists("requirements.txt") or os.path.exists("setup.py"):
                project_type = "python"
            else:
                return {"error": "Could not detect project type. Please specify project_type."}
        
        try:
            # Run tests based on project type
            if project_type == "python":
                result = subprocess.run(
                    ["pytest", "-v"],
                    capture_output=True,
                    text=True
                )
            elif project_type in ["node", "react"]:
                result = subprocess.run(
                    ["npm", "test"],
                    capture_output=True,
                    text=True
                )
            else:
                return {"error": f"Unsupported project type for testing: {project_type}"}
            
            self.logger.info(f"Ran tests for {project_type} project")
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except Exception as e:
            self.logger.error(f"Error running tests: {str(e)}")
            return {"error": f"Failed to run tests: {str(e)}"}
    
    def _install_dependencies(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Install dependencies for a project"""
        project_type = parameters.get("project_type")
        dependencies = parameters.get("dependencies", [])
        
        if not project_type:
            # Try to detect project type
            if os.path.exists("package.json"):
                project_type = "node"
            elif os.path.exists("requirements.txt") or os.path.exists("setup.py"):
                project_type = "python"
            else:
                return {"error": "Could not detect project type. Please specify project_type."}
        
        if not dependencies:
            return {"error": "No dependencies provided"}
        
        try:
            return self._install_project_dependencies(".", project_type, dependencies)
        except Exception as e:
            self.logger.error(f"Error installing dependencies: {str(e)}")
            return {"error": f"Failed to install dependencies: {str(e)}"}
    
    def _install_project_dependencies(self, project_dir: str, project_type: str, dependencies: List[str]) -> Dict[str, Any]:
        """Install dependencies for a project"""
        try:
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(project_dir)
            
            # Install dependencies based on project type
            if project_type == "python":
                result = subprocess.run(
                    ["pip", "install"] + dependencies,
                    capture_output=True,
                    text=True
                )
            elif project_type in ["node", "react"]:
                result = subprocess.run(
                    ["npm", "install", "--save"] + dependencies,
                    capture_output=True,
                    text=True
                )
            else:
                return {"error": f"Unsupported project type for dependency installation: {project_type}"}
            
            self.logger.info(f"Installed dependencies for {project_type} project")
            
            return {
                "success": result.returncode == 0,
                "dependencies": dependencies,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        finally:
            # Change back to original directory
            os.chdir(original_dir)
