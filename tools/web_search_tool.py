import json
import logging
import requests
from typing import Dict, Any, Optional

from mcp.core.tool import MCPTool

class WebSearchTool(MCPTool):
    """
    Web search tool that uses DuckDuckGo Instant Answer API to perform searches.
    
    This tool can be registered with an MCP server to provide web search capabilities
    to LLMs and other agents in the SoulCoreHub ecosystem.
    """
    
    def __init__(self):
        """Initialize the WebSearchTool with its metadata."""
        super().__init__(
            name="web_search",
            description="Search the web for information using DuckDuckGo",
            parameters={
                "query": {
                    "type": "string",
                    "description": "The search query to look up"
                }
            },
            required_parameters=["query"]
        )
        self.logger = logging.getLogger("WebSearchTool")
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a web search using the DuckDuckGo Instant Answer API.
        
        Args:
            parameters: Dictionary containing the 'query' parameter
            
        Returns:
            Dictionary containing search results with Abstract, RelatedTopics, and URL
        """
        query = parameters.get("query", "")
        if not query:
            return {"error": "No search query provided"}
        
        self.logger.info(f"Performing web search for: {query}")
        
        try:
            # Construct the DuckDuckGo API URL
            url = f"https://api.duckduckgo.com/?q={query}&format=json"
            response = requests.get(url, headers={"User-Agent": "SoulCoreHub/1.0"})
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Extract the relevant information
            result = {
                "Abstract": data.get("Abstract", ""),
                "AbstractURL": data.get("AbstractURL", ""),
                "RelatedTopics": self._process_related_topics(data.get("RelatedTopics", [])),
                "URL": data.get("AbstractURL") or data.get("Redirect", ""),
                "Heading": data.get("Heading", "")
            }
            
            # Check if we have useful data
            if not result["Abstract"] and not result["RelatedTopics"]:
                self.logger.warning(f"No useful data found for query: {query}")
                return {
                    "result": "No detailed information found for this query.",
                    "query": query
                }
            
            self.logger.info(f"Search complete. Found {len(result['RelatedTopics'])} related topics")
            return result
            
        except requests.RequestException as e:
            self.logger.error(f"Error during web search: {str(e)}")
            return {"error": f"Search request failed: {str(e)}"}
        except json.JSONDecodeError:
            self.logger.error("Failed to parse API response")
            return {"error": "Failed to parse search results"}
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return {"error": f"Search failed: {str(e)}"}
    
    def _process_related_topics(self, topics: list) -> list:
        """
        Process and simplify the related topics from DuckDuckGo response.
        
        Args:
            topics: List of related topics from the API response
            
        Returns:
            Simplified list of topics with Text and URL
        """
        simplified_topics = []
        
        for topic in topics[:5]:  # Limit to first 5 topics for brevity
            if isinstance(topic, dict):
                if "Topics" in topic:
                    # This is a category with subtopics
                    for subtopic in topic.get("Topics", [])[:3]:  # Limit subtopics
                        if isinstance(subtopic, dict):
                            simplified_topics.append({
                                "Text": subtopic.get("Text", ""),
                                "URL": subtopic.get("FirstURL", "")
                            })
                else:
                    # This is a regular topic
                    simplified_topics.append({
                        "Text": topic.get("Text", ""),
                        "URL": topic.get("FirstURL", "")
                    })
        
        return simplified_topics
