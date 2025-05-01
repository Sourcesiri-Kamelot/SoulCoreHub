#!/usr/bin/env python3
"""
GitHub Connector - Enables Anima to search and access GitHub repositories
Provides knowledge retrieval from GitHub for programming and computer science topics
"""

import os
import json
import logging
import requests
import base64
from pathlib import Path
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("github_connector.log"),
        logging.StreamHandler()
    ]
)

class GitHubConnector:
    """GitHub connector for accessing repositories and code examples"""
    
    def __init__(self, token=None):
        """
        Initialize the GitHub connector
        
        Args:
            token (str): GitHub API token (optional)
        """
        self.token = token or os.environ.get("GITHUB_API_TOKEN")
        self.cache_dir = Path.home() / "SoulCoreHub" / "data" / "github_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_expiry = 24  # Cache expiry in hours
        logging.info("GitHub connector initialized")
    
    def _get_headers(self):
        """Get headers for GitHub API requests"""
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        
        return headers
    
    def _get_cache_path(self, cache_key):
        """Get the path for a cached item"""
        # Create a safe filename from the cache key
        safe_key = "".join(c if c.isalnum() else "_" for c in cache_key)
        return self.cache_dir / f"{safe_key}.json"
    
    def _get_from_cache(self, cache_key):
        """
        Get an item from the cache
        
        Args:
            cache_key (str): Cache key
            
        Returns:
            dict: Cached data or None if not found or expired
        """
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, "r") as f:
                cached = json.load(f)
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(cached["timestamp"])
            if datetime.now() - cached_time > timedelta(hours=self.cache_expiry):
                return None
            
            return cached["data"]
        except Exception as e:
            logging.error(f"Error reading from cache: {str(e)}")
            return None
    
    def _save_to_cache(self, cache_key, data):
        """
        Save an item to the cache
        
        Args:
            cache_key (str): Cache key
            data: Data to cache
        """
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, "w") as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "data": data
                }, f)
        except Exception as e:
            logging.error(f"Error saving to cache: {str(e)}")
    
    def search_code(self, query, language=None, limit=10):
        """
        Search for code on GitHub
        
        Args:
            query (str): Search query
            language (str): Programming language filter (optional)
            limit (int): Maximum number of results
            
        Returns:
            list: Search results
        """
        # Build the query
        q = query
        if language:
            q += f" language:{language}"
        
        # Check cache first
        cache_key = f"search_code_{q}_{limit}"
        cached = self._get_from_cache(cache_key)
        if cached:
            logging.info(f"Retrieved code search results from cache for '{q}'")
            return cached
        
        # Make the API request
        try:
            url = "https://api.github.com/search/code"
            params = {
                "q": q,
                "per_page": min(limit, 100)  # GitHub API limit
            }
            
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            
            results = response.json()
            
            # Process the results
            processed_results = []
            for item in results.get("items", [])[:limit]:
                processed_results.append({
                    "name": item.get("name"),
                    "path": item.get("path"),
                    "repository": item.get("repository", {}).get("full_name"),
                    "url": item.get("html_url"),
                    "repository_url": item.get("repository", {}).get("html_url")
                })
            
            # Cache the results
            self._save_to_cache(cache_key, processed_results)
            
            logging.info(f"Found {len(processed_results)} code results for '{q}'")
            return processed_results
        except Exception as e:
            logging.error(f"Error searching code: {str(e)}")
            return []
    
    def search_repositories(self, query, language=None, sort="stars", limit=10):
        """
        Search for repositories on GitHub
        
        Args:
            query (str): Search query
            language (str): Programming language filter (optional)
            sort (str): Sort order (stars, forks, updated)
            limit (int): Maximum number of results
            
        Returns:
            list: Search results
        """
        # Build the query
        q = query
        if language:
            q += f" language:{language}"
        
        # Check cache first
        cache_key = f"search_repos_{q}_{sort}_{limit}"
        cached = self._get_from_cache(cache_key)
        if cached:
            logging.info(f"Retrieved repository search results from cache for '{q}'")
            return cached
        
        # Make the API request
        try:
            url = "https://api.github.com/search/repositories"
            params = {
                "q": q,
                "sort": sort,
                "order": "desc",
                "per_page": min(limit, 100)  # GitHub API limit
            }
            
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            
            results = response.json()
            
            # Process the results
            processed_results = []
            for item in results.get("items", [])[:limit]:
                processed_results.append({
                    "name": item.get("name"),
                    "full_name": item.get("full_name"),
                    "description": item.get("description"),
                    "url": item.get("html_url"),
                    "stars": item.get("stargazers_count"),
                    "forks": item.get("forks_count"),
                    "language": item.get("language")
                })
            
            # Cache the results
            self._save_to_cache(cache_key, processed_results)
            
            logging.info(f"Found {len(processed_results)} repository results for '{q}'")
            return processed_results
        except Exception as e:
            logging.error(f"Error searching repositories: {str(e)}")
            return []
    
    def get_file_content(self, repo, path):
        """
        Get the content of a file from a GitHub repository
        
        Args:
            repo (str): Repository name (e.g., "username/repo")
            path (str): Path to the file
            
        Returns:
            str: File content
        """
        # Check cache first
        cache_key = f"file_content_{repo}_{path}"
        cached = self._get_from_cache(cache_key)
        if cached:
            logging.info(f"Retrieved file content from cache for '{repo}/{path}'")
            return cached
        
        # Make the API request
        try:
            url = f"https://api.github.com/repos/{repo}/contents/{path}"
            
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            content_data = response.json()
            
            # GitHub API returns base64-encoded content
            if content_data.get("encoding") == "base64":
                content = base64.b64decode(content_data.get("content")).decode("utf-8")
            else:
                content = content_data.get("content", "")
            
            # Cache the content
            self._save_to_cache(cache_key, content)
            
            logging.info(f"Retrieved file content for '{repo}/{path}'")
            return content
        except Exception as e:
            logging.error(f"Error getting file content: {str(e)}")
            return None
    
    def get_repository_structure(self, repo, path=""):
        """
        Get the structure of a GitHub repository
        
        Args:
            repo (str): Repository name (e.g., "username/repo")
            path (str): Path within the repository (optional)
            
        Returns:
            list: Repository structure
        """
        # Check cache first
        cache_key = f"repo_structure_{repo}_{path}"
        cached = self._get_from_cache(cache_key)
        if cached:
            logging.info(f"Retrieved repository structure from cache for '{repo}/{path}'")
            return cached
        
        # Make the API request
        try:
            url = f"https://api.github.com/repos/{repo}/contents/{path}"
            
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            contents = response.json()
            
            # Process the results
            structure = []
            for item in contents:
                structure.append({
                    "name": item.get("name"),
                    "path": item.get("path"),
                    "type": item.get("type"),
                    "url": item.get("html_url"),
                    "download_url": item.get("download_url")
                })
            
            # Cache the structure
            self._save_to_cache(cache_key, structure)
            
            logging.info(f"Retrieved repository structure for '{repo}/{path}'")
            return structure
        except Exception as e:
            logging.error(f"Error getting repository structure: {str(e)}")
            return []
    
    def search_topics(self, query, limit=10):
        """
        Search for topics on GitHub
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results
            
        Returns:
            list: Search results
        """
        # Check cache first
        cache_key = f"search_topics_{query}_{limit}"
        cached = self._get_from_cache(cache_key)
        if cached:
            logging.info(f"Retrieved topic search results from cache for '{query}'")
            return cached
        
        # Make the API request
        try:
            url = "https://api.github.com/search/topics"
            params = {
                "q": query,
                "per_page": min(limit, 100)  # GitHub API limit
            }
            
            headers = self._get_headers()
            # Topics API requires this specific preview header
            headers["Accept"] = "application/vnd.github.mercy-preview+json"
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            results = response.json()
            
            # Process the results
            processed_results = []
            for item in results.get("items", [])[:limit]:
                processed_results.append({
                    "name": item.get("name"),
                    "display_name": item.get("display_name", item.get("name")),
                    "description": item.get("description"),
                    "url": f"https://github.com/topics/{item.get('name')}"
                })
            
            # Cache the results
            self._save_to_cache(cache_key, processed_results)
            
            logging.info(f"Found {len(processed_results)} topic results for '{query}'")
            return processed_results
        except Exception as e:
            logging.error(f"Error searching topics: {str(e)}")
            return []
    
    def get_programming_languages(self):
        """
        Get a list of popular programming languages on GitHub
        
        Returns:
            list: Programming languages
        """
        # Check cache first
        cache_key = "programming_languages"
        cached = self._get_from_cache(cache_key)
        if cached:
            logging.info("Retrieved programming languages from cache")
            return cached
        
        # Make the API request
        try:
            url = "https://api.github.com/search/repositories"
            params = {
                "q": "stars:>1000",
                "sort": "stars",
                "order": "desc",
                "per_page": 100
            }
            
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            
            results = response.json()
            
            # Extract languages
            languages = {}
            for item in results.get("items", []):
                lang = item.get("language")
                if lang:
                    languages[lang] = languages.get(lang, 0) + 1
            
            # Sort by popularity
            sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)
            language_list = [lang for lang, count in sorted_languages]
            
            # Cache the languages
            self._save_to_cache(cache_key, language_list)
            
            logging.info(f"Retrieved {len(language_list)} programming languages")
            return language_list
        except Exception as e:
            logging.error(f"Error getting programming languages: {str(e)}")
            return []
    
    def find_code_examples(self, language, concept, limit=5):
        """
        Find code examples for a specific programming concept
        
        Args:
            language (str): Programming language
            concept (str): Programming concept
            limit (int): Maximum number of results
            
        Returns:
            list: Code examples
        """
        # Build the query
        query = f"{concept} language:{language}"
        
        # Search for code
        results = self.search_code(query, limit=limit)
        
        # Get file content for each result
        examples = []
        for result in results:
            repo = result.get("repository")
            path = result.get("path")
            
            if repo and path:
                content = self.get_file_content(repo, path)
                if content:
                    examples.append({
                        "name": result.get("name"),
                        "path": path,
                        "repository": repo,
                        "url": result.get("url"),
                        "content": content
                    })
        
        logging.info(f"Found {len(examples)} code examples for '{concept}' in {language}")
        return examples

