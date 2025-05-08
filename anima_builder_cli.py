#!/usr/bin/env python3
"""
Anima Builder CLI - Enhanced Builder Mode for SoulCoreHub
A simplified interface to the builder functionality
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Define project directories
PROJECTS_DIR = Path("projects").resolve()
TEMPLATES_DIR = Path("templates").resolve()

# Ensure directories exist
PROJECTS_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

# Templates for different project types
TEMPLATES = {
    "python": "# {name}\n\ndef main():\n    print('Welcome to {name}')\n\nif __name__ == '__main__':\n    main()",
    "html": "<!DOCTYPE html>\n<html>\n<head>\n    <title>{name}</title>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n</head>\n<body>\n    <h1>{name}</h1>\n    <p>Created with SoulCoreHub</p>\n</body>\n</html>",
    "flask": "from flask import Flask, render_template\n\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return 'Welcome to {name}'\n\nif __name__ == '__main__':\n    app.run(debug=True)",
    "node": "// {name}\n\nconsole.log('Welcome to {name}');\n",
    "react": "import React from 'react';\n\nfunction {name}() {{\n  return (\n    <div>\n      <h1>{name}</h1>\n      <p>Created with SoulCoreHub</p>\n    </div>\n  );\n}}\n\nexport default {name};"
}

def print_banner():
    """Print the Anima Builder banner"""
    print("\n" + "=" * 60)
    print("🧠 ANIMA BUILDER MODE")
    print("=" * 60)
    print("Create projects, generate code, and build with soul.")
    print("Type 'help' for available commands.")
    print("=" * 60 + "\n")

def build_project(name, project_type):
    """
    Build a new project with the specified name and type
    
    Args:
        name: Project name
        project_type: Type of project (python, html, flask, node, react)
    """
    if project_type not in TEMPLATES:
        print(f"❌ Unknown project type: {project_type}")
        print(f"Available types: {', '.join(TEMPLATES.keys())}")
        return False
    
    # Create project directory
    project_dir = PROJECTS_DIR / name
    project_dir.mkdir(exist_ok=True)
    
    # Determine file extension
    extensions = {
        "python": "py",
        "flask": "py",
        "html": "html",
        "node": "js",
        "react": "jsx"
    }
    
    # Create main file
    main_file = project_dir / f"{name}.{extensions[project_type]}"
    main_file.write_text(TEMPLATES[project_type].format(name=name))
    
    # Create README
    readme = project_dir / "README.md"
    readme.write_text(f"# {name}\n\nCreated with SoulCoreHub Anima Builder\n\n## Overview\n\nA {project_type} project.\n")
    
    print(f"✅ Created project '{name}' of type '{project_type}'")
    print(f"📁 Location: {project_dir}")
    return True

def list_projects():
    """List all existing projects"""
    if not PROJECTS_DIR.exists():
        print("❌ Projects directory not found")
        return
    
    projects = [p for p in PROJECTS_DIR.iterdir() if p.is_dir()]
    
    if not projects:
        print("No projects found.")
        return
    
    print("\n📁 PROJECTS:")
    print("-" * 40)
    for project in projects:
        print(f"- {project.name}")
    print("-" * 40)

def show_help():
    """Show help information"""
    print("\n📚 AVAILABLE COMMANDS:")
    print("-" * 40)
    print("build <name> as <type>    Create a new project")
    print("list                      List all projects")
    print("help                      Show this help message")
    print("exit                      Exit Builder Mode")
    print("-" * 40)
    print("\nAvailable project types:", ", ".join(TEMPLATES.keys()))
    print("-" * 40)

def main():
    """Main function for the Anima Builder CLI"""
    print_banner()
    
    while True:
        try:
            user_input = input("\nbuilder> ").strip()
            
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Exiting Builder Mode...")
                break
            
            elif user_input.lower() == "help":
                show_help()
            
            elif user_input.lower() == "list":
                list_projects()
            
            elif user_input.lower().startswith("build "):
                parts = user_input.split()
                if len(parts) >= 4 and parts[2].lower() == "as":
                    project_name = parts[1]
                    project_type = parts[3].lower()
                    build_project(project_name, project_type)
                else:
                    print("❌ Invalid build command. Use: build <name> as <type>")
                    print("Example: build myproject as python")
            
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            print("\n👋 Exiting Builder Mode...")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
