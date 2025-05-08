#!/usr/bin/env python3
"""
Anima SAM Commands
This module integrates AWS SAM commands into Anima's command system
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/anima_sam_commands.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("anima_sam_commands")

class AnimaSAMCommands:
    """Anima SAM Commands class for integrating with Anima's command system"""
    
    def __init__(self):
        """Initialize the AnimaSAMCommands class"""
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.builder_script = os.path.join(self.project_root, "anima_builder_sam.py")
    
    def run_builder_command(self, command, args=None):
        """Run a command using the anima_builder_sam.py script"""
        cmd = f"python {self.builder_script} {command}"
        if args:
            for key, value in args.items():
                if value is not None:
                    cmd += f" --{key} {value}"
        
        try:
            result = subprocess.run(cmd, shell=True, check=True, 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   universal_newlines=True)
            return {
                "success": True,
                "output": result.stdout.strip()
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {cmd}")
            logger.error(f"Error: {str(e)}")
            logger.error(f"STDOUT: {e.stdout}")
            logger.error(f"STDERR: {e.stderr}")
            return {
                "success": False,
                "error": str(e),
                "output": e.stdout + "\n" + e.stderr
            }
    
    def handle_command(self, command, args):
        """Handle a SAM command from Anima"""
        if command == "sam_init":
            return self.run_builder_command("init")
        elif command == "sam_build":
            return self.run_builder_command("build")
        elif command == "sam_deploy":
            return self.run_builder_command("deploy")
        elif command == "sam_local":
            return self.run_builder_command("local")
        elif command == "sam_logs":
            if "function_name" not in args:
                return {
                    "success": False,
                    "error": "function_name is required"
                }
            return self.run_builder_command("logs", {"function_name": args["function_name"]})
        elif command == "sam_validate":
            return self.run_builder_command("validate")
        elif command == "sam_stripe":
            if "user_id" not in args:
                return {
                    "success": False,
                    "error": "user_id is required"
                }
            return self.run_builder_command("stripe", {
                "user_id": args["user_id"],
                "units": args.get("units", 1),
                "reason": args.get("reason")
            })
        elif command == "sam_add_stripe":
            return self.run_builder_command("add-stripe")
        elif command == "sam_create_chaining":
            return self.run_builder_command("create-chaining")
        else:
            return {
                "success": False,
                "error": f"Unknown SAM command: {command}"
            }

# Register commands with Anima's command system
def register_commands(command_registry):
    """Register SAM commands with Anima's command system"""
    sam_commands = AnimaSAMCommands()
    
    command_registry.register_command(
        "sam_init",
        "Initialize a new AWS SAM application",
        sam_commands.handle_command
    )
    
    command_registry.register_command(
        "sam_build",
        "Build the AWS SAM application",
        sam_commands.handle_command
    )
    
    command_registry.register_command(
        "sam_deploy",
        "Deploy the AWS SAM application to AWS",
        sam_commands.handle_command
    )
    
    command_registry.register_command(
        "sam_local",
        "Run the AWS SAM application locally",
        sam_commands.handle_command
    )
    
    command_registry.register_command(
        "sam_logs",
        "View logs for a specific Lambda function",
        sam_commands.handle_command,
        params=["function_name"]
    )
    
    command_registry.register_command(
        "sam_validate",
        "Validate the AWS SAM template",
        sam_commands.handle_command
    )
    
    command_registry.register_command(
        "sam_stripe",
        "Record Stripe usage for a user",
        sam_commands.handle_command,
        params=["user_id", "units", "reason"]
    )
    
    command_registry.register_command(
        "sam_add_stripe",
        "Add Stripe billing function to the AWS SAM template",
        sam_commands.handle_command
    )
    
    command_registry.register_command(
        "sam_create_chaining",
        "Create Lambda chaining example",
        sam_commands.handle_command
    )
    
    return True
