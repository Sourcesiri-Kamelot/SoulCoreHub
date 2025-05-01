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

# Import EvoVe modules
from modules.mcp_bridge import MCPBridge
from modules.repair_ops import RepairOperations
from modules.system_monitor import SystemMonitor
from modules.cli_sync import CLISync
from modules.voice_interface import VoiceInterface

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("logs/evove.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("EvoVe")

class EvoVe:
    """
    EvoVe - Autonomous system maintenance and evolution engine.
    Monitors, repairs, and adapts the SoulCoreHub system.
    """
    
    def __init__(self, config_path="config/evove_config.json"):
        """Initialize the EvoVe system with configuration."""
        self.logger = logger
        self.logger.info("Initializing EvoVe autonomous system")
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.mcp_bridge = MCPBridge(self.config.get("mcp", {}))
        self.repair_ops = RepairOperations(self)
        self.system_monitor = SystemMonitor(self)
        self.cli_sync = CLISync(self)
        
        # Initialize voice interface if enabled
        if self.config.get("voice_enabled", False):
            self.voice = VoiceInterface(self)
        else:
            self.voice = None
            
        # System state
        self.running = False
        self.health_status = "initializing"
        
        self.logger.info("EvoVe initialization complete")
    
    def _load_config(self, config_path):
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            self.logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            self.logger.info("Using default configuration")
            return {
                "mcp": {
                    "host": "localhost",
                    "port": 8765
                },
                "monitoring": {
                    "interval": 30,
                    "critical_services": ["mcp_server_divine.py", "anima_voice.py"]
                },
                "repair": {
                    "auto_repair": True,
                    "backup_before_repair": True
                },
                "voice_enabled": False
            }
    
    def start(self):
        """Start the EvoVe system."""
        if self.running:
            self.logger.warning("EvoVe is already running")
            return
            
        self.running = True
        self.logger.info("Starting EvoVe autonomous system")
        
        # Start system monitor
        self.system_monitor.start()
        
        # Connect to MCP
        self.mcp_bridge.connect()
        
        # Start CLI sync
        self.cli_sync.start()
        
        # Start voice interface if enabled
        if self.voice:
            self.voice.start()
            
        self.logger.info("EvoVe system started successfully")
        
    def stop(self):
        """Stop the EvoVe system."""
        if not self.running:
            self.logger.warning("EvoVe is not running")
            return
            
        self.running = False
        self.logger.info("Stopping EvoVe autonomous system")
        
        # Stop components
        if self.voice:
            self.voice.stop()
        self.cli_sync.stop()
        self.mcp_bridge.disconnect()
        self.system_monitor.stop()
        
        self.logger.info("EvoVe system stopped")
    
    def repair_mcp(self):
        """Repair the MCP system if it's down."""
        self.logger.info("Initiating MCP repair sequence")
        return self.repair_ops.repair_mcp_server()
    
    def check_health(self):
        """Check the health of the entire system."""
        return self.system_monitor.check_health()
    
    def adapt_to_changes(self):
        """Adapt to system changes and optimize configurations."""
        self.logger.info("Adapting to system changes")
        # Implement adaptation logic
        pass
    
    def backup_system(self, backup_path=None):
        """Create a backup of the current system state."""
        if not backup_path:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            backup_path = f"backups/system-{timestamp}.zip"
        
        self.logger.info(f"Creating system backup at {backup_path}")
        return self.repair_ops.create_backup(backup_path)

def main():
    """Main entry point for EvoVe."""
    parser = argparse.ArgumentParser(description="EvoVe Autonomous System")
    parser.add_argument("--config", help="Path to configuration file", default="config/evove_config.json")
    parser.add_argument("--repair", help="Repair mode", action="store_true")
    parser.add_argument("--monitor", help="Monitor mode only", action="store_true")
    args = parser.parse_args()
    
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("backups", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    
    # Initialize EvoVe
    evove = EvoVe(args.config)
    
    if args.repair:
        # Run in repair mode
        logger.info("Running in repair mode")
        evove.repair_mcp()
    elif args.monitor:
        # Run in monitor mode
        logger.info("Running in monitor mode")
        evove.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            evove.stop()
    else:
        # Run in full mode
        evove.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            evove.stop()

if __name__ == "__main__":
    main()


