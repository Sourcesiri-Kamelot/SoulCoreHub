# modules/net_sense.py
"""
Network Sensor Module
-------------------
Monitors network connectivity and remote services.
"""

import logging
import threading
import time
import socket
import subprocess
import json
import requests
from datetime import datetime

logger = logging.getLogger("EvoVe.NetSense")

class NetworkSensor:
    """Monitors network connectivity and remote services."""
    
    def __init__(self, evove):
        """Initialize the network sensor."""
        self.evove = evove
        self.config = evove.config.get("network", {})
        self.running = False
        self.sensor_thread = None
        self.endpoints = self.config.get("endpoints", [])
        self.check_interval = self.config.get("check_interval", 60)
        self.timeout = self.config.get("timeout", 5)
        self.alert_channels = self.config.get("alert_channels", ["log"])
        self.status = {}
        self.history = {}
        
        # Add default endpoints if none are configured
        if not self.endpoints:
            self.endpoints = [
                {
                    "name": "MCP Server",
                    "type": "socket",
                    "host": "localhost",
                    "port": 8765,
                    "critical": True
                },
                {
                    "name": "Internet",
                    "type": "ping",
                    "host": "8.8.8.8",
                    "critical": True
                },
                {
                    "name": "DNS",
                    "type": "dns",
                    "host": "google.com",
                    "critical": True
                }
            ]
        
    def start(self):
        """Start the network sensor."""
        if self.running:
            logger.warning("Network sensor is already running")
            return
            
        self.running = True
        logger.info("Starting network sensor")
        
        self.sensor_thread = threading.Thread(target=self._sensor_loop)
        self.sensor_thread.daemon = True
        self.sensor_thread.start()
        
    def stop(self):
        """Stop the network sensor."""
        if not self.running:
            logger.warning("Network sensor is not running")
            return
            
        self.running = False
        logger.info("Stopping network sensor")
        
        if self.sensor_thread:
            self.sensor_thread.join(timeout=5)
    
    def _sensor_loop(self):
        """Main sensor loop."""
        while self.running:
            try:
                self._check_all_endpoints()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in network sensor loop: {e}")
                time.sleep(10)  # Shorter interval on error
    
    def _check_all_endpoints(self):
        """Check all configured endpoints."""
        logger.debug("Checking network endpoints")
        
        for endpoint in self.endpoints:
            name = endpoint.get("name", endpoint.get("host", "unknown"))
            endpoint_type = endpoint.get("type", "ping")
            host = endpoint.get("host")
            
            if not host:
                logger.warning(f"Skipping endpoint {name}: no host specified")
                continue
                
            try:
                status = self._check_endpoint(endpoint)
                
                # Update status
                self.status[name] = status
                
                # Update history
                if name not in self.history:
                    self.history[name] = []
                    
                self.history[name].append({
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": status
                })
                
                # Trim history
                if len(self.history[name]) > 100:
                    self.history[name] = self.history[name][-100:]
                
                # Handle status changes
                self._handle_status_change(name, endpoint, status)
                
            except Exception as e:
                logger.error(f"Error checking endpoint {name}: {e}")
    
    def _check_endpoint(self, endpoint):
        """Check a single endpoint."""
        endpoint_type = endpoint.get("type", "ping")
        host = endpoint.get("host")
        port = endpoint.get("port")
        path = endpoint.get("path", "/")
        timeout = endpoint.get("timeout", self.timeout)
        
        if endpoint_type == "ping":
            return self._check_ping(host, timeout)
        elif endpoint_type == "socket":
            return self._check_socket(host, port, timeout)
        elif endpoint_type == "http":
            return self._check_http(host, port, path, timeout)
        elif endpoint_type == "dns":
            return self._check_dns(host, timeout)
        else:
            logger.warning(f"Unknown endpoint type: {endpoint_type}")
            return {"status": "unknown", "message": f"Unknown endpoint type: {endpoint_type}"}
    
    def _check_ping(self, host, timeout):
        """Check connectivity using ping."""
        try:
            # Use the ping command
            param = '-n' if subprocess.call('ping', shell=True) == 0 else '-c'
            command = ['ping', param, '1', host]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
            
            if result.returncode == 0:
                return {"status": "online", "message": "Ping successful"}
            else:
                return {"status": "offline", "message": "Ping failed"}
                
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Ping timed out"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _check_socket(self, host, port, timeout):
        """Check connectivity using a socket connection."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.connect((host, port))
                return {"status": "online", "message": f"Socket connection to {host}:{port} successful"}
        except socket.timeout:
            return {"status": "timeout", "message": f"Socket connection to {host}:{port} timed out"}
        except ConnectionRefusedError:
            return {"status": "offline", "message": f"Connection to {host}:{port} refused"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _check_http(self, host, port, path, timeout):
        """Check connectivity using an HTTP request."""
        try:
            protocol = "https" if port == 443 else "http"
            url = f"{protocol}://{host}"
            if port and port != 80 and port != 443:
                url += f":{port}"
            url += path
            
            response = requests.get(url, timeout=timeout)
            return {
                "status": "online" if response.status_code < 400 else "error",
                "message": f"HTTP status: {response.status_code}",
                "status_code": response.status_code
            }
        except requests.exceptions.Timeout:
            return {"status": "timeout", "message": f"HTTP request to {url} timed out"}
        except requests.exceptions.ConnectionError:
            return {"status": "offline", "message": f"Failed to connect to {url}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _check_dns(self, host, timeout):
        """Check DNS resolution."""
        try:
            socket.gethostbyname(host)
            return {"status": "online", "message": f"DNS resolution for {host} successful"}
        except socket.timeout:
            return {"status": "timeout", "message": f"DNS resolution for {host} timed out"}
        except socket.gaierror:
            return {"status": "offline", "message": f"DNS resolution for {host} failed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _handle_status_change(self, name, endpoint, status):
        """Handle changes in endpoint status."""
        # Get previous status
        prev_status = None
        if name in self.history and len(self.history[name]) > 1:
            prev_status = self.history[name][-2]["status"]["status"]
            
        current_status = status["status"]
        
        # If status changed or endpoint is critical and offline
        if (prev_status and prev_status != current_status) or \
           (endpoint.get("critical", False) and current_status != "online"):
            
            message = f"Endpoint {name} is {current_status}: {status['message']}"
            
            # Log the status change
            if current_status == "online":
                logger.info(message)
            else:
                logger.warning(message)
            
            # Send alerts
            self._send_alerts(name, endpoint, status, prev_status)
    
    def _send_alerts(self, name, endpoint, status, prev_status):
        """Send alerts for endpoint status changes."""
        message = f"Network Alert: {name} is {status['status']}"
        if prev_status:
            message += f" (was {prev_status})"
        message += f"\nDetails: {status['message']}"
        
        # Send to configured alert channels

def _send_alerts(self, name, endpoint, status, prev_status):
        """Send alerts for endpoint status changes."""
        message = f"Network Alert: {name} is {status['status']}"
        if prev_status:
            message += f" (was {prev_status})"
        message += f"\nDetails: {status['message']}"
        
        # Send to configured alert channels
        for channel in self.alert_channels:
            if channel == "log":
                # Already logged in _handle_status_change
                pass
            elif channel == "slack" and "slack_webhook" in self.config:
                self._send_slack_alert(message, endpoint, status)
            elif channel == "terminal":
                self._send_terminal_alert(message)
            elif channel == "mcp" and hasattr(self.evove, 'mcp_bridge'):
                self._send_mcp_alert(name, endpoint, status, prev_status)
    
    def _send_slack_alert(self, message, endpoint, status):
        """Send an alert to Slack."""
        webhook_url = self.config.get("slack_webhook")
        if not webhook_url:
            logger.warning("Slack webhook URL not configured")
            return
            
        try:
            # Prepare the Slack message
            color = "danger" if status["status"] != "online" else "good"
            payload = {
                "attachments": [
                    {
                        "color": color,
                        "title": "EvoVe Network Alert",
                        "text": message,
                        "fields": [
                            {
                                "title": "Endpoint",
                                "value": endpoint.get("name", endpoint.get("host", "unknown")),
                                "short": True
                            },
                            {
                                "title": "Status",
                                "value": status["status"],
                                "short": True
                            }
                        ],
                        "ts": int(time.time())
                    }
                ]
            }
            
            # Send the message
            requests.post(webhook_url, json=payload, timeout=5)
            
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
    
    def _send_terminal_alert(self, message):
        """Send an alert to the terminal."""
        try:
            # Use notify-send on Linux
            if subprocess.call("which notify-send", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
                subprocess.run(["notify-send", "EvoVe Network Alert", message])
            # Use osascript on macOS
            elif subprocess.call("which osascript", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
                subprocess.run(["osascript", "-e", f'display notification "{message}" with title "EvoVe Network Alert"'])
        except Exception as e:
            logger.error(f"Failed to send terminal alert: {e}")
    
    def _send_mcp_alert(self, name, endpoint, status, prev_status):
        """Send an alert through the MCP system."""
        if not hasattr(self.evove, 'mcp_bridge') or not self.evove.mcp_bridge.connected:
            return
            
        try:
            self.evove.mcp_bridge.send_message({
                "type": "network_alert",
                "endpoint": name,
                "status": status["status"],
                "previous_status": prev_status,
                "message": status["message"],
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "critical": endpoint.get("critical", False)
            })
        except Exception as e:
            logger.error(f"Failed to send MCP alert: {e}")
    
    def get_status_report(self):
        """Get a report of all endpoint statuses."""
        return {
            "status": self.status,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def add_endpoint(self, endpoint):
        """Add a new endpoint to monitor."""
        if "name" not in endpoint or "host" not in endpoint:
            logger.error("Endpoint must have a name and host")
            return False
            
        # Check if endpoint already exists
        for existing in self.endpoints:
            if existing.get("name") == endpoint.get("name"):
                logger.warning(f"Endpoint {endpoint['name']} already exists")
                return False
                
        self.endpoints.append(endpoint)
        logger.info(f"Added endpoint: {endpoint['name']}")
        return True
    
    def remove_endpoint(self, name):
        """Remove an endpoint from monitoring."""
        for i, endpoint in enumerate(self.endpoints):
            if endpoint.get("name") == name:
                self.endpoints.pop(i)
                logger.info(f"Removed endpoint: {name}")
                return True
                
        logger.warning(f"Endpoint {name} not found")
        return False



