#!/usr/bin/env python3
"""
EvoVe Autonomous System
-----------------------
Self-evolving, self-repairing component of the SoulCoreHub system.
Provides monitoring, adaptation, and recovery capabilities.
"""

import os
import sys
import time
import logging
import argparse
import json
import threading
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent))

# Import EvoVe modules
try:
    from modules.mcp_bridge import MCPBridge
    from modules.repair_ops import RepairOperations
    from modules.system_monitor import SystemMonitor
    from modules.cli_sync import CLISync
    from modules.voice_interface import VoiceInterface
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all required modules are installed.")
    sys.exit(1)

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("logs/evove.log"),
        logging.StreamHandler()
    ]
)

class EvoVeAutonomous:
    """Self-evolving, self-repairing component of SoulCoreHub"""
    
    def __init__(self, args=None):
        """
        Initialize the EvoVe Autonomous System
        
        Args:
            args: Command-line arguments
        """
        self.args = args or {}
        self.running = False
        self.initialized = False
        
        # Initialize components
        self.mcp_bridge = None
        self.repair_ops = None
        self.system_monitor = None
        self.cli_sync = None
        self.voice = None
        
        # Initialize system
        self.initialize_system()
        
    def initialize_system(self):
        """Initialize the EvoVe system components"""
        try:
            logging.info("Initializing EvoVe Autonomous System")
            
            # Initialize MCP Bridge
            self.mcp_bridge = MCPBridge(agent_name="EvoVe")
            logging.info("MCP Bridge initialized")
            
            # Initialize Repair Operations
            self.repair_ops = RepairOperations(mcp_bridge=self.mcp_bridge)
            logging.info("Repair Operations initialized")
            
            # Initialize System Monitor
            self.system_monitor = SystemMonitor(mcp_bridge=self.mcp_bridge)
            logging.info("System Monitor initialized")
            
            # Initialize CLI Sync
            self.cli_sync = CLISync(mcp_bridge=self.mcp_bridge)
            logging.info("CLI Sync initialized")
            
            # Initialize Voice Interface
            self.voice = VoiceInterface(mcp_bridge=self.mcp_bridge)
            logging.info("Voice Interface initialized")
            
            # Run initial health check
            self.run_health_check()
            
            self.initialized = True
            logging.info("EvoVe system initialization complete")
            
            # Announce system startup
            self.voice.speak("EvoVe autonomous system initialized and ready.")
            
        except Exception as e:
            logging.error(f"Error initializing EvoVe system: {str(e)}")
            self.initialized = False
    
    def run_health_check(self):
        """Run a comprehensive health check"""
        try:
            logging.info("Running health check")
            
            # Run repair operations health check
            health_results = self.repair_ops.run_health_check()
            
            # Check system status
            status_report = self.system_monitor.get_status_report()
            
            # Announce status if voice is enabled
            if self.voice:
                self.voice.announce_status(status_report)
            
            return {
                "health_check": health_results,
                "status_report": status_report
            }
        except Exception as e:
            logging.error(f"Error running health check: {str(e)}")
            return {"error": str(e)}
    
    def start(self):
        """Start the EvoVe system"""
        if not self.initialized:
            logging.error("Cannot start: EvoVe system not initialized")
            return False
        
        if self.running:
            logging.warning("EvoVe system is already running")
            return True
        
        try:
            logging.info("Starting EvoVe system")
            
            # Start CLI worker
            self.cli_sync.start_worker()
            
            # Start system monitoring
            self.system_monitor.start_monitoring(interval=30)
            
            self.running = True
            logging.info("EvoVe system started")
            
            # Announce system start
            self.voice.speak("EvoVe system is now active and monitoring SoulCore.")
            
            return True
        except Exception as e:
            logging.error(f"Error starting EvoVe system: {str(e)}")
            return False
    
    def stop(self):
        """Stop the EvoVe system"""
        if not self.running:
            logging.warning("EvoVe system is not running")
            return True
        
        try:
            logging.info("Stopping EvoVe system")
            
            # Stop system monitoring
            self.system_monitor.stop_monitoring()
            
            # Stop CLI worker
            self.cli_sync.stop_worker()
            
            self.running = False
            logging.info("EvoVe system stopped")
            
            # Announce system stop
            self.voice.speak("EvoVe system shutting down.")
            
            return True
        except Exception as e:
            logging.error(f"Error stopping EvoVe system: {str(e)}")
            return False
    
    def run_maintenance(self):
        """Run maintenance tasks"""
        try:
            logging.info("Running maintenance tasks")
            
            # Repair directory structure
            self.repair_ops.repair_directory_structure()
            
            # Repair file permissions
            self.repair_ops.repair_permissions()
            
            # Repair MCP server
            self.repair_ops.repair_mcp_server()
            
            logging.info("Maintenance tasks completed")
            
            # Announce maintenance completion
            self.voice.speak("Maintenance tasks completed successfully.")
            
            return True
        except Exception as e:
            logging.error(f"Error running maintenance: {str(e)}")
            self.voice.speak("Error during maintenance tasks.")
            return False
    
    def run_command(self, command, cwd=None):
        """
        Run a shell command
        
        Args:
            command (str): Command to execute
            cwd (str): Working directory
            
        Returns:
            dict: Command result
        """
        try:
            logging.info(f"Running command: {command}")
            
            # Use CLI Sync to run command
            result = self.cli_sync.sync_execute(command, cwd, timeout=60)
            
            return result
        except Exception as e:
            logging.error(f"Error running command: {str(e)}")
            return {"error": str(e)}
    
    def main_loop(self):
        """Main processing loop"""
        try:
            # Start the system
            if not self.start():
                return False
            
            # Run until interrupted
            while self.running:
                try:
                    # Run health check every 5 minutes
                    self.run_health_check()
                    
                    # Sleep for a while
                    time.sleep(300)
                except KeyboardInterrupt:
                    logging.info("Interrupted by user")
                    break
                except Exception as e:
                    logging.error(f"Error in main loop: {str(e)}")
                    time.sleep(60)
            
            # Stop the system
            self.stop()
            
            return True
        except Exception as e:
            logging.error(f"Error in main loop: {str(e)}")
            return False

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="EvoVe Autonomous System")
    
    parser.add_argument(
        "--no-voice",
        action="store_true",
        help="Disable voice output"
    )
    
    parser.add_argument(
        "--maintenance",
        action="store_true",
        help="Run maintenance tasks and exit"
    )
    
    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Run health check and exit"
    )
    
    parser.add_argument(
        "--command",
        type=str,
        help="Run a single command and exit"
    )
    
    return parser.parse_args()

# Main entry point
if __name__ == "__main__":
    # Parse arguments
    args = parse_arguments()
    
    try:
        # Create EvoVe instance
        evove = EvoVeAutonomous(args)
        
        # Disable voice if requested
        if args.no_voice and evove.voice:
            evove.voice.disable_voice()
        
        # Run maintenance if requested
        if args.maintenance:
            evove.run_maintenance()
            sys.exit(0)
        
        # Run health check if requested
        if args.health_check:
            evove.run_health_check()
            sys.exit(0)
        
        # Run command if requested
        if args.command:
            result = evove.run_command(args.command)
            print(json.dumps(result, indent=2))
            sys.exit(0)
        
        # Run main loop
        evove.main_loop()
        
    except KeyboardInterrupt:
        logging.info("Interrupted by user")
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        sys.exit(1)
