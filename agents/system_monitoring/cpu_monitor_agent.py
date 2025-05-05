"""
CPU Monitor Agent - Monitors CPU usage and process activity, alerting if usage is abnormally high or suspicious.
"""

import logging
import time
import threading
import json
import os
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from collections import deque

class CPUMonitorAgent:
    def __init__(self):
        self.name = "CPU Monitor Agent"
        self.status = "active"
        self.running = False
        self.thresholds = {
            "high_cpu": 80.0,  # High CPU usage threshold (percentage)
            "critical_cpu": 95.0,  # Critical CPU usage threshold (percentage)
            "sustained_period": 60,  # Sustained high usage period (seconds)
            "process_cpu_threshold": 50.0  # Process CPU usage threshold (percentage)
        }
        self.cpu_history = deque(maxlen=100)  # Store recent CPU measurements
        self.process_history = {}  # pid -> list of CPU usage
        self.alerts = []
        self.max_alerts = 100
        self.log_file = Path("logs/cpu_monitor.log")
        self.config_file = Path("config/cpu_thresholds.json")
        self.data_file = Path("memory/cpu_data.json")
        
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
        self.load_config()
        
        self.logger.info(f"{self.name} initialized")
        
        # Thread for monitoring
        self._thread = None
        self._thread = None
        
        # Event bus reference (will be set by orchestrator)
        self.event_bus = None

    def load_config(self):
        """Load CPU monitoring thresholds from config file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.thresholds = json.load(f)
                    self.logger.info(f"Loaded CPU monitoring thresholds")
            else:
                # Create default thresholds if file doesn't exist
                os.makedirs(self.config_file.parent, exist_ok=True)
                with open(self.config_file, 'w') as f:
                    json.dump(self.thresholds, f, indent=2)
                self.logger.info("Created default CPU monitoring thresholds")
        except Exception as e:
            self.logger.error(f"Error loading CPU monitoring thresholds: {e}")

    def save_data(self):
        """Save CPU monitoring data to file"""
        try:
            os.makedirs(self.data_file.parent, exist_ok=True)
            
            # Convert deque to list for serialization
            cpu_history_list = list(self.cpu_history)
            
            with open(self.data_file, 'w') as f:
                json.dump({
                    "cpu_history": cpu_history_list,
                    "alerts": self.alerts[:self.max_alerts],
                    "last_update": datetime.now().isoformat()
                }, f, indent=2)
            self.logger.debug(f"Saved CPU monitoring data")
        except Exception as e:
            self.logger.error(f"Error saving CPU monitoring data: {e}")

    def add_alert(self, alert_type, details, severity="medium"):
        """Add a new CPU alert"""
        alert = {
            "type": alert_type,
            "details": details,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to the beginning of the list (most recent first)
        self.alerts.insert(0, alert)
        
        # Trim the list if it exceeds the maximum
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[:self.max_alerts]
        
        # Log the alert
        self.logger.warning(f"CPU alert: {alert_type} - {details}")
        
        # Emit event if event bus is available
        if self.event_bus:
            self.event_bus.emit("CPU_ALERT", {
                "alert": alert,
                "source_agent": self.name
            })
        
        return alert

    def check_cpu_usage(self):
        """Check current CPU usage and detect anomalies"""
        try:
            # Get current CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Record the measurement with timestamp
            measurement = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent
            }
            self.cpu_history.append(measurement)
            
            # Check if CPU usage is high
            if cpu_percent >= self.thresholds["critical_cpu"]:
                self.add_alert("critical_cpu_usage", f"CPU usage is critical: {cpu_percent}%", "high")
            elif cpu_percent >= self.thresholds["high_cpu"]:
                self.add_alert("high_cpu_usage", f"CPU usage is high: {cpu_percent}%", "medium")
            
            # Check for sustained high usage
            if len(self.cpu_history) >= 5:  # Need at least a few measurements
                recent_measurements = list(self.cpu_history)[-5:]
                avg_recent_cpu = sum(m["cpu_percent"] for m in recent_measurements) / len(recent_measurements)
                
                if avg_recent_cpu >= self.thresholds["high_cpu"]:
                    self.add_alert("sustained_high_cpu", f"Sustained high CPU usage: {avg_recent_cpu}%", "medium")
            
            return cpu_percent
        except Exception as e:
            self.logger.error(f"Error checking CPU usage: {e}")
            return None

    def check_process_usage(self):
        """Check CPU usage by process and detect anomalies"""
        try:
            # Get all running processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    # Get process info
                    proc_info = proc.info
                    
                    # Skip processes with 0 CPU usage
                    if proc_info['cpu_percent'] is None or proc_info['cpu_percent'] < 0.1:
                        continue
                    
                    # Add to our list
                    processes.append(proc_info)
                    
                    # Track history for this process
                    pid = proc_info['pid']
                    if pid not in self.process_history:
                        self.process_history[pid] = deque(maxlen=10)
                    
                    self.process_history[pid].append({
                        "timestamp": datetime.now().isoformat(),
                        "cpu_percent": proc_info['cpu_percent']
                    })
                    
                    # Check if process CPU usage is high
                    if proc_info['cpu_percent'] >= self.thresholds["process_cpu_threshold"]:
                        self.add_alert(
                            "high_process_cpu", 
                            f"Process {proc_info['name']} (PID {pid}) has high CPU usage: {proc_info['cpu_percent']}%",
                            "medium"
                        )
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Sort processes by CPU usage (highest first)
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            return processes[:10]  # Return top 10 processes
        except Exception as e:
            self.logger.error(f"Error checking process usage: {e}")
            return []

    def monitor_cpu(self):
        """Monitor CPU usage and processes"""
        self.logger.info("Starting CPU monitoring")
        self.running = True
        
        save_counter = 0
        
        while self.running:
            # Check CPU usage
            cpu_percent = self.check_cpu_usage()
            self.logger.debug(f"Current CPU usage: {cpu_percent}%")
            
            # Check process usage every 5 cycles
            if save_counter % 5 == 0:
                top_processes = self.check_process_usage()
                self.logger.debug(f"Top processes: {len(top_processes)}")
            
            # Save data every 10 cycles
            if save_counter % 10 == 0:
                self.save_data()
            
            save_counter += 1
            
            # Sleep for a bit
            time.sleep(5)

    def start(self):
        """Start the CPU monitoring in a background thread"""
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.monitor_cpu, daemon=True)
            self._thread.start()
            self.logger.info("CPU monitoring started")
            return True
        return False

    def stop(self):
        """Stop the CPU monitoring"""
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
            self.logger.info("CPU monitoring stopped")
            
            # Save data one last time
            self.save_data()
            
            return True
        return False

    def heartbeat(self):
        """Check if the agent is running properly"""
        if self._thread and self._thread.is_alive():
            self.logger.debug("Heartbeat check: OK")
            return True
        self.logger.warning("Heartbeat check: Failed - thread not running")
        return False

    def run(self):
        """Run the agent (for CLI execution)"""
        # For CLI execution, do an immediate CPU check and return the results
        cpu_percent = self.check_cpu_usage()
        top_processes = self.check_process_usage()
        
        return {
            "cpu_percent": cpu_percent,
            "top_processes": top_processes,
            "alerts_count": len(self.alerts)
        }

    def handle_event(self, event):
        """Handle events from the event bus"""
        event_type = event.get("type", "")
        data = event.get("data", {})
        
        if event_type == "CHECK_CPU":
            # Perform an immediate CPU check
            cpu_percent = self.check_cpu_usage()
            
            # Emit the result if event bus is available
            if self.event_bus:
                self.event_bus.emit("CPU_STATUS", {
                    "cpu_percent": cpu_percent,
                    "source_agent": self.name,
                    "request_id": data.get("request_id")
                })
            
            return True
        
        elif event_type == "CHECK_PROCESSES":
            # Perform an immediate process check
            top_processes = self.check_process_usage()
            
            # Emit the result if event bus is available
            if self.event_bus:
                self.event_bus.emit("PROCESS_STATUS", {
                    "processes": top_processes,
                    "source_agent": self.name,
                    "request_id": data.get("request_id")
                })
            
            return True
        
        elif event_type == "UPDATE_THRESHOLDS":
            # Update monitoring thresholds
            if "thresholds" in data:
                new_thresholds = data["thresholds"]
                # Update only the provided thresholds
                for key, value in new_thresholds.items():
                    if key in self.thresholds:
                        self.thresholds[key] = value
                
                # Save the updated thresholds
                with open(self.config_file, 'w') as f:
                    json.dump(self.thresholds, f, indent=2)
                
                self.logger.info(f"Updated CPU monitoring thresholds: {new_thresholds}")
                return True
        
        return False

    def diagnose(self):
        """Return diagnostic information about the agent"""
        # Get current CPU usage
        try:
            cpu_percent = psutil.cpu_percent(interval=0.5)
        except:
            cpu_percent = None
        
        return {
            "name": self.name,
            "status": "running" if self.heartbeat() else "stopped",
            "current_cpu": cpu_percent,
            "alerts_count": len(self.alerts),
            "history_entries": len(self.cpu_history),
            "thread_alive": self._thread.is_alive() if self._thread else False,
            "thresholds": self.thresholds
        }
