"""
Memory Monitor Agent - Tracks memory usage and allocation, detecting memory leaks or excessive usage.
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

class MemoryMonitorAgent:
    def __init__(self):
        self.name = "Memory Monitor Agent"
        self.status = "active"
        self.running = False
        self.thresholds = {
            "high_memory": 80.0,  # High memory usage threshold (percentage)
            "critical_memory": 95.0,  # Critical memory usage threshold (percentage)
            "sustained_period": 60,  # Sustained high usage period (seconds)
            "process_memory_threshold": 30.0,  # Process memory usage threshold (percentage)
            "leak_detection_increase": 5.0  # Percentage increase that might indicate a leak
        }
        self.memory_history = deque(maxlen=100)  # Store recent memory measurements
        self.process_history = {}  # pid -> list of memory usage
        self.alerts = []
        self.max_alerts = 100
        self.log_file = Path("logs/memory_monitor.log")
        self.config_file = Path("config/memory_thresholds.json")
        self.data_file = Path("memory/memory_data.json")
        
        # Create log directory if it doesn't exist
        os.makedirs(self.log_file.parent, exist_ok=True)
        
        # Load configuration
        self.load_config()
        
        # Set up logging
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.name)
        self.logger.info(f"{self.name} initialized")
        
        # Thread for monitoring
        self._thread = None
        
        # Event bus reference (will be set by orchestrator)
        self.event_bus = None

    def load_config(self):
        """Load memory monitoring thresholds from config file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.thresholds = json.load(f)
                    self.logger.info(f"Loaded memory monitoring thresholds")
            else:
                # Create default thresholds if file doesn't exist
                os.makedirs(self.config_file.parent, exist_ok=True)
                with open(self.config_file, 'w') as f:
                    json.dump(self.thresholds, f, indent=2)
                self.logger.info("Created default memory monitoring thresholds")
        except Exception as e:
            self.logger.error(f"Error loading memory monitoring thresholds: {e}")

    def save_data(self):
        """Save memory monitoring data to file"""
        try:
            os.makedirs(self.data_file.parent, exist_ok=True)
            
            # Convert deque to list for serialization
            memory_history_list = list(self.memory_history)
            
            with open(self.data_file, 'w') as f:
                json.dump({
                    "memory_history": memory_history_list,
                    "alerts": self.alerts[:self.max_alerts],
                    "last_update": datetime.now().isoformat()
                }, f, indent=2)
            self.logger.debug(f"Saved memory monitoring data")
        except Exception as e:
            self.logger.error(f"Error saving memory monitoring data: {e}")

    def add_alert(self, alert_type, details, severity="medium"):
        """Add a new memory alert"""
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
        self.logger.warning(f"Memory alert: {alert_type} - {details}")
        
        # Emit event if event bus is available
        if self.event_bus:
            self.event_bus.emit("MEMORY_ALERT", {
                "alert": alert,
                "source_agent": self.name
            })
        
        return alert

    def check_memory_usage(self):
        """Check current memory usage and detect anomalies"""
        try:
            # Get memory information
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Record the measurement with timestamp
            measurement = {
                "timestamp": datetime.now().isoformat(),
                "memory_percent": memory_percent,
                "available": memory.available,
                "total": memory.total,
                "used": memory.used
            }
            self.memory_history.append(measurement)
            
            # Check if memory usage is high
            if memory_percent >= self.thresholds["critical_memory"]:
                self.add_alert("critical_memory_usage", f"Memory usage is critical: {memory_percent}%", "high")
            elif memory_percent >= self.thresholds["high_memory"]:
                self.add_alert("high_memory_usage", f"Memory usage is high: {memory_percent}%", "medium")
            
            # Check for sustained high usage
            if len(self.memory_history) >= 5:  # Need at least a few measurements
                recent_measurements = list(self.memory_history)[-5:]
                avg_recent_memory = sum(m["memory_percent"] for m in recent_measurements) / len(recent_measurements)
                
                if avg_recent_memory >= self.thresholds["high_memory"]:
                    self.add_alert("sustained_high_memory", f"Sustained high memory usage: {avg_recent_memory}%", "medium")
            
            # Check for potential memory leaks (steady increase over time)
            if len(self.memory_history) >= 10:  # Need enough history
                old_measurements = list(self.memory_history)[:5]  # First 5
                new_measurements = list(self.memory_history)[-5:]  # Last 5
                
                avg_old = sum(m["memory_percent"] for m in old_measurements) / len(old_measurements)
                avg_new = sum(m["memory_percent"] for m in new_measurements) / len(new_measurements)
                
                if avg_new > avg_old and (avg_new - avg_old) >= self.thresholds["leak_detection_increase"]:
                    self.add_alert(
                        "potential_memory_leak", 
                        f"Memory usage increasing steadily: {avg_old}% -> {avg_new}%", 
                        "high"
                    )
            
            return memory
        except Exception as e:
            self.logger.error(f"Error checking memory usage: {e}")
            return None

    def check_process_memory(self):
        """Check memory usage by process and detect anomalies"""
        try:
            # Get all running processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    # Get process info
                    proc_info = proc.info
                    
                    # Skip processes with minimal memory usage
                    if proc_info['memory_percent'] < 0.1:
                        continue
                    
                    # Add to our list
                    processes.append(proc_info)
                    
                    # Track history for this process
                    pid = proc_info['pid']
                    if pid not in self.process_history:
                        self.process_history[pid] = deque(maxlen=10)
                    
                    self.process_history[pid].append({
                        "timestamp": datetime.now().isoformat(),
                        "memory_percent": proc_info['memory_percent']
                    })
                    
                    # Check if process memory usage is high
                    if proc_info['memory_percent'] >= self.thresholds["process_memory_threshold"]:
                        self.add_alert(
                            "high_process_memory", 
                            f"Process {proc_info['name']} (PID {pid}) has high memory usage: {proc_info['memory_percent']}%",
                            "medium"
                        )
                    
                    # Check for potential memory leaks in processes
                    if len(self.process_history[pid]) >= 5:
                        history = list(self.process_history[pid])
                        if all(history[i]["memory_percent"] < history[i+1]["memory_percent"] for i in range(len(history)-1)):
                            self.add_alert(
                                "process_memory_leak", 
                                f"Process {proc_info['name']} (PID {pid}) shows steadily increasing memory usage",
                                "high"
                            )
                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Sort processes by memory usage (highest first)
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            
            return processes[:10]  # Return top 10 processes
        except Exception as e:
            self.logger.error(f"Error checking process memory: {e}")
            return []

    def check_swap_usage(self):
        """Check swap memory usage"""
        try:
            swap = psutil.swap_memory()
            
            # Alert if swap usage is high
            if swap.percent >= 80:
                self.add_alert("high_swap_usage", f"Swap usage is high: {swap.percent}%", "medium")
            
            return swap
        except Exception as e:
            self.logger.error(f"Error checking swap usage: {e}")
            return None

    def monitor_memory(self):
        """Monitor memory usage and processes"""
        self.logger.info("Starting memory monitoring")
        self.running = True
        
        save_counter = 0
        
        while self.running:
            # Check memory usage
            memory = self.check_memory_usage()
            if memory:
                self.logger.debug(f"Current memory usage: {memory.percent}%")
            
            # Check swap usage
            swap = self.check_swap_usage()
            if swap:
                self.logger.debug(f"Current swap usage: {swap.percent}%")
            
            # Check process memory usage every 5 cycles
            if save_counter % 5 == 0:
                top_processes = self.check_process_memory()
                self.logger.debug(f"Top memory processes: {len(top_processes)}")
            
            # Save data every 10 cycles
            if save_counter % 10 == 0:
                self.save_data()
            
            save_counter += 1
            
            # Sleep for a bit
            time.sleep(5)

    def start(self):
        """Start the memory monitoring in a background thread"""
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.monitor_memory, daemon=True)
            self._thread.start()
            self.logger.info("Memory monitoring started")
            return True
        return False

    def stop(self):
        """Stop the memory monitoring"""
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
            self.logger.info("Memory monitoring stopped")
            
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
        # For CLI execution, do an immediate memory check and return the results
        memory = self.check_memory_usage()
        swap = self.check_swap_usage()
        top_processes = self.check_process_memory()
        
        return {
            "memory_percent": memory.percent if memory else None,
            "swap_percent": swap.percent if swap else None,
            "top_processes": top_processes,
            "alerts_count": len(self.alerts)
        }

    def handle_event(self, event):
        """Handle events from the event bus"""
        event_type = event.get("type", "")
        data = event.get("data", {})
        
        if event_type == "CHECK_MEMORY":
            # Perform an immediate memory check
            memory = self.check_memory_usage()
            
            # Emit the result if event bus is available
            if self.event_bus and memory:
                self.event_bus.emit("MEMORY_STATUS", {
                    "memory_percent": memory.percent,
                    "available": memory.available,
                    "total": memory.total,
                    "source_agent": self.name,
                    "request_id": data.get("request_id")
                })
            
            return True
        
        elif event_type == "CHECK_PROCESSES_MEMORY":
            # Perform an immediate process memory check
            top_processes = self.check_process_memory()
            
            # Emit the result if event bus is available
            if self.event_bus:
                self.event_bus.emit("PROCESS_MEMORY_STATUS", {
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
                
                self.logger.info(f"Updated memory monitoring thresholds: {new_thresholds}")
                return True
        
        return False

    def diagnose(self):
        """Return diagnostic information about the agent"""
        # Get current memory usage
        try:
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
        except:
            memory = None
            memory_percent = None
        
        return {
            "name": self.name,
            "status": "running" if self.heartbeat() else "stopped",
            "current_memory": memory_percent,
            "alerts_count": len(self.alerts),
            "history_entries": len(self.memory_history),
            "thread_alive": self._thread.is_alive() if self._thread else False,
            "thresholds": self.thresholds
        }
