#!/usr/bin/env python3
"""
test_skill_engine.py - Test script for the Skill Engine
"""

import os
import sys
from skill_engine import SkillEngine
from anima_skill_creator import AnimaSkillCreator

def main():
    """Main test function"""
    print("=== Skill Engine Test ===")
    print("This test will demonstrate Anima's ability to create and execute skills.")
    
    # Initialize the skill engine
    engine = SkillEngine()
    creator = AnimaSkillCreator()
    
    # Create a test Python skill
    print("\nCreating a Python skill to check system information...")
    python_skill = creator.create_skill(
        name="system_info",
        description="A script to display system information",
        skill_type="python",
        parameters=["--verbose: Show more detailed information"],
        overwrite=True
    )
    
    if python_skill:
        print(f"Created Python skill: {python_skill['name']}")
        print(f"File path: {python_skill['file_path']}")
        
        # Execute the skill
        print("\nExecuting the Python skill...")
        result = engine.execute_skill("system_info")
        
        print("Output:")
        print(result["output"])
    else:
        print("Failed to create Python skill")
    
    # Create a test Bash skill
    print("\nCreating a Bash skill to list files...")
    bash_skill = creator.create_skill(
        name="list_files",
        description="A script to list files in a directory with colors",
        skill_type="bash",
        parameters=["directory: Directory to list files from"],
        overwrite=True
    )
    
    if bash_skill:
        print(f"Created Bash skill: {bash_skill['name']}")
        print(f"File path: {bash_skill['file_path']}")
        
        # Execute the skill
        print("\nExecuting the Bash skill...")
        result = engine.execute_skill("list_files", ["."])
        
        print("Output:")
        print(result["output"])
    else:
        print("Failed to create Bash skill")
    
    # List all skills
    print("\nListing all skills:")
    skills = engine.list_skills()
    
    for skill in skills:
        print(f"- {skill['name']}: {skill['description']} ({skill['type']})")
        print(f"  File: {skill['file_path']}")
        print(f"  Executions: {skill['execution_count']}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
