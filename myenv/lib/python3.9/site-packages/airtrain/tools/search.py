"""
Search tools for AirTrain agents.

This module provides tools for searching for content within files and directories.
"""

import os
import re
import subprocess
from typing import Dict, Any, List, Optional, cast

from .registry import StatelessTool, register_tool
from airtrain.integrations.search.exa import (
    ExaCredentials,
    ExaSearchSkill,
    ExaSearchInputSchema,
    ExaSearchOutputSchema,
    ExaContentConfig,
)


@register_tool("search_term")
class SearchTermTool(StatelessTool):
    """Tool for searching for specific terms within files."""

    def __init__(self):
        self.name = "search_term"
        self.description = "Search for a specific term or pattern within files"
        self.parameters = {
            "type": "object",
            "properties": {
                "term": {
                    "type": "string",
                    "description": "The term or pattern to search for",
                },
                "directory": {
                    "type": "string",
                    "description": "Directory to search in (defaults to current directory)",
                },
                "file_pattern": {
                    "type": "string",
                    "description": "Pattern to filter files (e.g., *.py, *.txt)",
                },
                "case_sensitive": {
                    "type": "boolean",
                    "description": "Whether the search should be case-sensitive",
                },
                "regex": {
                    "type": "boolean",
                    "description": "Whether to treat the term as a regular expression",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                },
                "max_context_lines": {
                    "type": "integer",
                    "description": "Number of context lines to show before and after matches",
                },
            },
            "required": ["term"],
        }

    def __call__(
        self,
        term: str,
        directory: str = ".",
        file_pattern: str = "*",
        case_sensitive: bool = False,
        regex: bool = False,
        max_results: int = 100,
        max_context_lines: int = 2,
    ) -> Dict[str, Any]:
        """Search for a specific term within files."""
        try:
            # Try to use grep if available (more efficient than pure Python)
            try:
                return self._search_with_grep(
                    term,
                    directory,
                    file_pattern,
                    case_sensitive,
                    regex,
                    max_results,
                    max_context_lines,
                )
            except (subprocess.SubprocessError, FileNotFoundError):
                # Fall back to Python implementation if grep is not available
                return self._search_with_python(
                    term,
                    directory,
                    file_pattern,
                    case_sensitive,
                    regex,
                    max_results,
                    max_context_lines,
                )
        except Exception as e:
            return {"success": False, "error": f"Error searching for term: {str(e)}"}

    def _search_with_grep(
        self,
        term: str,
        directory: str,
        file_pattern: str,
        case_sensitive: bool,
        regex: bool,
        max_results: int,
        max_context_lines: int,
    ) -> Dict[str, Any]:
        """Use grep to search for terms (more efficient)."""
        # Prepare grep command
        cmd = ["grep"]

        # Add grep options
        if not case_sensitive:
            cmd.append("-i")  # Case insensitive

        if not regex:
            cmd.append("-F")  # Fixed string (not regex)

        # Add context lines
        if max_context_lines > 0:
            cmd.append(f"-C{max_context_lines}")  # Context lines

        # Add recursive search
        cmd.append("-r")

        # Add line numbers
        cmd.append("-n")

        # Add max count if specified
        if max_results > 0:
            cmd.append(f"--max-count={max_results}")

        # Add search term
        cmd.append(term)

        # Add directory
        cmd.append(directory)

        # Add file pattern if specified
        if file_pattern != "*":
            cmd.append("--include")
            cmd.append(file_pattern)

        # Execute grep command
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Process results
        if result.returncode != 0 and result.returncode != 1:  # 1 means no matches
            raise subprocess.SubprocessError(f"Grep error: {result.stderr}")

        # Parse output
        matches = []
        for line in result.stdout.splitlines():
            if not line.strip():
                continue

            # Parse grep output (filename:line_number:content)
            parts = line.split(":", 2)
            if len(parts) >= 3:
                filename = parts[0]
                line_number = int(parts[1])
                content = parts[2]

                matches.append(
                    {"file": filename, "line": line_number, "content": content}
                )

        return {
            "success": True,
            "term": term,
            "directory": directory,
            "file_pattern": file_pattern,
            "matches": matches,
            "match_count": len(matches),
            "truncated": result.stdout.count("\n") >= max_results,
        }

    def _search_with_python(
        self,
        term: str,
        directory: str,
        file_pattern: str,
        case_sensitive: bool,
        regex: bool,
        max_results: int,
        max_context_lines: int,
    ) -> Dict[str, Any]:
        """Use Python to search for terms (fallback method)."""
        import fnmatch
        import glob

        # Expand directory path
        directory = os.path.expanduser(directory)

        if not os.path.exists(directory):
            return {
                "success": False,
                "error": f"Directory '{directory}' does not exist",
            }

        if not os.path.isdir(directory):
            return {"success": False, "error": f"Path '{directory}' is not a directory"}

        # Compile regex if needed
        if regex:
            if case_sensitive:
                pattern = re.compile(term)
            else:
                pattern = re.compile(term, re.IGNORECASE)
        else:
            if case_sensitive:
                pattern = re.compile(re.escape(term))
            else:
                pattern = re.compile(re.escape(term), re.IGNORECASE)

        # Find all files matching the pattern
        matches = []
        match_count = 0
        truncated = False

        for root, _, files in os.walk(directory):
            for filename in fnmatch.filter(files, file_pattern):
                file_path = os.path.join(root, filename)

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()

                    # Search for matches in the file
                    for i, line in enumerate(lines):
                        if pattern.search(line):
                            line_number = i + 1

                            # Extract context lines
                            context_start = max(0, i - max_context_lines)
                            context_end = min(len(lines), i + max_context_lines + 1)
                            context_lines = lines[context_start:context_end]

                            matches.append(
                                {
                                    "file": file_path,
                                    "line": line_number,
                                    "content": line.rstrip("\n"),
                                    "context": {
                                        "start_line": context_start + 1,
                                        "end_line": context_end,
                                        "lines": [
                                            l.rstrip("\n") for l in context_lines
                                        ],
                                    },
                                }
                            )

                            match_count += 1
                            if match_count >= max_results:
                                truncated = True
                                break

                    if truncated:
                        break

                except Exception as e:
                    # Skip files that can't be read
                    continue

            if truncated:
                break

        return {
            "success": True,
            "term": term,
            "directory": directory,
            "file_pattern": file_pattern,
            "matches": matches,
            "match_count": match_count,
            "truncated": truncated,
        }

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


