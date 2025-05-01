# modules/mcp_sync_manager.py
"""
MCP Sync Manager Module
---------------------
Manages MCP tools and resources dynamically.
"""

import logging
import json
import os
import time
import threading
import hashlib
from datetime import datetime

logger = logging.getLogger("EvoVe.MCPSyncManager")

class MCPSyncManager:
    """Manages MCP tools and resources dynamically."""
    
    def __init__(self, evove):
        """Initialize the MCP sync manager."""
        self.evove = evove
        self.config = evove.config.get("mcp_sync", {})
        self.tools_file = self.config.get("tools_file", "mcp/mcp_tools.json")
        self.resources_file = self.config.get("resources_file", "mcp/mcp_resources.json")
        self.backup_dir = self.config.get("backup_dir", "backups/mcp")
        self.check_interval = self.config.get("check_interval", 300)  # 5 minutes
        self.running = False
        self.sync_thread = None
        self.tools_hash = None
        self.resources_hash = None
        
    def start(self):
        """Start the MCP sync manager."""
        if self.running:
            logger.warning("MCP sync manager is already running")
            return
            
        self.running = True
        logger.info("Starting MCP sync manager")
        
        # Create backup directory if it doesn't exist
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Calculate initial hashes
        self.tools_hash = self._calculate_file_hash(self.tools_file)
        self.resources_hash = self._calculate_file_hash(self.resources_file)
        
        # Start sync thread
        self.sync_thread = threading.Thread(target=self._sync_loop)
        self.sync_thread.daemon = True
        self.sync_thread.start()
        
    def stop(self):
        """Stop the MCP sync manager."""
        if not self.running:
            logger.warning("MCP sync manager is not running")
            return
            
        self.running = False
        logger.info("Stopping MCP sync manager")
        
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
    
    def _sync_loop(self):
        """Main sync loop."""
        while self.running:
            try:
                self._check_for_changes()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in MCP sync loop: {e}")
                time.sleep(60)  # Shorter interval on error
    
    def _check_for_changes(self):
        """Check for changes in MCP files."""
        logger.debug("Checking for MCP file changes")
        
        # Check tools file
        current_tools_hash = self._calculate_file_hash(self.tools_file)
        if current_tools_hash and current_tools_hash != self.tools_hash:
            logger.info("MCP tools file has changed")
            self._handle_tools_change()
            self.tools_hash = current_tools_hash
        
        # Check resources file
        current_resources_hash = self._calculate_file_hash(self.resources_file)
        if current_resources_hash and current_resources_hash != self.resources_hash:
            logger.info("MCP resources file has changed")
            self._handle_resources_change()
            self.resources_hash = current_resources_hash
    
    def _calculate_file_hash(self, file_path):
        """Calculate the hash of a file."""
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return None
    
    def _handle_tools_change(self):
        """Handle changes in the MCP tools file."""
        try:
            # Create backup
            self._backup_file(self.tools_file)
            
            # Load tools
            tools = self._load_json_file(self.tools_file)
            if not tools:
                return
                
            # Register tools with MCP
            if hasattr(self.evove, "mcp_bridge") and self.evove.mcp_bridge.connected:
                self._register_tools(tools)
            else:
                logger.warning("MCP bridge not connected, cannot register tools")
                
        except Exception as e:
            logger.error(f"Failed to handle tools change: {e}")
    
    def _handle_resources_change(self):
        """Handle changes in the MCP resources file."""
        try:
            # Create backup
            self._backup_file(self.resources_file)
            
            # Load resources
            resources = self._load_json_file(self.resources_file)
            if not resources:
                return
                
            # Register resources with MCP
            if hasattr(self.evove, "mcp_bridge") and self.evove.mcp_bridge.connected:
                self._register_resources(resources)
            else:
                logger.warning("MCP bridge not connected, cannot register resources")
                
        except Exception as e:
            logger.error(f"Failed to handle resources change: {e}")
    
    def _backup_file(self, file_path):
        """Create a backup of a file."""
        if not os.path.exists(file_path):
            return
            
        try:
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            file_name = os.path.basename(file_path)
            backup_path = os.path.join(self.backup_dir, f"{file_name}.{timestamp}")
            
            # Copy the file
            with open(file_path, 'rb') as src, open(backup_path, 'wb') as dst:
                dst.write(src.read())
                
            logger.info(f"Created backup of {file_path} at {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to backup {file_path}: {e}")
            return None
    
    def _load_json_file(self, file_path):
        """Load a JSON file."""
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return None
            
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            logger.error(f"Failed to load JSON file {file_path}: {e}")
            return None
    
    def _register_tools(self, tools):
        """Register tools with MCP."""
        if not isinstance(tools, list):
            logger.warning("Tools data is not a list")
            return
            
        for tool in tools:
            try:
                tool_name = tool.get("name")
                if not tool_name:
                    logger.warning("Tool missing name, skipping")
                    continue
                    
                logger.info(f"Registering tool: {tool_name}")
                
                # Send registration message
                self.evove.mcp_bridge.send_message({
                    "type": "register_tool",
                    "tool": tool
                })
                
            except Exception as e:
                logger.error(f"Failed to register tool: {e}")
    
    def _register_resources(self, resources):
        """Register resources with MCP."""
        if not isinstance(resources, list):
            logger.warning("Resources data is not a list")
            return
            
        for resource in resources:
            try:
                resource_name = resource.get("name")
                if not resource_name:
                    logger.warning("Resource missing name, skipping")
                    continue
                    
                logger.info(f"Registering resource: {resource_name}")
                
                # Send registration message
                self.evove.mcp_bridge.send_message({
                    "type": "register_resource",
                    "resource": resource
                })
                
            except Exception as e:
                logger.error(f"Failed to register resource: {e}")
    
    def add_tool(self, tool):
        """Add a new tool to the MCP tools file."""
        try:
            # Load existing tools
            tools = self._load_json_file(self.tools_file) or []
            
            # Check if tool already exists
            for i, existing_tool in enumerate(tools):
                if existing_tool.get("name") == tool.get("name"):
                    # Update existing tool
                    tools[i] = tool
                    logger.info(f"Updated existing tool: {tool.get('name')}")
                    break
            else:
                # Add new tool
                tools.append(tool)
                logger.info(f"Added new tool: {tool.get('name')}")
            
            # Save tools file
            with open(self.tools_file, 'w') as f:
                json.dump(tools, f, indent=2)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to add tool: {e}")
            return False
    
    def remove_tool(self, tool_name):
        """Remove a tool from the MCP tools file."""
        try:
            # Load existing tools
            tools = self._load_json_file(self.tools_file) or []
            
            # Find and remove the tool
            for i, tool in enumerate(tools):
                if tool.get("name") == tool_name:
                    tools.pop(i)
                    logger.info(f"Removed tool: {tool_name}")
                    break
            else:
                logger.warning(f"Tool not found: {tool_name}")
                return False
            
            # Save tools file
            with open(self.tools_file, 'w') as f:
                json.dump(tools, f, indent=2)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove tool: {e}")
            return False
    
    def add_resource(self, resource):
        """Add a new resource to the MCP resources file."""
        try:
            # Load existing resources
            resources = self._load_json_file(self.resources_file) or []
            
            # Check if resource already exists
            for i, existing_resource in enumerate(resources):
                if existing_resource.get("name") == resource.get("name"):
                    # Update existing resource
                    resources[i] = resource
                    logger.info(f"Updated existing resource: {resource.get('name')}")
                    break
            else:
                # Add new resource
                resources.append(resource)
                logger.info(f"Added new resource: {resource.get('name')}")
            
            # Save resources file
            with open(self.resources_file, 'w') as f:
                json.dump(resources, f, indent=2)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to add resource: {e}")
            return False
    
    def remove_resource(self, resource_name):
        """Remove a resource from the MCP resources file."""
        try:
            # Load existing resources
            resources = self._load_json_file(self.resources_file) or []
            
            # Find and remove the resource
            for i, resource in enumerate(resources):
                if resource.get("name") == resource_name:
                    resources.pop(i)
                    logger.info(f"Removed resource: {resource_name}")
                    break
            else:
                logger.warning(f"Resource not found: {resource_name}")
                return False
            
            # Save resources file
            with open(self.resources_file, 'w') as f:
                json.dump(resources, f, indent=2)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove resource: {e}")
            return False



