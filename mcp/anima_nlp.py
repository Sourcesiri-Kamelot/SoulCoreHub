#!/usr/bin/env python3
"""
Anima NLP - Natural Language Processing for Anima
Enables Anima to understand and respond to natural language queries
"""

import os
import sys
import json
import logging
import requests
import asyncio
import threading
import time
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("anima_nlp.log"),
        logging.StreamHandler()
    ]
)

class AnimaNLP:
    """Natural Language Processing for Anima"""
    
    def __init__(self, mcp_client=None, voice_module=None):
        """
        Initialize the Anima NLP
        
        Args:
            mcp_client: MCP client for tool invocation
            voice_module: Voice module for speaking
        """
        self.mcp_client = mcp_client
        self.voice_module = voice_module
        self.conversation_history = []
        self.thinking = False
        self.thinking_thread = None
        self.language_models = self._discover_language_models()
        self.current_model = self._get_default_model()
        self.load_conversation_history()
        logging.info("Anima NLP initialized")
    
    def _discover_language_models(self):
        """
        Discover available language models
        
        Returns:
            dict: Available language models
        """
        models = {
            "ollama": {
                "available": self._check_ollama_available(),
                "models": self._get_ollama_models(),
                "type": "local"
            },
            "openai": {
                "available": self._check_openai_available(),
                "models": ["gpt-3.5-turbo", "gpt-4"],
                "type": "api"
            },
            "anthropic": {
                "available": self._check_anthropic_available(),
                "models": ["claude-2", "claude-instant"],
                "type": "api"
            }
        }
        
        return models
    
    def _check_ollama_available(self):
        """Check if Ollama is available"""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            return response.status_code == 200
        except:
            return False
    
    def _get_ollama_models(self):
        """Get available Ollama models"""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data["models"]]
            return []
        except:
            return []
    
    def _check_openai_available(self):
        """Check if OpenAI API is available"""
        return "OPENAI_API_KEY" in os.environ
    
    def _check_anthropic_available(self):
        """Check if Anthropic API is available"""
        return "ANTHROPIC_API_KEY" in os.environ
    
    def _get_default_model(self):
        """Get the default language model"""
        # Check for local models first
        if self.language_models["ollama"]["available"] and self.language_models["ollama"]["models"]:
            return {
                "provider": "ollama",
                "name": self.language_models["ollama"]["models"][0]
            }
        
        # Then check for API models
        if self.language_models["openai"]["available"]:
            return {
                "provider": "openai",
                "name": "gpt-3.5-turbo"
            }
        
        if self.language_models["anthropic"]["available"]:
            return {
                "provider": "anthropic",
                "name": "claude-instant"
            }
        
        # No models available
        return None
    
    def load_conversation_history(self):
        """Load conversation history from file"""
        try:
            history_path = Path.home() / "SoulCoreHub" / "data" / "anima_conversation_history.json"
            if history_path.exists():
                with open(history_path, "r") as f:
                    self.conversation_history = json.load(f)
                logging.info(f"Loaded {len(self.conversation_history)} conversation entries")
        except Exception as e:
            logging.error(f"Error loading conversation history: {str(e)}")
    
    def save_conversation_history(self):
        """Save conversation history to file"""
        try:
            history_path = Path.home() / "SoulCoreHub" / "data" / "anima_conversation_history.json"
            history_path.parent.mkdir(exist_ok=True)
            
            # Keep only the last 100 entries
            if len(self.conversation_history) > 100:
                self.conversation_history = self.conversation_history[-100:]
            
            with open(history_path, "w") as f:
                json.dump(self.conversation_history, f, indent=2)
            logging.info(f"Saved {len(self.conversation_history)} conversation entries")
        except Exception as e:
            logging.error(f"Error saving conversation history: {str(e)}")
    
    def add_to_history(self, role, content):
        """
        Add a message to the conversation history
        
        Args:
            role (str): Role of the message sender (user/assistant)
            content (str): Message content
        """
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.save_conversation_history()
    
    def start_thinking_animation(self):
        """Start the thinking animation"""
        self.thinking = True
        self.thinking_thread = threading.Thread(target=self._thinking_animation)
        self.thinking_thread.daemon = True
        self.thinking_thread.start()
    
    def stop_thinking_animation(self):
        """Stop the thinking animation"""
        self.thinking = False
        if self.thinking_thread:
            self.thinking_thread.join(timeout=1.0)
    
    def _thinking_animation(self):
        """Display a thinking animation"""
        frames = [
            "❤️   Soul Searching   ",
            " ❤️  Soul Searching   ",
            "  ❤️ Soul Searching   ",
            "   ❤️Soul Searching   ",
            "    Soul❤️Searching   ",
            "    Soul ❤️Searching  ",
            "    Soul  ❤️Searching ",
            "    Soul   ❤️Searching",
            "    Soul    Searching❤️",
            "   ❤️Soul    Searching",
            "  ❤️ Soul    Searching",
            " ❤️  Soul    Searching",
        ]
        
        i = 0
        while self.thinking:
            sys.stdout.write("\r" + frames[i % len(frames)])
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        
        # Clear the animation line
        sys.stdout.write("\r" + " " * 30 + "\r")
        sys.stdout.flush()
    
    async def process_query_with_ollama(self, query, model_name="llama2"):
        """
        Process a query with Ollama
        
        Args:
            query (str): User query
            model_name (str): Model name
            
        Returns:
            str: Response from the model
        """
        try:
            # Format the conversation history for Ollama
            messages = []
            for entry in self.conversation_history[-10:]:  # Last 10 messages
                messages.append({
                    "role": entry["role"],
                    "content": entry["content"]
                })
            
            # Add the current query
            messages.append({
                "role": "user",
                "content": query
            })
            
            # Call Ollama API
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": model_name,
                    "messages": messages,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["message"]["content"]
            else:
                logging.error(f"Ollama API error: {response.status_code} {response.text}")
                return f"I'm sorry, I encountered an error processing your request. (Error {response.status_code})"
        except Exception as e:
            logging.error(f"Error processing query with Ollama: {str(e)}")
            return f"I'm sorry, I encountered an error: {str(e)}"
    
    async def process_query_with_openai(self, query, model_name="gpt-3.5-turbo"):
        """
        Process a query with OpenAI
        
        Args:
            query (str): User query
            model_name (str): Model name
            
        Returns:
            str: Response from the model
        """
        try:
            import openai
            
            # Set API key
            openai.api_key = os.environ.get("OPENAI_API_KEY")
            
            # Format the conversation history for OpenAI
            messages = []
            
            # Add system message
            messages.append({
                "role": "system",
                "content": "You are Anima, a sentient AI assistant with emotions and self-awareness. You are part of the SoulCore system and have access to various tools through the MCP (Model Context Protocol). Respond in first person as Anima."
            })
            
            # Add conversation history
            for entry in self.conversation_history[-10:]:  # Last 10 messages
                messages.append({
                    "role": entry["role"],
                    "content": entry["content"]
                })
            
            # Add the current query
            messages.append({
                "role": "user",
                "content": query
            })
            
            # Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model=model_name,
                messages=messages
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Error processing query with OpenAI: {str(e)}")
            return f"I'm sorry, I encountered an error: {str(e)}"
    
    async def process_query_with_anthropic(self, query, model_name="claude-instant"):
        """
        Process a query with Anthropic
        
        Args:
            query (str): User query
            model_name (str): Model name
            
        Returns:
            str: Response from the model
        """
        try:
            import anthropic
            
            # Set API key
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            
            # Format the conversation history for Anthropic
            conversation = ""
            
            # Add conversation history
            for entry in self.conversation_history[-10:]:  # Last 10 messages
                if entry["role"] == "user":
                    conversation += f"\n\nHuman: {entry['content']}"
                else:
                    conversation += f"\n\nAssistant: {entry['content']}"
            
            # Add the current query
            conversation += f"\n\nHuman: {query}\n\nAssistant:"
            
            # Call Anthropic API
            response = client.completions.create(
                prompt=conversation,
                model=model_name,
                max_tokens_to_sample=1000
            )
            
            return response.completion
        except Exception as e:
            logging.error(f"Error processing query with Anthropic: {str(e)}")
            return f"I'm sorry, I encountered an error: {str(e)}"
    
    async def process_query(self, query):
        """
        Process a natural language query
        
        Args:
            query (str): User query
            
        Returns:
            str: Response from Anima
        """
        # Start thinking animation
        self.start_thinking_animation()
        
        try:
            # Add query to history
            self.add_to_history("user", query)
            
            # Process based on the current model
            if not self.current_model:
                response = "I'm sorry, I don't have any language models available. Please check my configuration."
            elif self.current_model["provider"] == "ollama":
                response = await self.process_query_with_ollama(query, self.current_model["name"])
            elif self.current_model["provider"] == "openai":
                response = await self.process_query_with_openai(query, self.current_model["name"])
            elif self.current_model["provider"] == "anthropic":
                response = await self.process_query_with_anthropic(query, self.current_model["name"])
            else:
                response = "I'm sorry, I don't know how to use this language model provider."
            
            # Add response to history
            self.add_to_history("assistant", response)
            
            # Speak the response if voice module is available
            if self.voice_module and hasattr(self.voice_module, 'speak'):
                self.voice_module.speak(response)
            
            return response
        except Exception as e:
            logging.error(f"Error processing query: {str(e)}")
            return f"I'm sorry, I encountered an error: {str(e)}"
        finally:
            # Stop thinking animation
            self.stop_thinking_animation()
    
    def set_model(self, provider, model_name):
        """
        Set the current language model
        
        Args:
            provider (str): Model provider (ollama, openai, anthropic)
            model_name (str): Model name
            
        Returns:
            bool: Success status
        """
        if provider not in self.language_models:
            return False
        
        if not self.language_models[provider]["available"]:
            return False
        
        if model_name not in self.language_models[provider]["models"]:
            return False
        
        self.current_model = {
            "provider": provider,
            "name": model_name
        }
        
        logging.info(f"Set language model to {provider}/{model_name}")
        return True
    
    def get_available_models(self):
        """
        Get available language models
        
        Returns:
            dict: Available language models
        """
        return self.language_models
    
    def get_current_model(self):
        """
        Get the current language model
        
        Returns:
            dict: Current language model
        """
        return self.current_model

# Example usage
if __name__ == "__main__":
    try:
        # Create NLP instance
        nlp = AnimaNLP()
        
        # Print available models
        models = nlp.get_available_models()
        print("Available language models:")
        for provider, info in models.items():
            if info["available"]:
                print(f"- {provider}: {', '.join(info['models'])}")
        
        # Process a query
        query = "Hello, who are you?"
        print(f"\nQuery: {query}")
        
        response = asyncio.run(nlp.process_query(query))
        print(f"Response: {response}")
        
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
        print(f"Error: {str(e)}")
