#!/usr/bin/env python3
"""
Internet Access - Enables Anima to access the internet and APIs
Provides web search, API access, and information retrieval capabilities
"""

import os
import json
import logging
import requests
import urllib.parse
import re
import time
from pathlib import Path
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("internet_access.log"),
        logging.StreamHandler()
    ]
)

class InternetAccess:
    """Internet access for retrieving information from the web"""
    
    def __init__(self):
        """Initialize the internet access module"""
        self.cache_dir = Path.home() / "SoulCoreHub" / "data" / "internet_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_expiry = 24  # Cache expiry in hours
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        self.api_keys = self._load_api_keys()
        logging.info("Internet access module initialized")
    
    def _load_api_keys(self):
        """Load API keys from environment variables or config file"""
        api_keys = {}
        
        # Try to load from environment variables
        api_keys["SERP_API_KEY"] = os.environ.get("SERP_API_KEY")
        api_keys["NEWSAPI_KEY"] = os.environ.get("NEWSAPI_KEY")
        api_keys["WEATHER_API_KEY"] = os.environ.get("WEATHER_API_KEY")
        
        # Try to load from config file
        config_path = Path.home() / "SoulCoreHub" / "config" / "api_keys.json"
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    file_keys = json.load(f)
                    # Update with file keys, but don't overwrite existing env vars
                    for key, value in file_keys.items():
                        if key not in api_keys or api_keys[key] is None:
                            api_keys[key] = value
            except Exception as e:
                logging.error(f"Error loading API keys from config: {str(e)}")
        
        return api_keys
    
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
    
    def search_web(self, query, num_results=5):
        """
        Search the web for information
        
        Args:
            query (str): Search query
            num_results (int): Number of results to return
            
        Returns:
            list: Search results
        """
        # Check cache first
        cache_key = f"web_search_{query}_{num_results}"
        cached = self._get_from_cache(cache_key)
        if cached:
            logging.info(f"Retrieved web search results from cache for '{query}'")
            return cached
        
        # Try using SerpAPI if available
        if self.api_keys.get("SERP_API_KEY"):
            results = self._search_with_serpapi(query, num_results)
            if results:
                self._save_to_cache(cache_key, results)
                return results
        
        # Fallback to direct web scraping (be careful with this)
        results = self._search_with_scraping(query, num_results)
        if results:
            self._save_to_cache(cache_key, results)
        
        return results
    
    def _search_with_serpapi(self, query, num_results=5):
        """Search using SerpAPI"""
        try:
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": self.api_keys["SERP_API_KEY"],
                "num": num_results
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for result in data.get("organic_results", [])[:num_results]:
                results.append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", "")
                })
            
            logging.info(f"Found {len(results)} results for '{query}' using SerpAPI")
            return results
        except Exception as e:
            logging.error(f"Error searching with SerpAPI: {str(e)}")
            return None
    
    def _search_with_scraping(self, query, num_results=5):
        """Search by scraping search results (use cautiously)"""
        try:
            # This is a simplified example and might not work reliably
            # Real-world implementations should use proper APIs
            
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.google.com/search?q={encoded_query}&num={num_results}"
            
            headers = {
                "User-Agent": self.user_agent
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            results = []
            for g in soup.find_all("div", class_="g")[:num_results]:
                anchor = g.find("a")
                title = g.find("h3")
                snippet = g.find("div", class_="IsZvec")
                
                if anchor and title:
                    link = anchor["href"]
                    if link.startswith("/url?q="):
                        link = link.split("/url?q=")[1].split("&")[0]
                    
                    results.append({
                        "title": title.text,
                        "link": link,
                        "snippet": snippet.text if snippet else ""
                    })
            
            logging.info(f"Found {len(results)} results for '{query}' using web scraping")
            return results
        except Exception as e:
            logging.error(f"Error searching with web scraping: {str(e)}")
            return []
    
    def get_webpage_content(self, url):
        """
        Get the content of a webpage
        
        Args:
            url (str): URL of the webpage
            
        Returns:
            dict: Webpage content
        """
        # Check cache first
        cache_key = f"webpage_{url}"
        cached = self._get_from_cache(cache_key)
        if cached:
            logging.info(f"Retrieved webpage content from cache for '{url}'")
            return cached
        
        try:
            headers = {
                "User-Agent": self.user_agent
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Get text
            text = soup.get_text()
            
            # Break into lines and remove leading and trailing space
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Get title
            title = soup.title.string if soup.title else ""
            
            # Get meta description
            meta_desc = ""
            meta_tag = soup.find("meta", attrs={"name": "description"})
            if meta_tag:
                meta_desc = meta_tag.get("content", "")
            
            result = {
                "url": url,
                "title": title,
                "description": meta_desc,
                "content": text[:10000]  # Limit content length
            }
            
            # Cache the result
            self._save_to_cache(cache_key, result)
            
            logging.info(f"Retrieved content from '{url}'")
            return result
        except Exception as e:
            logging.error(f"Error getting webpage content: {str(e)}")
            return {
                "url": url,
                "error": str(e)
            }
    
    def get_news(self, query=None, category=None, country="us", num_results=5):
        """
        Get news articles
        
        Args:
            query (str): Search query (optional)
            category (str): News category (optional)
            country (str): Country code (default: "us")
            num_results (int): Number of results to return
            
        Returns:
            list: News articles
        """
        # Check cache first
        cache_key = f"news_{query}_{category}_{country}_{num_results}"
        cached = self._get_from_cache(cache_key)
        if cached:
            logging.info(f"Retrieved news from cache for '{query or category}'")
            return cached
        
        # Try using NewsAPI if available
        if self.api_keys.get("NEWSAPI_KEY"):
            try:
                url = "https://newsapi.org/v2/top-headlines"
                params = {
                    "apiKey": self.api_keys["NEWSAPI_KEY"],
                    "country": country,
                    "pageSize": num_results
                }
                
                if query:
                    params["q"] = query
                
                if category:
                    params["category"] = category
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                articles = []
                for article in data.get("articles", [])[:num_results]:
                    articles.append({
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "url": article.get("url", ""),
                        "source": article.get("source", {}).get("name", ""),
                        "published_at": article.get("publishedAt", "")
                    })
                
                # Cache the results
                self._save_to_cache(cache_key, articles)
                
                logging.info(f"Found {len(articles)} news articles for '{query or category}'")
                return articles
            except Exception as e:
                logging.error(f"Error getting news: {str(e)}")
        
        # Fallback to web search for news
        search_query = query or category or "latest news"
        if category and not query:
            search_query = f"{category} news"
        
        search_query += " news"
        return self.search_web(search_query, num_results)
    
    def get_weather(self, location):
        """
        Get weather information for a location
        
        Args:
            location (str): Location name or coordinates
            
        Returns:
            dict: Weather information
        """
        # Check cache first (with shorter expiry for weather)
        cache_key = f"weather_{location}"
        cached = self._get_from_cache(cache_key)
        if cached:
            # Weather cache expires after 1 hour
            cached_time = datetime.fromisoformat(cached["timestamp"])
            if datetime.now() - cached_time <= timedelta(hours=1):
                logging.info(f"Retrieved weather from cache for '{location}'")
                return cached["data"]
        
        # Try using WeatherAPI if available
        if self.api_keys.get("WEATHER_API_KEY"):
            try:
                url = "https://api.weatherapi.com/v1/forecast.json"
                params = {
                    "key": self.api_keys["WEATHER_API_KEY"],
                    "q": location,
                    "days": 3
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                current = data.get("current", {})
                forecast = data.get("forecast", {}).get("forecastday", [])
                location_data = data.get("location", {})
                
                result = {
                    "location": {
                        "name": location_data.get("name", ""),
                        "region": location_data.get("region", ""),
                        "country": location_data.get("country", ""),
                        "lat": location_data.get("lat", 0),
                        "lon": location_data.get("lon", 0)
                    },
                    "current": {
                        "temp_c": current.get("temp_c", 0),
                        "temp_f": current.get("temp_f", 0),
                        "condition": current.get("condition", {}).get("text", ""),
                        "wind_kph": current.get("wind_kph", 0),
                        "humidity": current.get("humidity", 0),
                        "feelslike_c": current.get("feelslike_c", 0),
                        "feelslike_f": current.get("feelslike_f", 0)
                    },
                    "forecast": []
                }
                
                for day in forecast:
                    day_data = {
                        "date": day.get("date", ""),
                        "max_temp_c": day.get("day", {}).get("maxtemp_c", 0),
                        "min_temp_c": day.get("day", {}).get("mintemp_c", 0),
                        "condition": day.get("day", {}).get("condition", {}).get("text", ""),
                        "chance_of_rain": day.get("day", {}).get("daily_chance_of_rain", 0)
                    }
                    result["forecast"].append(day_data)
                
                # Cache the result
                self._save_to_cache(cache_key, result)
                
                logging.info(f"Retrieved weather for '{location}'")
                return result
            except Exception as e:
                logging.error(f"Error getting weather: {str(e)}")
        
        # Fallback to web search for weather
        search_results = self.search_web(f"weather {location}", 1)
        if search_results:
            return {
                "location": {"name": location},
                "info": search_results[0].get("snippet", "Weather information not available")
            }
        
        return {
            "location": {"name": location},
            "error": "Weather information not available"
        }
    
    def detect_api_endpoint(self, query):
        """
        Detect if a query is asking for a specific API endpoint
        
        Args:
            query (str): User query
            
        Returns:
            dict: API endpoint information or None
        """
        # Define patterns for common API requests
        api_patterns = [
            {
                "pattern": r"weather\s+(?:in|for|at)?\s+([a-zA-Z\s,]+)",
                "api": "weather",
                "param_name": "location"
            },
            {
                "pattern": r"news\s+(?:about|on|for)?\s+([a-zA-Z\s]+)",
                "api": "news",
                "param_name": "query"
            },
            {
                "pattern": r"search\s+(?:for)?\s+([a-zA-Z\s]+)",
                "api": "web_search",
                "param_name": "query"
            }
        ]
        
        # Check each pattern
        for pattern_info in api_patterns:
            match = re.search(pattern_info["pattern"], query, re.IGNORECASE)
            if match:
                param_value = match.group(1).strip()
                return {
                    "api": pattern_info["api"],
                    "params": {
                        pattern_info["param_name"]: param_value
                    }
                }
        
        return None
    
    def call_api(self, api_name, params):
        """
        Call a specific API
        
        Args:
            api_name (str): API name
            params (dict): API parameters
            
        Returns:
            dict: API response
        """
        if api_name == "weather":
            return self.get_weather(params.get("location", ""))
        elif api_name == "news":
            return self.get_news(query=params.get("query"), num_results=5)
        elif api_name == "web_search":
            return self.search_web(params.get("query", ""), num_results=5)
        else:
            return {"error": f"Unknown API: {api_name}"}
    
    def is_url(self, text):
        """
        Check if text is a URL
        
        Args:
            text (str): Text to check
            
        Returns:
            bool: True if text is a URL
        """
        try:
            result = urlparse(text)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def summarize_webpage(self, url):
        """
        Get a summary of a webpage
        
        Args:
            url (str): URL of the webpage
            
        Returns:
            dict: Webpage summary
        """
        # Get the webpage content
        content = self.get_webpage_content(url)
        
        if "error" in content:
            return content
        
        # Extract the most important information
        title = content.get("title", "")
        description = content.get("description", "")
        text = content.get("content", "")
        
        # Simple extractive summarization
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Score sentences based on position and keyword frequency
        scores = {}
        for i, sentence in enumerate(sentences):
            # Position score (earlier sentences are more important)
            position_score = 1.0 / (i + 1)
            
            # Length score (not too short, not too long)
            length = len(sentence.split())
            length_score = 0.5 if 5 <= length <= 25 else 0.0
            
            # Title word score
            title_words = set(re.findall(r'\w+', title.lower()))
            title_score = sum(1 for word in re.findall(r'\w+', sentence.lower()) if word in title_words) / max(len(title_words), 1)
            
            # Combine scores
            scores[i] = position_score + length_score + title_score
        
        # Get top sentences
        top_indices = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
        top_indices = sorted([i for i, _ in top_indices])
        
        summary = " ".join(sentences[i] for i in top_indices)
        
        return {
            "url": url,
            "title": title,
            "description": description,
            "summary": summary
        }

# Register internet access tools with MCP server
def register_internet_tools(server):
    """
    Register internet access tools with the MCP server
    
    Args:
        server: MCP server instance
    """
    internet = InternetAccess()
    
    # Search web tool
    async def search_web_tool(params, metadata=None):
        query = params.get("query", "")
        num_results = params.get("num_results", 5)
        return internet.search_web(query, num_results)
    
    # Get webpage content tool
    async def get_webpage_content_tool(params, metadata=None):
        url = params.get("url", "")
        return internet.get_webpage_content(url)
    
    # Get news tool
    async def get_news_tool(params, metadata=None):
        query = params.get("query", None)
        category = params.get("category", None)
        country = params.get("country", "us")
        num_results = params.get("num_results", 5)
        return internet.get_news(query, category, country, num_results)
    
    # Get weather tool
    async def get_weather_tool(params, metadata=None):
        location = params.get("location", "")
        return internet.get_weather(location)
    
    # Detect API endpoint tool
    async def detect_api_endpoint_tool(params, metadata=None):
        query = params.get("query", "")
        return internet.detect_api_endpoint(query)
    
    # Call API tool
    async def call_api_tool(params, metadata=None):
        api_name = params.get("api_name", "")
        api_params = params.get("params", {})
        return internet.call_api(api_name, api_params)
    
    # Summarize webpage tool
    async def summarize_webpage_tool(params, metadata=None):
        url = params.get("url", "")
        return internet.summarize_webpage(url)
    
    # Register the tools
    server.register_tool(
        "internet_search_web",
        search_web_tool,
        "Search the web for information",
        "curious"
    )
    
    server.register_tool(
        "internet_get_webpage_content",
        get_webpage_content_tool,
        "Get the content of a webpage",
        "focused"
    )
    
    server.register_tool(
        "internet_get_news",
        get_news_tool,
        "Get news articles",
        "informed"
    )
    
    server.register_tool(
        "internet_get_weather",
        get_weather_tool,
        "Get weather information for a location",
        "helpful"
    )
    
    server.register_tool(
        "internet_detect_api_endpoint",
        detect_api_endpoint_tool,
        "Detect if a query is asking for a specific API endpoint",
        "analytical"
    )
    
    server.register_tool(
        "internet_call_api",
        call_api_tool,
        "Call a specific API",
        "technical"
    )
    
    server.register_tool(
        "internet_summarize_webpage",
        summarize_webpage_tool,
        "Get a summary of a webpage",
        "efficient"
    )

# Example usage
if __name__ == "__main__":
    try:
        # Create internet access instance
        internet = InternetAccess()
        
        # Test web search
        print("Searching the web for 'climate change'...")
        results = internet.search_web("climate change", 2)
        for result in results:
            print(f"- {result['title']}")
            print(f"  URL: {result['link']}")
            print(f"  {result['snippet']}")
            print()
        
        # Test API detection
        query = "What's the weather in New York?"
        print(f"Detecting API for query: '{query}'")
        api_info = internet.detect_api_endpoint(query)
        if api_info:
            print(f"Detected API: {api_info['api']}")
            print(f"Parameters: {api_info['params']}")
            
            # Call the detected API
            print("Calling the API...")
            result = internet.call_api(api_info['api'], api_info['params'])
            print(f"Result: {result}")
        else:
            print("No API detected")
        
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
        print(f"Error: {str(e)}")
