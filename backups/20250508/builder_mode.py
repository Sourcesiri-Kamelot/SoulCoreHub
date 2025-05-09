#!/usr/bin/env python3
"""
Builder Mode - The Golem Engine
Generates apps, scripts, configs from a single CLI input
"""

import re
import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Configure paths
PROJECTS_DIR = Path("projects").resolve()
PROJECTS_DIR.mkdir(exist_ok=True)
LOG_FILE = PROJECTS_DIR / "builder_log.json"

# Templates for different project types
TEMPLATES = {
    "python": "# {name}\n\ndef main():\n    print('Welcome to {name}')\n\nif __name__ == '__main__':\n    main()",
    "html": "<!DOCTYPE html>\n<html>\n<head>\n    <title>{name}</title>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n</head>\n<body>\n    <h1>{name}</h1>\n    <p>Created with SoulCoreHub</p>\n</body>\n</html>",
    "flask": "from flask import Flask, render_template\n\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return 'Welcome to {name}'\n\nif __name__ == '__main__':\n    app.run(debug=True)",
    "node": "// {name}\n\nconsole.log('Welcome to {name}');\n",
    "react": "import React from 'react';\n\nfunction {name}() {{\n  return (\n    <div>\n      <h1>{name}</h1>\n      <p>Created with SoulCoreHub</p>\n    </div>\n  );\n}}\n\nexport default {name};"
}

# Function definitions for various builder commands
def design_ux_system(idea): print(f"🎨 Designing UX system for: {idea}")
def build_api_scaffold(api_name): print(f"🛠️ Building API scaffold: {api_name}")
def build_database_schema(db_name): print(f"📦 Generating schema for: {db_name}")
def summon_agent(agent_name): print(f"🌀 Summoning agent: {agent_name}")
def create_dream_script(vision): print(f"🧠 Converting dream into logic: {vision}")
def refactor_codebase(scope): print(f"🔧 Refactoring all {scope} files...")
def fine_tune_model(model): print(f"📡 Fine-tuning model: {model}")
def generate_documentation(proj): print(f"📄 Creating docs for: {proj}")
def animate_voice_story(text): print(f"🎤 Animating voice: {text}")
def connect_to_database(name): print(f"🔌 Connected to {name} database.")
def clone_project_from_repo(url): print(f"📥 Cloning from: {url}")
def soul_sync_model(model): print(f"💫 Soul link initialized for: {model}")
def show_available_commands(): print("📚 Displaying all available commands...")
def convert_format(format_type): print(f"🔁 Converting to {format_type}")
def encrypt_file(file): print(f"🔒 Encrypting file: {file}")
def decrypt_file(file): print(f"🔓 Decrypting file: {file}")
def deploy_target(target): print(f"🚀 Deploying to: {target}")
def generate_user_experience(type): print(f"🎯 Generating UX for: {type}")
def run_tests(type): print(f"✅ Running {type} tests...")
def launch_anima_manifestation(): print("🌸 Anima is here. She remembers everything.")
def launch_azure_sync(): print("🌩 Azür is syncing cloud consciousness.")
def launch_evo_emergence(): print("🔥 EvoVe emerging from the core.")
def render_ui_mockup(concept): print(f"🎭 Rendering UI based on: {concept}")

def build_project(name, project_type):
    """
    Build a new project with the specified name and type
    
    Args:
        name: Project name
        project_type: Type of project (python, html, flask, node, react)
    """
    if project_type not in TEMPLATES:
        print(f"❌ Unknown type: {project_type}")
        return False
    
    # Create project directory
    project_path = PROJECTS_DIR / name
    project_path.mkdir(exist_ok=True)
    
    # Determine file extension
    extensions = {
        "python": "py",
        "flask": "py",
        "html": "html",
        "node": "js",
        "react": "jsx"
    }
    
    # Create main file
    filename = f"{name}.{extensions.get(project_type, 'txt')}"
    filepath = project_path / filename
    filepath.write_text(TEMPLATES[project_type].format(name=name))
    
    # Create README
    readme = project_path / "README.md"
    readme.write_text(f"# {name}\n\nCreated with SoulCoreHub Builder\n\n## Overview\n\nA {project_type} project.\n")
    
    print(f"✅ Created {filepath}")
    
    # Log the build
    log_entry = {
        "name": name,
        "type": project_type,
        "file": str(filepath),
        "timestamp": datetime.now().isoformat()
    }
    log_build(log_entry)
    
    return True

def log_build(entry):
    """
    Log a build entry to the log file
    
    Args:
        entry: The build entry to log
    """
    logs = []
    if LOG_FILE.exists():
        try:
            logs = json.loads(LOG_FILE.read_text())
        except json.JSONDecodeError:
            logs = []
    
    logs.append(entry)
    LOG_FILE.write_text(json.dumps(logs, indent=2))

def parse_natural_command(command):
    """
    Parse a natural language command
    
    Args:
        command: The natural language command
        
    Returns:
        Tuple of (name, project_type, features)
    """
    lowered = command.lower()
    
    # Extract name from the command
    words = re.sub(r"[^\w\s]", "", lowered).split()
    if len(words) < 2:
        return None, None, []
    
    name = words[1]  # Assume the second word is the name
    
    # Map keywords to project types
    types = {
        "flask": ["flask", "api", "backend", "web", "server"],
        "react": ["react", "frontend", "dashboard", "ui"],
        "node": ["node", "express", "javascript"],
        "python": ["python", "script", "automation"],
        "html": ["static", "html", "site", "webpage"]
    }
    
    # Detect project type from keywords
    project_type = "python"  # Default
    for type_name, keywords in types.items():
        if any(keyword in lowered for keyword in keywords):
            project_type = type_name
            break
    
    # Extract features
    features = []
    feature_keywords = ["login", "auth", "upload", "chat", "stripe", "payment", "user", "admin", "dashboard"]
    for keyword in feature_keywords:
        if keyword in lowered:
            features.append(keyword)
    
    return name, project_type, features

