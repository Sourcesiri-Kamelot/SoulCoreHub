#!/usr/bin/env python3
"""
Task Scheduler Agent - Keeps track of tasks and deadlines, sending reminders and auto-scheduling where possible.
"""

import logging
import time
import threading
import json
import os
from pathlib import Path
from datetime import datetime, timedelta

class TaskSchedulerAgent:
    def __init__(self):
        """Initialize the Task Scheduler Agent"""
        self.name = "Task Scheduler Agent"
        self.status = "active"
        self.running = False
        self.tasks = []
        self.reminders = []
        self.config_file = Path("config/task_scheduler_config.json")
        self.tasks_file = Path("data/tasks.json")
        self.log_file = Path("logs/task_scheduler.log")
        
        # Create log directory if it doesn't exist
        os.makedirs(self.log_file.parent, exist_ok=True)
        
        # Set up logging
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.name)
        
        # Load configuration
        self.config = self.load_config()
        
        # Load tasks
        self.load_tasks()
        
        # Thread for checking tasks
        self._thread = None
        
        self.logger.info(f"{self.name} initialized")
    
    def load_config(self):
        """Load task scheduler configuration from file"""
        default_config = {
            "reminder_intervals": [
                {"days": 7, "message": "You have a task due in a week: {task}"},
                {"days": 1, "message": "You have a task due tomorrow: {task}"},
                {"hours": 1, "message": "You have a task due in an hour: {task}"}
            ],
            "check_interval": 300,  # 5 minutes
            "auto_schedule": True,
            "working_hours": {
                "start": "09:00",
                "end": "17:00"
            },
            "working_days": [0, 1, 2, 3, 4]  # Monday to Friday (0 = Monday)
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.logger.info("Loaded task scheduler configuration")
                    return config
            else:
                # Create default configuration
                os.makedirs(self.config_file.parent, exist_ok=True)
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                self.logger.info("Created default task scheduler configuration")
                return default_config
        except Exception as e:
            self.logger.error(f"Error loading task scheduler configuration: {e}")
            return default_config
    
    def load_tasks(self):
        """Load tasks from file"""
        try:
            if self.tasks_file.exists():
                with open(self.tasks_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = data.get("tasks", [])
                    self.reminders = data.get("reminders", [])
                    self.logger.info(f"Loaded {len(self.tasks)} tasks and {len(self.reminders)} reminders")
            else:
                self.tasks = []
                self.reminders = []
                self.logger.info("No tasks file found, starting with empty task list")
        except Exception as e:
            self.logger.error(f"Error loading tasks: {e}")
            self.tasks = []
            self.reminders = []
    
    def save_tasks(self):
        """Save tasks to file"""
        try:
            os.makedirs(self.tasks_file.parent, exist_ok=True)
            with open(self.tasks_file, 'w') as f:
                json.dump({
                    "tasks": self.tasks,
                    "reminders": self.reminders,
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2)
            self.logger.info(f"Saved {len(self.tasks)} tasks and {len(self.reminders)} reminders")
        except Exception as e:
            self.logger.error(f"Error saving tasks: {e}")
    
    def add_task(self, title, description="", due_date=None, priority="medium", tags=None, estimated_time=None):
        """
        Add a new task
        
        Args:
            title (str): Task title
            description (str, optional): Task description
            due_date (str, optional): Due date in ISO format (YYYY-MM-DD)
            priority (str, optional): Task priority (low, medium, high)
            tags (list, optional): List of tags
            estimated_time (int, optional): Estimated time in minutes
            
        Returns:
            dict: The created task
        """
        # Generate a unique ID
        task_id = str(len(self.tasks) + 1)
        
        # Create the task
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "due_date": due_date,
            "priority": priority,
            "tags": tags or [],
            "estimated_time": estimated_time,
            "status": "pending",
            "completed_at": None
        }
        
        # Add the task
        self.tasks.append(task)
        
        # Create reminders
        if due_date:
            self.create_reminders(task)
        
        # Save tasks
        self.save_tasks()
        
        self.logger.info(f"Added task: {title}")
        
        return task
    
    def create_reminders(self, task):
        """
        Create reminders for a task
        
        Args:
            task (dict): The task to create reminders for
        """
        try:
            # Parse due date
            due_date = datetime.fromisoformat(task["due_date"])
            
            # Create reminders based on configuration
            for interval in self.config["reminder_intervals"]:
                # Calculate reminder time
                if "days" in interval:
                    reminder_time = due_date - timedelta(days=interval["days"])
                elif "hours" in interval:
                    reminder_time = due_date - timedelta(hours=interval["hours"])
                else:
                    continue
                
                # Create reminder
                reminder = {
                    "task_id": task["id"],
                    "time": reminder_time.isoformat(),
                    "message": interval["message"].format(task=task["title"]),
                    "sent": False
                }
                
                # Add reminder
                self.reminders.append(reminder)
            
            self.logger.info(f"Created {len(self.config['reminder_intervals'])} reminders for task: {task['title']}")
        
        except Exception as e:
            self.logger.error(f"Error creating reminders for task {task['title']}: {e}")
    
    def update_task(self, task_id, **kwargs):
        """
        Update a task
        
        Args:
            task_id (str): ID of the task to update
            **kwargs: Fields to update
            
        Returns:
            dict: The updated task or None if not found
        """
        # Find the task
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                # Update fields
                for key, value in kwargs.items():
                    if key in task:
                        task[key] = value
                
                # If due date changed, update reminders
                if "due_date" in kwargs:
                    # Remove old reminders
                    self.reminders = [r for r in self.reminders if r["task_id"] != task_id]
                    
                    # Create new reminders
                    if kwargs["due_date"]:
                        self.create_reminders(task)
                
                # Save tasks
                self.save_tasks()
                
                self.logger.info(f"Updated task: {task['title']}")
                
                return task
        
        self.logger.warning(f"Task not found: {task_id}")
        return None
    
    def complete_task(self, task_id):
        """
        Mark a task as completed
        
        Args:
            task_id (str): ID of the task to complete
            
        Returns:
            dict: The completed task or None if not found
        """
        # Find the task
        for task in self.tasks:
            if task["id"] == task_id:
                # Mark as completed
                task["status"] = "completed"
                task["completed_at"] = datetime.now().isoformat()
                
                # Remove reminders
                self.reminders = [r for r in self.reminders if r["task_id"] != task_id]
                
                # Save tasks
                self.save_tasks()
                
                self.logger.info(f"Completed task: {task['title']}")
                
                return task
        
        self.logger.warning(f"Task not found: {task_id}")
        return None
    
    def delete_task(self, task_id):
        """
        Delete a task
        
        Args:
            task_id (str): ID of the task to delete
            
        Returns:
            bool: True if task was deleted, False otherwise
        """
        # Find the task
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                # Remove the task
                deleted_task = self.tasks.pop(i)
                
                # Remove reminders
                self.reminders = [r for r in self.reminders if r["task_id"] != task_id]
                
                # Save tasks
                self.save_tasks()
                
                self.logger.info(f"Deleted task: {deleted_task['title']}")
                
                return True
        
        self.logger.warning(f"Task not found: {task_id}")
        return False
    
    def get_tasks(self, status=None, tag=None, priority=None):
        """
        Get tasks filtered by criteria
        
        Args:
            status (str, optional): Filter by status
            tag (str, optional): Filter by tag
            priority (str, optional): Filter by priority
            
        Returns:
            list: Filtered tasks
        """
        filtered_tasks = self.tasks
        
        # Filter by status
        if status:
            filtered_tasks = [t for t in filtered_tasks if t["status"] == status]
        
        # Filter by tag
        if tag:
            filtered_tasks = [t for t in filtered_tasks if tag in t["tags"]]
        
        # Filter by priority
        if priority:
            filtered_tasks = [t for t in filtered_tasks if t["priority"] == priority]
        
        return filtered_tasks
    
    def get_due_tasks(self, days=7):
        """
        Get tasks due within a certain number of days
        
        Args:
            days (int, optional): Number of days
            
        Returns:
            list: Tasks due within the specified number of days
        """
        now = datetime.now()
        cutoff = now + timedelta(days=days)
        
        due_tasks = []
        for task in self.tasks:
            if task["status"] == "pending" and task["due_date"]:
                try:
                    due_date = datetime.fromisoformat(task["due_date"])
                    if due_date <= cutoff:
                        due_tasks.append(task)
                except ValueError:
                    self.logger.warning(f"Invalid due date for task {task['id']}: {task['due_date']}")
        
        return due_tasks
    
    def check_reminders(self):
        """
        Check for due reminders
        
        Returns:
            list: Due reminders
        """
        now = datetime.now()
        due_reminders = []
        
        for reminder in self.reminders:
            if not reminder["sent"]:
                try:
                    reminder_time = datetime.fromisoformat(reminder["time"])
                    if reminder_time <= now:
                        # Mark as sent
                        reminder["sent"] = True
                        
                        # Add to due reminders
                        due_reminders.append(reminder)
                        
                        self.logger.info(f"Reminder due: {reminder['message']}")
                except ValueError:
                    self.logger.warning(f"Invalid reminder time: {reminder['time']}")
        
        # Save tasks if any reminders were sent
        if due_reminders:
            self.save_tasks()
        
        return due_reminders
    
    def auto_schedule_tasks(self):
        """
        Auto-schedule tasks based on priority and due date
        
        Returns:
            list: Scheduled tasks
        """
        if not self.config["auto_schedule"]:
            return []
        
        # Get pending tasks with estimated time
        pending_tasks = [t for t in self.tasks if t["status"] == "pending" and t["estimated_time"]]
        
        # Sort by priority and due date
        priority_values = {"high": 3, "medium": 2, "low": 1}
        
        def task_sort_key(task):
            priority = priority_values.get(task["priority"], 0)
            
            # Parse due date if available
            due_date = None
            if task["due_date"]:
                try:
                    due_date = datetime.fromisoformat(task["due_date"])
                except ValueError:
                    pass
            
            # Return sort key (higher priority and earlier due date first)
            return (-priority, due_date or datetime.max)
        
        sorted_tasks = sorted(pending_tasks, key=task_sort_key)
        
        # Schedule tasks
        scheduled_tasks = []
        current_time = datetime.now()
        
        for task in sorted_tasks:
            # Skip if already scheduled
            if "scheduled_time" in task:
                scheduled_tasks.append(task)
                continue
            
            # Find next available time slot
            while True:
                # Check if current time is within working hours
                current_weekday = current_time.weekday()
                current_hour = current_time.hour
                current_minute = current_time.minute
                
                working_start = self.config["working_hours"]["start"].split(":")
                working_end = self.config["working_hours"]["end"].split(":")
                
                working_start_hour = int(working_start[0])
                working_start_minute = int(working_start[1])
                working_end_hour = int(working_end[0])
                working_end_minute = int(working_end[1])
                
                # Check if current time is a working day
                if current_weekday not in self.config["working_days"]:
                    # Move to next day
                    current_time = current_time.replace(hour=working_start_hour, minute=working_start_minute)
                    current_time += timedelta(days=1)
                    continue
                
                # Check if current time is within working hours
                current_time_minutes = current_hour * 60 + current_minute
                working_start_minutes = working_start_hour * 60 + working_start_minute
                working_end_minutes = working_end_hour * 60 + working_end_minute
                
                if current_time_minutes < working_start_minutes:
                    # Move to start of working hours
                    current_time = current_time.replace(hour=working_start_hour, minute=working_start_minute)
                elif current_time_minutes >= working_end_minutes:
                    # Move to next day
                    current_time = current_time.replace(hour=working_start_hour, minute=working_start_minute)
                    current_time += timedelta(days=1)
                    continue
                
                # Schedule the task
                task["scheduled_time"] = current_time.isoformat()
                scheduled_tasks.append(task)
                
                # Move current time forward by estimated time
                current_time += timedelta(minutes=task["estimated_time"])
                break
        
        # Save tasks
        self.save_tasks()
        
        self.logger.info(f"Auto-scheduled {len(scheduled_tasks)} tasks")
        
        return scheduled_tasks
    
    def monitor_tasks(self):
        """Monitor tasks in a background thread"""
        self.logger.info("Starting task monitoring")
        self.running = True
        
        while self.running:
            try:
                # Check reminders
                due_reminders = self.check_reminders()
                
                # Auto-schedule tasks
                if self.config["auto_schedule"]:
                    self.auto_schedule_tasks()
                
                # Sleep until next check
                time.sleep(self.config["check_interval"])
            
            except Exception as e:
                self.logger.error(f"Error in task monitoring: {e}")
                time.sleep(60)  # Sleep for a minute before retrying
    
    def start(self):
        """Start the task monitoring in a background thread"""
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.monitor_tasks, daemon=True)
            self._thread.start()
            self.logger.info("Task monitoring started")
            return True
        return False
    
    def stop(self):
        """Stop the task monitoring"""
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
            self.logger.info("Task monitoring stopped")
            return True
        return False
    
    def heartbeat(self):
        """Check if the agent is running properly"""
        if self._thread and self._thread.is_alive():
            self.logger.debug("Heartbeat check: OK")
            return True
        self.logger.warning("Heartbeat check: Failed - thread not running")
        return False
    
    def handle_input(self, prompt):
        """
        Handle user input
        
        Args:
            prompt (str): User input
            
        Returns:
            str: Response to the user
        """
        prompt_lower = prompt.lower()
        
        # Add task command
        if "add task" in prompt_lower or "create task" in prompt_lower:
            # Extract task details
            # This is a very basic parser - in a real implementation, you'd use NLP
            title = None
            description = ""
            due_date = None
            priority = "medium"
            
            # Extract title
            if "title" in prompt_lower:
                title_parts = prompt.split("title", 1)[1].strip()
                if " " in title_parts:
                    title = title_parts.split(" ", 1)[0].strip()
                else:
                    title = title_parts
            else:
                # Use the whole prompt as title
                title = prompt.replace("add task", "").replace("create task", "").strip()
            
            # Extract description
            if "description" in prompt_lower:
                description_parts = prompt.split("description", 1)[1].strip()
                if " due" in description_parts.lower():
                    description = description_parts.split(" due", 1)[0].strip()
                elif " priority" in description_parts.lower():
                    description = description_parts.split(" priority", 1)[0].strip()
                else:
                    description = description_parts
            
            # Extract due date
            if "due" in prompt_lower:
                due_parts = prompt.split("due", 1)[1].strip()
                if " priority" in due_parts.lower():
                    due_date_str = due_parts.split(" priority", 1)[0].strip()
                else:
                    due_date_str = due_parts
                
                # Try to parse due date
                try:
                    # Handle various date formats
                    if "today" in due_date_str.lower():
                        due_date = datetime.now().date().isoformat()
                    elif "tomorrow" in due_date_str.lower():
                        due_date = (datetime.now() + timedelta(days=1)).date().isoformat()
                    elif "next week" in due_date_str.lower():
                        due_date = (datetime.now() + timedelta(days=7)).date().isoformat()
                    else:
                        # Try to parse as ISO date
                        due_date = datetime.fromisoformat(due_date_str).date().isoformat()
                except ValueError:
                    pass
            
            # Extract priority
            if "priority" in prompt_lower:
                priority_parts = prompt.split("priority", 1)[1].strip()
                if priority_parts.lower().startswith("high"):
                    priority = "high"
                elif priority_parts.lower().startswith("low"):
                    priority = "low"
                else:
                    priority = "medium"
            
            # Add the task
            if title:
                task = self.add_task(title, description, due_date, priority)
                
                # Format response
                response = f"✅ Task added: {task['title']}\n"
                if description:
                    response += f"Description: {description}\n"
                if due_date:
                    response += f"Due date: {due_date}\n"
                response += f"Priority: {priority}\n"
                response += f"ID: {task['id']}"
                
                return response
            else:
                return "⚠️ Please provide a task title"
        
        # List tasks command
        elif "list tasks" in prompt_lower or "show tasks" in prompt_lower:
            # Extract filters
            status = None
            if "pending" in prompt_lower:
                status = "pending"
            elif "completed" in prompt_lower:
                status = "completed"
            
            # Get tasks
            tasks = self.get_tasks(status=status)
            
            if not tasks:
                return "📝 No tasks found"
            
            # Format response
            response = f"📝 Tasks ({len(tasks)}):\n\n"
            
            for task in tasks:
                status_emoji = "✅" if task["status"] == "completed" else "⏳"
                priority_emoji = "🔴" if task["priority"] == "high" else "🟡" if task["priority"] == "medium" else "🟢"
                
                response += f"{status_emoji} {priority_emoji} {task['title']}"
                
                if task["due_date"]:
                    response += f" (Due: {task['due_date']})"
                
                response += f" [ID: {task['id']}]\n"
            
            return response
        
        # Complete task command
        elif "complete task" in prompt_lower or "mark task" in prompt_lower and "complete" in prompt_lower:
            # Extract task ID
            task_id = None
            
            # Try to extract ID
            if "id" in prompt_lower:
                id_parts = prompt.split("id", 1)[1].strip()
                if " " in id_parts:
                    task_id = id_parts.split(" ", 1)[0].strip()
                else:
                    task_id = id_parts
            else:
                # Try to extract the last word as ID
                words = prompt.split()
                if words:
                    task_id = words[-1]
            
            # Complete the task
            if task_id:
                task = self.complete_task(task_id)
                
                if task:
                    return f"✅ Task completed: {task['title']}"
                else:
                    return f"⚠️ Task not found with ID: {task_id}"
            else:
                return "⚠️ Please provide a task ID"
        
        # Delete task command
        elif "delete task" in prompt_lower or "remove task" in prompt_lower:
            # Extract task ID
            task_id = None
            
            # Try to extract ID
            if "id" in prompt_lower:
                id_parts = prompt.split("id", 1)[1].strip()
                if " " in id_parts:
                    task_id = id_parts.split(" ", 1)[0].strip()
                else:
                    task_id = id_parts
            else:
                # Try to extract the last word as ID
                words = prompt.split()
                if words:
                    task_id = words[-1]
            
            # Delete the task
            if task_id:
                success = self.delete_task(task_id)
                
                if success:
                    return f"✅ Task deleted with ID: {task_id}"
                else:
                    return f"⚠️ Task not found with ID: {task_id}"
            else:
                return "⚠️ Please provide a task ID"
        
        # Due tasks command
        elif "due tasks" in prompt_lower or "upcoming tasks" in prompt_lower:
            # Extract days
            days = 7
            
            if "today" in prompt_lower:
                days = 0
            elif "tomorrow" in prompt_lower:
                days = 1
            elif "week" in prompt_lower:
                days = 7
            elif "month" in prompt_lower:
                days = 30
            
            # Get due tasks
            tasks = self.get_due_tasks(days)
            
            if not tasks:
                return f"📝 No tasks due in the next {days} day(s)"
            
            # Format response
            response = f"📝 Tasks due in the next {days} day(s) ({len(tasks)}):\n\n"
            
            for task in tasks:
                priority_emoji = "🔴" if task["priority"] == "high" else "🟡" if task["priority"] == "medium" else "🟢"
                
                response += f"⏳ {priority_emoji} {task['title']}"
                
                if task["due_date"]:
                    response += f" (Due: {task['due_date']})"
                
                response += f" [ID: {task['id']}]\n"
            
            return response
        
        # Status command
        elif "status" in prompt_lower:
            pending_count = len(self.get_tasks(status="pending"))
            completed_count = len(self.get_tasks(status="completed"))
            due_count = len(self.get_due_tasks(7))
            
            return (
                f"📝 Task Scheduler Status:\n"
                f"• Running: {'Yes' if self.running else 'No'}\n"
                f"• Thread alive: {'Yes' if self._thread and self._thread.is_alive() else 'No'}\n"
                f"• Pending tasks: {pending_count}\n"
                f"• Completed tasks: {completed_count}\n"
                f"• Tasks due in the next 7 days: {due_count}\n"
                f"• Auto-scheduling: {'Enabled' if self.config['auto_schedule'] else 'Disabled'}"
            )
        
        # Help command
        elif "help" in prompt_lower:
            return (
                f"📝 Task Scheduler Commands:\n"
                f"• add task <title> [description <desc>] [due <date>] [priority <priority>] - Add a new task\n"
                f"• list tasks [pending|completed] - List tasks\n"
                f"• complete task <id> - Mark a task as completed\n"
                f"• delete task <id> - Delete a task\n"
                f"• due tasks [today|tomorrow|week|month] - Show tasks due in the specified period\n"
                f"• status - Show agent status\n"
                f"• help - Show this help message"
            )
        
        # Unknown command
        else:
            return (
                f"📝 Task Scheduler Agent here! I can help you manage your tasks.\n\n"
                f"Try these commands:\n"
                f"• add task Buy groceries due tomorrow priority high\n"
                f"• list tasks\n"
                f"• due tasks week\n"
                f"• complete task 1\n"
                f"• help"
            )
    
    def diagnose(self):
        """Return diagnostic information about the agent"""
        return {
            "name": self.name,
            "status": "running" if self.heartbeat() else "stopped",
            "thread_alive": self._thread.is_alive() if self._thread else False,
            "tasks_count": len(self.tasks),
            "reminders_count": len(self.reminders),
            "auto_schedule": self.config["auto_schedule"]
        }

# Example usage
if __name__ == "__main__":
    agent = TaskSchedulerAgent()
    agent.start()
    
    # Example commands
    print(agent.handle_input("add task Buy groceries due tomorrow priority high"))
    print(agent.handle_input("list tasks"))
    print(agent.handle_input("due tasks week"))
    print(agent.handle_input("status"))
    
    agent.stop()
