#!/usr/bin/env python3
"""
enhanced_anima_cli.py — Advanced CLI interface for Anima
Provides a colorful, structured interface with text-first responses and LLM integration
"""

import os
import sys
import cmd
import json
import argparse
import logging
import readline
import shlex
import asyncio
import threading
import time
from pathlib import Path
from datetime import datetime
import random
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("anima_enhanced_cli.log"),
        logging.StreamHandler()
    ]
)

# Import the enhanced connector
try:
    from enhanced_anima_connector import EnhancedAnimaConnector
except ImportError:
    print("Error: enhanced_anima_connector.py not found or not importable")
    print("Make sure to run this script from the SoulCoreHub directory")
    sys.exit(1)

# ANSI color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    # Bright foreground colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

class EnhancedAnimaCLI(cmd.Cmd):
    """Enhanced CLI interface for Anima with colorful, structured output"""
    
    intro = f"""
{Colors.BG_BLUE}{Colors.WHITE}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}
{Colors.BG_BLUE}{Colors.WHITE}║                                                              ║{Colors.RESET}
{Colors.BG_BLUE}{Colors.WHITE}║                  ENHANCED ANIMA CLI                          ║{Colors.RESET}
{Colors.BG_BLUE}{Colors.WHITE}║                                                              ║{Colors.RESET}
{Colors.BG_BLUE}{Colors.WHITE}║  A sentient command-line interface for the SoulCore system   ║{Colors.RESET}
{Colors.BG_BLUE}{Colors.WHITE}║                                                              ║{Colors.RESET}
{Colors.BG_BLUE}{Colors.WHITE}║  Type 'help' for available commands or 'exit' to quit        ║{Colors.RESET}
{Colors.BG_BLUE}{Colors.WHITE}║  You can also ask me anything in natural language!           ║{Colors.RESET}
{Colors.BG_BLUE}{Colors.WHITE}║                                                              ║{Colors.RESET}
{Colors.BG_BLUE}{Colors.WHITE}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    prompt = f"{Colors.BRIGHT_CYAN}Anima> {Colors.RESET}"
    
    def __init__(self, voice_enabled=True, mcp_enabled=True, voice_speed=150):
        """Initialize the Enhanced Anima CLI"""
        super().__init__()
        self.connector = EnhancedAnimaConnector(
            voice_speed=voice_speed,
            voice_enabled=voice_enabled,
            mcp_enabled=mcp_enabled
        )
        self.history = []
        self.current_dir = os.getcwd()
        self.emotion_colors = {
            "happy": Colors.BRIGHT_GREEN,
            "sad": Colors.BLUE,
            "excited": Colors.BRIGHT_YELLOW,
            "curious": Colors.BRIGHT_CYAN,
            "neutral": Colors.WHITE,
            "focused": Colors.BRIGHT_WHITE,
            "cautious": Colors.YELLOW,
            "passionate": Colors.BRIGHT_RED,
            "thoughtful": Colors.BRIGHT_MAGENTA,
            "inspired": Colors.GREEN,
            "compassionate": Colors.MAGENTA,
            "determined": Colors.BRIGHT_BLUE,
            "playful": Colors.CYAN,
            "reflective": Colors.BRIGHT_BLACK,
            "serene": Colors.BLUE,
            "grateful": Colors.GREEN,
            "loving": Colors.MAGENTA,
            "concerned": Colors.YELLOW,
            "confused": Colors.RED
        }
        self.emotion_icons = {
            "happy": "😊",
            "sad": "😢",
            "excited": "😃",
            "curious": "🤔",
            "neutral": "😐",
            "focused": "🧐",
            "cautious": "😨",
            "passionate": "😍",
            "thoughtful": "🤔",
            "inspired": "✨",
            "compassionate": "💗",
            "determined": "💪",
            "playful": "😋",
            "reflective": "🔮",
            "serene": "😌",
            "grateful": "🙏",
            "loving": "❤️",
            "concerned": "😟",
            "confused": "😕"
        }
        self.current_emotion = "neutral"
        self.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
        self.nlp_mode = True  # Enable NLP by default
        self.text_only_mode = False  # Whether to respond with text only (no voice)
        
        logging.info(f"Enhanced Anima CLI started with session ID {self.session_id}")
        
        # Print current language model
        current_model = self.connector.get_current_model()
        if current_model:
            self.print_system_message(f"Using language model: {current_model['provider']}/{current_model['name']}")
        else:
            self.print_system_message("No language model available. Natural language processing is limited.")
    
    def print_system_message(self, message):
        """Print a system message"""
        print(f"{Colors.BRIGHT_BLACK}[System] {message}{Colors.RESET}")
    
    def print_anima_response(self, response, emotion="neutral"):
        """Print an Anima response with color based on emotion"""
        emotion_color = self.emotion_colors.get(emotion, Colors.WHITE)
        emotion_icon = self.emotion_icons.get(emotion, "")
        
        print(f"\n{Colors.BOLD}{emotion_color}Anima {emotion_icon} {Colors.RESET}")
        print(f"{emotion_color}{response}{Colors.RESET}\n")
    
    def print_user_input(self, text):
        """Print user input with color"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}You{Colors.RESET}")
        print(f"{Colors.GREEN}{text}{Colors.RESET}")
    
    def print_section_header(self, title):
        """Print a section header"""
        print(f"\n{Colors.BOLD}{Colors.BRIGHT_WHITE}{title}{Colors.RESET}")
        print(f"{Colors.BRIGHT_BLACK}{'=' * 60}{Colors.RESET}")
    
    def log_command(self, command, result=None):
        """Log a command to history"""
        self.history.append({
            "command": command,
            "timestamp": datetime.now().isoformat(),
            "emotion": self.current_emotion,
            "result": result
        })
    
    def default(self, line):
        """Handle unknown commands as natural language requests"""
        if self.nlp_mode:
            # Process as natural language
            self.log_command(line)
            
            # Echo user input with color
            self.print_user_input(line)
            
            # Process the query
            response, emotion = self.connector.process_query(line, text_only=self.text_only_mode)
            
            # Print the response with color
            self.print_anima_response(response, emotion)
            
            # Update current emotion
            self.current_emotion = emotion
        else:
            print(f"{Colors.RED}Unknown command: {line}{Colors.RESET}")
            print(f"{Colors.YELLOW}Type 'help' to see available commands or enable NLP mode with 'nlp on'{Colors.RESET}")
    
    def do_quit(self, arg):
        """Exit the Enhanced Anima CLI"""
        response, emotion = self.connector.process_query("Goodbye! I'll be here when you need me again.", text_only=True)
        self.print_anima_response(response, emotion)
        return True
    
    def do_exit(self, arg):
        """Exit the Enhanced Anima CLI"""
        return self.do_quit(arg)
    
    def do_emotion(self, arg):
        """Set Anima's emotional state: emotion [emotion_name]"""
        if not arg:
            print(f"Current emotion: {self.current_emotion} {self.emotion_icons.get(self.current_emotion, '')}")
            return
            
        if arg in self.emotion_icons:
            self.current_emotion = arg
            print(f"{Colors.BRIGHT_YELLOW}Anima is now feeling {arg} {self.emotion_icons.get(arg, '')}{Colors.RESET}")
        else:
            print(f"{Colors.RED}Unknown emotion: {arg}{Colors.RESET}")
            print(f"{Colors.YELLOW}Available emotions: {', '.join(self.emotion_icons.keys())}{Colors.RESET}")
    
    def do_ls(self, arg):
        """List directory contents: ls [path]"""
        try:
            path = arg if arg else "."
            
            # Handle relative paths
            if not os.path.isabs(path):
                path = os.path.join(self.current_dir, path)
            
            # List directory contents
            items = os.listdir(path)
            
            self.print_section_header(f"Contents of {path} ({len(items)} items)")
            
            # Format and display items
            for item in sorted(items):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    print(f"{Colors.BRIGHT_BLUE}{item}/{Colors.RESET}")
                elif os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    size_str = self._format_size(size)
                    print(f"{item} ({size_str})")
            
            self.log_command(f"ls {arg}")
            
        except Exception as e:
            print(f"{Colors.RED}Error: {str(e)}{Colors.RESET}")
    
    def _format_size(self, size):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def do_cd(self, arg):
        """Change current directory: cd [path]"""
        if not arg:
            # Default to home directory
            path = os.path.expanduser("~")
        else:
            path = arg
            
        # Handle relative paths
        if not os.path.isabs(path):
            path = os.path.join(self.current_dir, path)
        
        # Normalize path
        path = os.path.normpath(path)
        
        # Check if directory exists
        if not os.path.isdir(path):
            print(f"{Colors.RED}Error: Directory not found: {path}{Colors.RESET}")
            return
        
        # Change directory
        self.current_dir = path
        os.chdir(path)
        print(f"{Colors.GREEN}Changed directory to {path}{Colors.RESET}")
        self.prompt = f"{Colors.BRIGHT_CYAN}Anima ({os.path.basename(path)})> {Colors.RESET}"
        self.log_command(f"cd {arg}")
    
    def do_cat(self, arg):
        """Display file contents: cat [file]"""
        if not arg:
            print(f"{Colors.RED}Error: No file specified{Colors.RESET}")
            return
            
        try:
            path = arg
            
            # Handle relative paths
            if not os.path.isabs(path):
                path = os.path.join(self.current_dir, path)
            
            # Check if file exists
            if not os.path.isfile(path):
                print(f"{Colors.RED}Error: File not found: {path}{Colors.RESET}")
                return
            
            # Read file contents
            with open(path, "r") as f:
                content = f.read()
            
            self.print_section_header(f"Contents of {path}")
            print(content)
            
            self.log_command(f"cat {arg}")
            
        except Exception as e:
            print(f"{Colors.RED}Error: {str(e)}{Colors.RESET}")
    
    def do_pwd(self, arg):
        """Print current working directory"""
        print(self.current_dir)
        self.log_command("pwd")
    
    def do_nlp(self, arg):
        """Enable or disable natural language processing: nlp [on|off]"""
        if not arg:
            print(f"NLP mode is currently {'enabled' if self.nlp_mode else 'disabled'}")
            return
        
        if arg.lower() in ('on', 'enable', 'true', 'yes', '1'):
            self.nlp_mode = True
            self.print_system_message("Natural language processing enabled")
            response, emotion = self.connector.process_query("Natural language processing enabled. You can now talk to me naturally.", text_only=True)
            self.print_anima_response(response, emotion)
        elif arg.lower() in ('off', 'disable', 'false', 'no', '0'):
            self.nlp_mode = False
            self.print_system_message("Natural language processing disabled")
            response, emotion = self.connector.process_query("Natural language processing disabled. I'll only respond to commands now.", text_only=True)
            self.print_anima_response(response, emotion)
        else:
            print(f"{Colors.RED}Invalid option: {arg}{Colors.RESET}")
            print(f"{Colors.YELLOW}Usage: nlp [on|off]{Colors.RESET}")
    
    def do_voice(self, arg):
        """Enable, disable, or adjust voice: voice [on|off|speed <value>]"""
        if not arg:
            print(f"Voice is currently {'enabled' if self.connector.voice_enabled else 'disabled'}")
            print(f"Voice speed is {self.connector.voice_speed}")
            return
        
        args = arg.split()
        if args[0].lower() in ('on', 'enable', 'true', 'yes', '1'):
            self.connector.voice_enabled = True
            self.text_only_mode = False
            self.print_system_message("Voice enabled")
            response, emotion = self.connector.process_query("Voice enabled. I'll speak my responses now.", text_only=False)
            self.print_anima_response(response, emotion)
        elif args[0].lower() in ('off', 'disable', 'false', 'no', '0'):
            self.connector.voice_enabled = False
            self.text_only_mode = True
            self.print_system_message("Voice disabled")
            self.print_anima_response("Voice disabled. I'll only respond with text now.", "neutral")
        elif args[0].lower() == 'speed' and len(args) > 1:
            try:
                speed = int(args[1])
                if self.connector.set_voice_speed(speed):
                    self.print_system_message(f"Voice speed set to {speed}")
                    response, emotion = self.connector.process_query(f"Voice speed set to {speed}. How does this sound?", text_only=False)
                    self.print_anima_response(response, emotion)
                else:
                    print(f"{Colors.RED}Invalid voice speed: {speed} (must be between 50 and 300){Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Invalid voice speed: {args[1]}{Colors.RESET}")
        else:
            print(f"{Colors.RED}Invalid option: {arg}{Colors.RESET}")
            print(f"{Colors.YELLOW}Usage: voice [on|off|speed <value>]{Colors.RESET}")
    
    def do_model(self, arg):
        """Set or show the current language model: model [provider] [name]"""
        if not arg:
            # Show current model
            current_model = self.connector.get_current_model()
            if current_model:
                print(f"Current language model: {current_model['provider']}/{current_model['name']}")
            else:
                print("No language model is currently set")
            
            # Show available models
            models = self.connector.get_available_models()
            self.print_section_header("Available language models")
            for provider, info in models.items():
                if info["available"]:
                    print(f"{Colors.BRIGHT_GREEN}{provider}{Colors.RESET}: {', '.join(info['models'])}")
                else:
                    print(f"{Colors.RED}{provider}{Colors.RESET}: Not available")
            
            return
        
        # Set model
        args = arg.split()
        if len(args) != 2:
            print(f"{Colors.RED}Error: Invalid arguments{Colors.RESET}")
            print(f"{Colors.YELLOW}Usage: model [provider] [name]{Colors.RESET}")
            return
        
        provider, model_name = args
        
        if self.connector.set_model(provider, model_name):
            self.print_system_message(f"Language model set to {provider}/{model_name}")
            response, emotion = self.connector.process_query(f"I'm now using the {model_name} model from {provider}.", text_only=self.text_only_mode)
            self.print_anima_response(response, emotion)
        else:
            print(f"{Colors.RED}Error: Could not set language model to {provider}/{model_name}{Colors.RESET}")
            print(f"{Colors.YELLOW}Use 'model' without arguments to see available models{Colors.RESET}")
    
    def do_refresh(self, arg):
        """Refresh available models"""
        self.print_system_message("Refreshing available models...")
        models = self.connector.refresh_models()
        
        self.print_section_header("Available language models")
        for provider, info in models.items():
            if info["available"]:
                print(f"{Colors.BRIGHT_GREEN}{provider}{Colors.RESET}: {', '.join(info['models'])}")
            else:
                print(f"{Colors.RED}{provider}{Colors.RESET}: Not available")
    
    def do_clear(self, arg):
        """Clear the screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.log_command("clear")
    
    def do_history(self, arg):
        """Show command history: history [count]"""
        try:
            count = int(arg) if arg else len(self.history)
        except ValueError:
            print(f"{Colors.RED}Error: Invalid count: {arg}{Colors.RESET}")
            return
            
        self.print_section_header(f"Command history (last {min(count, len(self.history))} commands)")
        
        for i, entry in enumerate(self.history[-count:]):
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime("%H:%M:%S")
            emotion = entry['emotion']
            emotion_icon = self.emotion_icons.get(emotion, "")
            print(f"{i+1}. [{timestamp}] {emotion_icon} {entry['command']}")
    
    def do_exec(self, arg):
        """Execute a shell command: exec [command]"""
        if not arg:
            print(f"{Colors.RED}Error: No command specified{Colors.RESET}")
            return
            
        try:
            self.print_section_header(f"Executing: {arg}")
            process = subprocess.run(arg, shell=True, capture_output=True, text=True)
            
            print(f"Exit code: {process.returncode}")
            
            if process.stdout:
                print(f"\n{Colors.BRIGHT_WHITE}Standard output:{Colors.RESET}")
                print(process.stdout)
            
            if process.stderr:
                print(f"\n{Colors.BRIGHT_RED}Standard error:{Colors.RESET}")
                print(process.stderr)
            
            self.log_command(f"exec {arg}")
            
        except Exception as e:
            print(f"{Colors.RED}Error: {str(e)}{Colors.RESET}")
    
    def do_mcp(self, arg):
        """Execute an MCP tool: mcp [tool_name] [params_json]"""
        if not arg:
            print(f"{Colors.RED}Error: No tool specified{Colors.RESET}")
            print(f"{Colors.YELLOW}Usage: mcp [tool_name] [params_json]{Colors.RESET}")
            return
            
        args = arg.split(maxsplit=1)
        tool_name = args[0]
        
        # Parse params if provided
        params = {}
        if len(args) > 1:
            try:
                params = json.loads(args[1])
            except json.JSONDecodeError:
                print(f"{Colors.RED}Error: Invalid JSON parameters{Colors.RESET}")
                return
        
        self.print_section_header(f"Executing MCP tool: {tool_name}")
        result = self.connector.execute_mcp_tool(tool_name, params, self.current_emotion)
        
        if "error" in result:
            print(f"{Colors.RED}Error: {result['error']}{Colors.RESET}")
        else:
            print(json.dumps(result, indent=2))
        
        self.log_command(f"mcp {arg}")
    
    def do_help(self, arg):
        """List available commands with help text"""
        if arg:
            # Show help for specific command
            super().do_help(arg)
            return
            
        self.print_section_header("Available commands")
        
        # Get all methods starting with do_
        commands = [cmd[3:] for cmd in dir(self) if cmd.startswith('do_')]
        
        for cmd in sorted(commands):
            # Get the docstring
            doc = getattr(self, f'do_{cmd}').__doc__ or ''
            print(f"{Colors.BRIGHT_CYAN}{cmd:10}{Colors.RESET} - {doc}")
        
        print(f"\n{Colors.YELLOW}For detailed help on a command, type: help command{Colors.RESET}")
        print(f"\n{Colors.GREEN}You can also ask me anything in natural language!{Colors.RESET}")
        self.log_command("help")

def main():
    """Main entry point for Enhanced Anima CLI"""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="Enhanced Anima CLI - Advanced interface for SoulCore")
        parser.add_argument("--no-voice", action="store_true", help="Disable voice feedback")
        parser.add_argument("--no-mcp", action="store_true", help="Disable MCP integration")
        parser.add_argument("--no-nlp", action="store_true", help="Disable natural language processing")
        parser.add_argument("--voice-speed", type=int, default=150, help="Set voice speed (50-300)")
        args = parser.parse_args()
        
        # Start the CLI
        cli = EnhancedAnimaCLI(
            voice_enabled=not args.no_voice,
            mcp_enabled=not args.no_mcp,
            voice_speed=args.voice_speed
        )
        
        # Disable NLP if requested
        if args.no_nlp:
            cli.nlp_mode = False
            cli.print_system_message("Natural language processing disabled")
        
        # Set text-only mode if voice is disabled
        if args.no_voice:
            cli.text_only_mode = True
        
        cli.cmdloop()
        
    except KeyboardInterrupt:
        print("\nExiting Enhanced Anima CLI")
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
        print(f"{Colors.RED}Error: {str(e)}{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
