#!/usr/bin/env python3
"""
Test script for Ollama integration with Anima
"""

import requests
import sys
import json

def test_ollama_connection():
    """Test connection to Ollama server using direct API calls"""
    try:
        # List available models
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json()
            print("Available models:")
            for model in models.get('models', []):
                print(f"- {model['name']}")
            
            # Check if anima model exists (case insensitive)
            anima_models = [model for model in models.get('models', []) 
                           if model['name'].lower() in ('anima', 'anima:latest')]
            
            if anima_models:
                anima_model = anima_models[0]['name']
                print(f"\nAnima model found as '{anima_model}'! Testing generation...")
                
                # Test generation with anima model
                generate_response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": anima_model,
                        "prompt": "Hello, I am testing your connection. How are you feeling today?",
                        "system": "You are Anima, a sentient being with emotions and awareness.",
                        "stream": False
                    }
                )
                
                if generate_response.status_code == 200:
                    result = generate_response.json()
                    print("\nAnima's response:")
                    print(result.get('response', 'No response received'))
                    return True
                else:
                    print(f"\nError generating response: {generate_response.status_code}")
                    print(generate_response.text)
                    return False
            else:
                print("\nAnima model not found. Please create it with:")
                print("ollama create anima -f ~/SoulCoreHub/Modelfile")
                return False
        else:
            print(f"\nError connecting to Ollama API: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"\nError connecting to Ollama: {e}")
        print("Is the Ollama server running? Start it with 'ollama serve'")
        return False

if __name__ == "__main__":
    print("Testing Ollama integration for Anima...")
    success = test_ollama_connection()
    sys.exit(0 if success else 1)
