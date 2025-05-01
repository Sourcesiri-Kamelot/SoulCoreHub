"""
Firewall Agent - Monitors and filters incoming/outgoing network traffic based on security rules.
"""

import logging
import time
import threading
import json
import os
from pathlib import Path

class FirewallAgent:
    def __init__(self):
        self.name = "Firewall Agent"
        self.status = "active"
        self.running = False
        self.rules = []
        self.blocked_ips = set()
        self.suspicious_activity = []
        self.log_file = Path("logs/firewall.log")
        self.config_file = Path("config/firewall_rules.json")
        
        # Create log directory if it doesn't exist
        os.makedirs(self.log_file.parent, exist_ok=True)
        
        # Load firewall rules
        self.load_rules()
        
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

    def load_rules(self):
        """Load firewall rules from config file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.rules = json.load(f)
                    self.logger.info(f"Loaded {len(self.rules)} firewall rules")
            else:
                # Create default rules if file doesn't exist
                self.rules = [
                    {"type": "block", "ip": "0.0.0.0/0", "port": 22, "protocol": "tcp", "description": "Block SSH from all"},
                    {"type": "allow", "ip": "192.168.1.0/24", "port": 22, "protocol": "tcp", "description": "Allow SSH from local network"}
                ]
                os.makedirs(self.config_file.parent, exist_ok=True)
                with open(self.config_file, 'w') as f:
                    json.dump(self.rules, f, indent=2)
                self.logger.info("Created default firewall rules")
        except Exception as e:
            self.logger.error(f"Error loading firewall rules: {e}")
            self.rules = []

    def save_rules(self):
        """Save firewall rules to config file"""
        try:
            os.makedirs(self.config_file.parent, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.rules, f, indent=2)
            self.logger.info(f"Saved {len(self.rules)} firewall rules")
        except Exception as e:
            self.logger.error(f"Error saving firewall rules: {e}")

    def add_rule(self, rule_type, ip, port, protocol, description=""):
        """Add a new firewall rule"""
        rule = {
            "type": rule_type,
            "ip": ip,
            "port": port,
            "protocol": protocol,
            "description": description
        }
        self.rules.append(rule)
        self.save_rules()
        self.logger.info(f"Added new {rule_type} rule for {ip}:{port}/{protocol}")
        return True

    def remove_rule(self, index):
        """Remove a firewall rule by index"""
        if 0 <= index < len(self.rules):
            rule = self.rules.pop(index)
            self.save_rules()
            self.logger.info(f"Removed rule: {rule}")
            return True
        return False

    def check_packet(self, source_ip, dest_ip, port, protocol):
        """Check if a packet should be allowed or blocked based on rules"""
        # This is a simplified simulation - in a real firewall, this would interact with the OS
        for rule in self.rules:
            if (self._ip_match(source_ip, rule["ip"]) and 
                (rule["port"] == port or rule["port"] == "*") and
                (rule["protocol"] == protocol or rule["protocol"] == "*")):
                
                if rule["type"] == "block":
                    self.blocked_ips.add(source_ip)
                    self.logger.warning(f"Blocked packet from {source_ip} to {dest_ip}:{port}/{protocol}")
                    return False
                elif rule["type"] == "allow":
                    return True
        
        # Default policy (allow if no matching rules)
        return True

    def _ip_match(self, ip, rule_ip):
        """Check if an IP matches a rule (including CIDR notation)"""
        # Simplified implementation - would use ipaddress module in production
        if rule_ip == "*" or rule_ip == "0.0.0.0/0":
            return True
        elif "/" in rule_ip:  # CIDR notation
            # Simplified CIDR check - would use ipaddress module in production
            network_part = rule_ip.split("/")[0]
            return ip.startswith(network_part.rsplit(".", 1)[0])
        else:
            return ip == rule_ip

    def monitor_network(self):
        """Monitor network traffic (simulation)"""
        self.logger.info("Starting network monitoring")
        self.running = True
        
        while self.running:
            # In a real implementation, this would hook into system network monitoring
            # For simulation, we'll just log that we're monitoring
            self.logger.debug("Monitoring network traffic...")
            
            # Simulate detecting some traffic
            if time.time() % 60 < 1:  # Roughly once a minute
                test_ip = f"192.168.1.{int(time.time() % 254)}"
                test_port = 80
                test_protocol = "tcp"
                
                allowed = self.check_packet(test_ip, "10.0.0.1", test_port, test_protocol)
                if allowed:
                    self.logger.debug(f"Allowed connection from {test_ip} to port {test_port}/{test_protocol}")
                
            time.sleep(5)  # Check every 5 seconds

    def start(self):
        """Start the firewall monitoring in a background thread"""
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.monitor_network, daemon=True)
            self._thread.start()
            self.logger.info("Firewall monitoring started")
            return True
        return False

    def stop(self):
        """Stop the firewall monitoring"""
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
            self.logger.info("Firewall monitoring stopped")
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
        return {"status": "running", "rules_count": len(self.rules)}

    def handle_event(self, event):
        """Handle events from the event bus"""
        event_type = event.get("type", "")
        data = event.get("data", {})
        
        if event_type == "SECURITY_ALERT":
            # Add a temporary block rule for the suspicious IP
            if "source_ip" in data:
                self.add_rule("block", data["source_ip"], "*", "*", "Added by security alert")
                self.logger.warning(f"Added block rule for {data['source_ip']} due to security alert")
                return True
        
        elif event_type == "FIREWALL_ADD_RULE":
            # Add a new rule from event data
            if all(k in data for k in ["type", "ip", "port", "protocol"]):
                self.add_rule(
                    data["type"], 
                    data["ip"], 
                    data["port"], 
                    data["protocol"], 
                    data.get("description", "")
                )
                return True
        
        elif event_type == "FIREWALL_REMOVE_RULE":
            # Remove a rule by index
            if "index" in data:
                return self.remove_rule(data["index"])
        
        return False

    def diagnose(self):
        """Return diagnostic information about the agent"""
        return {
            "name": self.name,
            "status": "running" if self.heartbeat() else "stopped",
            "rules_count": len(self.rules),
            "blocked_ips": list(self.blocked_ips),
            "thread_alive": self._thread.is_alive() if self._thread else False
        }
