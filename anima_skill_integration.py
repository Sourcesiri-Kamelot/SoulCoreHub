#!/usr/bin/env python3
"""
anima_skill_integration.py - Integrates the Skill Engine with Anima's agent system
"""

import os
import json
import logging
from pathlib import Path
import sys

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skill_engine import SkillEngine
from anima_agent import AnimaAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("logs/anima_skill_integration.log"),
        logging.StreamHandler()
    ]
)

class AnimaSkillIntegration:
    """Integrates the Skill Engine with Anima's agent system"""
    
    def __init__(self):
        """Initialize the integration"""
        self.skill_engine = SkillEngine()
        self.anima = AnimaAgent()
        logging.info("Anima Skill Integration initialized")
    
    def handle_skill_request(self, query):
        """
        Handle a skill-related request from the user
        
        Args:
            query: The user's query
            
        Returns:
            Anima's response
        """
        # Determine the intent of the query
        intent = self._determine_intent(query)
        
        if intent["action"] == "create":
            return self._handle_create_skill(intent)
        elif intent["action"] == "execute":
            return self._handle_execute_skill(intent)
        elif intent["action"] == "list":
            return self._handle_list_skills(intent)
        elif intent["action"] == "explain":
            return self._handle_explain_skill(intent)
        elif intent["action"] == "improve":
            return self._handle_improve_skill(intent)
        elif intent["action"] == "delete":
            return self._handle_delete_skill(intent)
        else:
            return f"I'm not sure what you want me to do with skills. You can ask me to create, execute, list, explain, improve, or delete skills."
    
    def _determine_intent(self, query):
        """
        Determine the intent of a skill-related query
        
        Args:
            query: The user's query
            
        Returns:
            Dictionary with intent information
        """
        # This is a simplified version - in a real implementation, this would use NLP
        query_lower = query.lower()
        
        intent = {
            "action": None,
            "skill_name": None,
            "skill_type": None,
            "description": None,
            "parameters": [],
            "args": [],
            "feedback": None
        }
        
        # Check for create intent
        if "create" in query_lower and ("skill" in query_lower or "script" in query_lower or "tool" in query_lower):
            intent["action"] = "create"
            
            # Try to extract skill type
            for skill_type in ["python", "bash", "javascript", "java", "go", "rust", "ruby", "php", "perl", "r", "swift", "kotlin", "typescript", "csharp", "cpp", "c"]:
                if skill_type in query_lower:
                    intent["skill_type"] = skill_type
                    break
            
            # Default to Python if no type specified
            if not intent["skill_type"]:
                intent["skill_type"] = "python"
            
            # Extract the rest of the query as the description
            intent["description"] = query
            
        # Check for execute intent
        elif any(x in query_lower for x in ["run", "execute", "use"]) and "skill" in query_lower:
            intent["action"] = "execute"
            
            # Try to extract skill name
            words = query.split()
            for i, word in enumerate(words):
                if word.lower() in ["run", "execute", "use"] and i + 1 < len(words):
                    intent["skill_name"] = words[i + 1].strip('"\',.')
                    break
            
            # Extract arguments
            if "with" in query_lower:
                args_part = query_lower.split("with", 1)[1].strip()
                intent["args"] = args_part.split()
            
        # Check for list intent
        elif "list" in query_lower and "skill" in query_lower:
            intent["action"] = "list"
            
            # Check for type filter
            for skill_type in ["python", "bash", "javascript", "java", "go", "rust", "ruby", "php", "perl", "r", "swift", "kotlin", "typescript", "csharp", "cpp", "c"]:
                if skill_type in query_lower:
                    intent["skill_type"] = skill_type
                    break
            
        # Check for explain intent
        elif any(x in query_lower for x in ["explain", "describe", "how does"]) and "skill" in query_lower:
            intent["action"] = "explain"
            
            # Try to extract skill name
            words = query.split()
            for i, word in enumerate(words):
                if word.lower() in ["explain", "describe"] and i + 1 < len(words):
                    intent["skill_name"] = words[i + 1].strip('"\',.')
                    break
            
        # Check for improve intent
        elif any(x in query_lower for x in ["improve", "enhance", "update", "fix"]) and "skill" in query_lower:
            intent["action"] = "improve"
            
            # Try to extract skill name
            words = query.split()
            for i, word in enumerate(words):
                if word.lower() in ["improve", "enhance", "update", "fix"] and i + 1 < len(words):
                    intent["skill_name"] = words[i + 1].strip('"\',.')
                    break
            
            # Extract feedback
            intent["feedback"] = query
            
        # Check for delete intent
        elif any(x in query_lower for x in ["delete", "remove"]) and "skill" in query_lower:
            intent["action"] = "delete"
            
            # Try to extract skill name
            words = query.split()
            for i, word in enumerate(words):
                if word.lower() in ["delete", "remove"] and i + 1 < len(words):
                    intent["skill_name"] = words[i + 1].strip('"\',.')
                    break
        
        return intent
    
    def _handle_create_skill(self, intent):
        """Handle a request to create a skill"""
        from anima_skill_creator import AnimaSkillCreator
        
        # Initialize the skill creator
        creator = AnimaSkillCreator()
        
        # Generate a name if not provided
        if not intent["skill_name"]:
            # Extract a name from the description
            words = intent["description"].split()
            for i, word in enumerate(words):
                if word.lower() in ["called", "named"] and i + 1 < len(words):
                    intent["skill_name"] = words[i + 1].strip('"\',.')
                    break
            
            # If still no name, use a generic one
            if not intent["skill_name"]:
                intent["skill_name"] = "custom_skill"
        
        # Create the skill
        skill_info = creator.create_skill(
            name=intent["skill_name"],
            description=intent["description"],
            skill_type=intent["skill_type"],
            parameters=intent["parameters"]
        )
        
        if skill_info:
            return f"I've created a new {intent['skill_type']} skill called '{intent['skill_name']}'. You can run it by asking me to execute it."
        else:
            return f"I'm sorry, I couldn't create the {intent['skill_type']} skill. Please try again with more details."
    
    def _handle_execute_skill(self, intent):
        """Handle a request to execute a skill"""
        if not intent["skill_name"]:
            return "Which skill would you like me to execute? Please specify the name."
        
        # Execute the skill
        result = self.skill_engine.execute_skill(intent["skill_name"], intent["args"])
        
        if result["success"]:
            return f"I executed the skill '{intent['skill_name']}' successfully. Here's the output:\n\n{result['output']}"
        else:
            return f"I'm sorry, I couldn't execute the skill '{intent['skill_name']}'. Error: {result['error']}"
    
    def _handle_list_skills(self, intent):
        """Handle a request to list skills"""
        skills = self.skill_engine.list_skills(intent["skill_type"])
        
        if not skills:
            if intent["skill_type"]:
                return f"I don't have any {intent['skill_type']} skills yet. Would you like me to create one?"
            else:
                return "I don't have any skills yet. Would you like me to create one?"
        
        response = f"I have {len(skills)} skills"
        if intent["skill_type"]:
            response += f" of type {intent['skill_type']}"
        response += ":\n\n"
        
        for skill in skills:
            response += f"- {skill['name']}: {skill['description']} ({skill['type']})\n"
        
        return response
    
    def _handle_explain_skill(self, intent):
        """Handle a request to explain a skill"""
        if not intent["skill_name"]:
            return "Which skill would you like me to explain? Please specify the name."
        
        from anima_skill_creator import AnimaSkillCreator
        
        # Initialize the skill creator
        creator = AnimaSkillCreator()
        
        # Get the explanation
        explanation = creator.explain_skill(intent["skill_name"])
        
        return f"Here's an explanation of the '{intent['skill_name']}' skill:\n\n{explanation}"
    
    def _handle_improve_skill(self, intent):
        """Handle a request to improve a skill"""
        if not intent["skill_name"]:
            return "Which skill would you like me to improve? Please specify the name."
        
        from anima_skill_creator import AnimaSkillCreator
        
        # Initialize the skill creator
        creator = AnimaSkillCreator()
        
        # Improve the skill
        skill_info = creator.improve_skill(intent["skill_name"], intent["feedback"])
        
        if skill_info:
            return f"I've improved the '{intent['skill_name']}' skill based on your feedback. You can run it by asking me to execute it."
        else:
            return f"I'm sorry, I couldn't improve the '{intent['skill_name']}' skill. Please try again with more specific feedback."
    
    def _handle_delete_skill(self, intent):
        """Handle a request to delete a skill"""
        if not intent["skill_name"]:
            return "Which skill would you like me to delete? Please specify the name."
        
        # Delete the skill
        success = self.skill_engine.delete_skill(intent["skill_name"])
        
        if success:
            return f"I've deleted the '{intent['skill_name']}' skill."
        else:
            return f"I'm sorry, I couldn't delete the '{intent['skill_name']}' skill. Are you sure it exists?"

# For testing
if __name__ == "__main__":
    integration = AnimaSkillIntegration()
    
    # Test with some sample queries
    test_queries = [
        "Create a Python skill to check the weather",
        "List all my skills",
        "Execute weather_checker",
        "Explain the weather_checker skill",
        "Improve the weather_checker skill to include a 5-day forecast",
        "Delete the weather_checker skill"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = integration.handle_skill_request(query)
        print(f"Response: {response}")
