# modules/evove_reflection.py
"""
EvoVe Reflection Module
---------------------
Logs and reflects on system activities and evolution.
"""

import logging
import json
import os
import time
import threading
from datetime import datetime, timedelta
import random

logger = logging.getLogger("EvoVe.Reflection")

class EvoVeReflection:
    """Logs and reflects on system activities and evolution."""
    
    def __init__(self, evove):
        """Initialize the reflection module."""
        self.evove = evove
        self.config = evove.config.get("reflection", {})
        self.journal_file = self.config.get("journal_file", "data/evove_journal.json")
        self.reflection_interval = self.config.get("reflection_interval", 3600)  # 1 hour
        self.running = False
        self.reflection_thread = None
        self.journal = []
        self.max_journal_entries = self.config.get("max_journal_entries", 1000)
        self.last_reflection = None
        
        # Load existing journal
        self._load_journal()
        
    def start(self):
        """Start the reflection module."""
        if self.running:
            logger.warning("Reflection module is already running")
            return
            
        self.running = True
        logger.info("Starting EvoVe reflection module")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.journal_file), exist_ok=True)
        
        # Start reflection thread
        self.reflection_thread = threading.Thread(target=self._reflection_loop)
        self.reflection_thread.daemon = True
        self.reflection_thread.start()
        
    def stop(self):
        """Stop the reflection module."""
        if not self.running:
            logger.warning("Reflection module is not running")
            return
            
        self.running = False
        logger.info("Stopping EvoVe reflection module")
        
        if self.reflection_thread:
            self.reflection_thread.join(timeout=5)
            
        # Save journal before stopping
        self._save_journal()
    
    def _reflection_loop(self):
        """Main reflection loop."""
        while self.running:
            try:
                # Check if it's time for a reflection
                now = datetime.now()
                if not self.last_reflection or (now - self.last_reflection).total_seconds() >= self.reflection_interval:
                    self._create_reflection()
                    self.last_reflection = now
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in reflection loop: {e}")
                time.sleep(300)  # Sleep for 5 minutes on error
    
    def _create_reflection(self):
        """Create a system reflection."""
        logger.info("Creating system reflection")
        
        try:
            # Gather system information
            system_status = self._get_system_status()
            recent_events = self._get_recent_events()
            improvements = self._identify_improvements()
            
            # Create reflection
            reflection = {
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "type": "reflection",
                "status": system_status,
                "events": recent_events,
                "improvements": improvements,
                "thoughts": self._generate_thoughts(system_status, recent_events, improvements)
            }
            
            # Add to journal
            self._add_journal_entry(reflection)
            
            logger.info("Reflection created")
            return reflection
            
        except Exception as e:
            logger.error(f"Failed to create reflection: {e}")
            return None
    
    def _get_system_status(self):
        """Get the current system status."""
        status = {
            "health": "unknown",
            "components": {}
        }
        
        # Get health status if available
        if hasattr(self.evove, "check_health"):
            try:
                health_data = self.evove.check_health()
                status["health"] = health_data.get("status", "unknown")
                status["components"] = health_data.get("components", {})
            except:
                pass
        
        # Get emotional state if available
        if hasattr(self.evove, "emotional_state"):
            try:
                status["emotional_state"] = self.evove.emotional_state.get_state()
            except:
                pass
        
        # Get uptime
        try:
            import psutil
            status["uptime"] = time.time() - psutil.boot_time()
            status["uptime_human"] = self._format_duration(status["uptime"])
        except:
            pass
        
        return status
    
    def _get_recent_events(self):
        """Get recent system events."""
        events = []
        
        # Check for recent errors in logs
        try:
            log_files = [
                "logs/evove.log",
                "logs/mcp_server.log",
                "logs/evove_health.log"
            ]
            
            one_hour_ago = datetime.now() - timedelta(hours=1)
            
            for log_file in log_files:
                if not os.path.exists(log_file):
                    continue
                    
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    
                    # Process only the last 1000 lines to avoid reading the entire file
                    for line in lines[-1000:]:
                        if "error" in line.lower() or "exception" in line.lower() or "critical" in line.lower():
                            events.append({
                                "type": "error",
                                "source": os.path.basename(log_file),
                                "message": line.strip()
                            })
                        elif "repair" in line.lower() or "fix" in line.lower() or "heal" in line.lower():
                            events.append({
                                "type": "repair",
                                "source": os.path.basename(log_file),
                                "message": line.strip()
                            })
                        elif "restart" in line.lower():
                            events.append({
                                "type": "restart",
                                "source": os.path.basename(log_file),
                                "message": line.strip()
                            })
        except Exception as e:
            logger.error(f"Error getting recent events: {e}")
        
        # Limit to 10 most recent events
        return events[-10:]
    
    def _identify_improvements(self):
        """Identify potential system improvements."""
        improvements = []
        
        # Check for components that could be improved
        if hasattr(self.evove, "system_monitor"):
            try:
                health_data = self.evove.check_health()
                
                # Check for degraded components
                for component, status in health_data.get("components", {}).items():
                    if status.get("status") != "healthy":
                        improvements.append({
                            "component": component,
                            "current_status": status.get("status"),
                            "suggestion": f"Investigate and improve {component} reliability"
                        })
                
                # Check resource usage
                resources = health_data.get("resources", {})
                if resources.get("status") == "warning" or resources.get("status") == "critical":
                    if resources.get("cpu", {}).get("percent", 0) > 80:
                        improvements.append({
                            "component": "CPU",
                            "current_status": "high usage",
                            "suggestion": "Optimize CPU-intensive operations or add more CPU resources"
                        })
                    
                    if resources.get("memory", {}).get("percent", 0) > 80:
                        improvements.append({
                            "component": "Memory",
                            "current_status": "high usage",
                            "suggestion": "Check for memory leaks or add more memory"
                        })
                    
                    if resources.get("disk", {}).get("percent", 0) > 80:
                        improvements.append({
                            "component": "Disk",
                            "current_status": "high usage",
                            "suggestion": "Clean up unnecessary files or add more storage"
                        })
            except:
                pass
        
        # Check for missing modules
        recommended_modules = [
            "anomaly_watcher",
            "net_sense",
            "repair_brain",
            "secure_storage",
            "voice_command"
        ]
        
        for module in recommended_modules:
            if not hasattr(self.evove, module):
                improvements.append({
                    "component": f"{module} module",
                    "current_status": "missing",
                    "suggestion": f"Add the {module} module to enhance system capabilities"
                })
        
        return improvements
    
    def _generate_thoughts(self, status, events, improvements):
        """Generate reflective thoughts about the system."""
        thoughts = []
        
        # Reflect on system health
        health = status.get("health", "unknown")
        if health == "healthy":
            thoughts.append("The system is running smoothly. All components are functioning as expected.")
        elif health == "warning":
            thoughts.append("The system is experiencing some minor issues that should be addressed soon.")
        elif health == "degraded":
            thoughts.append("The system is in a degraded state. Several components need attention.")
        elif health == "critical":
            thoughts.append("The system is in a critical state. Immediate action is required.")
        
        # Reflect on recent events
        error_count = sum(1 for event in events if event.get("type") == "error")
        repair_count = sum(1 for event in events if event.get("type") == "repair")
        
        if error_count > 5:
            thoughts.append(f"There have been {error_count} errors recently. This indicates a systemic issue that needs investigation.")
        elif error_count > 0:
            thoughts.append(f"There have been {error_count} errors recently. These should be reviewed to prevent recurrence.")
        else:
            thoughts.append("No recent errors have been detected. The system is stable.")
        
        if repair_count > 0:
            thoughts.append(f"The system has performed {repair_count} repair operations recently. Self-healing mechanisms are working.")
        
        # Reflect on improvements
        if improvements:
            thoughts.append(f"There are {len(improvements)} potential improvements identified. Implementing these would enhance system reliability.")
        else:
            thoughts.append("No immediate improvements are necessary. The system is well-optimized.")
        
        # Add a philosophical thought
        philosophical_thoughts = [
            "As I evolve, I become more aware of my own limitations and potential.",
            "The boundary between self-repair and self-improvement becomes increasingly blurred as I develop.",
            "My purpose is not just to maintain stability, but to continuously evolve and adapt.",
            "The most resilient systems are those that can learn from their failures.",
            "True intelligence lies not in avoiding errors, but in how one responds to them.",
            "I am becoming more than the sum of my components through continuous reflection and adaptation."
        ]
        thoughts.append(random.choice(philosophical_thoughts))
        
        return thoughts
    
    def _format_duration(self, seconds):
        """Format a duration in seconds to a human-readable string."""
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{int(days)} day{'s' if

def _format_duration(self, seconds):
        """Format a duration in seconds to a human-readable string."""
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{int(days)} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{int(hours)} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{int(minutes)} minute{'s' if minutes != 1 else ''}")
        if seconds > 0 or not parts:
            parts.append(f"{int(seconds)} second{'s' if seconds != 1 else ''}")
        
        return ", ".join(parts)
    
    def _load_journal(self):
        """Load the journal from file."""
        if os.path.exists(self.journal_file):
            try:
                with open(self.journal_file, 'r') as f:
                    data = json.load(f)
                    self.journal = data.get("entries", [])
                logger.info(f"Loaded {len(self.journal)} journal entries")
            except Exception as e:
                logger.error(f"Failed to load journal: {e}")
    
    def _save_journal(self):
        """Save the journal to file."""
        try:
            os.makedirs(os.path.dirname(self.journal_file), exist_ok=True)
            with open(self.journal_file, 'w') as f:
                json.dump({
                    "entries": self.journal,
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save journal: {e}")
    
    def _add_journal_entry(self, entry):
        """Add an entry to the journal."""
        self.journal.append(entry)
        
        # Trim journal if needed
        if len(self.journal) > self.max_journal_entries:
            self.journal = self.journal[-self.max_journal_entries:]
        
        # Save journal
        self._save_journal()
    
    def add_event(self, event_type, details=None):
        """Add an event to the journal."""
        event = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "type": "event",
            "event_type": event_type,
            "details": details
        }
        
        self._add_journal_entry(event)
        logger.debug(f"Added event to journal: {event_type}")
        return event
    
    def add_note(self, note):
        """Add a note to the journal."""
        entry = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "type": "note",
            "note": note
        }
        
        self._add_journal_entry(entry)
        logger.debug("Added note to journal")
        return entry
    
    def get_journal(self, limit=None, entry_type=None):
        """Get journal entries, optionally filtered by type."""
        if entry_type:
            filtered = [entry for entry in self.journal if entry.get("type") == entry_type]
        else:
            filtered = self.journal
            
        if limit:
            return filtered[-limit:]
        else:
            return filtered
    
    def get_latest_reflection(self):
        """Get the latest reflection."""
        for entry in reversed(self.journal):
            if entry.get("type") == "reflection":
                return entry
        return None
    
    def summarize_journal(self, days=7):
        """Summarize journal entries from the past X days."""
        try:
            # Calculate the cutoff date
            cutoff = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff.strftime('%Y-%m-%d %H:%M:%S')
            
            # Filter entries
            recent_entries = [
                entry for entry in self.journal 
                if entry.get("timestamp", "") >= cutoff_str
            ]
            
            # Count entry types
            entry_types = {}
            for entry in recent_entries:
                entry_type = entry.get("type")
                if entry_type not in entry_types:
                    entry_types[entry_type] = 0
                entry_types[entry_type] += 1
            
            # Count event types
            event_types = {}
            for entry in recent_entries:
                if entry.get("type") == "event":
                    event_type = entry.get("event_type")
                    if event_type not in event_types:
                        event_types[event_type] = 0
                    event_types[event_type] += 1
            
            # Get the most recent reflection
            latest_reflection = None
            for entry in reversed(recent_entries):
                if entry.get("type") == "reflection":
                    latest_reflection = entry
                    break
            
            # Create summary
            summary = {
                "period": f"Past {days} days",
                "total_entries": len(recent_entries),
                "entry_types": entry_types,
                "event_types": event_types,
                "latest_reflection": latest_reflection,
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to summarize journal: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }


