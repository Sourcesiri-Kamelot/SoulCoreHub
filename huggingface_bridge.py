#!/usr/bin/env python3
"""
SoulCoreHub - Hugging Face Python Bridge

This module provides a Python interface to the Hugging Face API and integrates
with SoulCoreHub's agent system. It allows Python-based agents to leverage
Hugging Face models for various AI tasks.

Author: SoulCoreHub
Version: 1.0.0
"""

import os
import json
import time
import logging
import requests
from typing import Dict, List, Any, Optional, Union
import subprocess
import threading
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/huggingface_bridge.log'
)
logger = logging.getLogger('huggingface_bridge')

# Ensure the logs directory exists
Path('logs').mkdir(exist_ok=True)

class HuggingFaceBridge:
    """Bridge between SoulCoreHub Python agents and Hugging Face API"""
    
    def __init__(self, config_path: str = 'config/huggingface_config.json'):
        """Initialize the Hugging Face bridge with configuration"""
        self.config = self._load_config(config_path)
        self.api_token = self.config.get('apiToken')
        self.js_bridge_process = None
        self.cache = {}
        self.stats = {
            'calls': 0,
            'errors': 0,
            'cache_hits': 0,
            'model_usage': {}
        }
        
        # Set up headers for API requests
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        logger.info("HuggingFace Bridge initialized")
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            # Return default config
            return {
                "defaultTextModel": "mistralai/Mistral-7B-Instruct-v0.2",
                "apiToken": os.environ.get("HF_TOKEN", ""),
                "logLevel": "info",
                "maxHistoryItems": 50
            }
    
    def generate_text(self, prompt: str, model: Optional[str] = None, 
                     params: Optional[Dict] = None) -> str:
        """
        Generate text using a Hugging Face model
        
        Args:
            prompt: Input text prompt
            model: Model name (optional, uses default from config if not provided)
            params: Additional parameters for the model
            
        Returns:
            Generated text response
        """
        model = model or self.config.get('defaultTextModel')
        
        # Check cache first
        cache_key = f"text_{model}_{prompt}"
        if self.config.get('caching', {}).get('enabled', True) and cache_key in self.cache:
            self.stats['cache_hits'] += 1
            return self.cache[cache_key]
        
        # Prepare parameters
        default_params = self.config.get('modelParameters', {}).get('textGeneration', {})
        if params:
            # Merge with defaults, with provided params taking precedence
            request_params = {**default_params, **params}
        else:
            request_params = default_params
            
        # Prepare the API request
        payload = {
            "inputs": prompt,
            "parameters": request_params
        }
        
        try:
            # Make API request
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers=self.headers,
                json=payload
            )
            
            # Update stats
            self.stats['calls'] += 1
            self._update_model_usage(model)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract the generated text
                if isinstance(result, list) and len(result) > 0:
                    if 'generated_text' in result[0]:
                        generated_text = result[0]['generated_text']
                    else:
                        generated_text = result[0].get('text', '')
                elif isinstance(result, dict):
                    generated_text = result.get('generated_text', '')
                else:
                    generated_text = str(result)
                
                # Cache the result
                if self.config.get('caching', {}).get('enabled', True):
                    self.cache[cache_key] = generated_text
                
                return generated_text
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                self.stats['errors'] += 1
                return f"Error: {error_msg}"
                
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            self.stats['errors'] += 1
            return f"Error: {str(e)}"
    
    def generate_image(self, prompt: str, model: Optional[str] = None,
                      params: Optional[Dict] = None) -> str:
        """
        Generate an image from text prompt
        
        Args:
            prompt: Text description of the image
            model: Model name (optional)
            params: Additional parameters
            
        Returns:
            Path to the generated image file
        """
        model = model or self.config.get('defaultImageModel')
        
        # Prepare parameters
        default_params = self.config.get('modelParameters', {}).get('imageGeneration', {})
        if params:
            request_params = {**default_params, **params}
        else:
            request_params = default_params
            
        # Create a unique filename
        timestamp = int(time.time())
        output_dir = Path('generated_images')
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"image_{timestamp}.png"
        
        try:
            # Make API request
            payload = {
                "inputs": prompt,
                "parameters": request_params
            }
            
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers=self.headers,
                json=payload
            )
            
            # Update stats
            self.stats['calls'] += 1
            self._update_model_usage(model)
            
            if response.status_code == 200:
                # Save the image
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Image generated and saved to {output_path}")
                return str(output_path)
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                self.stats['errors'] += 1
                return f"Error: {error_msg}"
                
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            self.stats['errors'] += 1
            return f"Error: {str(e)}"
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        model = self.config.get('sentimentModel')
        
        try:
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers=self.headers,
                json={"inputs": text}
            )
            
            # Update stats
            self.stats['calls'] += 1
            self._update_model_usage(model)
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                self.stats['errors'] += 1
                return {"error": error_msg}
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            self.stats['errors'] += 1
            return {"error": str(e)}
    
    def summarize_text(self, text: str, max_length: int = 100) -> str:
        """
        Summarize a longer text
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summarized text
        """
        model = self.config.get('summarizationModel')
        
        try:
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers=self.headers,
                json={"inputs": text, "parameters": {"max_length": max_length}}
            )
            
            # Update stats
            self.stats['calls'] += 1
            self._update_model_usage(model)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('summary_text', '')
                return result.get('summary_text', '')
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                self.stats['errors'] += 1
                return f"Error: {error_msg}"
                
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            self.stats['errors'] += 1
            return f"Error: {str(e)}"
    
    def get_embeddings(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """
        Get vector embeddings for text(s)
        
        Args:
            texts: Single text or list of texts
            
        Returns:
            List of embedding vectors
        """
        model = self.config.get('embeddingModel')
        
        # Ensure texts is a list
        if isinstance(texts, str):
            texts = [texts]
            
        try:
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers=self.headers,
                json={"inputs": texts}
            )
            
            # Update stats
            self.stats['calls'] += 1
            self._update_model_usage(model)
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                self.stats['errors'] += 1
                return []
                
        except Exception as e:
            logger.error(f"Error getting embeddings: {e}")
            self.stats['errors'] += 1
            return []
    
    def start_js_bridge(self) -> None:
        """Start the JavaScript bridge process for Node.js integration"""
        try:
            # Start the Node.js bridge in a subprocess
            cmd = ["node", "huggingface_bridge_server.js"]
            self.js_bridge_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Start a thread to monitor the process output
            threading.Thread(
                target=self._monitor_js_process,
                daemon=True
            ).start()
            
            logger.info("Started JavaScript bridge process")
        except Exception as e:
            logger.error(f"Failed to start JavaScript bridge: {e}")
    
    def stop_js_bridge(self) -> None:
        """Stop the JavaScript bridge process"""
        if self.js_bridge_process:
            try:
                self.js_bridge_process.terminate()
                self.js_bridge_process = None
                logger.info("Stopped JavaScript bridge process")
            except Exception as e:
                logger.error(f"Error stopping JavaScript bridge: {e}")
    
    def _monitor_js_process(self) -> None:
        """Monitor the JavaScript bridge process output"""
        while self.js_bridge_process:
            try:
                # Read output line by line
                for line in iter(self.js_bridge_process.stdout.readline, b''):
                    if line:
                        logger.info(f"JS Bridge: {line.decode().strip()}")
                
                # Check if process is still running
                if self.js_bridge_process.poll() is not None:
                    logger.warning("JS Bridge process exited")
                    break
                    
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error monitoring JS process: {e}")
                break
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        return self.stats
    
    def _update_model_usage(self, model: str) -> None:
        """Update model usage statistics"""
        if model in self.stats['model_usage']:
            self.stats['model_usage'][model] += 1
        else:
            self.stats['model_usage'][model] = 1
    
    def clear_cache(self) -> None:
        """Clear the response cache"""
        self.cache = {}
        logger.info("Cache cleared")


# Create a singleton instance
huggingface_bridge = HuggingFaceBridge()

if __name__ == "__main__":
    # Simple test if run directly
    bridge = huggingface_bridge
    
    print("Testing HuggingFace Bridge...")
    
    # Test text generation
    prompt = "SoulCoreHub is a powerful AI system that"
    print(f"Generating text for prompt: '{prompt}'")
    response = bridge.generate_text(prompt)
    print(f"Response: {response}")
    
    # Test sentiment analysis
    text = "I love how SoulCoreHub integrates with various AI systems seamlessly!"
    print(f"Analyzing sentiment for: '{text}'")
    sentiment = bridge.analyze_sentiment(text)
    print(f"Sentiment: {sentiment}")
    
    print("Stats:", bridge.get_stats())
