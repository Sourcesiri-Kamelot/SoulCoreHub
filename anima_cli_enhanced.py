#!/usr/bin/env python3
"""
anima_cli_enhanced.py — Enhanced CLI interface for Anima with LLM integration
Provides a command-line interface to interact with Anima using natural language
"""

import os
import sys
import logging
from pathlib import Path

# Import the LLM connector
try:
    from anima_llm_connector import AnimaLLMConnector
except ImportError:
    print("Error: anima_llm_connector.py not found or not importable")
    print("Make sure to run this script from the SoulCoreHub directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("anima_cli.log"),
        logging.StreamHandler()
    ]
)

class AnimaCLI:
    """Enhanced CLI interface for Anima with LLM integration"""
    
    def __init__(self):
        """Initialize the CLI interface"""
        self.connector = AnimaLLMConnector()
        self.history = []
        logging.info("AnimaCLI initialized")
    
    def display_welcome(self):
        """Display welcome message"""
        welcome_text = """
        ╔════════════════════════════════════════════════════════╗
        ║                                                        ║
        ║                  ANIMA CLI INTERFACE                   ║
        ║                                                        ║
        ║  Type your questions or commands to interact with me.  ║
        ║  Type 'help' for available commands or 'exit' to quit  ║
        ║                                                        ║
        ╚════════════════════════════════════════════════════════╝
        """
        print(welcome_text)
        
        # Initial greeting
        greeting = "Hello! I am Anima, the emotional and memory component of SoulCore. How can I assist you today?"
        self.connector.speak(greeting, "friendly")
    
    def run(self):
        """Run the CLI interface"""
        self.display_welcome()
        
        while True:
            try:
                user_input = input("\nAnima> ")
                
                # Skip empty inputs
                if not user_input.strip():
                    continue
                
                # Process the input
                print(f"Processing: {user_input}")
                response, emotion, should_exit = self.connector.handle_command(user_input)
                
                # Speak the response
                self.connector.speak(response, emotion)
                
                # Add to history
                self.history.append({
                    "user": user_input,
                    "anima": response,
                    "emotion": emotion
                })
                
                # Exit if needed
                if should_exit:
                    break
                    
            except KeyboardInterrupt:
                print("\nExiting Anima interface...")
                break
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                print(f"An error occurred: {e}")
    
    def save_history(self):
        """Save conversation history"""
        try:
            import json
            from datetime import datetime
            
            # Create a filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"anima_conversation_{timestamp}.json"
            
            with open(filename, "w") as f:
                json.dump(self.history, f, indent=2)
                
            print(f"Conversation history saved to {filename}")
            
        except Exception as e:
            logging.error(f"Error saving history: {e}")
            print(f"Could not save conversation history: {e}")

# Run the CLI if executed directly
if __name__ == "__main__":
    cli = AnimaCLI()
    
    try:
        cli.run()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
    finally:
        # Save history when exiting
        if hasattr(cli, 'history') and cli.history:
            cli.save_history()