@register_tool("web_search")
class WebSearchTool(StatelessTool):
    """Tool for searching the web using the Exa API."""

    def __init__(self):
        self.name = "web_search"
        self.description = "Search the web for information using the Exa search API"
        self.parameters = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to execute",
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return (default: 5)",
                },
                "include_domains": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of domains to include in the search",
                },
                "exclude_domains": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of domains to exclude from the search",
                },
                "use_autoprompt": {
                    "type": "boolean",
                    "description": "Whether to use Exa's autoprompt feature for better results",
                },
            },
            "required": ["query"],
        }

        # Exa API key from environment variable
        api_key = os.environ.get("EXA_API_KEY", "")
        if api_key:
            self.credentials = ExaCredentials(api_key=api_key)
            self.skill = ExaSearchSkill(credentials=self.credentials)
        else:
            self.credentials = None
            self.skill = None

    async def _async_search(
        self,
        query: str,
        num_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        use_autoprompt: bool = False,
    ) -> Dict[str, Any]:
        """Execute the search asynchronously."""
        if not self.credentials or not self.skill:
            return {
                "success": False,
                "error": "Exa API key not configured. Set the EXA_API_KEY environment variable.",
            }

        try:
            # Create input for the search
            search_input = ExaSearchInputSchema(
                query=query,
                numResults=num_results,
                includeDomains=include_domains,
                excludeDomains=exclude_domains,
                useAutoprompt=use_autoprompt,
                contents=ExaContentConfig(text=True),
            )

            # Execute search
            result = await self.skill.process(search_input)

            # Process results into a simplified format
            search_results = []
            for item in result.results:
                search_results.append(
                    {
                        "title": item.title or "No title",
                        "url": item.url,
                        "content": (
                            item.text[:1000] if item.text else "No content available"
                        ),
                        "score": item.score,
                        "published": item.published,
                    }
                )

            return {
                "success": True,
                "query": query,
                "results": search_results,
                "result_count": len(search_results),
                "autoprompt": result.autopromptString,
            }

        except Exception as e:
            return {"success": False, "error": f"Error performing web search: {str(e)}"}

    def __call__(
        self,
        query: str,
        num_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        use_autoprompt: bool = False,
    ) -> Dict[str, Any]:
        """
        Search the web for information.

        Args:
            query: The search query to execute
            num_results: Number of results to return
            include_domains: List of domains to include in search results
            exclude_domains: List of domains to exclude from search results
            use_autoprompt: Whether to use Exa's autoprompt feature

        Returns:
            Dictionary containing search results or error information
        """
        import asyncio

        if not self.credentials or not self.skill:
            return {
                "success": False,
                "error": "Exa API key not configured. Set the EXA_API_KEY environment variable.",
            }

        # Run the async search in a new event loop
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self._async_search(
                    query=query,
                    num_results=num_results,
                    include_domains=include_domains,
                    exclude_domains=exclude_domains,
                    use_autoprompt=use_autoprompt,
                )
            )
            loop.close()
            return result
        except Exception as e:
            return {"success": False, "error": f"Error executing search: {str(e)}"}

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
