# modules/voice_command.py
"""
Voice Command Dispatcher
----------------------
Processes voice commands and dispatches them to appropriate handlers.
"""

import logging
import re
import json
import threading
import time
import subprocess
import os
import sys
import argparse

logger = logging.getLogger("EvoVe.VoiceCommand")

class VoiceCommand:
    """Processes and dispatches voice commands."""
    
    def __init__(self, evove):
        """Initialize the voice command dispatcher."""
        self.evove = evove
        self.config = evove.config.get("voice_command", {})
        self.command_patterns = self._setup_command_patterns()
        
    def _setup_command_patterns(self):
        """Set up command patterns and their handlers."""
        return [
            {
                "pattern": r"status(?:\s+of\s+(\w+))?",
                "handler": self._handle_status_command,
                "help": "Check status of the system or a specific component"
            },
            {
                "pattern": r"restart(?:\s+(\w+))?",
                "handler": self._handle_restart_command,
                "help": "Restart the system or a specific component"
            },
            {
                "pattern": r"repair(?:\s+(\w+))?",
                "handler": self._handle_repair_command,
                "help": "Repair the system or a specific component"
            },
            {
                "pattern": r"backup(?:\s+as\s+(\w+))?",
                "handler": self._handle_backup_command,
                "help": "Create a backup, optionally with a specific name"
            },
            {
                "pattern": r"monitor(?:\s+(\w+))?",
                "handler": self._handle_monitor_command,
                "help": "Start monitoring the system or a specific component"
            },
            {
                "pattern": r"stop(?:\s+monitoring)?(?:\s+(\w+))?",
                "handler": self._handle_stop_command,
                "help": "Stop monitoring or a specific component"
            },
            {
                "pattern": r"help(?:\s+(\w+))?",
                "handler": self._handle_help_command,
                "help": "Show help information"
            }
        ]
    
    def process_command(self, command_text):
        """Process a voice command."""
        logger.info(f"Processing voice command: {command_text}")
        
        command_text = command_text.lower().strip()
        
        # Check for exact matches first
        if command_text == "help":
            return self._handle_help_command(None)
            
        # Try to match patterns
        for pattern_info in self.command_patterns:
            pattern = pattern_info["pattern"]
            handler = pattern_info["handler"]
            
            match = re.match(pattern, command_text)
            if match:
                # Extract the argument if any
                arg = match.group(1) if match.groups() else None
                return handler(arg)
        
        # No match found
        return {
            "status": "error",
            "message": f"Unknown command: {command_text}",
            "help": "Try 'help' for a list of available commands"
        }
    
    def _handle_status_command(self, component):
        """Handle status command."""
        if not component:
            # Get overall system status
            health_data = self.evove.check_health()
            return {
                "status": "success",
                "system_status": health_data["status"],
                

 def _handle_status_command(self, component):
        """Handle status command."""
        if not component:
            # Get overall system status
            health_data = self.evove.check_health()
            return {
                "status": "success",
                "system_status": health_data["status"],
                "components": health_data["components"],
                "resources": health_data.get("resources", {})
            }
        else:
            # Get status of a specific component
            component = component.lower()
            
            if component == "mcp":
                mcp_status = "online" if self.evove.mcp_bridge.connected else "offline"
                return {
                    "status": "success",
                    "component": "mcp",
                    "component_status": mcp_status
                }
            elif component == "anima":
                # Check if Anima is running
                anima_running = self._check_process_running("anima_voice.py")
                return {
                    "status": "success",
                    "component": "anima",
                    "component_status": "running" if anima_running else "stopped"
                }
            elif component == "network":
                # Get network status if available
                if hasattr(self.evove, "net_sense"):
                    return {
                        "status": "success",
                        "component": "network",
                        "report": self.evove.net_sense.get_status_report()
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Network sensor not available"
                    }
            else:
                return {
                    "status": "error",
                    "message": f"Unknown component: {component}"
                }
    
    def _handle_restart_command(self, component):
        """Handle restart command."""
        if not component or component == "evove" or component == "self":
            # Restart EvoVe
            logger.info("Restarting EvoVe...")
            
            # Schedule a restart
            threading.Thread(target=self._restart_self).start()
            
            return {
                "status": "success",
                "message": "Restarting EvoVe..."
            }
        elif component == "mcp":
            # Restart MCP server
            success = self.evove.repair_mcp()
            return {
                "status": "success" if success else "error",
                "message": "MCP server " + ("restarted successfully" if success else "failed to restart")
            }
        elif component == "anima":
            # Restart Anima
            success = self._restart_process("anima_voice.py")
            return {
                "status": "success" if success else "error",
                "message": "Anima " + ("restarted successfully" if success else "failed to restart")
            }
        elif component == "all":
            # Restart everything
            logger.info("Restarting all components...")
            
            # First restart MCP
            self.evove.repair_mcp()
            
            # Then restart Anima
            self._restart_process("anima_voice.py")
            
            # Finally restart EvoVe
            threading.Thread(target=self._restart_self).start()
            
            return {
                "status": "success",
                "message": "Restarting all components..."
            }
        else:
            return {
                "status": "error",
                "message": f"Unknown component: {component}"
            }
    
    def _restart_self(self):
        """Restart the EvoVe process."""
        logger.info("Restarting EvoVe...")
        time.sleep(1)  # Give time for response to be sent
        
        # Stop EvoVe
        self.evove.stop()
        
        # Restart the process
        python = sys.executable
        os.execl(python, python, *sys.argv)
    
    def _restart_process(self, process_name):
        """Restart a process by name."""
        try:
            # Kill the process
            subprocess.run(["pkill", "-f", process_name], check=False)
            time.sleep(2)
            
            # Check if it's still running
            if self._check_process_running(process_name):
                # Force kill
                subprocess.run(["pkill", "-9", "-f", process_name], check=False)
                time.sleep(1)
            
            # Start the process
            if process_name == "anima_voice.py":
                subprocess.Popen([sys.executable, "anima_voice.py"], 
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
            
            # Check if it started
            time.sleep(2)
            return self._check_process_running(process_name)
            
        except Exception as e:
            logger.error(f"Failed to restart process {process_name}: {e}")
            return False
    
    def _check_process_running(self, process_name):
        """Check if a process is running."""
        try:
            output = subprocess.check_output(["pgrep", "-f", process_name])
            return bool(output.strip())
        except subprocess.CalledProcessError:
            return False
    
    def _handle_repair_command(self, component):
        """Handle repair command."""
        if not component or component == "mcp":
            # Repair MCP
            success = self.evove.repair_mcp()
            return {
                "status": "success" if success else "error",
                "message": "MCP repair " + ("successful" if success else "failed")
            }
        elif component == "system" or component == "all":
            # Run full system repair
            logger.info("Running full system repair...")
            
            # Create backup first
            if hasattr(self.evove, "secure_storage"):
                self.evove.secure_storage.create_encrypted_backup("pre-repair")
            
            # Repair MCP
            mcp_success = self.evove.repair_mcp()
            
            # Run health check script
            health_script = "scripts/evove_healthcheck.sh"
            if os.path.exists(health_script):
                subprocess.run(["bash", health_script], check=False)
            
            return {
                "status": "success",
                "message": "System repair completed",
                "details": {
                    "mcp_repair": "success" if mcp_success else "failed"
                }
            }
        else:
            return {
                "status": "error",
                "message": f"Unknown component: {component}"
            }
    
    def _handle_backup_command(self, name):
        """Handle backup command."""
        if hasattr(self.evove, "secure_storage"):
            backup_file = self.evove.secure_storage.create_encrypted_backup(name)
            if backup_file:
                return {
                    "status": "success",
                    "message": f"Backup created: {os.path.basename(backup_file)}"
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to create backup"
                }
        else:
            # Fall back to basic backup
            try:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                backup_name = name if name else f"backup-{timestamp}"
                backup_file = f"backups/{backup_name}.tar.gz"
                
                os.makedirs("backups", exist_ok=True)
                
                subprocess.run([
                    "tar", "-czf", backup_file, 
                    "--exclude=backups", "--exclude=venv", "--exclude=__pycache__",
                    "."
                ], check=True)
                
                return {
                    "status": "success",
                    "message": f"Backup created: {backup_file}"
                }
            except Exception as e:
                logger.error(f"Failed to create backup: {e}")
                return {
                    "status": "error",
                    "message": f"Failed to create backup: {str(e)}"
                }
    
    def _handle_monitor_command(self, component):
        """Handle monitor command."""
        if not component or component == "all":
            # Start all monitoring
            if hasattr(self.evove, "system_monitor"):
                self.evove.system_monitor.start()
            
            if hasattr(self.evove, "net_sense"):
                self.evove.net_sense.start()
                
            if hasattr(self.evove, "anomaly_watcher"):
                self.evove.anomaly_watcher.start()
                
            return {
                "status": "success",
                "message": "Started monitoring all components"
            }
        elif component == "system":
            # Start system monitoring
            if hasattr(self.evove, "system_monitor"):
                self.evove.system_monitor.start()
                return {
                    "status": "success",
                    "message": "Started system monitoring"
                }
            else:
                return {
                    "status": "error",
                    "message": "System monitor not available"
                }
        elif component == "network":
            # Start network monitoring
            if hasattr(self.evove, "net_sense"):
                self.evove.net_sense.start()
                return {
                    "status": "success",
                    "message": "Started network monitoring"
                }
            else:
                return {
                    "status": "error",
                    "message": "Network sensor not available"
                }
        elif component == "anomalies":
            # Start anomaly monitoring
            if hasattr(self.evove, "anomaly_watcher"):
                self.evove.anomaly_watcher.start()
                return {
                    "status": "success",
                    "message": "Started anomaly monitoring"
                }
            else:
                return {
                    "status": "error",
                    "message": "Anomaly watcher not available"
                }
        else:
            return {
                "status": "error",
                "message": f"Unknown component: {component}"
            }
    
    def _handle_stop_command(self, component):
        """Handle stop command."""
        if not component or component == "all":
            # Stop all monitoring
            if hasattr(self.evove, "system_monitor"):
                self.evove.system_monitor.stop()
            
            if hasattr(self.evove, "net_sense"):
                self.evove.net_sense.stop()
                
            if hasattr(self.evove, "anomaly_watcher"):
                self.evove.anomaly_watcher.stop()
                
            return {
                "status": "success",
                "message": "Stopped all monitoring"
            }
        elif component == "system":
            # Stop system monitoring
            if hasattr(self.evove, "system_monitor"):
                self.evove.system_monitor.stop()
                return {
                    "status": "success",
                    "message": "Stopped system monitoring"
                }
            else:
                return {
                    "status": "error",
                    "message": "System monitor not available"
                }
        elif component == "network":
            # Stop network monitoring
            if hasattr(self.evove, "net_sense"):
                self.evove.net_sense.stop()
                return {
                    "status": "success",
                    "message": "Stopped network monitoring"
                }
            else:
                return {
                    "status": "error",
                    "message": "Network sensor not available"
                }
        elif component == "anomalies":
            # Stop anomaly monitoring
            if hasattr(self.evove, "anomaly_watcher"):
                self.evove.anomaly_watcher.stop()
                return {
                    "status": "success",
                    "message": "Stopped anomaly monitoring"
                }
            else:
                return {
                    "status": "error",
                    "message": "Anomaly watcher not available"
                }
        else:
            return {
                "status": "error",
                "message": f"Unknown component: {component}"
            }
    
    def _handle_help_command(self, topic):
        """Handle help command."""
        if not topic:
            # General help
            commands = []
            for pattern_info in self.command_patterns:
                commands.append({
                    "pattern": pattern_info["pattern"],
                    "help": pattern_info["help"]
                })
                
            return {
                "status": "success",
                "message": "Available commands:",
                "commands": commands
            }
        else:
            # Help for a specific topic
            topic = topic.lower()
            
            for pattern_info in self.command_patterns:
                if re.search(topic, pattern_info["pattern"]):
                    return {
                        "status": "success",
                        "command": pattern_info["pattern"],
                        "help": pattern_info["help"]
                    }
            
            return {
                "status": "error",
                "message": f"No help available for topic: {topic}"
            }

