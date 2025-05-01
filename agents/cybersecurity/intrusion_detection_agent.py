"""
Intrusion Detection Agent - Detects unauthorized intrusion attempts or suspicious activities in the system.
"""

import logging
import time
import threading
import json
import os
import random
from pathlib import Path
from datetime import datetime

class IntrusionDetectionAgent:
    def __init__(self):
        self.name = "Intrusion Detection Agent"
        self.status = "active"
        self.running = False
        self.detection_patterns = []
        self.alerts = []
        self.max_alerts = 100  # Maximum number of alerts to store
        self.log_file = Path("logs/intrusion_detection.log")
        self.config_file = Path("config/intrusion_patterns.json")
        self.alert_file = Path("logs/security_alerts.json")
        
        # Create log directory if it doesn't exist
        os.makedirs(self.log_file.parent, exist_ok=True)
        
        # Load detection patterns
        self.load_patterns()
        
        # Load previous alerts
        self.load_alerts()
        
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

    def load_patterns(self):
        """Load intrusion detection patterns from config file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.detection_patterns = json.load(f)
                    self.logger.info(f"Loaded {len(self.detection_patterns)} detection patterns")
            else:
                # Create default patterns if file doesn't exist
                self.detection_patterns = [
                    {"type": "login_attempt", "threshold": 5, "timeframe": 60, "severity": "high", "description": "Multiple failed login attempts"},
                    {"type": "port_scan", "threshold": 10, "timeframe": 30, "severity": "medium", "description": "Port scanning activity"},
                    {"type": "unusual_traffic", "threshold": 1000, "timeframe": 60, "severity": "low", "description": "Unusual network traffic volume"}
                ]
                os.makedirs(self.config_file.parent, exist_ok=True)
                with open(self.config_file, 'w') as f:
                    json.dump(self.detection_patterns, f, indent=2)
                self.logger.info("Created default detection patterns")
        except Exception as e:
            self.logger.error(f"Error loading detection patterns: {e}")
            self.detection_patterns = []

    def load_alerts(self):
        """Load previous security alerts"""
        try:
            if self.alert_file.exists():
                with open(self.alert_file, 'r') as f:
                    self.alerts = json.load(f)
                    self.logger.info(f"Loaded {len(self.alerts)} previous alerts")
            else:
                self.alerts = []
        except Exception as e:
            self.logger.error(f"Error loading previous alerts: {e}")
            self.alerts = []

    def save_alerts(self):
        """Save security alerts to file"""
        try:
            os.makedirs(self.alert_file.parent, exist_ok=True)
            with open(self.alert_file, 'w') as f:
                json.dump(self.alerts, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving alerts: {e}")

    def add_alert(self, alert_type, source, details, severity="medium"):
        """Add a new security alert"""
        alert = {
            "type": alert_type,
            "source": source,
            "details": details,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to the beginning of the list (most recent first)
        self.alerts.insert(0, alert)
        
        # Trim the list if it exceeds the maximum
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[:self.max_alerts]
        
        # Save alerts to file
        self.save_alerts()
        
        # Log the alert
        self.logger.warning(f"Security alert: {alert_type} from {source} - {details}")
        
        # Emit event if event bus is available
        if self.event_bus:
            self.event_bus.emit("SECURITY_ALERT", {
                "alert": alert,
                "source_agent": self.name,
                "source_ip": source
            })
        
        return alert

    def analyze_log_entry(self, log_entry):
        """Analyze a log entry for potential intrusions"""
        # This is a simplified simulation - in a real IDS, this would be much more sophisticated
        
        # Check for failed login attempts
        if "Failed login" in log_entry:
            parts = log_entry.split()
            if len(parts) >= 4:
                source_ip = parts[3]
                return self.add_alert("login_attempt", source_ip, "Failed login attempt", "medium")
        
        # Check for port scanning
        if "port scan" in log_entry.lower() or "nmap" in log_entry.lower():
            parts = log_entry.split()
            if len(parts) >= 2:
                source_ip = parts[1]
                return self.add_alert("port_scan", source_ip, "Potential port scanning detected", "high")
        
        # Check for unusual traffic patterns
        if "traffic spike" in log_entry.lower():
            parts = log_entry.split()
            if len(parts) >= 2:
                source_ip = parts[1]
                return self.add_alert("unusual_traffic", source_ip, "Unusual traffic volume detected", "low")
        
        return None

    def monitor_logs(self):
        """Monitor system logs for intrusion attempts (simulation)"""
        self.logger.info("Starting log monitoring")
        self.running = True
        
        # Simulated log entries for testing
        simulated_logs = [
            "Failed login attempt from 192.168.1.100",
            "Possible port scan detected from 10.0.0.25",
            "Traffic spike from 172.16.0.5",
            "System update completed successfully",
            "User logged in from 192.168.1.50",
            "Failed login attempt from 192.168.1.100",
            "Failed login attempt from 192.168.1.100"
        ]
        
        log_index = 0
        
        while self.running:
            # In a real implementation, this would read actual system logs
            # For simulation, we'll use our simulated logs
            
            # Simulate a new log entry every few seconds
            if random.random() < 0.3:  # 30% chance of a new log entry
                log_entry = simulated_logs[log_index % len(simulated_logs)]
                log_index += 1
                
                self.logger.debug(f"Analyzing log entry: {log_entry}")
                alert = self.analyze_log_entry(log_entry)
                
                if alert:
                    self.logger.warning(f"Alert generated: {alert['type']} - {alert['details']}")
            
            time.sleep(5)  # Check every 5 seconds

    def start(self):
        """Start the intrusion detection monitoring in a background thread"""
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.monitor_logs, daemon=True)
            self._thread.start()
            self.logger.info("Intrusion detection monitoring started")
            return True
        return False

    def stop(self):
        """Stop the intrusion detection monitoring"""
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
            self.logger.info("Intrusion detection monitoring stopped")
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
        self.start()
        return {"status": "running", "alerts_count": len(self.alerts)}

    def handle_event(self, event):
        """Handle events from the event bus"""
        event_type = event.get("type", "")
        data = event.get("data", {})
        
        if event_type == "LOG_ENTRY":
            # Analyze a log entry from another agent
            if "content" in data:
                alert = self.analyze_log_entry(data["content"])
                return alert is not None
        
        elif event_type == "CLEAR_ALERTS":
            # Clear all alerts
            self.alerts = []
            self.save_alerts()
            self.logger.info("Cleared all security alerts")
            return True
        
        return False

    def diagnose(self):
        """Return diagnostic information about the agent"""
        return {
            "name": self.name,
            "status": "running" if self.heartbeat() else "stopped",
            "patterns_count": len(self.detection_patterns),
            "alerts_count": len(self.alerts),
            "recent_alerts": self.alerts[:5] if self.alerts else [],
            "thread_alive": self._thread.is_alive() if self._thread else False
        }
