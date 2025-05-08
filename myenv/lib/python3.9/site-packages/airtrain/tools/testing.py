"""
Testing tools for AirTrain agents.

This module provides tools for running tests and test frameworks.
"""

import os
import subprocess
from typing import Dict, Any, Optional, List

from .registry import StatelessTool, register_tool


@register_tool("run_pytest")
class RunPytestTool(StatelessTool):
    """Tool for running Python pytest on test files."""

    def __init__(self):
        self.name = "run_pytest"
        self.description = "Run pytest on a specific test file or directory"
        self.parameters = {
            "type": "object",
            "properties": {
                "test_path": {
                    "type": "string",
                    "description": "Path to the test file or directory to run",
                },
                "args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Additional pytest arguments",
                },
                "working_dir": {
                    "type": "string",
                    "description": "Working directory to run pytest from",
                },
                "verbose": {
                    "type": "boolean",
                    "description": "Run tests in verbose mode",
                },
                "capture_output": {
                    "type": "boolean",
                    "description": "Capture stdout/stderr or show directly",
                },
                "timeout": {
                    "type": "number",
                    "description": "Timeout in seconds for the test run",
                },
            },
            "required": ["test_path"],
        }

    def __call__(
        self,
        test_path: str,
        args: Optional[List[str]] = None,
        working_dir: Optional[str] = None,
        verbose: bool = False,
        capture_output: bool = True,
        timeout: float = 60.0,
    ) -> Dict[str, Any]:
        """Run pytest on a specific test file or directory."""
        try:
            # Expand user path if present
            test_path = os.path.expanduser(test_path)

            # Validate test path
            if not os.path.exists(test_path):
                return {
                    "success": False,
                    "error": f"Test path '{test_path}' does not exist",
                }

            # Prepare pytest command
            cmd = ["pytest", test_path]

            # Add verbosity flag if requested
            if verbose:
                cmd.append("-v")

            # Add any additional arguments
            if args:
                cmd.extend(args)

            # Run pytest
            process = subprocess.run(
                cmd,
                cwd=working_dir,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
            )

            result = {
                "success": process.returncode == 0,
                "return_code": process.returncode,
                "test_path": test_path,
                "command": " ".join(cmd),
            }

            if capture_output:
                result["stdout"] = process.stdout
                result["stderr"] = process.stderr

                # Parse test summary from output
                if "failed" in process.stdout or "passed" in process.stdout:
                    summary_lines = []
                    for line in process.stdout.splitlines():
                        if "failed" in line or "passed" in line or "skipped" in line:
                            if "===" in line and "===" in line:
                                summary_lines.append(line.strip())

                    if summary_lines:
                        result["summary"] = summary_lines

            return result

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Pytest run timed out after {timeout} seconds",
            }
        except Exception as e:
            return {"success": False, "error": f"Error running pytest: {str(e)}"}

    def to_dict(self):
        """Convert tool to dictionary format for LLM function calling."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
