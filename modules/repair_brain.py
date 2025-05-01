# modules/repair_brain.py
"""
Repair Brain Module
-----------------
Uses AI to generate repair suggestions for system issues.
"""

import logging
import json
import os
import time
import requests
import threading
from queue import Queue, Empty

logger = logging.getLogger("EvoVe.RepairBrain")

class RepairBrain:
    """Uses AI to generate repair suggestions."""
    
    def __init__(self, evove):
        """Initialize the repair brain."""
        self.evove = evove
        self.config = evove.config.get("repair_brain", {})
        self.api_key = self.config.get("api_key", os.environ.get("OPENAI_API_KEY"))
        self.amazon_q_endpoint = self.config.get("amazon_q_endpoint")
        self.suggestion_cache = {}
        self.cache_ttl = self.config.get("cache_ttl", 3600)  # 1 hour
        self.max_cache_size = self.config.get("max_cache_size", 100)
        self.suggestion_queue = Queue()
        self.processing_thread = None
        self.running = False
        
    def start(self):
        """Start the repair brain."""
        if self.running:
            logger.warning("Repair brain is already running")
            return
            
        self.running = True
        logger.info("Starting repair brain")
        
        self.processing_thread = threading.Thread(target=self._process_queue)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
    def stop(self):
        """Stop the repair brain."""
        if not self.running:
            logger.warning("Repair brain is not running")
            return
            
        self.running = False
        logger.info("Stopping repair brain")
        
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
    
    def _process_queue(self):
        """Process the suggestion queue."""
        while self.running:
            try:
                # Get an item from the queue with a timeout
                try:
                    item = self.suggestion_queue.get(timeout=1)
                except Empty:
                    continue
                    
                # Process the item
                log_chunk = item.get("log_chunk")
                callback = item.get("callback")
                
                if log_chunk:
                    suggestion = self._get_suggestion(log_chunk)
                    
                    if callback:
                        callback(suggestion)
                        
                self.suggestion_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing repair suggestion: {e}")
                time.sleep(1)
    
    def ask_for_repair(self, log_chunk, callback=None):
        """Ask for a repair suggestion based on log data."""
        # Check cache first
        cache_key = self._get_cache_key(log_chunk)
        if cache_key in self.suggestion_cache:
            cached = self.suggestion_cache[cache_key]
            if time.time() - cached["timestamp"] < self.cache_ttl:
                logger.debug("Using cached repair suggestion")
                if callback:
                    callback(cached["suggestion"])
                return cached["suggestion"]
        
        # Queue the request
        self.suggestion_queue.put({
            "log_chunk": log_chunk,
            "callback": callback
        })
        
        return "Processing repair suggestion..."
    
    def _get_suggestion(self, log_chunk):
        """Get a repair suggestion for the given log chunk."""
        # Try Amazon Q first if configured
        if self.amazon_q_endpoint:
            suggestion = self._query_amazon_q(log_chunk)
            if suggestion:
                return suggestion
        
        # Fall back to OpenAI if configured
        if self.api_key:
            suggestion = self._query_openai(log_chunk)
            if suggestion:
                return suggestion
        
        # Fall back to rule-based suggestions
        return self._rule_based_suggestion(log_chunk)
    
    def _query_amazon_q(self, log_chunk):
        """Query Amazon Q for a repair suggestion."""
        if not self.amazon_q_endpoint:
            return None
            
        try:
            prompt = self._create_prompt(log_chunk)
            
            response = requests.post(
                self.amazon_q_endpoint,
                json={"prompt": prompt},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                suggestion = result.get("suggestion", result.get("response", "No suggestion provided"))
                
                # Cache the suggestion
                self._cache_suggestion(log_chunk, suggestion)
                
                return suggestion
            else:
                logger.warning(f"Amazon Q API returned status {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error querying Amazon Q: {e}")
            return None
    
    def _query_openai(self, log_chunk):
        """Query OpenAI for a repair suggestion."""
        if not self.api_key:
            return None
            
        try:
            prompt = self._create_prompt(log_chunk)
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are an expert system administrator and developer. Your task is to analyze system logs and provide specific, actionable repair suggestions."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                suggestion = result["choices"][0]["message"]["content"].strip()
                
                # Cache the suggestion
                self._cache_suggestion(log_chunk, suggestion)
                
                return suggestion
            else:
                logger.warning(f"OpenAI API returned status {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error querying OpenAI: {e}")
            return None
    
    def _create_prompt(self, log_chunk):
        """Create a prompt for the AI model."""
        return f"""
The following system logs show an error or issue that needs to be fixed:


{log_chunk}

Based on these logs, please provide:
1. A brief analysis of what went wrong
2. Specific, actionable steps to fix the issue
3. Any preventive measures to avoid this issue in the future

Format your response as a concise, step-by-step guide that a system administrator could follow.
"""
    
    def _rule_based_suggestion(self, log_chunk):
        """Generate a rule-based suggestion when AI is not available."""
        log_lower = log_chunk.lower()
        
        if "connection refused" in log_lower or "could not connect" in log_lower:
            return "Connection issue detected. Check if the target service is running and accessible. Verify network connectivity and firewall settings."
            
        elif "permission denied" in log_lower:
            return "Permission issue detected. Check file and directory permissions. Ensure the process has the necessary access rights."
            
        elif "out of memory" in log_lower or "memory error" in log_lower:
            return "Memory issue detected. Consider increasing available memory, optimizing memory usage, or restarting the service."
            
        elif "disk full" in log_lower or "no space left" in log_lower:
            return "Disk space issue detected. Free up disk space by removing unnecessary files or logs. Consider adding more storage."
            
        elif "timeout" in log_lower:
            return "Timeout detected. Check network latency and service response times. Consider increasing timeout values or optimizing the service."
            
        elif "mcp" in log_lower and ("error" in log_lower or "failed" in log_lower):
            return "MCP issue detected. Try restarting the MCP server using scripts/check_mcp_health.sh."
            
        else:
            return "Issue detected in logs. Review the full logs for more context. Consider restarting the affected service or checking recent system changes."
    
    def _get_cache_key(self, log_chunk):
        """Generate a cache key for a log chunk."""
        # Use a simple hash of the log chunk as the cache key
        return str(hash(log_chunk))
    
    def _cache_suggestion(self, log_chunk, suggestion):
        """Cache a suggestion for future use."""
        cache_key = self._get_cache_key(log_chunk)
        
        self.suggestion_cache[cache_key] = {
            "suggestion": suggestion,
            "timestamp": time.time()
        }
        
        # Trim cache if needed
        if len(self.suggestion_cache) > self.max_cache_size:
            # Remove oldest entries
            oldest_key = min(self.suggestion_cache.keys(), key=lambda k: self.suggestion_cache[k]["timestamp"])
            self.suggestion_cache.pop(oldest_key)


