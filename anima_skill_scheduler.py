"""
Anima Skill Scheduler - Interface for Anima to schedule skills.

This module provides a natural language interface for Anima to schedule skills
for execution at specific times or intervals.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Tuple

from scheduler import AnimaScheduler
from skill_engine import SkillEngine
from conversation_state import ConversationState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/skill_scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('anima.skill_scheduler')

class AnimaSkillScheduler:
    """Interface for Anima to schedule skills."""
    
    def __init__(self, skill_engine: SkillEngine, conversation_state: ConversationState):
        """Initialize the skill scheduler.
        
        Args:
            skill_engine: The skill engine to use for executing skills.
            conversation_state: The conversation state manager.
        """
        self.skill_engine = skill_engine
        self.scheduler = AnimaScheduler(skill_engine)
        self.conversation_state = conversation_state
        logger.info("Anima Skill Scheduler initialized")
    
    def process_scheduling_request(self, request: str) -> Dict[str, Any]:
        """Process a natural language scheduling request.
        
        Args:
            request: A natural language request for scheduling a skill.
            
        Returns:
            A response dictionary with the result of the scheduling operation.
        """
        # Extract the skill name and scheduling details
        skill_name, schedule_text = self._extract_skill_and_schedule(request)
        
        if not skill_name:
            return {
                "success": False,
                "message": "I couldn't determine which skill you want to schedule. Please specify a skill name."
            }
        
        # Check if the skill exists
        skill_info = self.skill_engine.get_skill(skill_name)
        if not skill_info:
            return {
                "success": False,
                "message": f"The skill '{skill_name}' doesn't exist. Would you like me to create it first?"
            }
        
        # Parse the scheduling request
        schedule_config = self.scheduler.parse_schedule_request(schedule_text)
        
        try:
            # Schedule the skill
            job_id = self.scheduler.schedule_skill(skill_name, schedule_config)
            
            # Update conversation state
            self._update_conversation_state(skill_name, schedule_config, job_id)
            
            # Generate a human-readable schedule description
            schedule_description = self._describe_schedule(schedule_config)
            
            return {
                "success": True,
                "message": f"I've scheduled the '{skill_name}' skill to run {schedule_description}.",
                "job_id": job_id,
                "skill_name": skill_name,
                "schedule": schedule_config
            }
        except Exception as e:
            logger.error(f"Error scheduling skill {skill_name}: {str(e)}")
            return {
                "success": False,
                "message": f"I encountered an error while scheduling the skill: {str(e)}"
            }
    
    def _extract_skill_and_schedule(self, request: str) -> Tuple[Optional[str], str]:
        """Extract the skill name and scheduling details from a request.
        
        Args:
            request: A natural language request for scheduling a skill.
            
        Returns:
            A tuple of (skill_name, schedule_text).
        """
        # Common patterns for scheduling requests
        patterns = [
            r"schedule\s+(?:the\s+)?(\w+)(?:\s+skill)?\s+(.*)",
            r"run\s+(?:the\s+)?(\w+)(?:\s+skill)?\s+(.*)",
            r"execute\s+(?:the\s+)?(\w+)(?:\s+skill)?\s+(.*)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                skill_name = match.group(1).lower()
                schedule_text = match.group(2)
                return skill_name, schedule_text
        
        # If no pattern matches, try to find a skill name in the request
        skills = self.skill_engine.list_skills()
        for skill in skills:
            skill_name = skill.get('name', '').lower()
            if skill_name and skill_name in request.lower():
                # Remove the skill name from the request to get the schedule text
                schedule_text = request.lower().replace(skill_name, "")
                return skill_name, schedule_text
        
        # If no skill name is found, return None
        return None, request
    
    def _update_conversation_state(self, skill_name: str, schedule_config: Dict[str, Any], job_id: str):
        """Update the conversation state with scheduling information.
        
        Args:
            skill_name: The name of the scheduled skill.
            schedule_config: The scheduling configuration.
            job_id: The ID of the scheduled job.
        """
        # Get the current scheduled skills from the conversation state
        state = self.conversation_state.get_state()
        scheduled_skills = state.get("scheduled_skills", {})
        
        # Add or update the scheduled skill
        scheduled_skills[job_id] = {
            "skill_name": skill_name,
            "schedule": schedule_config
        }
        
        # Update the conversation state
        state["scheduled_skills"] = scheduled_skills
        self.conversation_state.set_state(state)
    
    def _describe_schedule(self, schedule_config: Dict[str, Any]) -> str:
        """Generate a human-readable description of a schedule.
        
        Args:
            schedule_config: The scheduling configuration.
            
        Returns:
            A human-readable description of the schedule.
        """
        schedule_type = schedule_config.get('type', '').lower()
        
        if schedule_type == 'interval':
            return self._describe_interval_schedule(schedule_config)
        elif schedule_type == 'cron':
            return self._describe_cron_schedule(schedule_config)
        elif schedule_type == 'date':
            return self._describe_date_schedule(schedule_config)
        else:
            return "according to the specified schedule"
    
    def _describe_interval_schedule(self, config: Dict[str, Any]) -> str:
        """Generate a description for an interval schedule."""
        for unit in ['seconds', 'minutes', 'hours', 'days', 'weeks']:
            if unit in config:
                value = config[unit]
                unit_singular = unit[:-1]  # Remove trailing 's'
                if value == 1:
                    return f"every {value} {unit_singular}"
                else:
                    return f"every {value} {unit}"
        return "at regular intervals"
    
    def _describe_cron_schedule(self, config: Dict[str, Any]) -> str:
        """Generate a description for a cron schedule."""
        # Handle day of week
        day_of_week = config.get('day_of_week')
        day_text = ""
        if day_of_week:
            days = {
                '0': 'Monday',
                '1': 'Tuesday',
                '2': 'Wednesday',
                '3': 'Thursday',
                '4': 'Friday',
                '5': 'Saturday',
                '6': 'Sunday',
                '0-4': 'weekdays',
                '5-6': 'weekends'
            }
            day_text = f"on {days.get(day_of_week, day_of_week)} "
        
        # Handle time
        hour = config.get('hour')
        minute = config.get('minute', '0')
        
        if hour:
            hour_int = int(hour)
            minute_int = int(minute)
            
            if hour_int == 0 and minute_int == 0:
                time_text = "at midnight"
            elif hour_int == 12 and minute_int == 0:
                time_text = "at noon"
            else:
                am_pm = "AM" if hour_int < 12 else "PM"
                hour_12 = hour_int if hour_int <= 12 else hour_int - 12
                hour_12 = 12 if hour_12 == 0 else hour_12
                
                if minute_int == 0:
                    time_text = f"at {hour_12} {am_pm}"
                else:
                    time_text = f"at {hour_12}:{minute_int:02d} {am_pm}"
        else:
            time_text = "at the scheduled time"
        
        return f"{day_text}{time_text}"
    
    def _describe_date_schedule(self, config: Dict[str, Any]) -> str:
        """Generate a description for a date schedule."""
        run_date = config.get('run_date')
        if run_date:
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(run_date)
                return f"once on {dt.strftime('%B %d, %Y at %I:%M %p')}"
            except ValueError:
                return f"once at the specified date and time"
        return "once at the specified time"
    
    def list_scheduled_skills(self) -> List[Dict[str, Any]]:
        """List all scheduled skills.
        
        Returns:
            A list of dictionaries containing information about scheduled skills.
        """
        jobs = self.scheduler.get_scheduled_jobs()
        return [
            {
                "job_id": job_id,
                "skill_name": info["skill_name"],
                "schedule": info["schedule"],
                "schedule_description": self._describe_schedule(info["schedule"]),
                "created_at": info["created_at"]
            }
            for job_id, info in jobs.items()
        ]
    
    def unschedule_skill(self, job_id_or_skill_name: str) -> Dict[str, Any]:
        """Unschedule a skill.
        
        Args:
            job_id_or_skill_name: The ID of the scheduled job or the name of the skill.
            
        Returns:
            A response dictionary with the result of the unscheduling operation.
        """
        # Check if the input is a job ID
        if job_id_or_skill_name in self.scheduler.scheduled_jobs:
            job_id = job_id_or_skill_name
            skill_name = self.scheduler.scheduled_jobs[job_id]["skill_name"]
        else:
            # Assume it's a skill name
            skill_name = job_id_or_skill_name
            jobs = self.scheduler.get_job_by_skill_name(skill_name)
            
            if not jobs:
                return {
                    "success": False,
                    "message": f"No scheduled jobs found for skill '{skill_name}'."
                }
            
            # If there are multiple jobs for the skill, unschedule all of them
            for job in jobs:
                job_id = job["job_id"]
                self.scheduler.unschedule_skill(job_id)
                
                # Update conversation state
                self._remove_from_conversation_state(job_id)
            
            return {
                "success": True,
                "message": f"Unscheduled {len(jobs)} job(s) for skill '{skill_name}'."
            }
        
        # Unschedule the job
        success = self.scheduler.unschedule_skill(job_id)
        
        if success:
            # Update conversation state
            self._remove_from_conversation_state(job_id)
            
            return {
                "success": True,
                "message": f"Successfully unscheduled the '{skill_name}' skill."
            }
        else:
            return {
                "success": False,
                "message": f"Failed to unschedule the job with ID '{job_id}'."
            }
    
    def _remove_from_conversation_state(self, job_id: str):
        """Remove a scheduled job from the conversation state.
        
        Args:
            job_id: The ID of the scheduled job to remove.
        """
        state = self.conversation_state.get_state()
        scheduled_skills = state.get("scheduled_skills", {})
        
        if job_id in scheduled_skills:
            del scheduled_skills[job_id]
            state["scheduled_skills"] = scheduled_skills
            self.conversation_state.set_state(state)
    
    def shutdown(self):
        """Shutdown the scheduler."""
        self.scheduler.shutdown()
