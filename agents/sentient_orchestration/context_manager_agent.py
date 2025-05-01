"""
Context Manager Agent - Manages shared context and information between agents to keep knowledge consistent.
"""

import logging
import time
import threading
import json
import os
from pathlib import Path
from datetime import datetime

class ContextManagerAgent:
    def __init__(self):
        self.name = "Context Manager Agent"
        self.status = "active"
        self.running = False
        self.context = {}  # The shared context data
        self.context_history = []  # History of context changes
        self.max_history = 100  # Maximum number of history entries to keep
        self.log_file = Path("logs/context_manager.log")
        self.context_file = Path("memory/shared_context.json")
        
        # Create log directory if it doesn't exist
        os.makedirs(self.log_file.parent, exist_ok=True)
        
        # Set up logging
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.name)
        self.logger.info(f"{self.name} initialized")
        
        # Thread for periodic saving
        self._thread = None
        
        # Event bus reference (will be set by orchestrator)
        self.event_bus = None
        
        # Load existing context
        self.load_context()

    def load_context(self):
        """Load shared context from file"""
        try:
            if self.context_file.exists():
                with open(self.context_file, 'r') as f:
                    data = json.load(f)
                    self.context = data.get("context", {})
                    self.context_history = data.get("history", [])
                    self.logger.info(f"Loaded shared context with {len(self.context)} entries")
            else:
                self.context = {}
                self.context_history = []
        except Exception as e:
            self.logger.error(f"Error loading shared context: {e}")
            self.context = {}
            self.context_history = []

    def save_context(self):
        """Save shared context to file"""
        try:
            os.makedirs(self.context_file.parent, exist_ok=True)
            with open(self.context_file, 'w') as f:
                json.dump({
                    "context": self.context,
                    "history": self.context_history,
                    "last_update": datetime.now().isoformat()
                }, f, indent=2)
            self.logger.debug(f"Saved shared context")
        except Exception as e:
            self.logger.error(f"Error saving shared context: {e}")

    def get_value(self, key, default=None):
        """Get a value from the shared context"""
        return self.context.get(key, default)

    def set_value(self, key, value, source=None):
        """Set a value in the shared context"""
        # Record the change in history
        self.context_history.insert(0, {
            "key": key,
            "old_value": self.context.get(key),
            "new_value": value,
            "source": source or "unknown",
            "timestamp": datetime.now().isoformat()
        })
        
        # Trim history if needed
        if len(self.context_history) > self.max_history:
            self.context_history = self.context_history[:self.max_history]
        
        # Update the context
        self.context[key] = value
        self.logger.info(f"Set context value: {key} = {value} (source: {source})")
        
        # Save the context
        self.save_context()
        
        # Emit event if event bus is available
        if self.event_bus:
            self.event_bus.emit("CONTEXT_UPDATED", {
                "key": key,
                "value": value,
                "source": source,
                "source_agent": self.name
            })
        
        return True

    def delete_value(self, key, source=None):
        """Delete a value from the shared context"""
        if key in self.context:
            # Record the change in history
            self.context_history.insert(0, {
                "key": key,
                "old_value": self.context.get(key),
                "new_value": None,
                "source": source or "unknown",
                "timestamp": datetime.now().isoformat(),
                "action": "delete"
            })
            
            # Trim history if needed
            if len(self.context_history) > self.max_history:
                self.context_history = self.context_history[:self.max_history]
            
            # Delete the value
            old_value = self.context.pop(key)
            self.logger.info(f"Deleted context value: {key} (was: {old_value}, source: {source})")
            
            # Save the context
            self.save_context()
            
            # Emit event if event bus is available
            if self.event_bus:
                self.event_bus.emit("CONTEXT_DELETED", {
                    "key": key,
                    "old_value": old_value,
                    "source": source,
                    "source_agent": self.name
                })
            
            return True
        return False

    def get_all_context(self):
        """Get the entire shared context"""
        return self.context.copy()

    def get_history(self, key=None, limit=None):
        """Get history of context changes, optionally filtered by key"""
        if key is None:
            history = self.context_history
        else:
            history = [entry for entry in self.context_history if entry["key"] == key]
        
        if limit is not None:
            history = history[:limit]
        
        return history

    def periodic_save(self):
        """Periodically save the context to disk"""
        self.logger.info("Starting periodic context saving")
        self.running = True
        
        while self.running:
            # Save the context
            self.save_context()
            
            # Sleep for a while
            time.sleep(60)  # Save every minute

    def start(self):
        """Start the context manager"""
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.periodic_save, daemon=True)
            self._thread.start()
            self.logger.info("Context manager started")
            return True
        return False

    def stop(self):
        """Stop the context manager"""
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
            self.logger.info("Context manager stopped")
            
            # Save one last time
            self.save_context()
            
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
            "context_entries": len(self.context),
            "history_entries": len(self.context_history)
        }

    def handle_event(self, event):
        """Handle events from the event bus"""
        event_type = event.get("type", "")
        data = event.get("data", {})
        
        if event_type == "SET_CONTEXT":
            # Set a context value
            if "key" in data and "value" in data:
                source = data.get("source", event.get("source_agent", "unknown"))
                return self.set_value(data["key"], data["value"], source)
        
        elif event_type == "DELETE_CONTEXT":
            # Delete a context value
            if "key" in data:
                source = data.get("source", event.get("source_agent", "unknown"))
                return self.delete_value(data["key"], source)
        
        elif event_type == "GET_CONTEXT":
            # Get a context value (and respond with it)
            if "key" in data and self.event_bus:
                value = self.get_value(data["key"])
                self.event_bus.emit("CONTEXT_VALUE", {
                    "key": data["key"],
                    "value": value,
                    "source_agent": self.name,
                    "request_id": data.get("request_id")
                })
                return True
        
        return False

    def diagnose(self):
        """Return diagnostic information about the agent"""
        return {
            "name": self.name,
            "status": "running" if self.heartbeat() else "stopped",
            "context_entries": len(self.context),
            "history_entries": len(self.context_history),
            "thread_alive": self._thread.is_alive() if self._thread else False,
            "sample_keys": list(self.context.keys())[:5]  # Show a few keys as a sample
        }
