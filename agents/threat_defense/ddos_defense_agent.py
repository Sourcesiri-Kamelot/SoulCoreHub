"""
DDOS Defense Agent - Detects and mitigates distributed denial-of-service attacks in real-time.
"""

import logging
import time
import threading
import json
import os
import random
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, deque

class DDOSDefenseAgent:
    def __init__(self):
        self.name = "DDOS Defense Agent"
        self.status = "active"
        self.running = False
        self.traffic_history = defaultdict(lambda: deque(maxlen=100))  # IP -> list of timestamps
        self.blocked_ips = set()
        self.mitigation_active = False
        self.thresholds = {
            "requests_per_minute": 60,  # Max requests per minute from a single IP
            "concurrent_connections": 20,  # Max concurrent connections from a single IP
            "traffic_increase_factor": 5.0  # Sudden traffic increase factor that triggers alert
        }
        self.log_file = Path("logs/ddos_defense.log")
        self.config_file = Path("config/ddos_thresholds.json")
        self.blocked_file = Path("memory/blocked_ips.json")
        
        # Create log directory if it doesn't exist
        os.makedirs(self.log_file.parent, exist_ok=True)
        
        # Load configuration
        self.load_config()
        
        # Load previously blocked IPs
        self.load_blocked_ips()
        
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
        
        # Traffic statistics
        self.baseline_traffic = 100  # Baseline requests per minute
        self.current_traffic = 100  # Current requests per minute
        self.attack_detected = False
        self.attack_start_time = None
        self.attack_end_time = None

    def load_config(self):
        """Load DDOS defense thresholds from config file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.thresholds = json.load(f)
                    self.logger.info(f"Loaded DDOS defense thresholds")
            else:
                # Create default thresholds if file doesn't exist
                os.makedirs(self.config_file.parent, exist_ok=True)
                with open(self.config_file, 'w') as f:
                    json.dump(self.thresholds, f, indent=2)
                self.logger.info("Created default DDOS defense thresholds")
        except Exception as e:
            self.logger.error(f"Error loading DDOS defense thresholds: {e}")

    def load_blocked_ips(self):
        """Load previously blocked IPs"""
        try:
            if self.blocked_file.exists():
                with open(self.blocked_file, 'r') as f:
                    data = json.load(f)
                    self.blocked_ips = set(data.get("blocked_ips", []))
                    self.logger.info(f"Loaded {len(self.blocked_ips)} previously blocked IPs")
            else:
                self.blocked_ips = set()
        except Exception as e:
            self.logger.error(f"Error loading blocked IPs: {e}")
            self.blocked_ips = set()

    def save_blocked_ips(self):
        """Save blocked IPs to file"""
        try:
            os.makedirs(self.blocked_file.parent, exist_ok=True)
            with open(self.blocked_file, 'w') as f:
                json.dump({
                    "blocked_ips": list(self.blocked_ips),
                    "last_update": datetime.now().isoformat()
                }, f, indent=2)
            self.logger.info(f"Saved {len(self.blocked_ips)} blocked IPs")
        except Exception as e:
            self.logger.error(f"Error saving blocked IPs: {e}")

    def record_request(self, ip_address):
        """Record a request from an IP address"""
        # Skip if IP is already blocked
        if ip_address in self.blocked_ips:
            return False
        
        # Record the timestamp
        self.traffic_history[ip_address].append(datetime.now())
        
        # Check if this IP exceeds thresholds
        return self.check_ip_thresholds(ip_address)

    def check_ip_thresholds(self, ip_address):
        """Check if an IP address exceeds the defined thresholds"""
        # Get the history for this IP
        history = self.traffic_history[ip_address]
        
        # Skip if not enough history
        if len(history) < 5:
            return False
        
        # Check requests per minute
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        requests_last_minute = sum(1 for ts in history if ts > one_minute_ago)
        
        if requests_last_minute > self.thresholds["requests_per_minute"]:
            self.logger.warning(f"IP {ip_address} exceeded requests per minute threshold: {requests_last_minute}")
            self.block_ip(ip_address, f"Exceeded requests per minute threshold: {requests_last_minute}")
            return True
        
        return False

    def block_ip(self, ip_address, reason):
        """Block an IP address"""
        if ip_address not in self.blocked_ips:
            self.blocked_ips.add(ip_address)
            self.logger.warning(f"Blocked IP {ip_address}: {reason}")
            self.save_blocked_ips()
            
            # Emit event if event bus is available
            if self.event_bus:
                self.event_bus.emit("IP_BLOCKED", {
                    "ip": ip_address,
                    "reason": reason,
                    "source_agent": self.name
                })
            
            return True
        return False

    def unblock_ip(self, ip_address):
        """Unblock an IP address"""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            self.logger.info(f"Unblocked IP {ip_address}")
            self.save_blocked_ips()
            return True
        return False

    def detect_ddos_attack(self):
        """Detect if a DDOS attack is in progress based on traffic patterns"""
        # In a real implementation, this would analyze actual traffic data
        # For simulation, we'll use random fluctuations
        
        # Simulate traffic fluctuations
        if self.attack_detected:
            # If attack is ongoing, simulate gradual decrease if mitigation is active
            if self.mitigation_active:
                self.current_traffic = max(self.baseline_traffic, 
                                          int(self.current_traffic * 0.9))  # Decrease by 10%
                
                # Check if attack is over
                if self.current_traffic <= self.baseline_traffic * 1.5:
                    self.attack_detected = False
                    self.attack_end_time = datetime.now()
                    self.logger.info(f"DDOS attack mitigated. Duration: {self.attack_end_time - self.attack_start_time}")
                    
                    # Emit event if event bus is available
                    if self.event_bus:
                        self.event_bus.emit("DDOS_MITIGATED", {
                            "duration_seconds": (self.attack_end_time - self.attack_start_time).total_seconds(),
                            "source_agent": self.name
                        })
            else:
                # If no mitigation, traffic continues to increase
                self.current_traffic = int(self.current_traffic * 1.1)  # Increase by 10%
        else:
            # Randomly decide if an attack starts
            if random.random() < 0.01:  # 1% chance of attack starting
                self.attack_detected = True
                self.attack_start_time = datetime.now()
                self.current_traffic = self.baseline_traffic * 10  # 10x traffic spike
                self.logger.warning(f"DDOS attack detected! Traffic spike to {self.current_traffic} requests/minute")
                
                # Emit event if event bus is available
                if self.event_bus:
                    self.event_bus.emit("DDOS_DETECTED", {
                        "traffic_level": self.current_traffic,
                        "baseline": self.baseline_traffic,
                        "source_agent": self.name
                    })
            else:
                # Normal traffic fluctuations
                self.current_traffic = max(50, min(150, 
                                                  self.current_traffic + random.randint(-10, 10)))
        
        return self.attack_detected

    def activate_mitigation(self):
        """Activate DDOS mitigation measures"""
        if not self.mitigation_active:
            self.mitigation_active = True
            self.logger.info("DDOS mitigation measures activated")
            
            # In a real implementation, this would configure network devices, CDN, etc.
            # For simulation, we'll just log it
            
            # Emit event if event bus is available
            if self.event_bus:
                self.event_bus.emit("MITIGATION_ACTIVATED", {
                    "source_agent": self.name
                })
            
            return True
        return False

    def deactivate_mitigation(self):
        """Deactivate DDOS mitigation measures"""
        if self.mitigation_active:
            self.mitigation_active = False
            self.logger.info("DDOS mitigation measures deactivated")
            
            # Emit event if event bus is available
            if self.event_bus:
                self.event_bus.emit("MITIGATION_DEACTIVATED", {
                    "source_agent": self.name
                })
            
            return True
        return False

    def monitor_traffic(self):
        """Monitor network traffic for DDOS attacks"""
        self.logger.info("Starting DDOS defense monitoring")
        self.running = True
        
        while self.running:
            # Detect if a DDOS attack is in progress
            attack_detected = self.detect_ddos_attack()
            
            # If attack is detected, activate mitigation
            if attack_detected and not self.mitigation_active:
                self.activate_mitigation()
            
            # If attack is over, deactivate mitigation
            if not attack_detected and self.mitigation_active:
                self.deactivate_mitigation()
            
            # Simulate some incoming requests
            for _ in range(random.randint(1, 5)):
                # Generate a random IP address
                ip = f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
                self.record_request(ip)
            
            # Sleep for a bit
            time.sleep(5)

    def start(self):
        """Start the DDOS defense monitoring in a background thread"""
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.monitor_traffic, daemon=True)
            self._thread.start()
            self.logger.info("DDOS defense monitoring started")
            return True
        return False

    def stop(self):
        """Stop the DDOS defense monitoring"""
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
            self.logger.info("DDOS defense monitoring stopped")
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
        return {
            "status": "running", 
            "blocked_ips": len(self.blocked_ips),
            "attack_detected": self.attack_detected,
            "mitigation_active": self.mitigation_active
        }

    def handle_event(self, event):
        """Handle events from the event bus"""
        event_type = event.get("type", "")
        data = event.get("data", {})
        
        if event_type == "SUSPICIOUS_TRAFFIC":
            # Record suspicious traffic from another agent
            if "source_ip" in data:
                self.record_request(data["source_ip"])
                return True
        
        elif event_type == "BLOCK_IP":
            # Block an IP address
            if "ip" in data:
                reason = data.get("reason", "Blocked by event")
                return self.block_ip(data["ip"], reason)
        
        elif event_type == "UNBLOCK_IP":
            # Unblock an IP address
            if "ip" in data:
                return self.unblock_ip(data["ip"])
        
        elif event_type == "ACTIVATE_MITIGATION":
            # Manually activate mitigation
            return self.activate_mitigation()
        
        elif event_type == "DEACTIVATE_MITIGATION":
            # Manually deactivate mitigation
            return self.deactivate_mitigation()
        
        return False

    def diagnose(self):
        """Return diagnostic information about the agent"""
        return {
            "name": self.name,
            "status": "running" if self.heartbeat() else "stopped",
            "blocked_ips_count": len(self.blocked_ips),
            "current_traffic": self.current_traffic,
            "baseline_traffic": self.baseline_traffic,
            "attack_detected": self.attack_detected,
            "mitigation_active": self.mitigation_active,
            "thread_alive": self._thread.is_alive() if self._thread else False
        }
