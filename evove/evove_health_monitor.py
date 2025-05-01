#!/usr/bin/env python3
"""
evove_health_monitor.py — Health monitoring system for SoulCore components
Part of the EvoVe (Repair, Mutation, Adaptive Binding) subsystem
"""

import os
import sys
import json
import time
import logging
import subprocess
import psutil
import requests
import websockets
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("evove_health.log"),
        logging.StreamHandler()
    ]
)

class HealthMonitor:
    """Monitor the health of SoulCore components"""
    
    def __init__(self, soulcore_path=None):
        """Initialize the health monitor"""
        self.soulcore_path = soulcore_path or Path.home() / "SoulCoreHub"
        self.components = {
            "anima": {
                "status": "unknown", 
                "last_check": None,
                "pid": None,
                "check_method": self._check_anima,
                "process_name": "anima_autonomous.py"
            },
            "gptsoul": {
                "status": "unknown", 
                "last_check": None,
                "pid": None,
                "check_method": self._check_gptsoul,
                "process_name": "activate_gptsoul.py"
            },
            "mcp_server": {
                "status": "unknown", 
                "last_check": None,
                "pid": None,
                "check_method": self._check_mcp_server,
                "process_name": "mcp_main.py"
            },
            "azur": {
                "status": "unknown", 
                "last_check": None,
                "pid": None,
                "check_method": self._check_azur,
                "process_name": "azure_connector.py"
            },
            "ollama": {
                "status": "unknown", 
                "last_check": None,
                "pid": None,
                "check_method": self._check_ollama,
                "process_name": "ollama"
            }
        }
        self.health_history = []
        self.health_file = Path("~/SoulCoreHub/evove/health_history.json").expanduser()
        self._load_health_history()
        logging.info(f"HealthMonitor initialized with {len(self.components)} components")
    
    def _load_health_history(self):
        """Load health history from file"""
        try:
            if self.health_file.exists():
                with open(self.health_file, "r") as f:
                    self.health_history = json.load(f)
                logging.info(f"Loaded health history with {len(self.health_history)} entries")
        except Exception as e:
            logging.error(f"Error loading health history: {e}")
            self.health_history = []
    
    def _save_health_history(self):
        """Save health history to file"""
        try:
            # Ensure directory exists
            self.health_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Keep only the last 1000 entries
            if len(self.health_history) > 1000:
                self.health_history = self.health_history[-1000:]
            
            with open(self.health_file, "w") as f:
                json.dump(self.health_history, f, indent=2)
            logging.info(f"Saved health history with {len(self.health_history)} entries")
        except Exception as e:
            logging.error(f"Error saving health history: {e}")
    
    def check_component(self, name):
        """Check if a component is running and responsive"""
        if name not in self.components:
            logging.warning(f"Unknown component: {name}")
            return False
        
        component = self.components[name]
        check_method = component["check_method"]
        
        try:
            # Call the appropriate check method
            status, pid = check_method()
            
            # Update component status
            old_status = component["status"]
            component["status"] = status
            component["last_check"] = datetime.now().isoformat()
            component["pid"] = pid
            
            # Log status change
            if old_status != status:
                if status == "running":
                    logging.info(f"Component {name} is now running (PID: {pid})")
                elif status == "failed":
                    logging.warning(f"Component {name} has failed")
                elif status == "degraded":
                    logging.warning(f"Component {name} is running in degraded state")
            
            # Add to health history
            self.health_history.append({
                "component": name,
                "status": status,
                "timestamp": component["last_check"],
                "pid": pid
            })
            
            # Save health history periodically
            if len(self.health_history) % 10 == 0:
                self._save_health_history()
            
            return status == "running"
        except Exception as e:
            logging.error(f"Error checking component {name}: {e}")
            component["status"] = "unknown"
            component["last_check"] = datetime.now().isoformat()
            return False
    
    def check_all(self):
        """Check all components"""
        results = {}
        for name in self.components:
            results[name] = {
                "success": self.check_component(name),
                "status": self.components[name]["status"],
                "last_check": self.components[name]["last_check"],
                "pid": self.components[name]["pid"]
            }
        return results
    
    def _find_process_by_name(self, process_name):
        """Find a process by name"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Check if process_name is in the command line
                if proc.info['cmdline'] and any(process_name in cmd for cmd in proc.info['cmdline']):
                    return proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return None
    
    def _check_process_memory_usage(self, pid):
        """Check memory usage of a process"""
        try:
            process = psutil.Process(pid)
            memory_info = process.memory_info()
            return memory_info.rss / (1024 * 1024)  # MB
        except Exception:
            return None
    
    def _check_process_cpu_usage(self, pid):
        """Check CPU usage of a process"""
        try:
            process = psutil.Process(pid)
            return process.cpu_percent(interval=0.1)
        except Exception:
            return None
    
    def _check_anima(self):
        """Check if Anima is running"""
        # First check if process is running
        pid = self._find_process_by_name(self.components["anima"]["process_name"])
        if not pid:
            return "failed", None
        
        # Check if Anima is responsive by checking for recent log entries
        try:
            anima_log = Path("~/SoulCoreHub/anima_launcher.log").expanduser()
            if anima_log.exists():
                # Check if log was updated in the last 5 minutes
                if datetime.fromtimestamp(anima_log.stat().st_mtime) > datetime.now() - timedelta(minutes=5):
                    # Check memory usage
                    memory_usage = self._check_process_memory_usage(pid)
                    if memory_usage and memory_usage > 500:  # More than 500 MB
                        return "degraded", pid
                    return "running", pid
            
            # Try to check if Anima responds to a simple command
            result = subprocess.run(
                ["python", "-c", "from anima_voice import speak; speak('EvoVe health check')"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return "running", pid
            
            return "degraded", pid
        except Exception as e:
            logging.error(f"Error checking Anima: {e}")
            return "degraded", pid
    
    def _check_gptsoul(self):
        """Check if GPTSoul is running"""
        # First check if process is running
        pid = self._find_process_by_name(self.components["gptsoul"]["process_name"])
        if not pid:
            return "failed", None
        
        # For now, just check if process is running
        return "running", pid
    
    def _check_mcp_server(self):
        """Check if MCP server is running"""
        # First check if process is running
        pid = self._find_process_by_name(self.components["mcp_server"]["process_name"])
        if not pid:
            return "failed", None
        
        # Check if MCP server is responsive
        try:
            # Try to connect to MCP server
            async def test_connection():
                try:
                    async with websockets.connect("ws://localhost:8765", timeout=2) as websocket:
                        return True
                except Exception:
                    return False
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(test_connection())
            loop.close()
            
            if result:
                return "running", pid
            else:
                return "degraded", pid
        except Exception as e:
            logging.error(f"Error checking MCP server: {e}")
            return "degraded", pid
    
    def _check_azur(self):
        """Check if Azür is running"""
        # First check if process is running
        pid = self._find_process_by_name(self.components["azur"]["process_name"])
        if not pid:
            return "failed", None
        
        # For now, just check if process is running
        return "running", pid
    
    def _check_ollama(self):
        """Check if Ollama is running"""
        # First check if process is running
        pid = self._find_process_by_name(self.components["ollama"]["process_name"])
        if not pid:
            return "failed", None
        
        # Check if Ollama API is responsive
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                return "running", pid
            else:
                return "degraded", pid
        except Exception:
            return "degraded", pid
    
    def get_component_status(self, name):
        """Get the status of a component"""
        if name not in self.components:
            return None
        return self.components[name]
    
    def get_all_statuses(self):
        """Get the status of all components"""
        return self.components
    
    def get_health_summary(self):
        """Get a summary of system health"""
        total = len(self.components)
        running = sum(1 for c in self.components.values() if c["status"] == "running")
        degraded = sum(1 for c in self.components.values() if c["status"] == "degraded")
        failed = sum(1 for c in self.components.values() if c["status"] == "failed")
        unknown = sum(1 for c in self.components.values() if c["status"] == "unknown")
        
        if failed > 0:
            overall = "critical"
        elif degraded > 0:
            overall = "warning"
        elif unknown > 0:
            overall = "unknown"
        elif running == total:
            overall = "healthy"
        else:
            overall = "unknown"
        
        return {
            "overall": overall,
            "components": {
                "total": total,
                "running": running,
                "degraded": degraded,
                "failed": failed,
                "unknown": unknown
            },
            "timestamp": datetime.now().isoformat()
        }

# For testing
if __name__ == "__main__":
    monitor = HealthMonitor()
    results = monitor.check_all()
    
    print("Component Status:")
    print("================")
    
    for name, result in results.items():
        status_color = "\033[92m"  # Green for running
        if result["status"] == "failed":
            status_color = "\033[91m"  # Red for failed
        elif result["status"] == "degraded":
            status_color = "\033[93m"  # Yellow for degraded
        elif result["status"] == "unknown":
            status_color = "\033[94m"  # Blue for unknown
            
        print(f"{name}: {status_color}{result['status']}\033[0m (PID: {result['pid']})")
    
    summary = monitor.get_health_summary()
    print("\nHealth Summary:")
    print("==============")
    print(f"Overall: {summary['overall']}")
    print(f"Running: {summary['components']['running']}/{summary['components']['total']}")
    print(f"Degraded: {summary['components']['degraded']}")
    print(f"Failed: {summary['components']['failed']}")
    print(f"Unknown: {summary['components']['unknown']}")
