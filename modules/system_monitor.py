#!/usr/bin/env python3
"""
System Monitor Module - Monitors system health and performance
Provides real-time monitoring of SoulCore components
"""

import os
import sys
import json
import time
import logging
import psutil
import threading
from datetime import datetime
from pathlib import Path

class SystemMonitor:
    """Monitors system health and performance"""
    
    def __init__(self, mcp_bridge=None):
        """
        Initialize the System Monitor
        
        Args:
            mcp_bridge: MCP Bridge for communication
        """
        self.mcp_bridge = mcp_bridge
        self.monitoring = False
        self.monitor_thread = None
        self.system_stats = {}
        self.component_status = {}
        logging.info("System Monitor initialized")
    
    def get_system_stats(self):
        """
        Get current system statistics
        
        Returns:
            dict: System statistics
        """
        try:
            stats = {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "timestamp": datetime.now().isoformat()
            }
            
            self.system_stats = stats
            return stats
        except Exception as e:
            logging.error(f"Error getting system stats: {str(e)}")
            return {}
    
    def check_component_status(self):
        """
        Check the status of key components
        
        Returns:
            dict: Component status
        """
        try:
            # Check MCP server
            mcp_running = False
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and any('mcp_main.py' in cmd for cmd in proc.info['cmdline']):
                        mcp_running = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Check Anima
            anima_running = False
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and any('anima_' in cmd for cmd in proc.info['cmdline']):
                        anima_running = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Check web server
            server_running = False
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and any('server.js' in cmd for cmd in proc.info['cmdline']):
                        server_running = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            status = {
                "mcp_server": mcp_running,
                "anima": anima_running,
                "web_server": server_running,
                "timestamp": datetime.now().isoformat()
            }
            
            self.component_status = status
            return status
        except Exception as e:
            logging.error(f"Error checking component status: {str(e)}")
            return {}
    
    def monitor_loop(self, interval=5):
        """
        Continuous monitoring loop
        
        Args:
            interval (int): Monitoring interval in seconds
        """
        self.monitoring = True
        
        while self.monitoring:
            try:
                # Get system stats
                stats = self.get_system_stats()
                
                # Check component status
                status = self.check_component_status()
                
                # Log critical issues
                if stats.get("cpu_percent", 0) > 90:
                    logging.warning(f"High CPU usage: {stats['cpu_percent']}%")
                
                if stats.get("memory_percent", 0) > 90:
                    logging.warning(f"High memory usage: {stats['memory_percent']}%")
                
                if stats.get("disk_percent", 0) > 90:
                    logging.warning(f"High disk usage: {stats['disk_percent']}%")
                
                if not status.get("mcp_server", False):
                    logging.warning("MCP server is not running")
                
                # Save monitoring data
                self.save_monitoring_data(stats, status)
                
                # Wait for next interval
                time.sleep(interval)
            except Exception as e:
                logging.error(f"Error in monitor loop: {str(e)}")
                time.sleep(interval)
    
    def save_monitoring_data(self, stats, status):
        """
        Save monitoring data to file
        
        Args:
            stats (dict): System statistics
            status (dict): Component status
        """
        try:
            # Ensure logs directory exists
            logs_dir = Path(__file__).parent.parent / "logs"
            if not logs_dir.exists():
                os.makedirs(logs_dir)
            
            # Save to monitoring log
            log_file = logs_dir / "system_monitor.log"
            
            with open(log_file, "a") as f:
                timestamp = datetime.now().isoformat()
                log_entry = {
                    "timestamp": timestamp,
                    "stats": stats,
                    "status": status
                }
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logging.error(f"Error saving monitoring data: {str(e)}")
    
    def start_monitoring(self, interval=5):
        """
        Start the monitoring thread
        
        Args:
            interval (int): Monitoring interval in seconds
            
        Returns:
            bool: True if monitoring started, False otherwise
        """
        if self.monitoring:
            logging.warning("Monitoring is already running")
            return False
        
        try:
            self.monitor_thread = threading.Thread(
                target=self.monitor_loop,
                args=(interval,),
                daemon=True
            )
            self.monitor_thread.start()
            logging.info(f"Started system monitoring with interval {interval}s")
            return True
        except Exception as e:
            logging.error(f"Error starting monitoring: {str(e)}")
            return False
    
    def stop_monitoring(self):
        """
        Stop the monitoring thread
        
        Returns:
            bool: True if monitoring stopped, False otherwise
        """
        if not self.monitoring:
            logging.warning("Monitoring is not running")
            return False
        
        try:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            logging.info("Stopped system monitoring")
            return True
        except Exception as e:
            logging.error(f"Error stopping monitoring: {str(e)}")
            return False
    
    def get_status_report(self):
        """
        Get a comprehensive status report
        
        Returns:
            dict: Status report
        """
        stats = self.get_system_stats()
        status = self.check_component_status()
        
        return {
            "system_stats": stats,
            "component_status": status,
            "monitoring_active": self.monitoring,
            "timestamp": datetime.now().isoformat()
        }

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    monitor = SystemMonitor()
    
    # Get current status
    report = monitor.get_status_report()
    print("System Status Report:")
    print(f"CPU: {report['system_stats'].get('cpu_percent', 'N/A')}%")
    print(f"Memory: {report['system_stats'].get('memory_percent', 'N/A')}%")
    print(f"Disk: {report['system_stats'].get('disk_percent', 'N/A')}%")
    print(f"MCP Server: {'Running' if report['component_status'].get('mcp_server', False) else 'Stopped'}")
    print(f"Anima: {'Running' if report['component_status'].get('anima', False) else 'Stopped'}")
    
    # Start monitoring for a few seconds
    monitor.start_monitoring(interval=2)
    time.sleep(6)
    monitor.stop_monitoring()
