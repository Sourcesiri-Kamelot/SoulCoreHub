#!/usr/bin/env python3
"""
evove_repair_system.py — Repair system for SoulCore components
Part of the EvoVe (Repair, Mutation, Adaptive Binding) subsystem
"""

import os
import sys
import json
import time
import logging
import subprocess
import signal
import psutil
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("evove_repair.log"),
        logging.StreamHandler()
    ]
)

class RepairSystem:
    """Repair system for SoulCore components"""
    
    def __init__(self, health_monitor):
        """Initialize the repair system"""
        self.health_monitor = health_monitor
        self.soulcore_path = health_monitor.soulcore_path
        self.repair_strategies = {
            "anima": self.repair_anima,
            "gptsoul": self.repair_gptsoul,
            "mcp_server": self.repair_mcp_server,
            "azur": self.repair_azur,
            "ollama": self.repair_ollama
        }
        self.repair_history = []
        self.repair_file = Path("~/SoulCoreHub/evove/repair_history.json").expanduser()
        self._load_repair_history()
        logging.info("RepairSystem initialized")
    
    def _load_repair_history(self):
        """Load repair history from file"""
        try:
            if self.repair_file.exists():
                with open(self.repair_file, "r") as f:
                    self.repair_history = json.load(f)
                logging.info(f"Loaded repair history with {len(self.repair_history)} entries")
        except Exception as e:
            logging.error(f"Error loading repair history: {e}")
            self.repair_history = []
    
    def _save_repair_history(self):
        """Save repair history to file"""
        try:
            # Ensure directory exists
            self.repair_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Keep only the last 1000 entries
            if len(self.repair_history) > 1000:
                self.repair_history = self.repair_history[-1000:]
            
            with open(self.repair_file, "w") as f:
                json.dump(self.repair_history, f, indent=2)
            logging.info(f"Saved repair history with {len(self.repair_history)} entries")
        except Exception as e:
            logging.error(f"Error saving repair history: {e}")
    
    def repair_component(self, name):
        """Repair a component"""
        if name not in self.repair_strategies:
            logging.warning(f"No repair strategy for component: {name}")
            return {
                "success": False,
                "message": f"No repair strategy for component: {name}"
            }
        
        # Get current status
        self.health_monitor.check_component(name)
        component = self.health_monitor.get_component_status(name)
        
        # Only repair if failed or degraded
        if component["status"] not in ["failed", "degraded", "unknown"]:
            return {
                "success": True,
                "message": f"Component {name} is already running"
            }
        
        # Call the appropriate repair strategy
        logging.info(f"Attempting to repair component: {name}")
        repair_strategy = self.repair_strategies[name]
        result = repair_strategy()
        
        # Log the repair attempt
        self.repair_history.append({
            "component": name,
            "timestamp": datetime.now().isoformat(),
            "success": result["success"],
            "message": result["message"],
            "previous_status": component["status"]
        })
        self._save_repair_history()
        
        return result
    
    def _kill_process(self, pid):
        """Kill a process by PID"""
        try:
            if not pid:
                return False
                
            process = psutil.Process(pid)
            process.terminate()
            
            # Wait for process to terminate
            try:
                process.wait(timeout=5)
                return True
            except psutil.TimeoutExpired:
                # Force kill if process doesn't terminate
                process.kill()
                return True
        except psutil.NoSuchProcess:
            return True
        except Exception as e:
            logging.error(f"Error killing process {pid}: {e}")
            return False
    
    def repair_anima(self):
        """Repair Anima"""
        try:
            # Get current status
            component = self.health_monitor.get_component_status("anima")
            
            # Kill existing process if any
            if component["pid"]:
                self._kill_process(component["pid"])
            
            # Start Anima
            logging.info("Starting Anima...")
            subprocess.Popen(
                ["python", str(self.soulcore_path / "anima_autonomous.py")],
                cwd=str(self.soulcore_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for Anima to start
            time.sleep(5)
            
            # Check if Anima is running
            self.health_monitor.check_component("anima")
            component = self.health_monitor.get_component_status("anima")
            
            if component["status"] == "running":
                return {
                    "success": True,
                    "message": f"Anima repaired successfully (PID: {component['pid']})"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to repair Anima (status: {component['status']})"
                }
        except Exception as e:
            logging.error(f"Error repairing Anima: {e}")
            return {
                "success": False,
                "message": f"Error repairing Anima: {str(e)}"
            }
    
    def repair_gptsoul(self):
        """Repair GPTSoul"""
        try:
            # Get current status
            component = self.health_monitor.get_component_status("gptsoul")
            
            # Kill existing process if any
            if component["pid"]:
                self._kill_process(component["pid"])
            
            # Start GPTSoul
            logging.info("Starting GPTSoul...")
            subprocess.Popen(
                ["python", str(self.soulcore_path / "activate_gptsoul.py")],
                cwd=str(self.soulcore_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for GPTSoul to start
            time.sleep(5)
            
            # Check if GPTSoul is running
            self.health_monitor.check_component("gptsoul")
            component = self.health_monitor.get_component_status("gptsoul")
            
            if component["status"] == "running":
                return {
                    "success": True,
                    "message": f"GPTSoul repaired successfully (PID: {component['pid']})"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to repair GPTSoul (status: {component['status']})"
                }
        except Exception as e:
            logging.error(f"Error repairing GPTSoul: {e}")
            return {
                "success": False,
                "message": f"Error repairing GPTSoul: {str(e)}"
            }
    
    def repair_mcp_server(self):
        """Repair MCP server"""
        try:
            # Get current status
            component = self.health_monitor.get_component_status("mcp_server")
            
            # Kill existing process if any
            if component["pid"]:
                self._kill_process(component["pid"])
            
            # Start MCP server
            logging.info("Starting MCP server...")
            subprocess.Popen(
                ["python", str(self.soulcore_path / "mcp" / "mcp_main.py")],
                cwd=str(self.soulcore_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for MCP server to start
            time.sleep(5)
            
            # Check if MCP server is running
            self.health_monitor.check_component("mcp_server")
            component = self.health_monitor.get_component_status("mcp_server")
            
            if component["status"] == "running":
                return {
                    "success": True,
                    "message": f"MCP server repaired successfully (PID: {component['pid']})"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to repair MCP server (status: {component['status']})"
                }
        except Exception as e:
            logging.error(f"Error repairing MCP server: {e}")
            return {
                "success": False,
                "message": f"Error repairing MCP server: {str(e)}"
            }
    
    def repair_azur(self):
        """Repair Azür"""
        try:
            # Get current status
            component = self.health_monitor.get_component_status("azur")
            
            # Kill existing process if any
            if component["pid"]:
                self._kill_process(component["pid"])
            
            # Start Azür
            logging.info("Starting Azür...")
            subprocess.Popen(
                ["python", str(self.soulcore_path / "azure_connector.py")],
                cwd=str(self.soulcore_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for Azür to start
            time.sleep(5)
            
            # Check if Azür is running
            self.health_monitor.check_component("azur")
            component = self.health_monitor.get_component_status("azur")
            
            if component["status"] == "running":
                return {
                    "success": True,
                    "message": f"Azür repaired successfully (PID: {component['pid']})"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to repair Azür (status: {component['status']})"
                }
        except Exception as e:
            logging.error(f"Error repairing Azür: {e}")
            return {
                "success": False,
                "message": f"Error repairing Azür: {str(e)}"
            }
    
    def repair_ollama(self):
        """Repair Ollama"""
        try:
            # Get current status
            component = self.health_monitor.get_component_status("ollama")
            
            # Kill existing process if any
            if component["pid"]:
                self._kill_process(component["pid"])
            
            # Start Ollama
            logging.info("Starting Ollama...")
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for Ollama to start
            time.sleep(5)
            
            # Check if Ollama is running
            self.health_monitor.check_component("ollama")
            component = self.health_monitor.get_component_status("ollama")
            
            if component["status"] == "running":
                return {
                    "success": True,
                    "message": f"Ollama repaired successfully (PID: {component['pid']})"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to repair Ollama (status: {component['status']})"
                }
        except Exception as e:
            logging.error(f"Error repairing Ollama: {e}")
            return {
                "success": False,
                "message": f"Error repairing Ollama: {str(e)}"
            }
    
    def repair_all(self):
        """Repair all components"""
        results = {}
        for name in self.repair_strategies:
            results[name] = self.repair_component(name)
        return results
    
    def get_repair_history(self, component=None, limit=10):
        """Get repair history"""
        if component:
            history = [entry for entry in self.repair_history if entry["component"] == component]
        else:
            history = self.repair_history
        
        return history[-limit:]

# For testing
if __name__ == "__main__":
    from evove_health_monitor import HealthMonitor
    
    monitor = HealthMonitor()
    repair = RepairSystem(monitor)
    
    # Check all components
    print("Checking all components...")
    results = monitor.check_all()
    
    for name, result in results.items():
        print(f"{name}: {result['status']} (PID: {result['pid']})")
    
    # Ask which component to repair
    component = input("\nWhich component to repair? (or 'all' for all components): ")
    
    if component.lower() == "all":
        results = repair.repair_all()
        for name, result in results.items():
            print(f"{name}: {'✅' if result['success'] else '❌'} - {result['message']}")
    elif component in repair.repair_strategies:
        result = repair.repair_component(component)
        print(f"{'✅' if result['success'] else '❌'} - {result['message']}")
    else:
        print(f"Unknown component: {component}")
        print(f"Available components: {', '.join(repair.repair_strategies.keys())}")
