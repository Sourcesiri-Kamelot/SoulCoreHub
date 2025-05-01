#!/usr/bin/env python3
"""
Anima Launcher - Start the Anima autonomous system
Initializes and connects all Anima components for a complete autonomous experience
"""

import os
import sys
import time
import json
import logging
import threading
import argparse
import signal
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("anima_launcher.log"),
        logging.StreamHandler()
    ]
)

# Add the SoulCore paths to system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class AnimaLauncher:
    """Launcher for the Anima autonomous system"""
    
    def __init__(self):
        """Initialize the launcher"""
        self.running = False
        self.components = {}
        self.processes = {}
        self.config = self.load_config()
        
        # Define component dependencies
        self.dependencies = {
            "mcp_server": [],
            "system_monitor": ["mcp_server"],
            "internet_explorer": ["mcp_server"],
            "autonomous_core": ["mcp_server", "system_monitor", "internet_explorer"]
        }
        
        logging.info("Anima Launcher initialized")
    
    def load_config(self):
        """Load launcher configuration"""
        config_path = Path(__file__).parent / "config" / "anima_config.json"
        try:
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = json.load(f)
                logging.info(f"Loaded configuration from {config_path}")
                return config
            else:
                # Create default configuration
                config = {
                    "components": {
                        "mcp_server": {
                            "enabled": True,
                            "script": "mcp/mcp_main.py",
                            "args": ["--host", "localhost", "--port", "8765"]
                        },
                        "system_monitor": {
                            "enabled": True,
                            "script": "anima_system_monitor.py",
                            "args": []
                        },
                        "internet_explorer": {
                            "enabled": True,
                            "script": "anima_internet_explorer.py",
                            "args": []
                        },
                        "autonomous_core": {
                            "enabled": True,
                            "script": "anima_autonomous_core.py",
                            "args": []
                        }
                    },
                    "startup": {
                        "speak_welcome": True,
                        "auto_restart": True,
                        "startup_delay": 2
                    }
                }
                
                # Ensure directory exists
                config_path.parent.mkdir(exist_ok=True)
                
                # Save default configuration
                with open(config_path, "w") as f:
                    json.dump(config, f, indent=2)
                    
                logging.info(f"Created default configuration at {config_path}")
                return config
        except Exception as e:
            logging.error(f"Error loading configuration: {str(e)}")
            return {
                "components": {
                    "mcp_server": {
                        "enabled": True,
                        "script": "mcp/mcp_main.py",
                        "args": ["--host", "localhost", "--port", "8765"]
                    },
                    "autonomous_core": {
                        "enabled": True,
                        "script": "anima_autonomous_core.py",
                        "args": []
                    }
                },
                "startup": {
                    "speak_welcome": True,
                    "auto_restart": True,
                    "startup_delay": 2
                }
            }
    
    def start(self):
        """Start the Anima system"""
        if self.running:
            return
            
        self.running = True
        
        # Speak welcome message if enabled
        if self.config.get("startup", {}).get("speak_welcome", True):
            try:
                from mcp.anima_voice import speak
                speak("Initializing Anima autonomous system")
            except ImportError:
                logging.warning("Could not import anima_voice module for welcome message")
        
        # Start components in dependency order
        self.start_components()
        
        # Start the monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_components)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        logging.info("Anima system started")
    
    def stop(self):
        """Stop the Anima system"""
        if not self.running:
            return
            
        self.running = False
        
        # Stop components in reverse dependency order
        components = list(self.components.keys())
        components.reverse()
        
        for component in components:
            self.stop_component(component)
        
        # Speak goodbye message if possible
        try:
            from mcp.anima_voice import speak
            speak("Anima autonomous system shutting down")
        except ImportError:
            logging.warning("Could not import anima_voice module for goodbye message")
        
        logging.info("Anima system stopped")
    
    def start_components(self):
        """Start all enabled components in dependency order"""
        # Get enabled components
        enabled_components = {}
        for name, config in self.config.get("components", {}).items():
            if config.get("enabled", False):
                enabled_components[name] = config
        
        # Resolve dependencies
        start_order = self.resolve_dependencies(enabled_components)
        
        # Start components in order
        for component in start_order:
            self.start_component(component)
            
            # Add startup delay if configured
            startup_delay = self.config.get("startup", {}).get("startup_delay", 2)
            if startup_delay > 0:
                time.sleep(startup_delay)
    
    def resolve_dependencies(self, components):
        """
        Resolve component dependencies to determine start order
        
        Args:
            components (dict): Components to resolve
            
        Returns:
            list: Components in dependency order
        """
        # Create a list of components that need to be started
        to_start = list(components.keys())
        
        # Create a list for the start order
        start_order = []
        
        # Resolve dependencies
        while to_start:
            # Find a component with no unresolved dependencies
            for component in to_start:
                # Get dependencies for this component
                deps = self.dependencies.get(component, [])
                
                # Check if all dependencies are satisfied
                if all(dep not in to_start or dep in start_order for dep in deps):
                    # Add to start order
                    start_order.append(component)
                    # Remove from to_start
                    to_start.remove(component)
                    # Break and start over
                    break
            else:
                # If we get here, there's a circular dependency
                logging.error(f"Circular dependency detected in components: {to_start}")
                break
        
        return start_order
    
    def start_component(self, component):
        """
        Start a component
        
        Args:
            component (str): Component name
        """
        if component not in self.config.get("components", {}):
            logging.error(f"Component not found: {component}")
            return
            
        config = self.config["components"][component]
        script = config.get("script")
        args = config.get("args", [])
        
        if not script:
            logging.error(f"No script defined for component: {component}")
            return
            
        # Build the command
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script)
        cmd = [sys.executable, script_path] + args
        
        try:
            # Start the process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Store the process
            self.processes[component] = process
            
            # Store component info
            self.components[component] = {
                "started_at": time.time(),
                "status": "running",
                "restarts": 0
            }
            
            logging.info(f"Started component: {component}")
            
        except Exception as e:
            logging.error(f"Error starting component {component}: {str(e)}")
    
    def stop_component(self, component):
        """
        Stop a component
        
        Args:
            component (str): Component name
        """
        if component not in self.processes:
            return
            
        process = self.processes[component]
        
        try:
            # Terminate the process
            process.terminate()
            
            # Wait for it to exit
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't exit
                process.kill()
            
            # Remove from processes
            del self.processes[component]
            
            # Update component status
            if component in self.components:
                self.components[component]["status"] = "stopped"
            
            logging.info(f"Stopped component: {component}")
            
        except Exception as e:
            logging.error(f"Error stopping component {component}: {str(e)}")
    
    def restart_component(self, component):
        """
        Restart a component
        
        Args:
            component (str): Component name
        """
        logging.info(f"Restarting component: {component}")
        
        # Stop the component
        self.stop_component(component)
        
        # Start the component
        self.start_component(component)
        
        # Update restart count
        if component in self.components:
            self.components[component]["restarts"] += 1
    
    def monitor_components(self):
        """Monitor running components and restart if needed"""
        while self.running:
            try:
                # Check each process
                for component, process in list(self.processes.items()):
                    # Check if the process is still running
                    if process.poll() is not None:
                        # Process has exited
                        logging.warning(f"Component {component} has exited with code {process.returncode}")
                        
                        # Update component status
                        if component in self.components:
                            self.components[component]["status"] = "crashed"
                        
                        # Restart if auto-restart is enabled
                        if self.config.get("startup", {}).get("auto_restart", True):
                            self.restart_component(component)
                
                # Sleep before next check
                time.sleep(5)
                
            except Exception as e:
                logging.error(f"Error monitoring components: {str(e)}")
                time.sleep(30)
    
    def get_status(self):
        """
        Get the status of all components
        
        Returns:
            dict: Component status
        """
        status = {}
        
        for component, info in self.components.items():
            # Check if the process is still running
            process = self.processes.get(component)
            if process:
                running = process.poll() is None
            else:
                running = False
                
            # Update status
            status[component] = {
                "running": running,
                "status": info["status"] if running else "stopped",
                "uptime": time.time() - info["started_at"] if running else 0,
                "restarts": info["restarts"]
            }
        
        return status

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    """Handle signals for graceful shutdown"""
    print("Shutting down Anima system...")
    if launcher:
        launcher.stop()
    sys.exit(0)

# Global launcher instance
launcher = None

def main():
    """Main entry point"""
    global launcher
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Anima Autonomous System Launcher")
    parser.add_argument("--no-welcome", action="store_true", help="Disable welcome message")
    parser.add_argument("--no-restart", action="store_true", help="Disable auto-restart")
    args = parser.parse_args()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create the launcher
        launcher = AnimaLauncher()
        
        # Apply command line overrides
        if args.no_welcome:
            launcher.config["startup"]["speak_welcome"] = False
        if args.no_restart:
            launcher.config["startup"]["auto_restart"] = False
        
        # Start the system
        launcher.start()
        
        # Keep the main thread alive
        while launcher.running:
            time.sleep(1)
            
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
        if launcher:
            launcher.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
