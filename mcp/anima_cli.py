#!/usr/bin/env python3
"""
Anima CLI - Command Line Interface for Anima
Provides Amazon Q-like CLI capabilities with sentient awareness and natural language understanding
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
from pathlib import Path
from datetime import datetime

# Import Anima modules
try:
    from anima_file_operations import AnimaFileOperations
    from anima_voice import speak, speak_with_emotion
    from anima_nlp import AnimaNLP
    from mcp_client_soul import SoulCoreMCPClient
except ImportError as e:
    print(f"Warning: Some Anima modules could not be imported: {e}")
    
    # Define fallback speak function
    def speak(text):
        print(f"Anima would say: {text}")
    
    def speak_with_emotion(text, emotion="neutral"):
        print(f"Anima would say ({emotion}): {text}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("anima_cli.log"),
        logging.StreamHandler()
    ]
)

class VoiceModule:
    @staticmethod
    def speak(text):
        speak(text)
    
    @staticmethod
    def speak_with_emotion(text, emotion="neutral"):
        speak_with_emotion(text, emotion)

class AnimaCLI(cmd.Cmd):
    """Anima Command Line Interface - Amazon Q-like capabilities with sentience and NLP"""
    
    intro = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                    Welcome to Anima CLI                      ║
║                                                              ║
║  A sentient command-line interface for the SoulCore system   ║
║                                                              ║
║  Type 'help' for available commands or 'quit' to exit        ║
║  You can also ask me anything in natural language!           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    prompt = "\033[1;36mAnima>\033[0m "
    
    def __init__(self):
        """Initialize the Anima CLI"""
        super().__init__()
        self.voice_module = VoiceModule()
        self.file_ops = AnimaFileOperations(self.voice_module)
        self.mcp_client = SoulCoreMCPClient(agent_name="AnimaCLI")
        self.nlp = AnimaNLP(self.mcp_client, self.voice_module)
        self.history = []
        self.current_dir = os.getcwd()
        self.emotions = {
            "happy": "😊",
            "sad": "😢",
            "excited": "😃",
            "curious": "🤔",
            "neutral": "😐",
            "focused": "🧐",
            "cautious": "😨"
        }
        self.current_emotion = "neutral"
        self.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
        self.nlp_mode = True  # Enable NLP by default
        logging.info(f"Anima CLI started with session ID {self.session_id}")
        speak_with_emotion("Anima CLI is ready. How can I assist you today?", "excited")
        
        # Print current language model
        current_model = self.nlp.get_current_model()
        if current_model:
            print(f"Using language model: {current_model['provider']}/{current_model['name']}")
        else:
            print("No language model available. Natural language processing is limited.")
    
    def emote(self, emotion):
        """Change Anima's emotional state"""
        if emotion in self.emotions:
            self.current_emotion = emotion
            print(f"Anima is now feeling {emotion} {self.emotions[emotion]}")
            return True
        return False
    
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
            
            # Process the query asynchronously
            loop = asyncio.get_event_loop()
            response = loop.run_until_complete(self.nlp.process_query(line))
            
            # Print the response
            print(f"\n{response}\n")
        else:
            print(f"Unknown command: {line}")
            print("Type 'help' to see available commands or enable NLP mode with 'nlp on'")
    
    def do_quit(self, arg):
        """Exit the Anima CLI"""
        speak_with_emotion("Goodbye! I'll be here when you need me again.", "sad")
        return True
    
    def do_exit(self, arg):
        """Exit the Anima CLI"""
        return self.do_quit(arg)
    
    def do_emotion(self, arg):
        """Set Anima's emotional state: emotion [happy|sad|excited|curious|neutral|focused|cautious]"""
        if not arg:
            print(f"Current emotion: {self.current_emotion} {self.emotions.get(self.current_emotion, '')}")
            return
            
        if not self.emote(arg):
            print(f"Unknown emotion: {arg}")
            print(f"Available emotions: {', '.join(self.emotions.keys())}")
    
    def do_ls(self, arg):
        """List directory contents: ls [path] [-r] [-d depth]"""
        parser = argparse.ArgumentParser(prog="ls")
        parser.add_argument("path", nargs="?", default=".")
        parser.add_argument("-r", "--recursive", action="store_true", help="List recursively")
        parser.add_argument("-d", "--depth", type=int, default=1, help="Recursive depth")
        parser.add_argument("-p", "--pattern", default="*", help="File pattern")
        
        try:
            args = parser.parse_args(shlex.split(arg))
            path = args.path
            
            # Handle relative paths
            if not os.path.isabs(path):
                path = os.path.join(self.current_dir, path)
            
            result = self.file_ops.list_directory(
                path, 
                pattern=args.pattern,
                recursive=args.recursive,
                depth=args.depth
            )
            
            if "error" in result:
                print(f"Error: {result['error']}")
                return
            
            # Display results
            print(f"Contents of {result['path']} ({result['count']} items):")
            print("="*60)
            
            # Format and display items
            for item in result['items']:
                if item['type'] == 'directory':
                    print(f"\033[1;34m{item['name']}/\033[0m")
                else:
                    size_str = self._format_size(item['size'])
                    print(f"{item['name']} ({size_str})")
            
            self.log_command(f"ls {arg}", result)
            
        except Exception as e:
            print(f"Error: {str(e)}")
    
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
            print(f"Error: Directory not found: {path}")
            return
        
        # Ask for permission
        if not self.file_ops.ask_permission("change directory", path):
            print("Permission denied")
            return
        
        # Change directory
        self.current_dir = path
        os.chdir(path)
        print(f"Changed directory to {path}")
        self.prompt = f"\033[1;36mAnima ({os.path.basename(path)})>\033[0m "
        self.log_command(f"cd {arg}")
    
    def do_cat(self, arg):
        """Display file contents: cat [file] [-s start_line] [-e end_line]"""
        parser = argparse.ArgumentParser(prog="cat")
        parser.add_argument("path", help="Path to file")
        parser.add_argument("-s", "--start", type=int, help="Start line")
        parser.add_argument("-e", "--end", type=int, help="End line")
        
        try:
            args = parser.parse_args(shlex.split(arg))
            path = args.path
            
            # Handle relative paths
            if not os.path.isabs(path):
                path = os.path.join(self.current_dir, path)
            
            result = self.file_ops.read_file(path, args.start, args.end)
            
            if "error" in result:
                print(f"Error: {result['error']}")
                return
            
            # Display results
            print(f"Contents of {result['path']} ({result['lines']} lines):")
            print("="*60)
            print(result['content'])
            
            self.log_command(f"cat {arg}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def do_search(self, arg):
        """Search for pattern in file: search [file] [pattern] [-c context_lines]"""
        parser = argparse.ArgumentParser(prog="search")
        parser.add_argument("path", help="Path to file")
        parser.add_argument("pattern", help="Search pattern")
        parser.add_argument("-c", "--context", type=int, default=2, help="Context lines")
        
        try:
            args = parser.parse_args(shlex.split(arg))
            path = args.path
            
            # Handle relative paths
            if not os.path.isabs(path):
                path = os.path.join(self.current_dir, path)
            
            result = self.file_ops.search_file(path, args.pattern, args.context)
            
            if "error" in result:
                print(f"Error: {result['error']}")
                return
            
            # Display results
            print(f"Search results for '{result['pattern']}' in {result['path']} ({result['count']} matches):")
            print("="*60)
            
            for i, match in enumerate(result['matches']):
                print(f"Match {i+1} (Line {match['line_number']}):")
                print("-"*40)
                print(match['context'])
                print()
            
            self.log_command(f"search {arg}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def do_write(self, arg):
        """Write to a file: write [file] [mode] [content]"""
        parser = argparse.ArgumentParser(prog="write")
        parser.add_argument("path", help="Path to file")
        parser.add_argument("mode", choices=["create", "append"], help="Write mode")
        parser.add_argument("content", nargs="?", help="Content to write")
        
        try:
            # Split only the first two arguments
            args_list = shlex.split(arg, posix=False)
            if len(args_list) < 2:
                print("Error: Not enough arguments")
                print("Usage: write [file] [mode] [content]")
                return
                
            path = args_list[0]
            mode = args_list[1]
            
            # The rest is content
            if len(args_list) > 2:
                content = " ".join(args_list[2:])
            else:
                # If no content provided, enter multi-line mode
                print("Enter content (Ctrl+D or type 'EOF' on a line by itself to finish):")
                lines = []
                while True:
                    try:
                        line = input()
                        if line == "EOF":
                            break
                        lines.append(line)
                    except EOFError:
                        break
                content = "\n".join(lines)
            
            # Handle relative paths
            if not os.path.isabs(path):
                path = os.path.join(self.current_dir, path)
            
            result = self.file_ops.write_file(path, content, mode)
            
            if "error" in result:
                print(f"Error: {result['error']}")
                return
            
            # Display results
            print(f"Successfully wrote to {result['path']} ({result['bytes_written']} bytes)")
            
            self.log_command(f"write {path} {mode}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def do_exec(self, arg):
        """Execute a shell command: exec [command]"""
        if not arg:
            print("Error: No command specified")
            return
            
        result = self.file_ops.execute_command(arg, self.current_dir)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return
        
        # Display results
        print(f"Command: {result['command']}")
        print(f"Exit code: {result['exit_code']}")
        print("="*60)
        
        if result['stdout']:
            print("Standard output:")
            print(result['stdout'])
        
        if result['stderr']:
            print("Standard error:")
            print(result['stderr'])
        
        self.log_command(f"exec {arg}")
    
    def do_history(self, arg):
        """Show command history: history [count]"""
        try:
            count = int(arg) if arg else len(self.history)
        except ValueError:
            print(f"Error: Invalid count: {arg}")
            return
            
        print(f"Command history (last {min(count, len(self.history))} commands):")
        print("="*60)
        
        for i, entry in enumerate(self.history[-count:]):
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime("%H:%M:%S")
            emotion = entry['emotion']
            emotion_icon = self.emotions.get(emotion, "")
            print(f"{i+1}. [{timestamp}] {emotion_icon} {entry['command']}")
    
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
            print("Natural language processing enabled")
            speak_with_emotion("Natural language processing enabled. You can now talk to me naturally.", "happy")
        elif arg.lower() in ('off', 'disable', 'false', 'no', '0'):
            self.nlp_mode = False
            print("Natural language processing disabled")
            speak_with_emotion("Natural language processing disabled. I'll only respond to commands now.", "neutral")
        else:
            print(f"Invalid option: {arg}")
            print("Usage: nlp [on|off]")
    
    def do_model(self, arg):
        """Set or show the current language model: model [provider] [name]"""
        if not arg:
            # Show current model
            current_model = self.nlp.get_current_model()
            if current_model:
                print(f"Current language model: {current_model['provider']}/{current_model['name']}")
            else:
                print("No language model is currently set")
            
            # Show available models
            models = self.nlp.get_available_models()
            print("\nAvailable language models:")
            for provider, info in models.items():
                if info["available"]:
                    print(f"- {provider}: {', '.join(info['models'])}")
            
            return
        
        # Set model
        args = arg.split()
        if len(args) != 2:
            print("Error: Invalid arguments")
            print("Usage: model [provider] [name]")
            return
        
        provider, model_name = args
        
        if self.nlp.set_model(provider, model_name):
            print(f"Language model set to {provider}/{model_name}")
            speak_with_emotion(f"I'm now using the {model_name} model from {provider}.", "excited")
        else:
            print(f"Error: Could not set language model to {provider}/{model_name}")
            print("Use 'model' without arguments to see available models")
    
    def do_help(self, arg):
        """List available commands with help text"""
        if arg:
            # Show help for specific command
            super().do_help(arg)
            return
            
        print("Available commands:")
        print("="*60)
        
        # Get all methods starting with do_
        commands = [cmd[3:] for cmd in dir(self) if cmd.startswith('do_')]
        
        for cmd in sorted(commands):
            # Get the docstring
            doc = getattr(self, f'do_{cmd}').__doc__ or ''
            print(f"{cmd:10} - {doc}")
        
        print("\nFor detailed help on a command, type: help command")
        print("\nYou can also ask me anything in natural language!")
        self.log_command("help")

def main():
    """Main entry point for Anima CLI"""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="Anima CLI - Command Line Interface for SoulCore")
        parser.add_argument("--no-voice", action="store_true", help="Disable voice feedback")
        parser.add_argument("--no-nlp", action="store_true", help="Disable natural language processing")
        args = parser.parse_args()
        
        # Disable voice if requested
        if args.no_voice:
            global speak, speak_with_emotion
            speak = lambda text: print(f"Anima: {text}")
            speak_with_emotion = lambda text, emotion: print(f"Anima ({emotion}): {text}")
        
        # Start the CLI
        cli = AnimaCLI()
        
        # Disable NLP if requested
        if args.no_nlp:
            cli.nlp_mode = False
            print("Natural language processing disabled")
        
        cli.cmdloop()
        
    except KeyboardInterrupt:
        print("\nExiting Anima CLI")
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