# Register GitHub tools with MCP server
def register_github_tools(server):
    """
    Register GitHub tools with the MCP server
    
    Args:
        server: MCP server instance
    """
    github = GitHubConnector()
    
    # Search code tool
    async def search_code_tool(params, metadata=None):
        query = params.get("query", "")
        language = params.get("language", None)
        limit = params.get("limit", 10)
        return github.search_code(query, language, limit)
    
    # Search repositories tool
    async def search_repositories_tool(params, metadata=None):
        query = params.get("query", "")
        language = params.get("language", None)
        sort = params.get("sort", "stars")
        limit = params.get("limit", 10)
        return github.search_repositories(query, language, sort, limit)
    
    # Get file content tool
    async def get_file_content_tool(params, metadata=None):
        repo = params.get("repo", "")
        path = params.get("path", "")
        return github.get_file_content(repo, path)
    
    # Get repository structure tool
    async def get_repository_structure_tool(params, metadata=None):
        repo = params.get("repo", "")
        path = params.get("path", "")
        return github.get_repository_structure(repo, path)
    
    # Find code examples tool
    async def find_code_examples_tool(params, metadata=None):
        language = params.get("language", "")
        concept = params.get("concept", "")
        limit = params.get("limit", 5)
        return github.find_code_examples(language, concept, limit)
    
    # Register the tools
    server.register_tool(
        "github_search_code",
        search_code_tool,
        "Search for code on GitHub",
        "curious"
    )
    
    server.register_tool(
        "github_search_repositories",
        search_repositories_tool,
        "Search for repositories on GitHub",
        "curious"
    )
    
    server.register_tool(
        "github_get_file_content",
        get_file_content_tool,
        "Get the content of a file from a GitHub repository",
        "focused"
    )
    
    server.register_tool(
        "github_get_repository_structure",
        get_repository_structure_tool,
        "Get the structure of a GitHub repository",
        "curious"
    )
    
    server.register_tool(
        "github_find_code_examples",
        find_code_examples_tool,
        "Find code examples for a specific programming concept",
        "helpful"
    )

# Example usage
if __name__ == "__main__":
    try:
        # Create GitHub connector
        github = GitHubConnector()
        
        # Test searching for code
        print("Searching for Python sorting algorithms...")
        results = github.search_code("sorting algorithm", "python", limit=3)
        for result in results:
            print(f"- {result['name']} ({result['repository']})")
            print(f"  URL: {result['url']}")
            print()
        
        # Test finding code examples
        print("Finding code examples for Python decorators...")
        examples = github.find_code_examples("python", "decorator", limit=1)
        for example in examples:
            print(f"- {example['name']} ({example['repository']})")
            print(f"  URL: {example['url']}")
            print("  Content preview:")
            content = example['content']
            print("  " + "\n  ".join(content.split("\n")[:10]))
            print()
        
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
        print(f"Error: {str(e)}")
