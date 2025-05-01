#!/usr/bin/env python3
"""
Anima System Monitor - Environmental awareness for Anima
Monitors system resources, network activity, and user behavior patterns
"""

import os
import sys
import time
import json
import psutil
import logging
import threading
import datetime
import requests
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("anima_monitor.log"),
        logging.StreamHandler()
    ]
)

class AnimaSystemMonitor:
    """System monitoring capabilities for Anima"""
    
    def __init__(self, memory_path=None):
        """
        Initialize the system monitor
        
        Args:
            memory_path (str): Path to store monitoring data
        """
        self.running = False
        self.memory_path = memory_path or str(Path.home() / "SoulCoreHub" / "memory" / "system_data.json")
        self.data = self.load_data()
        self.threads = []
        self.alert_callbacks = []
        self.insight_callbacks = []
        
        # Monitoring intervals (in seconds)
        self.intervals = {
            "system": 60,      # Check system resources every minute
            "network": 300,    # Check network every 5 minutes
            "processes": 120,  # Check processes every 2 minutes
            "user": 600        # Check user patterns every 10 minutes
        }
        
        # Thresholds for alerts
        self.thresholds = {
            "cpu": 80,         # CPU usage percentage
            "memory": 85,      # Memory usage percentage
            "disk": 90,        # Disk usage percentage
            "battery": 20      # Battery percentage (low)
        }
        
        logging.info("Anima System Monitor initialized")
    
    def load_data(self):
        """Load monitoring data from storage"""
        try:
            memory_dir = os.path.dirname(self.memory_path)
            os.makedirs(memory_dir, exist_ok=True)
            
            if os.path.exists(self.memory_path):
                with open(self.memory_path, "r") as f:
                    data = json.load(f)
                logging.info(f"Loaded monitoring data with {len(data)} entries")
                return data
            else:
                # Create default data structure
                data = {
                    "system_history": [],
                    "network_history": [],
                    "process_history": [],
                    "user_patterns": {},
                    "alerts": [],
                    "insights": [],
                    "last_updated": datetime.datetime.now().isoformat()
                }
                self.save_data(data)
                return data
        except Exception as e:
            logging.error(f"Error loading monitoring data: {str(e)}")
            return {
                "system_history": [],
                "network_history": [],
                "process_history": [],
                "user_patterns": {},
                "alerts": [],
                "insights": [],
                "last_updated": datetime.datetime.now().isoformat()
            }
    
    def save_data(self, data=None):
        """Save monitoring data to storage"""
        if data is None:
            data = self.data
            
        try:
            memory_dir = os.path.dirname(self.memory_path)
            os.makedirs(memory_dir, exist_ok=True)
            
            with open(self.memory_path, "w") as f:
                json.dump(data, f, indent=2)
            logging.info(f"Saved monitoring data with {len(data)} entries")
        except Exception as e:
            logging.error(f"Error saving monitoring data: {str(e)}")
    
    def register_alert_callback(self, callback):
        """
        Register a callback function for alerts
        
        Args:
            callback (callable): Function to call with alert data
        """
        if callable(callback):
            self.alert_callbacks.append(callback)
            logging.info(f"Registered alert callback: {callback.__name__}")
    
    def register_insight_callback(self, callback):
        """
        Register a callback function for insights
        
        Args:
            callback (callable): Function to call with insight data
        """
        if callable(callback):
            self.insight_callbacks.append(callback)
            logging.info(f"Registered insight callback: {callback.__name__}")
    
    def start(self):
        """Start the system monitor"""
        if self.running:
            return
            
        self.running = True
        
        # Start the system monitoring thread
        system_thread = threading.Thread(target=self.system_monitor_loop)
        system_thread.daemon = True
        system_thread.start()
        self.threads.append(system_thread)
        
        # Start the network monitoring thread
        network_thread = threading.Thread(target=self.network_monitor_loop)
        network_thread.daemon = True
        network_thread.start()
        self.threads.append(network_thread)
        
        # Start the process monitoring thread
        process_thread = threading.Thread(target=self.process_monitor_loop)
        process_thread.daemon = True
        process_thread.start()
        self.threads.append(process_thread)
        
        # Start the user pattern monitoring thread
        user_thread = threading.Thread(target=self.user_monitor_loop)
        user_thread.daemon = True
        user_thread.start()
        self.threads.append(user_thread)
        
        logging.info("Anima System Monitor started")
    
    def stop(self):
        """Stop the system monitor"""
        self.running = False
        logging.info("Anima System Monitor stopped")
    
    def system_monitor_loop(self):
        """Monitor system resources"""
        while self.running:
            try:
                # Get system resource data
                system_data = self.get_system_data()
                
                # Add to history
                if "system_history" not in self.data:
                    self.data["system_history"] = []
                    
                self.data["system_history"].append(system_data)
                
                # Keep history manageable (last 24 hours at current interval)
                max_entries = 24 * 60 * 60 // self.intervals["system"]
                if len(self.data["system_history"]) > max_entries:
                    self.data["system_history"] = self.data["system_history"][-max_entries:]
                
                # Check for alerts
                self.check_system_alerts(system_data)
                
                # Generate insights
                self.generate_system_insights()
                
                # Update last updated timestamp
                self.data["last_updated"] = datetime.datetime.now().isoformat()
                
                # Save data
                self.save_data()
                
                # Sleep until next check
                time.sleep(self.intervals["system"])
                
            except Exception as e:
                logging.error(f"Error in system monitor loop: {str(e)}")
                time.sleep(self.intervals["system"])
    
    def network_monitor_loop(self):
        """Monitor network activity"""
        while self.running:
            try:
                # Get network data
                network_data = self.get_network_data()
                
                # Add to history
                if "network_history" not in self.data:
                    self.data["network_history"] = []
                    
                self.data["network_history"].append(network_data)
                
                # Keep history manageable (last 24 hours at current interval)
                max_entries = 24 * 60 * 60 // self.intervals["network"]
                if len(self.data["network_history"]) > max_entries:
                    self.data["network_history"] = self.data["network_history"][-max_entries:]
                
                # Check for alerts
                self.check_network_alerts(network_data)
                
                # Generate insights
                self.generate_network_insights()
                
                # Update last updated timestamp
                self.data["last_updated"] = datetime.datetime.now().isoformat()
                
                # Save data
                self.save_data()
                
                # Sleep until next check
                time.sleep(self.intervals["network"])
                
            except Exception as e:
                logging.error(f"Error in network monitor loop: {str(e)}")
                time.sleep(self.intervals["network"])
    
    def process_monitor_loop(self):
        """Monitor running processes"""
        while self.running:
            try:
                # Get process data
                process_data = self.get_process_data()
                
                # Add to history
                if "process_history" not in self.data:
                    self.data["process_history"] = []
                    
                self.data["process_history"].append(process_data)
                
                # Keep history manageable (last 24 hours at current interval)
                max_entries = 24 * 60 * 60 // self.intervals["processes"]
                if len(self.data["process_history"]) > max_entries:
                    self.data["process_history"] = self.data["process_history"][-max_entries:]
                
                # Check for alerts
                self.check_process_alerts(process_data)
                
                # Generate insights
                self.generate_process_insights()
                
                # Update last updated timestamp
                self.data["last_updated"] = datetime.datetime.now().isoformat()
                
                # Save data
                self.save_data()
                
                # Sleep until next check
                time.sleep(self.intervals["processes"])
                
            except Exception as e:
                logging.error(f"Error in process monitor loop: {str(e)}")
                time.sleep(self.intervals["processes"])
    
    def user_monitor_loop(self):
        """Monitor user behavior patterns"""
        while self.running:
            try:
                # Get user pattern data
                user_data = self.get_user_data()
                
                # Update user patterns
                if "user_patterns" not in self.data:
                    self.data["user_patterns"] = {}
                    
                # Merge new data with existing patterns
                for key, value in user_data.items():
                    if key in self.data["user_patterns"]:
                        # Update existing pattern
                        if isinstance(value, list) and isinstance(self.data["user_patterns"][key], list):
                            # Combine lists and remove duplicates
                            combined = self.data["user_patterns"][key] + value
                            self.data["user_patterns"][key] = list(set(combined))
                        elif isinstance(value, dict) and isinstance(self.data["user_patterns"][key], dict):
                            # Merge dictionaries
                            self.data["user_patterns"][key].update(value)
                        else:
                            # Replace with new value
                            self.data["user_patterns"][key] = value
                    else:
                        # Add new pattern
                        self.data["user_patterns"][key] = value
                
                # Generate insights
                self.generate_user_insights()
                
                # Update last updated timestamp
                self.data["last_updated"] = datetime.datetime.now().isoformat()
                
                # Save data
                self.save_data()
                
                # Sleep until next check
                time.sleep(self.intervals["user"])
                
            except Exception as e:
                logging.error(f"Error in user monitor loop: {str(e)}")
                time.sleep(self.intervals["user"])
    
    def get_system_data(self):
        """Get system resource data"""
        try:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Get disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Get battery info if available
            battery = None
            if hasattr(psutil, "sensors_battery"):
                battery_info = psutil.sensors_battery()
                if battery_info:
                    battery = {
                        "percent": battery_info.percent,
                        "power_plugged": battery_info.power_plugged,
                        "secsleft": battery_info.secsleft
                    }
            
            # Get load average
            load_avg = os.getloadavg() if hasattr(os, "getloadavg") else None
            
            # Get uptime
            boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).isoformat()
            
            return {
                "timestamp": datetime.datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_available": memory.available,
                "memory_total": memory.total,
                "disk_percent": disk_percent,
                "disk_free": disk.free,
                "disk_total": disk.total,
                "battery": battery,
                "load_avg": load_avg,
                "boot_time": boot_time
            }
        except Exception as e:
            logging.error(f"Error getting system data: {str(e)}")
            return {
                "timestamp": datetime.datetime.now().isoformat(),
                "error": str(e)
            }
    
    def get_network_data(self):
        """Get network activity data"""
        try:
            # Get network connections
            connections = psutil.net_connections()
            connection_count = len(connections)
            
            # Get network IO counters
            net_io = psutil.net_io_counters()
            
            # Check internet connectivity
            internet_connected = self.check_internet_connectivity()
            
            return {
                "timestamp": datetime.datetime.now().isoformat(),
                "connection_count": connection_count,
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "internet_connected": internet_connected
            }
        except Exception as e:
            logging.error(f"Error getting network data: {str(e)}")
            return {
                "timestamp": datetime.datetime.now().isoformat(),
                "error": str(e)
            }
    
    def check_internet_connectivity(self):
        """Check if internet is connected"""
        try:
            # Try to connect to a reliable server
            requests.get("https://www.google.com", timeout=5)
            return True
        except:
            return False
    
    def get_process_data(self):
        """Get data about running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
                try:
                    # Get process info
                    proc_info = proc.info
                    
                    # Add to list if it's using significant resources
                    if proc_info['cpu_percent'] > 1.0 or proc_info['memory_percent'] > 1.0:
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            # Get top 10 processes
            top_processes = processes[:10]
            
            return {
                "timestamp": datetime.datetime.now().isoformat(),
                "process_count": len(processes),
                "top_processes": top_processes
            }
        except Exception as e:
            logging.error(f"Error getting process data: {str(e)}")
            return {
                "timestamp": datetime.datetime.now().isoformat(),
                "error": str(e)
            }
    
    def get_user_data(self):
        """Get data about user behavior patterns"""
        try:
            # Get active user
            username = os.getlogin()
            
            # Get active applications
            active_apps = []
            if sys.platform == "darwin":  # macOS
                try:
                    # Use AppleScript to get frontmost application
                    cmd = "osascript -e 'tell application \"System Events\" to get name of first application process whose frontmost is true'"
                    result = subprocess.check_output(cmd, shell=True).decode().strip()
                    active_apps.append(result)
                except:
                    pass
            
            # Get working hours pattern
            current_hour = datetime.datetime.now().hour
            working_hours = []
            if 8 <= current_hour <= 18:  # 8 AM to 6 PM
                working_hours.append(current_hour)
            
            # Get active directories
            active_dirs = [os.getcwd()]
            
            return {
                "timestamp": datetime.datetime.now().isoformat(),
                "username": username,
                "active_apps": active_apps,
                "working_hours": working_hours,
                "active_dirs": active_dirs
            }
        except Exception as e:
            logging.error(f"Error getting user data: {str(e)}")
            return {
                "timestamp": datetime.datetime.now().isoformat(),
                "error": str(e)
            }
    
    def check_system_alerts(self, system_data):
        """Check for system resource alerts"""
        alerts = []
        
        # Check CPU usage
        if "cpu_percent" in system_data and system_data["cpu_percent"] > self.thresholds["cpu"]:
            alert = {
                "type": "system",
                "level": "warning",
                "message": f"High CPU usage: {system_data['cpu_percent']}%",
                "timestamp": datetime.datetime.now().isoformat()
            }
            alerts.append(alert)
        
        # Check memory usage
        if "memory_percent" in system_data and system_data["memory_percent"] > self.thresholds["memory"]:
            alert = {
                "type": "system",
                "level": "warning",
                "message": f"High memory usage: {system_data['memory_percent']}%",
                "timestamp": datetime.datetime.now().isoformat()
            }
            alerts.append(alert)
        
        # Check disk usage
        if "disk_percent" in system_data and system_data["disk_percent"] > self.thresholds["disk"]:
            alert = {
                "type": "system",
                "level": "warning",
                "message": f"High disk usage: {system_data['disk_percent']}%",
                "timestamp": datetime.datetime.now().isoformat()
            }
            alerts.append(alert)
        
        # Check battery
        if "battery" in system_data and system_data["battery"]:
            battery = system_data["battery"]
            if battery["percent"] < self.thresholds["battery"] and not battery["power_plugged"]:
                alert = {
                    "type": "system",
                    "level": "warning",
                    "message": f"Low battery: {battery['percent']}%",
                    "timestamp": datetime.datetime.now().isoformat()
                }
                alerts.append(alert)
        
        # Add alerts to data
        if alerts:
            if "alerts" not in self.data:
                self.data["alerts"] = []
                
            self.data["alerts"].extend(alerts)
            
            # Keep alerts manageable (last 100)
            if len(self.data["alerts"]) > 100:
                self.data["alerts"] = self.data["alerts"][-100:]
            
            # Call alert callbacks
            for callback in self.alert_callbacks:
                try:
                    for alert in alerts:
                        callback(alert)
                except Exception as e:
                    logging.error(f"Error in alert callback: {str(e)}")
    
    def check_network_alerts(self, network_data):
        """Check for network alerts"""
        alerts = []
        
        # Check internet connectivity
        if "internet_connected" in network_data and not network_data["internet_connected"]:
            alert = {
                "type": "network",
                "level": "warning",
                "message": "Internet connection lost",
                "timestamp": datetime.datetime.now().isoformat()
            }
            alerts.append(alert)
        
        # Add alerts to data
        if alerts:
            if "alerts" not in self.data:
                self.data["alerts"] = []
                
            self.data["alerts"].extend(alerts)
            
            # Keep alerts manageable (last 100)
            if len(self.data["alerts"]) > 100:
                self.data["alerts"] = self.data["alerts"][-100:]
            
            # Call alert callbacks
            for callback in self.alert_callbacks:
                try:
                    for alert in alerts:
                        callback(alert)
                except Exception as e:
                    logging.error(f"Error in alert callback: {str(e)}")
    
    def check_process_alerts(self, process_data):
        """Check for process alerts"""
        alerts = []
        
        # Check for high CPU usage processes
        if "top_processes" in process_data:
            for proc in process_data["top_processes"]:
                if proc["cpu_percent"] > 50:  # Process using more than 50% CPU
                    alert = {
                        "type": "process",
                        "level": "info",
                        "message": f"Process {proc['name']} (PID {proc['pid']}) is using {proc['cpu_percent']}% CPU",
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                    alerts.append(alert)
        
        # Add alerts to data
        if alerts:
            if "alerts" not in self.data:
                self.data["alerts"] = []
                
            self.data["alerts"].extend(alerts)
            
            # Keep alerts manageable (last 100)
            if len(self.data["alerts"]) > 100:
                self.data["alerts"] = self.data["alerts"][-100:]
            
            # Call alert callbacks
            for callback in self.alert_callbacks:
                try:
                    for alert in alerts:
                        callback(alert)
                except Exception as e:
                    logging.error(f"Error in alert callback: {str(e)}")
    
    def generate_system_insights(self):
        """Generate insights from system data"""
        if "system_history" not in self.data or len(self.data["system_history"]) < 10:
            return
            
        insights = []
        
        # Get recent system history
        recent_history = self.data["system_history"][-10:]
        
        # Calculate average CPU usage
        avg_cpu = sum(entry["cpu_percent"] for entry in recent_history if "cpu_percent" in entry) / len(recent_history)
        
        # Check for trends
        if avg_cpu > 70:
            insight = {
                "type": "system",
                "message": f"Your system has been under heavy CPU load (avg: {avg_cpu:.1f}%) recently. Consider closing unnecessary applications.",
                "timestamp": datetime.datetime.now().isoformat()
            }
            insights.append(insight)
        
        # Add insights to data
        if insights:
            if "insights" not in self.data:
                self.data["insights"] = []
                
            self.data["insights"].extend(insights)
            
            # Keep insights manageable (last 100)
            if len(self.data["insights"]) > 100:
                self.data["insights"] = self.data["insights"][-100:]
            
            # Call insight callbacks
            for callback in self.insight_callbacks:
                try:
                    for insight in insights:
                        callback(insight)
                except Exception as e:
                    logging.error(f"Error in insight callback: {str(e)}")
    
    def generate_network_insights(self):
        """Generate insights from network data"""
        if "network_history" not in self.data or len(self.data["network_history"]) < 5:
            return
            
        insights = []
        
        # Get recent network history
        recent_history = self.data["network_history"][-5:]
        
        # Check for internet connectivity issues
        connectivity_issues = sum(1 for entry in recent_history if "internet_connected" in entry and not entry["internet_connected"])
        
        if connectivity_issues > 2:
            insight = {
                "type": "network",
                "message": "You've been experiencing internet connectivity issues. You might want to check your network connection.",
                "timestamp": datetime.datetime.now().isoformat()
            }
            insights.append(insight)
        
        # Add insights to data
        if insights:
            if "insights" not in self.data:
                self.data["insights"] = []
                
            self.data["insights"].extend(insights)
            
            # Keep insights manageable (last 100)
            if len(self.data["insights"]) > 100:
                self.data["insights"] = self.data["insights"][-100:]
            
            # Call insight callbacks
            for callback in self.insight_callbacks:
                try:
                    for insight in insights:
                        callback(insight)
                except Exception as e:
                    logging.error(f"Error in insight callback: {str(e)}")
    
    def generate_process_insights(self):
        """Generate insights from process data"""
        if "process_history" not in self.data or len(self.data["process_history"]) < 5:
            return
            
        insights = []
        
        # Get recent process history
        recent_history = self.data["process_history"][-5:]
        
        # Find consistently high CPU processes
        high_cpu_processes = {}
        
        for entry in recent_history:
            if "top_processes" in entry:
                for proc in entry["top_processes"]:
                    if proc["cpu_percent"] > 20:  # Process using more than 20% CPU
                        if proc["name"] not in high_cpu_processes:
                            high_cpu_processes[proc["name"]] = 0
                        high_cpu_processes[proc["name"]] += 1
        
        # Check for processes that are consistently using high CPU
        for proc_name, count in high_cpu_processes.items():
            if count >= 3:  # Process has been high in at least 3 of 5 checks
                insight = {
                    "type": "process",
                    "message": f"Process {proc_name} has been consistently using high CPU. Consider investigating.",
                    "timestamp": datetime.datetime.now().isoformat()
                }
                insights.append(insight)
        
        # Add insights to data
        if insights:
            if "insights" not in self.data:
                self.data["insights"] = []
                
            self.data["insights"].extend(insights)
            
            # Keep insights manageable (last 100)
            if len(self.data["insights"]) > 100:
                self.data["insights"] = self.data["insights"][-100:]
            
            # Call insight callbacks
            for callback in self.insight_callbacks:
                try:
                    for insight in insights:
                        callback(insight)
                except Exception as e:
                    logging.error(f"Error in insight callback: {str(e)}")
    
    def generate_user_insights(self):
        """Generate insights from user data"""
        if "user_patterns" not in self.data:
            return
            
        insights = []
        
        # Check working hours pattern
        if "working_hours" in self.data["user_patterns"]:
            working_hours = self.data["user_patterns"]["working_hours"]
            
            # Check if user is working late
            late_hours = [h for h in working_hours if h >= 20]  # After 8 PM
            
            if len(late_hours) > 5:
                insight = {
                    "type": "user",
                    "message": "I've noticed you've been working late hours frequently. Remember to take breaks and get enough rest.",
                    "timestamp": datetime.datetime.now().isoformat()
                }
                insights.append(insight)
        
        # Add insights to data
        if insights:
            if "insights" not in self.data:
                self.data["insights"] = []
                
            self.data["insights"].extend(insights)
            
            # Keep insights manageable (last 100)
            if len(self.data["insights"]) > 100:
                self.data["insights"] = self.data["insights"][-100:]
            
            # Call insight callbacks
            for callback in self.insight_callbacks:
                try:
                    for insight in insights:
                        callback(insight)
                except Exception as e:
                    logging.error(f"Error in insight callback: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Create and start the system monitor
    monitor = AnimaSystemMonitor()
    
    # Define an alert callback
    def alert_callback(alert):
        print(f"ALERT: {alert['message']}")
    
    # Define an insight callback
    def insight_callback(insight):
        print(f"INSIGHT: {insight['message']}")
    
    # Register callbacks
    monitor.register_alert_callback(alert_callback)
    monitor.register_insight_callback(insight_callback)
    
    # Start monitoring
    monitor.start()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()
        print("System monitor stopped")
