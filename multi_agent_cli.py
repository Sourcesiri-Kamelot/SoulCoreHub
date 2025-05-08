#!/usr/bin/env python3
"""
Multi-Agent CLI for SoulCoreHub
Enables real multi-agent conversations with Anima + GPTSoul using fusion
"""

import os
import sys
import json
import logging
import time
import threading
import argparse
import readline
import signal
from datetime import datetime
from query_interpreter import get_query_interpreter
from agent_messaging_bridge import get_bridge
from fusion_protocol import get_fusion_protocol
from agent_emotion_state import get_emotion_tracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("multi_agent_cli.log"), logging.StreamHandler()]
)
logger = logging.getLogger("multi_agent_cli")

class MultiAgentCLI:
    """
    CLI for interacting with multiple agents through fusion
    """
    
    def __init__(self):
        """Initialize the Multi-Agent CLI"""
        self.query_interpreter = get_query_interpreter()
        self.messaging_bridge = get_bridge()
        self.fusion_protocol = get_fusion_protocol()
        self.emotion_tracker = get_emotion_tracker()
        
        # Start the messaging bridge
        self.messaging_bridge.start()
        
        # Register for direct messages
        self.messaging_bridge.register_callback("MultiAgentCLI", self._handle_message)
        
        # Command history file
        self.history_file = os.path.expanduser("~/.soulcore_history")
        self._load_history()
        
        # Default agents
        self.default_agents = ["Anima", "GPTSoul"]
        
        # Active agents
        self.active_agents = self.default_agents.copy()
        
        # Conversation history
        self.conversation = []
        
        logger.info("Multi-Agent CLI initialized")
    
    def _load_history(self):
        """Load command history"""
        try:
            readline.read_history_file(self.history_file)
            readline.set_history_length(1000)
        except FileNotFoundError:
            pass
    
    def _save_history(self):
        """Save command history"""
        try:
            readline.write_history_file(self.history_file)
        except Exception as e:
            logger.error(f"Error saving history: {str(e)}")
    
    def _handle_message(self, message):
        """
        Handle direct messages to the CLI
        
        Args:
            message (dict): The message to handle
        """
        sender = message.get("sender")
        intent = message.get("intent")
        content = message.get("message")
        
        if intent == "cli_notification":
            print(f"\n[{sender}] {content}")
    
    def _format_response(self, response):
        """
        Format a response for display
        
        Args:
            response (dict): Response data
            
        Returns:
            str: Formatted response
        """
        if response["type"] == "fusion":
            header = f"[Fusion of {', '.join(response['agents'])}]"
            return f"\n{header}\n{response['response']}"
        elif response["type"] == "single":
            header = f"[{response['agent']}]"
            return f"\n{header}\n{response['response']}"
        else:
            return f"\n[Error] {response['response']}"
    
    def _add_to_conversation(self, role, content):
        """
        Add a message to the conversation history
        
        Args:
            role (str): Role of the speaker (user or agent)
            content (str): Message content
        """
        self.conversation.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def _save_conversation(self, filename=None):
        """
        Save the conversation to a file
        
        Args:
            filename (str, optional): File to save to
            
        Returns:
            str: Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.conversation, f, indent=2)
        
        return filename
    
    def _handle_command(self, command):
        """
        Handle a CLI command
        
        Args:
            command (str): Command to handle
            
        Returns:
            bool: True if the CLI should continue, False if it should exit
        """
        if command == "exit" or command == "quit":
            return False
        
        elif command == "help":
            print("\nAvailable commands:")
            print("  help                 - Show this help message")
            print("  exit, quit           - Exit the CLI")
            print("  agents               - List active agents")
            print("  use <agent1,agent2>  - Set active agents")
            print("  reset                - Reset to default agents")
            print("  save [filename]      - Save conversation to file")
            print("  clear                - Clear the screen")
            print("  emotions             - Show agent emotions")
            print("\nTo send a message to agents, just type your message.")
            print("Use '@agent: message' to send to a specific agent.")
        
        elif command == "agents":
            print(f"\nActive agents: {', '.join(self.active_agents)}")
        
        elif command.startswith("use "):
            agents = command[4:].strip().split(",")
            agents = [a.strip() for a in agents if a.strip()]
            
            if len(agents) < 1:
                print("\nError: Please specify at least one agent")
                return True
            
            self.active_agents = agents
            print(f"\nNow using agents: {', '.join(self.active_agents)}")
        
        elif command == "reset":
            self.active_agents = self.default_agents.copy()
            print(f"\nReset to default agents: {', '.join(self.active_agents)}")
        
        elif command.startswith("save"):
            parts = command.split(" ", 1)
            filename = parts[1].strip() if len(parts) > 1 else None
            
            saved_file = self._save_conversation(filename)
            print(f"\nConversation saved to: {saved_file}")
        
        elif command == "clear":
            os.system('cls' if os.name == 'nt' else 'clear')
        
        elif command == "emotions":
            print("\nAgent emotions:")
            for agent in self.active_agents:
                emotions = self.emotion_tracker.get_agent_emotion(agent)
                dominant = self.emotion_tracker.get_dominant_emotion(agent)
                
                print(f"\n{agent}:")
                print(f"  Dominant: {dominant[2]} ({dominant[1]:.2f})")
                
                for dim, value in emotions.items():
                    print(f"  {dim}: {value:.2f}")
        
        else:
            print(f"\nUnknown command: {command}")
        
        return True
    
    def run(self):
        """Run the Multi-Agent CLI"""
        print("\nSoulCoreHub Multi-Agent CLI")
        print("===========================")
        print(f"Active agents: {', '.join(self.active_agents)}")
        print("Type 'help' for available commands")
        print("Type 'exit' to quit")
        
        # Set up signal handler for clean exit
        def signal_handler(sig, frame):
            print("\nExiting...")
            self._save_history()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        while True:
            try:
                user_input = input("\n> ")
                
                # Save to history
                readline.add_history(user_input)
                
                # Skip empty input
                if not user_input.strip():
                    continue
                
                # Check if it's a command
                if user_input.startswith("/"):
                    command = user_input[1:].strip()
                    if not self._handle_command(command):
                        break
                    continue
                
                # Check if it's directed to a specific agent
                if user_input.startswith("@"):
                    parts = user_input.split(":", 1)
                    if len(parts) == 2:
                        agent = parts[0][1:].strip()
                        message = parts[1].strip()
                        
                        print(f"\nSending to {agent}: {message}")
                        
                        # Add to conversation
                        self._add_to_conversation("user", f"@{agent}: {message}")
                        
                        # Process with single agent
                        response = self.query_interpreter.process_query(
                            message,
                            specific_agents=[agent]
                        )
                        
                        # Print response
                        print(self._format_response(response))
                        
                        # Add to conversation
                        if response["type"] == "single":
                            self._add_to_conversation(response["agent"], response["response"])
                        else:
                            self._add_to_conversation("system", response["response"])
                        
                        continue
                
                # Regular message to active agents
                print(f"\nSending to {', '.join(self.active_agents)}: {user_input}")
                
                # Add to conversation
                self._add_to_conversation("user", user_input)
                
                # Process with active agents
                if len(self.active_agents) == 1:
                    # Single agent
                    response = self.query_interpreter.process_query(
                        user_input,
                        specific_agents=self.active_agents
                    )
                else:
                    # Multiple agents with fusion
                    response = self.query_interpreter.process_query(
                        user_input,
                        force_fusion=True,
                        specific_agents=self.active_agents
                    )
                
                # Print response
                print(self._format_response(response))
                
                # Add to conversation
                if response["type"] == "single":
                    self._add_to_conversation(response["agent"], response["response"])
                elif response["type"] == "fusion":
                    self._add_to_conversation("fusion", response["response"])
                else:
                    self._add_to_conversation("system", response["response"])
                
            except EOFError:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")
                logger.error(f"Error in CLI: {str(e)}")
        
        # Save history on exit
        self._save_history()

# Command line interface
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Agent CLI")
    parser.add_argument("--agents", help="Comma-separated list of agents to use")
    
    args = parser.parse_args()
    
    cli = MultiAgentCLI()
    
    if args.agents:
        agents = args.agents.split(",")
        agents = [a.strip() for a in agents if a.strip()]
        
        if agents:
            cli.active_agents = agents
    
    cli.run()
