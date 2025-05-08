"""
Scheduler for Anima's skills.

This module provides functionality to schedule skills for execution at specific times
or intervals. It uses APScheduler to manage the scheduling of tasks in the background.
"""

import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('anima.scheduler')

class AnimaScheduler:
    """Scheduler for Anima's skills."""
    
    def __init__(self, skill_engine):
        """Initialize the scheduler.
        
        Args:
            skill_engine: The skill engine to use for executing skills.
        """
        self.skill_engine = skill_engine
        self.scheduler = BackgroundScheduler(
            jobstores={'default': MemoryJobStore()},
            executors={'default': ThreadPoolExecutor(20)},
            job_defaults={'coalesce': False, 'max_instances': 3},
            timezone='UTC'
        )
        self.scheduler.start()
        self.scheduled_jobs = {}
        self._load_scheduled_skills()
        logger.info("Anima Scheduler initialized")
        
    def _load_scheduled_skills(self):
        """Load and schedule all skills that have scheduling information."""
        skills = self.skill_engine.list_skills()
        for skill in skills:
            skill_name = skill.get('name')
            if 'schedule' in skill and skill['schedule']:
                try:
                    self.schedule_skill(skill_name, skill['schedule'])
                    logger.info(f"Loaded scheduled skill: {skill_name}")
                except Exception as e:
                    logger.error(f"Failed to load scheduled skill {skill_name}: {str(e)}")
    
    def schedule_skill(self, skill_name: str, schedule_config: Dict[str, Any]) -> str:
        """Schedule a skill for execution.
        
        Args:
            skill_name: The name of the skill to schedule.
            schedule_config: Configuration for scheduling the skill.
                Examples:
                - {'type': 'interval', 'seconds': 30}
                - {'type': 'cron', 'hour': '*/2'}
                - {'type': 'date', 'run_date': '2023-12-31 23:59:59'}
                
        Returns:
            The ID of the scheduled job.
        """
        # Check if skill exists
        skill_info = self.skill_engine.get_skill(skill_name)
        if not skill_info:
            raise ValueError(f"Skill '{skill_name}' does not exist")
        
        schedule_type = schedule_config.get('type', '').lower()
        job_id = f"{skill_name}_{int(time.time())}"
        
        # Create the appropriate trigger based on the schedule type
        if schedule_type == 'interval':
            trigger = self._create_interval_trigger(schedule_config)
        elif schedule_type == 'cron':
            trigger = self._create_cron_trigger(schedule_config)
        elif schedule_type == 'date':
            trigger = self._create_date_trigger(schedule_config)
        else:
            raise ValueError(f"Unknown schedule type: {schedule_type}")
        
        # Extract arguments if provided
        args = schedule_config.get('args', {})
        
        # Add the job to the scheduler
        self.scheduler.add_job(
            self._execute_skill,
            trigger=trigger,
            args=[skill_name, args],
            id=job_id,
            name=skill_name,
            replace_existing=True
        )
        
        # Update the skill's schedule information
        self._update_skill_schedule(skill_name, schedule_config)
        
        # Store job information
        self.scheduled_jobs[job_id] = {
            'skill_name': skill_name,
            'schedule': schedule_config,
            'created_at': datetime.now().isoformat()
        }
        
        logger.info(f"Scheduled skill '{skill_name}' with job ID '{job_id}'")
        return job_id
    
    def _create_interval_trigger(self, config: Dict[str, Any]) -> IntervalTrigger:
        """Create an interval trigger from the given configuration."""
        interval_params = {}
        for unit in ['weeks', 'days', 'hours', 'minutes', 'seconds']:
            if unit in config:
                interval_params[unit] = config[unit]
        
        if not interval_params:
            raise ValueError("Interval schedule must specify at least one time unit")
        
        return IntervalTrigger(**interval_params)
    
    def _create_cron_trigger(self, config: Dict[str, Any]) -> CronTrigger:
        """Create a cron trigger from the given configuration."""
        cron_params = {}
        for field in ['year', 'month', 'day', 'week', 'day_of_week', 'hour', 'minute', 'second']:
            if field in config:
                cron_params[field] = config[field]
        
        return CronTrigger(**cron_params)
    
    def _create_date_trigger(self, config: Dict[str, Any]) -> DateTrigger:
        """Create a date trigger from the given configuration."""
        run_date = config.get('run_date')
        if not run_date:
            raise ValueError("Date schedule must specify 'run_date'")
        
        return DateTrigger(run_date=run_date)
    
    def _execute_skill(self, skill_name: str, args: Dict[str, Any] = None):
        """Execute a skill with the given arguments."""
        try:
            logger.info(f"Executing scheduled skill: {skill_name}")
            result = self.skill_engine.execute_skill(skill_name, args or {})
            logger.info(f"Scheduled skill execution completed: {skill_name}")
            self._log_execution(skill_name, True, result)
            return result
        except Exception as e:
            logger.error(f"Error executing scheduled skill {skill_name}: {str(e)}")
            self._log_execution(skill_name, False, str(e))
            return {"error": str(e)}
    
    def _log_execution(self, skill_name: str, success: bool, result: Any):
        """Log the execution of a skill."""
        log_entry = {
            'skill_name': skill_name,
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'result': result
        }
        
        # Log to file
        with open("logs/skill_executions.log", "a") as f:
            f.write(f"{datetime.now().isoformat()} - {skill_name} - Success: {success}\n")
            f.write(f"Result: {result}\n\n")
    
    def _update_skill_schedule(self, skill_name: str, schedule_config: Dict[str, Any]):
        """Update the schedule information for a skill."""
        skill_info = self.skill_engine.get_skill(skill_name)
        if skill_info:
            skill_info['schedule'] = schedule_config
            self.skill_engine.update_skill(skill_name, skill_info.get('description'), 
                                          skill_info.get('code'), skill_info.get('parameters'))
    
    def unschedule_skill(self, job_id: str) -> bool:
        """Unschedule a skill.
        
        Args:
            job_id: The ID of the scheduled job to remove.
            
        Returns:
            True if the job was removed, False otherwise.
        """
        if job_id in self.scheduled_jobs:
            try:
                self.scheduler.remove_job(job_id)
                skill_name = self.scheduled_jobs[job_id]['skill_name']
                
                # Update the skill's schedule information
                skill_info = self.skill_engine.get_skill(skill_name)
                if skill_info and 'schedule' in skill_info:
                    # Remove schedule from skill info
                    skill_info.pop('schedule', None)
                    self.skill_engine.update_skill(skill_name, skill_info.get('description'), 
                                                  skill_info.get('code'), skill_info.get('parameters'))
                
                del self.scheduled_jobs[job_id]
                logger.info(f"Unscheduled job '{job_id}' for skill '{skill_name}'")
                return True
            except Exception as e:
                logger.error(f"Error unscheduling job {job_id}: {str(e)}")
                return False
        return False
    
    def get_scheduled_jobs(self) -> Dict[str, Dict[str, Any]]:
        """Get all scheduled jobs.
        
        Returns:
            A dictionary of job IDs to job information.
        """
        return self.scheduled_jobs
    
    def get_job_by_skill_name(self, skill_name: str) -> List[Dict[str, Any]]:
        """Get all jobs for a specific skill.
        
        Args:
            skill_name: The name of the skill.
            
        Returns:
            A list of job information dictionaries.
        """
        return [
            {'job_id': job_id, **job_info}
            for job_id, job_info in self.scheduled_jobs.items()
            if job_info['skill_name'] == skill_name
        ]
    
    def parse_schedule_request(self, request: str) -> Dict[str, Any]:
        """Parse a natural language scheduling request.
        
        Args:
            request: A natural language request for scheduling a skill.
            
        Returns:
            A schedule configuration dictionary.
        """
        # This is a simplified implementation
        # In a real system, you would use NLP to parse the request
        
        request = request.lower()
        
        # Check for interval patterns
        if "every" in request:
            return self._parse_interval_request(request)
        
        # Check for cron patterns
        if any(term in request for term in ["at", "on", "daily", "weekly", "monthly"]):
            return self._parse_cron_request(request)
        
        # Check for one-time execution
        if any(term in request for term in ["once", "one time", "single"]):
            return self._parse_date_request(request)
        
        # Default to a daily schedule
        return {'type': 'cron', 'hour': '12', 'minute': '0'}
    
    def _parse_interval_request(self, request: str) -> Dict[str, Any]:
        """Parse an interval-based scheduling request."""
        config = {'type': 'interval'}
        
        # Extract the interval value and unit
        import re
        match = re.search(r'every\s+(\d+)\s+(\w+)', request)
        if match:
            value = int(match.group(1))
            unit = match.group(2).rstrip('s')  # Remove trailing 's' if present
            
            if unit in ['second', 'minute', 'hour', 'day', 'week']:
                config[f'{unit}s'] = value
            else:
                # Default to hours if unit is not recognized
                config['hours'] = 1
        else:
            # Default to hourly if no specific interval is found
            config['hours'] = 1
        
        return config
    
    def _parse_cron_request(self, request: str) -> Dict[str, Any]:
        """Parse a cron-based scheduling request."""
        config = {'type': 'cron'}
        
        # Daily at specific time
        import re
        time_match = re.search(r'at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', request)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            
            # Adjust for AM/PM
            if time_match.group(3) == 'pm' and hour < 12:
                hour += 12
            elif time_match.group(3) == 'am' and hour == 12:
                hour = 0
            
            config['hour'] = str(hour)
            config['minute'] = str(minute)
        else:
            # Default to noon
            config['hour'] = '12'
            config['minute'] = '0'
        
        # Check for specific days
        if "monday" in request:
            config['day_of_week'] = '0'
        elif "tuesday" in request:
            config['day_of_week'] = '1'
        elif "wednesday" in request:
            config['day_of_week'] = '2'
        elif "thursday" in request:
            config['day_of_week'] = '3'
        elif "friday" in request:
            config['day_of_week'] = '4'
        elif "saturday" in request:
            config['day_of_week'] = '5'
        elif "sunday" in request:
            config['day_of_week'] = '6'
        elif "weekday" in request:
            config['day_of_week'] = '0-4'
        elif "weekend" in request:
            config['day_of_week'] = '5-6'
        
        return config
    
    def _parse_date_request(self, request: str) -> Dict[str, Any]:
        """Parse a one-time scheduling request."""
        # This is a simplified implementation
        # In a real system, you would use a more sophisticated date parser
        
        from datetime import datetime, timedelta
        
        config = {'type': 'date'}
        
        # Default to tomorrow at noon
        run_date = datetime.now() + timedelta(days=1)
        run_date = run_date.replace(hour=12, minute=0, second=0, microsecond=0)
        
        config['run_date'] = run_date.isoformat()
        return config
    
    def shutdown(self):
        """Shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Anima Scheduler shut down")