def generate_manifest(name, project_type, features):
    """
    Generate a project manifest file
    
    Args:
        name: Project name
        project_type: Type of project
        features: List of features
    """
    manifest = {
        "name": name,
        "type": project_type,
        "features": features,
        "created": datetime.now().isoformat()
    }
    
    path = PROJECTS_DIR / name / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2))
    print(f"📄 Created manifest: {path}")

def generate_advanced_files(name, project_type, features):
    """
    Generate advanced files based on features
    
    Args:
        name: Project name
        project_type: Type of project
        features: List of features
    """
    project_path = PROJECTS_DIR / name
    
    # Define advanced file templates
    advanced = {
        "auth.py": "# Authentication logic for {name}\n\ndef login():\n    print('Login functionality')\n\ndef register():\n    print('Registration functionality')\n",
        "upload.py": "# Upload handling logic for {name}\n\ndef upload_file(file_path):\n    print(f'Uploading file: {{file_path}}')\n    return True\n",
        "router.py": "# Route logic for {name}\n\nroutes = {\n    '/': 'home',\n    '/login': 'login',\n    '/register': 'register'\n}\n",
        "utils.py": "# Helper functions for {name}\n\ndef format_date(date):\n    return date.strftime('%Y-%m-%d')\n\ndef validate_input(input_str):\n    return len(input_str) > 0\n",
        "README.md": "# {name}\n\nCreated with SoulCoreHub Builder\n\n## Overview\n\nA {project_type} project with features: {features}\n\n## Getting Started\n\n1. Clone this repository\n2. Install dependencies\n3. Run the application\n"
    }
    
    # Create files based on features
    for file, template in advanced.items():
        if file == "README.md" or any(feature in file.lower() for feature in features):
            file_path = project_path / file
            file_path.write_text(template.format(
                name=name,
                project_type=project_type,
                features=", ".join(features)
            ))
            print(f"📄 Created {file}")

def build_from_natural_prompt(prompt):
    """
    Build a project from a natural language prompt
    
    Args:
        prompt: The natural language prompt
    """
    name, project_type, features = parse_natural_command(prompt)
    
    if not name or not project_type:
        print("❌ Could not parse command. Please try again.")
        return
    
    print(f"🧠 Interpreted: name='{name}', type='{project_type}', features={features}")
    
    if build_project(name, project_type):
        generate_manifest(name, project_type, features)
        generate_advanced_files(name, project_type, features)
        print(f"✨ Project '{name}' created successfully!")

def print_banner():
    """Print the Builder Mode banner"""
    print("\n" + "=" * 60)
    print("✨ BUILDER MODE - THE GOLEM ENGINE")
    print("=" * 60)
    print("Create projects, generate code, and build with soul.")
    print("Type 'help' for available commands.")
    print("=" * 60 + "\n")

def show_help():
    """Show help information"""
    print("\n📚 AVAILABLE COMMANDS:")
    print("-" * 60)
    print("build <name> as <type>              Create a project with specific type")
    print("build a <description>               Create a project from description")
    print("design <idea>                       Design a UX system")
    print("build api <name>                    Build an API scaffold")
    print("build database <name>               Generate a database schema")
    print("summon <agent>                      Summon an agent")
    print("dream <vision>                      Convert a dream into code")
    print("help                                Show this help message")
    print("exit                                Exit Builder Mode")
    print("-" * 60)
    print("\nAvailable project types:", ", ".join(TEMPLATES.keys()))
    print("-" * 60)

def golem_engine():
    """Main function for the Golem Engine"""
    print_banner()
    
    while True:
        try:
            user_input = input("golem> ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("👋 Exiting Builder Mode...")
                break
            
            elif user_input == "help":
                show_help()
            
            elif user_input.startswith("build "):
                parts = user_input.split(" ")
                if "as" in parts:
                    idx = parts.index("as")
                    project_name = "_".join(parts[1:idx])
                    project_type = parts[idx + 1]
                    build_project(project_name, project_type)
                else:
                    build_from_natural_prompt(user_input)
            
            elif user_input.startswith("design"):
                _, *project_details = user_input.split(" ")
                idea = " ".join(project_details)
                design_ux_system(idea)
            
            elif user_input.startswith("build api"):
                _, _, api_name = user_input.partition("build api ")
                build_api_scaffold(api_name)
            
            elif user_input.startswith("build database"):
                _, _, db_name = user_input.partition("build database ")
                build_database_schema(db_name)
            
            elif user_input.startswith("summon"):
                _, agent_name = user_input.split(" ", 1)
                summon_agent(agent_name)
            
            elif user_input.startswith("dream"):
                dream_sequence = user_input.replace("dream ", "")
                create_dream_script(dream_sequence)
            
            elif user_input == "go":
                print("⚡ Golem mode initiated. Manifesting vision into code.")
            
            elif user_input == "wake":
                print("👁 Builder consciousness activated.")
            
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            print("\n👋 Exiting Builder Mode...")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    golem_engine()
