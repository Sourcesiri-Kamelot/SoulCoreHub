#!/usr/bin/env python3
"""
CLI Sync Module - Command-line interface synchronization for EvoVe
Enables EvoVe to interact with the command line and other CLI tools
"""

import os
import sys
import json
import logging
import subprocess
import threading
import queue
from pathlib import Path

class CLISync:
    """Command-line interface synchronization for EvoVe"""
    
    def __init__(self, mcp_bridge=None):
        """
        Initialize the CLI Sync
        
        Args:
            mcp_bridge: MCP Bridge for communication
        """
        self.mcp_bridge = mcp_bridge
        self.command_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.worker_thread = None
        self.running = False
        logging.info("CLI Sync initialized")
    
    def execute_command(self, command, cwd=None):
        """
        Execute a shell command
        
        Args:
            command (str): Command to execute
            cwd (str): Working directory
            
        Returns:
            dict: Result with output or error
        """
        if self.mcp_bridge:
            return self.mcp_bridge.execute_command(command, cwd)
        
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd
            )
            
            stdout, stderr = process.communicate()
            exit_code = process.returncode
            
            return {
                "command": command,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
                "success": exit_code == 0
            }
        except Exception as e:
            logging.error(f"Error executing command: {str(e)}")
            return {"error": str(e)}
    
    def worker_loop(self):
        """Worker loop for processing commands"""
        self.running = True
        
        while self.running:
            try:
                # Get command from queue with timeout
                try:
                    command_data = self.command_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                # Execute command
                command = command_data.get("command", "")
                cwd = command_data.get("cwd", None)
                command_id = command_data.get("id", None)
                
                result = self.execute_command(command, cwd)
                
                # Add command ID to result
                if command_id:
                    result["id"] = command_id
                
                # Put result in result queue
                self.result_queue.put(result)
                
                # Mark task as done
                self.command_queue.task_done()
            except Exception as e:
                logging.error(f"Error in worker loop: {str(e)}")
    
    def start_worker(self):
        """
        Start the worker thread
        
        Returns:
            bool: True if worker started, False otherwise
        """
        if self.running:
            logging.warning("Worker is already running")
            return False
        
        try:
            self.worker_thread = threading.Thread(
                target=self.worker_loop,
                daemon=True
            )
            self.worker_thread.start()
            logging.info("Started CLI worker thread")
            return True
        except Exception as e:
            logging.error(f"Error starting worker: {str(e)}")
            return False
    
    def stop_worker(self):
        """
        Stop the worker thread
        
        Returns:
            bool: True if worker stopped, False otherwise
        """
        if not self.running:
            logging.warning("Worker is not running")
            return False
        
        try:
            self.running = False
            if self.worker_thread:
                self.worker_thread.join(timeout=5)
            logging.info("Stopped CLI worker thread")
            return True
        except Exception as e:
            logging.error(f"Error stopping worker: {str(e)}")
            return False
    
    def queue_command(self, command, cwd=None, command_id=None):
        """
        Queue a command for execution
        
        Args:
            command (str): Command to execute
            cwd (str): Working directory
            command_id: Identifier for the command
            
        Returns:
            str: Command ID
        """
        if not self.running:
            self.start_worker()
        
        # Generate command ID if not provided
        if command_id is None:
            import uuid
            command_id = str(uuid.uuid4())
        
        # Queue command
        self.command_queue.put({
            "command": command,
            "cwd": cwd,
            "id": command_id
        })
        
        return command_id
    
    def get_result(self, timeout=None):
        """
        Get a result from the result queue
        
        Args:
            timeout (float): Timeout in seconds
            
        Returns:
            dict: Command result or None if timeout
        """
        try:
            return self.result_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def sync_execute(self, command, cwd=None, timeout=30):
        """
        Execute a command synchronously
        
        Args:
            command (str): Command to execute
            cwd (str): Working directory
            timeout (float): Timeout in seconds
            
        Returns:
            dict: Command result
        """
        # Queue command
        command_id = self.queue_command(command, cwd)
        
        # Wait for result
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = self.get_result(timeout=0.1)
            
            if result and result.get("id") == command_id:
                return result
        
        return {"error": f"Command timed out after {timeout} seconds", "command": command}

# Example usage
if __name__ == "__main__":
    import time
    logging.basicConfig(level=logging.INFO)
    
    cli_sync = CLISync()
    cli_sync.start_worker()
    
    # Queue some commands
    cli_sync.queue_command("echo 'Hello from CLI Sync'")
    cli_sync.queue_command("ls -la")
    
    # Get results
    for _ in range(2):
        result = cli_sync.get_result(timeout=5)
        if result:
            print(f"Command: {result.get('command')}")
            print(f"Output: {result.get('stdout')}")
    
    # Synchronous execution
    result = cli_sync.sync_execute("date")
    print(f"Date command output: {result.get('stdout')}")
    
    cli_sync.stop_worker()
