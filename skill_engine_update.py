"""
Updates to the skill engine to support scheduling of skills.

This module extends the existing skill engine with scheduling capabilities.
"""

import json
import os
from typing import Dict, Any, Optional, List

# Assuming the original skill_engine.py has a SkillEngine class
from skill_engine import SkillEngine

class ScheduleAwareSkillEngine(SkillEngine):
    """Extension of the SkillEngine that supports scheduling."""
    
    def __init__(self, skills_dir: str = "skills"):
        """Initialize the ScheduleAwareSkillEngine.
        
        Args:
            skills_dir: Directory where skills are stored.
        """
        super().__init__(skills_dir)
    
    def add_schedule_to_skill(self, skill_name: str, schedule_config: Dict[str, Any]) -> bool:
        """Add scheduling information to a skill.
        
        Args:
            skill_name: The name of the skill to update.
            schedule_config: The scheduling configuration to add.
            
        Returns:
            True if the skill was updated successfully, False otherwise.
        """
        if not self.skill_exists(skill_name):
            return False
        
        skill_data = self.get_skill(skill_name)
        skill_data['schedule'] = schedule_config
        return self.update_skill(skill_name, skill_data)
    
    def remove_schedule_from_skill(self, skill_name: str) -> bool:
        """Remove scheduling information from a skill.
        
        Args:
            skill_name: The name of the skill to update.
            
        Returns:
            True if the skill was updated successfully, False otherwise.
        """
        if not self.skill_exists(skill_name):
            return False
        
        skill_data = self.get_skill(skill_name)
        if 'schedule' in skill_data:
            del skill_data['schedule']
            return self.update_skill(skill_name, skill_data)
        return True
    
    def get_scheduled_skills(self) -> Dict[str, Dict[str, Any]]:
        """Get all skills that have scheduling information.
        
        Returns:
            A dictionary mapping skill names to their data for all scheduled skills.
        """
        scheduled_skills = {}
        for skill_name, skill_data in self.list_skills().items():
            if 'schedule' in skill_data and skill_data['schedule']:
                scheduled_skills[skill_name] = skill_data
        return scheduled_skills
    
    def create_skill_with_schedule(self, skill_name: str, skill_code: str, 
                                  description: str, language: str,
                                  schedule_config: Dict[str, Any]) -> bool:
        """Create a new skill with scheduling information.
        
        Args:
            skill_name: The name of the skill.
            skill_code: The code for the skill.
            description: A description of the skill.
            language: The programming language of the skill.
            schedule_config: The scheduling configuration.
            
        Returns:
            True if the skill was created successfully, False otherwise.
        """
        # Create the skill first
        success = self.create_skill(skill_name, skill_code, description, language)
        if not success:
            return False
        
        # Then add the schedule
        return self.add_schedule_to_skill(skill_name, schedule_config)

# Function to update the existing skill_engine.py file
def update_skill_engine():
    """Update the skill_engine.py file to include scheduling capabilities."""
    skill_engine_path = "skill_engine.py"
    
    # Read the current content
    with open(skill_engine_path, 'r') as f:
        content = f.read()
    
    # Check if scheduling is already supported
    if 'schedule' in content:
        print("Skill engine already supports scheduling.")
        return
    
    # Add scheduling support to the SkillEngine class
    schedule_methods = """
    def add_schedule_to_skill(self, skill_name: str, schedule_config: Dict[str, Any]) -> bool:
        """Add scheduling information to a skill."""
        if not self.skill_exists(skill_name):
            return False
        
        skill_data = self.get_skill(skill_name)
        skill_data['schedule'] = schedule_config
        return self.update_skill(skill_name, skill_data)
    
    def remove_schedule_from_skill(self, skill_name: str) -> bool:
        """Remove scheduling information from a skill."""
        if not self.skill_exists(skill_name):
            return False
        
        skill_data = self.get_skill(skill_name)
        if 'schedule' in skill_data:
            del skill_data['schedule']
            return self.update_skill(skill_name, skill_data)
        return True
    
    def get_scheduled_skills(self) -> Dict[str, Dict[str, Any]]:
        """Get all skills that have scheduling information."""
        scheduled_skills = {}
        for skill_name, skill_data in self.list_skills().items():
            if 'schedule' in skill_data and skill_data['schedule']:
                scheduled_skills[skill_name] = skill_data
        return scheduled_skills
    """
    
    # Find the end of the SkillEngine class
    import re
    class_end_match = re.search(r'class SkillEngine.*?(\n\S)', content, re.DOTALL)
    if class_end_match:
        insert_pos = class_end_match.start(1)
        updated_content = content[:insert_pos] + schedule_methods + content[insert_pos:]
        
        # Update the imports if needed
        if 'from typing import Dict, Any' not in content:
            import_pos = content.find('import')
            updated_content = content[:import_pos] + 'from typing import Dict, Any, Optional, List\n' + content[import_pos:]
        
        # Write the updated content
        with open(skill_engine_path, 'w') as f:
            f.write(updated_content)
        
        print("Successfully updated skill_engine.py with scheduling capabilities.")
    else:
        print("Could not find the end of the SkillEngine class. Manual update required.")

if __name__ == "__main__":
    update_skill_engine()
