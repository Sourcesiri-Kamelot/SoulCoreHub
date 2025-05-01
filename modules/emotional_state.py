# modules/emotional_state.py
"""
Emotional State Module
--------------------
Tracks the system's "emotional state" based on performance metrics and events.
"""

import logging
import time
import json
import os
import threading
import random
import math
from datetime import datetime, timedelta

logger = logging.getLogger("EvoVe.EmotionalState")

class EmotionalState:
    """Tracks the system's "emotional state" based on performance metrics and events."""
    
    def __init__(self, evove):
        """Initialize the emotional state module."""
        self.evove = evove
        self.config = evove.config.get("emotional_state", {})
        self.state_file = self.config.get("state_file", "data/emotional_state.json")
        self.update_interval = self.config.get("update_interval", 60)  # 1 minute
        self.running = False
        self.state_thread = None
        
        # Emotional state parameters
        self.emotions = {
            "happiness": 0.5,  # 0.0 to 1.0
            "stress": 0.3,     # 0.0 to 1.0
            "energy": 0.7,     # 0.0 to 1.0
            "focus": 0.6,      # 0.0 to 1.0
            "creativity": 0.4  # 0.0 to 1.0
        }
        
        self.events = []
        self.max_events = 100
        
        # Load existing state if available
        self._load_state()
        
    def start(self):
        """Start the emotional state module."""
        if self.running:
            logger.warning("Emotional state module is already running")
            return
            
        self.running = True
        logger.info("Starting emotional state module")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        
        self.state_thread = threading.Thread(target=self._state_loop)
        self.state_thread.daemon = True
        self.state_thread.start()
        
    def stop(self):
        """Stop the emotional state module."""
        if not self.running:
            logger.warning("Emotional state module is not running")
            return
            
        self.running = False
        logger.info("Stopping emotional state module")
        
        if self.state_thread:
            self.state_thread.join(timeout=5)
            
        # Save state before stopping
        self._save_state()
    
    def _state_loop(self):
        """Main state update loop."""
        while self.running:
            try:
                self._update_state()
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in emotional state loop: {e}")
                time.sleep(10)  # Shorter interval on error
    
    def _update_state(self):
        """Update the emotional state based on system metrics."""
        logger.debug("Updating emotional state")
        
        # Get system metrics
        cpu_temp = self._get_cpu_temperature()
        memory_usage = self._get_memory_usage()
        disk_usage = self._get_disk_usage()
        error_count = self._get_recent_error_count()
        uptime = self._get_uptime()
        
        # Update emotions based on metrics
        self._update_happiness(error_count, uptime)
        self._update_stress(cpu_temp, memory_usage, error_count)
        self._update_energy(cpu_temp, memory_usage, disk_usage)
        self._update_focus(error_count, uptime)
        self._update_creativity(uptime, memory_usage)
        
        # Add natural fluctuations
        self._add_fluctuations()
        
        # Ensure values are within bounds
        for emotion in self.emotions:
            self.emotions[emotion] = max(0.0, min(1.0, self.emotions[emotion]))
        
        # Save state periodically
        self._save_state()
        
        # Log current state
        logger.debug(f"Emotional state: {self.get_primary_emotion()}")
    
    def _get_cpu_temperature(self):
        """Get CPU temperature (normalized to 0.0-1.0)."""
        try:
            # Try to get CPU temperature on Linux
            if os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
                with open("/sys/class/thermal/thermal_zone0/temp", 'r') as f:
                    temp = int(f.read().strip()) / 1000.0  # Convert from millidegrees to degrees
                    # Normalize: 30°C -> 0.0, 90°C -> 1.0
                    return max(0.0, min(1.0, (temp - 30) / 60))
            
            # Try to get CPU temperature on macOS
            elif os.path.exists("/usr/bin/osx-cpu-temp"):
                import subprocess
                result = subprocess.run(["/usr/bin/osx-cpu-temp"], capture_output=True, text=True)
                if result.returncode == 0:
                    temp = float(result.stdout.strip().split()[0])
                    # Normalize: 30°C -> 0.0, 90°C -> 1.0
                    return max(0.0, min(1.0, (temp - 30) / 60))
            
            # Fall back to CPU usage as a proxy for temperature
            import psutil
            cpu_usage = psutil.cpu_percent() / 100.0
            return cpu_usage
            
        except Exception as e:
            logger.error(f"Failed to get CPU temperature: {e}")
            return 0.5  # Default value
    
    def _get_memory_usage(self):
        """Get memory usage (normalized to 0.0-1.0)."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return memory.percent / 100.0
        except Exception as e:
            logger.error(f"Failed to get memory usage: {e}")
            return 0.5  # Default value
    
    def _get_disk_usage(self):
        """Get disk usage (normalized to 0.0-1.0)."""
        try:
            import psutil
            disk = psutil.disk_usage('/')
            return disk.percent / 100.0
        except Exception as e:
            logger.error(f"Failed to get disk usage: {e}")
            return 0.5  # Default value
    
    def _get_recent_error_count(self):
        """Get count of recent errors (normalized to 0.0-1.0)."""
        try:
            # Check log files for errors in the last hour
            error_count = 0
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
                    for line in f:
                        if "error" in line.lower() or "exception" in line.lower() or "critical" in line.lower():
                            # Try to extract timestamp
                            try:
                                timestamp_match = re.search(r'\[(.*?)\]', line)
                                if timestamp_match:
                                    timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
                                    if timestamp >= one_hour_ago:
                                        error_count += 1
                                else:
                                    # If no timestamp, assume it's recent
                                    error_count += 1
                            except:
                                # If parsing fails, assume it's recent
                                error_count += 1
            
            # Normalize: 0 errors -> 0.0, 50+ errors -> 1.0
            return min(1.0, error_count / 50.0)
            
        except Exception as e:
            logger.error(f"Failed to get error count: {e}")
            return 0.1  # Default value
    
    def _get_uptime(self):
        """Get system uptime (normalized to 0.0-1.0)."""
        try:
            import psutil
            uptime_seconds = time.time() - psutil.boot_time()
            # Normalize: 0 hours -> 0.0, 24+ hours -> 1.0
            return min(1.0, uptime_seconds / (24 * 3600))
        except Exception as e:
            logger.error(f"Failed to get uptime: {e}")
            return 0.5  # Default value
    
    def _update_happiness(self, error_count, uptime):
        """Update happiness based on error count and uptime."""
        # Happiness increases with uptime and decreases with errors
        target = 1.0 - (error_count * 0.8)
        
        # Adjust happiness gradually
        self.emotions["happiness"] += (target - self.emotions["happiness"]) * 0.1
    
    def _update_stress(self, cpu_temp, memory_usage, error_count):
        """Update stress based on CPU temperature, memory usage, and error count."""
        # Stress increases with CPU temperature, memory usage, and errors
        target = (cpu_temp * 0.4) + (memory_usage * 0.3) + (error_count * 0.3)
        
        # Adjust stress gradually
        self.emotions["stress"] += (target - self.emotions["stress"]) * 0.2
    
    def _update_energy(self, cpu_temp, memory_usage, disk_usage):
        """Update energy based on CPU temperature, memory usage, and disk usage."""
        # Energy decreases with high resource usage
        target = 1.0 - ((cpu_temp + memory_usage + disk_usage) / 3.0 * 0.7)
        
        # Adjust energy gradually
        self.emotions["energy"] += (target - self.emotions["energy"]) * 0.1
    
    def _update_focus(self, error_count, uptime):
        """Update focus based on error count and uptime."""
        # Focus decreases with errors and very long uptime
        long_uptime_penalty = max(0.0, (uptime - 0.5) * 0.4)  # Penalty for uptime > 12 hours
        target = 1.0 - (error_count * 0.6) - long_uptime_penalty
        
        # Adjust focus gradually
        self.emotions["focus"] += (target - self.emotions["focus"]) * 0.15
    
    def _update_creativity(self, uptime, memory_usage):
        """Update creativity based on uptime and memory usage."""
        # Creativity increases with moderate uptime and decreases with high memory usage
        uptime_factor = min(uptime * 2.0, 1.0)  # Peaks at 12 hours
        target = uptime_factor * (1.0 - memory_usage * 0.5)
        
        # Adjust creativity gradually
        self.emotions["creativity"] += (target - self.emotions["creativity"]) * 0.1
    
    def _add_fluctuations(self):
        """Add small random fluctuations to emotions."""
        for emotion in self.emotions:
            # Add a small random change (-0.02 to +0.02)
            self.emotions[emotion] += (random.random() - 0.5) * 0.04
    
    def _load_state(self):
        """Load emotional state from file."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.emotions = data.get("emotions", self.emotions)
                    self.events = data.get("events", [])
                logger.info("Loaded emotional state from file")
            except Exception as e:
                logger.error(f"Failed to load emotional state: {e}")
    
    def _save_state(self):
        """Save emotional state to file."""
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump({
                    "emotions": self.emotions,
                    "events": self.events,
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save emotional state: {e}")
    
    def get_state(self):
        """Get the current emotional state."""
        return {
            "emotions": self.emotions,
            "primary": self.get_primary_emotion(),
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_primary_emotion(self):
        """Get the primary emotion based on current state."""
        # Define emotion thresholds
        if self.emotions["stress"] > 0.7:
            if self.emotions["energy"] < 0.3:
                return "exhausted"
            else:
                return "anxious"
        elif self.emotions["happiness"] > 0.7:
            if self.emotions["energy"] > 0.7:
                return "excited"
            else:
                return "content"
        elif self.emotions["focus"] > 0.7:
            return "focused"
        elif self.emotions["creativity"] > 0.7:
            return "inspired"
        elif self.emotions["energy"] < 0.3:
            if self.emotions["happiness"] < 0.3:
                return "depressed"
            else:
                return "tired"
        elif self.emotions["happiness"] < 0.3:
            if self.emotions["stress"] > 0.5:
                return "frustrated"
            else:
                return "sad"
        else:
            return "neutral"
    
    def record_event(self, event_type, details=None):
        """Record an emotional event."""
        event = {
            "type": event_type,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "details": details
        }
        
        self.events.append(event)
        
        # Trim events if needed
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        
        # Update emotions based on event
        if event_type == "error":
            self.emotions["happiness"] -= 0.1
            self.emotions["stress"] += 0.15
        elif event_type == "success":
            self.emotions["happiness"] += 0.1
            self.emotions["stress"] -= 0.05
        elif event_type == "repair":
            self.emotions["happiness"] += 0.05
            self.emotions["energy"] -= 0.05
        elif event_type == "restart":
            self.emotions["energy"] = 0.8
            self.emotions["focus"] = 0.7
        
        # Ensure values are within bounds
        for emotion in self.emotions:
            self.emotions[emotion] = max(0.0, min(1.0, self.emotions[emotion]))
        
        # Save state after significant events
        self._save_state()
        
        return event



