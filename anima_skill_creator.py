#!/usr/bin/env python3
"""
anima_skill_creator.py - Anima's interface for creating and managing skills
Allows Anima to dynamically create tools and scripts based on user needs
"""

import os
import json
import logging
import requests
from pathlib import Path
from datetime import datetime
import argparse
import sys

from skill_engine import SkillEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("logs/anima_skill_creator.log"),
        logging.StreamHandler()
    ]
)

# Ollama API endpoint
OLLAMA_API = "http://localhost:11434/api"
DEFAULT_MODEL = "wizardlm-uncensored"

class AnimaSkillCreator:
    """Anima's interface for creating and managing skills"""
    
    def __init__(self, model=DEFAULT_MODEL):
        """Initialize the skill creator"""
        self.model = model
        self.skill_engine = SkillEngine()
        logging.info(f"Anima Skill Creator initialized with model: {model}")
    
    def generate_skill_code(self, skill_name, skill_description, skill_type, parameters=None):
        """
        Generate code for a skill using LLM
        
        Args:
            skill_name: Name of the skill
            skill_description: Description of what the skill should do
            skill_type: Type of skill (python, bash, etc.)
            parameters: Optional parameters for the skill
            
        Returns:
            Generated code for the skill
        """
        # Prepare the prompt
        prompt = f"""Create a {skill_type} script that accomplishes the following task:

Name: {skill_name}
Description: {skill_description}
"""

        if parameters:
            prompt += "\nParameters:\n"
            for param in parameters:
                prompt += f"- {param}\n"

        prompt += f"""
Requirements:
1. The code should be complete and ready to run
2. Include proper error handling
3. Add helpful comments
4. For Python, use proper functions and main() structure
5. For Bash, include proper shebang and error handling
6. Make the code efficient and readable

Return ONLY the code without any explanations or markdown formatting.
"""

        try:
            # Call Ollama API
            response = requests.post(
                f"{OLLAMA_API}/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": "You are an expert programmer who writes clean, efficient, and well-documented code. Focus only on generating the requested code without any explanations or markdown formatting.",
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                code = result.get("response", "").strip()
                
                # Clean up the code (remove markdown code blocks if present)
                code = self._clean_code(code)
                
                logging.info(f"Generated {skill_type} code for skill '{skill_name}'")
                return code
            else:
                logging.error(f"Error generating code: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error generating code: {e}")
            return None
    
    def _clean_code(self, code):
        """
        Clean up code by removing markdown formatting
        
        Args:
            code: Code to clean
            
        Returns:
            Cleaned code
        """
        # Remove markdown code block markers
        code = code.replace("```python", "").replace("```bash", "").replace("```javascript", "")
        code = code.replace("```java", "").replace("```go", "").replace("```rust", "")
        code = code.replace("```ruby", "").replace("```php", "").replace("```perl", "")
        code = code.replace("```r", "").replace("```swift", "").replace("```kotlin", "")
        code = code.replace("```typescript", "").replace("```csharp", "").replace("```cpp", "")
        code = code.replace("```c", "").replace("```", "")
        
        # Trim whitespace
        code = code.strip()
        
        return code
    
    def create_skill(self, name, description, skill_type, parameters=None, overwrite=False):
        """
        Create a new skill
        
        Args:
            name: Name of the skill
            description: Description of what the skill should do
            skill_type: Type of skill (python, bash, etc.)
            parameters: Optional parameters for the skill
            overwrite: Whether to overwrite an existing skill
            
        Returns:
            Skill information or None if creation failed
        """
        # Generate the code
        code = self.generate_skill_code(name, description, skill_type, parameters)
        
        if not code:
            return None
        
        # Create the skill
        skill_info = self.skill_engine.create_skill(
            name=name,
            description=description,
            skill_type=skill_type,
            code=code,
            parameters=parameters,
            overwrite=overwrite
        )
        
        return skill_info
    
    def improve_skill(self, name, feedback):
        """
        Improve an existing skill based on feedback
        
        Args:
            name: Name of the skill to improve
            feedback: Feedback on what to improve
            
        Returns:
            Updated skill information or None if improvement failed
        """
        # Get the existing skill
        skill_info = self.skill_engine.get_skill(name)
        
        if not skill_info:
            return None
        
        # Prepare the prompt
        prompt = f"""Improve this {skill_info['type']} code based on the following feedback:

Feedback: {feedback}

Current code:
```
{skill_info['code']}
```

Requirements:
1. Keep the same basic functionality but improve it according to the feedback
2. Maintain or improve error handling
3. Keep helpful comments
4. Make the code efficient and readable

Return ONLY the improved code without any explanations or markdown formatting.
"""

        try:
            # Call Ollama API
            response = requests.post(
                f"{OLLAMA_API}/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": "You are an expert programmer who writes clean, efficient, and well-documented code. Focus only on generating the improved code without any explanations or markdown formatting.",
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                improved_code = result.get("response", "").strip()
                
                # Clean up the code
                improved_code = self._clean_code(improved_code)
                
                # Update the skill
                updated_skill = self.skill_engine.update_skill(
                    name=name,
                    code=improved_code
                )
                
                logging.info(f"Improved skill '{name}' based on feedback")
                return updated_skill
            else:
                logging.error(f"Error improving code: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error improving code: {e}")
            return None
    
    def explain_skill(self, name):
        """
        Generate an explanation of a skill
        
        Args:
            name: Name of the skill to explain
            
        Returns:
            Explanation of the skill
        """
        # Get the skill
        skill_info = self.skill_engine.get_skill(name)
        
        if not skill_info:
            return f"Skill '{name}' not found"
        
        # Prepare the prompt
        prompt = f"""Explain this {skill_info['type']} code in detail:

```
{skill_info['code']}
```

Provide:
1. A high-level overview of what the code does
2. Explanation of key functions and their purpose
3. Description of any algorithms or techniques used
4. How to use the code, including examples of parameters
5. Any potential limitations or edge cases
"""

        try:
            # Call Ollama API
            response = requests.post(
                f"{OLLAMA_API}/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": "You are an expert programmer who explains code clearly and concisely. Provide a detailed but understandable explanation.",
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                explanation = result.get("response", "").strip()
                
                logging.info(f"Generated explanation for skill '{name}'")
                return explanation
            else:
                logging.error(f"Error generating explanation: {response.status_code} - {response.text}")
                return f"Error generating explanation for skill '{name}'"
                
        except Exception as e:
            logging.error(f"Error generating explanation: {e}")
            return f"Error generating explanation: {str(e)}"

def main():
    """Command-line interface for Anima Skill Creator"""
    parser = argparse.ArgumentParser(description="Anima Skill Creator")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create skill command
    create_parser = subparsers.add_parser("create", help="Create a new skill")
    create_parser.add_argument("name", help="Name of the skill")
    create_parser.add_argument("description", help="Description of what the skill should do")
    create_parser.add_argument("type", help="Type of skill (python, bash, etc.)")
    create_parser.add_argument("--params", nargs="+", help="Parameters for the skill")
    create_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing skill")
    
    # List skills command
    list_parser = subparsers.add_parser("list", help="List available skills")
    list_parser.add_argument("--type", help="Filter by skill type")
    
    # Execute skill command
    execute_parser = subparsers.add_parser("execute", help="Execute a skill")
    execute_parser.add_argument("name", help="Name of the skill to execute")
    execute_parser.add_argument("args", nargs="*", help="Arguments to pass to the skill")
    
    # Improve skill command
    improve_parser = subparsers.add_parser("improve", help="Improve an existing skill")
    improve_parser.add_argument("name", help="Name of the skill to improve")
    improve_parser.add_argument("feedback", help="Feedback on what to improve")
    
    # Explain skill command
    explain_parser = subparsers.add_parser("explain", help="Explain a skill")
    explain_parser.add_argument("name", help="Name of the skill to explain")
    
    # Delete skill command
    delete_parser = subparsers.add_parser("delete", help="Delete a skill")
    delete_parser.add_argument("name", help="Name of the skill to delete")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize the skill creator
    creator = AnimaSkillCreator()
    
    # Execute the command
    if args.command == "create":
        skill_info = creator.create_skill(
            name=args.name,
            description=args.description,
            skill_type=args.type,
            parameters=args.params,
            overwrite=args.overwrite
        )
        
        if skill_info:
            print(f"Created skill '{args.name}' successfully!")
            print(f"Type: {skill_info['type']}")
            print(f"File: {skill_info['file_path']}")
        else:
            print(f"Failed to create skill '{args.name}'")
            
    elif args.command == "list":
        skills = creator.skill_engine.list_skills(args.type)
        
        if skills:
            print(f"Available skills ({len(skills)}):")
            for skill in skills:
                print(f"- {skill['name']}: {skill['description']} ({skill['type']})")
                if skill.get('parameters'):
                    print(f"  Parameters: {', '.join(skill['parameters'])}")
                print(f"  File: {skill['file_path']}")
                print(f"  Executions: {skill['execution_count']}")
                print()
        else:
            print("No skills found")
            
    elif args.command == "execute":
        result = creator.skill_engine.execute_skill(args.name, args.args)
        
        if result["success"]:
            print(f"Executed skill '{args.name}' successfully!")
            print("Output:")
            print(result["output"])
        else:
            print(f"Failed to execute skill '{args.name}'")
            print("Error:")
            print(result["error"])
            
    elif args.command == "improve":
        skill_info = creator.improve_skill(args.name, args.feedback)
        
        if skill_info:
            print(f"Improved skill '{args.name}' successfully!")
        else:
            print(f"Failed to improve skill '{args.name}'")
            
    elif args.command == "explain":
        explanation = creator.explain_skill(args.name)
        print(explanation)
            
    elif args.command == "delete":
        success = creator.skill_engine.delete_skill(args.name)
        
        if success:
            print(f"Deleted skill '{args.name}' successfully!")
        else:
            print(f"Failed to delete skill '{args.name}'")
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
