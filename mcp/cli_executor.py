"""
CLI Executor for SoulCoreHub
Executes command line tools with real-time feedback similar to Amazon Q's DevOps interface
"""

import asyncio
import json
import os
import shlex
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable, AsyncGenerator

class CLIExecutor:
    """
    Executes command line tools with real-time feedback and logging
    """
    
    def __init__(self, log_dir: str = "logs/cli_execution"):
        """
        Initialize the CLI executor
        
        Args:
            log_dir: Directory to store execution logs
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
    
    async def execute_command(self, command: str, 
                             stream_callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
        """
        Execute a command and stream output with feedback
        
        Args:
            command: The command to execute
            stream_callback: Optional callback function to receive streaming output
            
        Returns:
            Dictionary containing execution results
        """
        cmd_parts = shlex.split(command)
        
        # Log the command
        log_entry = {
            "command": command,
            "timestamp": datetime.now().isoformat(),
            "status": "started"
        }
        
        # Send initial feedback
        if stream_callback:
            await stream_callback(f"Executing: {command}\n")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd_parts,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Stream stdout in real-time
            stdout_lines = []
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                    
                line_str = line.decode('utf-8')
                stdout_lines.append(line_str)
                
                if stream_callback:
                    await stream_callback(line_str)
            
            # Get final output
            stdout, stderr = await process.communicate()
            
            # Combine streamed lines with any remaining output
            full_stdout = ''.join(stdout_lines) + stdout.decode('utf-8')
            stderr_str = stderr.decode('utf-8') if stderr else ""
            
            # Update log with results
            log_entry["status"] = "completed" if process.returncode == 0 else "failed"
            log_entry["return_code"] = process.returncode
            log_entry["stderr"] = stderr_str
            
            # Save log
            log_file = f"{self.log_dir}/{int(time.time())}.json"
            with open(log_file, 'w') as f:
                json.dump(log_entry, f, indent=2)
            
            # Send error feedback if needed
            if stream_callback and stderr_str:
                await stream_callback(f"\nError output:\n{stderr_str}")
            
            # Send completion feedback
            if stream_callback:
                status = "✓ Success" if process.returncode == 0 else "✗ Failed"
                await stream_callback(f"\n{status} (exit code: {process.returncode})\n")
            
            return {
                "success": process.returncode == 0,
                "stdout": full_stdout,
                "stderr": stderr_str,
                "return_code": process.returncode,
                "log_file": log_file
            }
            
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            
            # Update log with error
            log_entry["status"] = "error"
            log_entry["error"] = error_msg
            
            # Save log
            log_file = f"{self.log_dir}/{int(time.time())}.json"
            with open(log_file, 'w') as f:
                json.dump(log_entry, f, indent=2)
            
            # Send error feedback
            if stream_callback:
                await stream_callback(f"\n{error_msg}\n")
            
            return {
                "success": False,
                "error": error_msg,
                "log_file": log_file
            }
    
    async def stream_command(self, command: str) -> AsyncGenerator[str, None]:
        """
        Execute a command and yield output as it becomes available
        
        Args:
            command: The command to execute
            
        Yields:
            Command output lines as they are generated
        """
        buffer = []
        
        async def collect_output(output: str):
            buffer.append(output)
            yield output
        
        await self.execute_command(command, collect_output)
        
        for line in buffer:
            yield line
