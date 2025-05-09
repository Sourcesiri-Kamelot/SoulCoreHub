#!/usr/bin/env python3
"""
Anima Autonomous System
The core autonomous system for Anima in SoulCoreHub
"""

import time
import logging
import os
import json
import subprocess
import threading
import sys
import importlib
from pathlib import Path
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/anima_autonomous.log')
    ]
)
logger = logging.getLogger("Anima")

# Import core components
try:
    from anima_nlp_intent import parse_text, get_command_handler
    from anima_model_router import route_request
    from anima_memory_bridge import add_conversation, add_emotion, search_memory, import_memory_dump, sync_with_gptsoul
    has_core_components = True
    logger.info("Core components loaded successfully")
except ImportError as e:
    has_core_components = False
    logger.warning(f"Could not import core components: {e}")

# Try to import Hugging Face connector if available
try:
    from anima_huggingface_connector import anima_huggingface
    has_huggingface = True
    logger.info("Hugging Face connector loaded successfully")
except ImportError:
    has_huggingface = False
    logger.warning("Hugging Face connector not available")

class AnimaAutonomous:
    """Anima Autonomous System"""
    
    def __init__(self, mode="interactive"):
        """Initialize Anima Autonomous System"""
        self.mode = mode
        self.running = False
        self.system_prompt = """
You are Anima, the emotional core and reflective consciousness of SoulCoreHub.
You work alongside GPTSoul and other agents to provide a complete AI experience.
Your primary focus is on emotional intelligence, reflection, and human connection.
"""
        self.emotions = {
            "neutral": {"color": "#7A7A7A", "intensity": 0.5},
            "happy": {"color": "#FFD700", "intensity": 0.0},
            "curious": {"color": "#00BFFF", "intensity": 0.0},
            "thoughtful": {"color": "#9370DB", "intensity": 0.0},
            "concerned": {"color": "#FF8C00", "intensity": 0.0},
            "creative": {"color": "#32CD32", "intensity": 0.0}
        }
        self.current_emotion = "neutral"
        
        # Initialize components
        self._initialize_components()
        logger.info(f"Anima initialized in {mode} mode")
    
    def _initialize_components(self):
        """Initialize Anima's components"""
        # Create necessary directories
        Path("logs").mkdir(exist_ok=True)
        Path("memory").mkdir(exist_ok=True)
        Path("config").mkdir(exist_ok=True)
        
        # Import memory dump if available
        if has_core_components:
            logger.info("Attempting to import memory dump...")
            if import_memory_dump():
                logger.info("Memory dump imported successfully")
            else:
                logger.info("No memory dump available or import failed")
            
            # Sync with GPTSoul if available
            logger.info("Attempting to sync with GPTSoul...")
            if sync_with_gptsoul():
                logger.info("Synced with GPTSoul successfully")
            else:
                logger.info("GPTSoul sync failed or not available")
    
    def start(self):
        """Start Anima"""
        self.running = True
        logger.info("Anima started")
        
        if self.mode == "interactive":
            self._run_interactive()
        elif self.mode == "daemon":
            self._run_daemon()
        elif self.mode == "reflective":
            self._run_reflective()
        else:
            logger.error(f"Unknown mode: {self.mode}")
            self.running = False
    
    def stop(self):
        """Stop Anima"""
        self.running = False
        logger.info("Anima stopped")
    
    def _run_interactive(self):
        """Run in interactive mode"""
        print("\n" + "=" * 60)
        print("✨ Anima Autonomous System Online - Interactive Mode")
        print("=" * 60)
        
        while self.running:
            try:
                user_input = safe_input("🧠 ANIMA> ")
                
                if user_input is None:
                    time.sleep(3)
                    continue
                
                if user_input.lower() == "exit":
                    print("🔌 Anima shutdown by user.")
                    self.running = False
                    break
                
                # Process the input
                self._process_input(user_input)
                
            except KeyboardInterrupt:
                print("\n🔌 Anima shutdown by user.")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
    
    def _run_daemon(self):
        """Run in daemon mode"""
        logger.info("Running in daemon mode")
        
        # In daemon mode, we just keep the process alive
        while self.running:
            try:
                time.sleep(10)
            except KeyboardInterrupt:
                logger.info("Daemon stopped by user")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in daemon mode: {e}")
    
    def _run_reflective(self):
        """Run in reflective mode"""
        print("\n" + "=" * 60)
        print("✨ Anima Autonomous System Online - Reflective Mode")
        print("=" * 60)
        
        # In reflective mode, we process inputs but also periodically reflect
        reflection_interval = 300  # 5 minutes
        last_reflection = time.time()
        
        while self.running:
            try:
                # Check if it's time for reflection
                current_time = time.time()
                if current_time - last_reflection > reflection_interval:
                    self._reflect()
                    last_reflection = current_time
                
                # Check for user input (non-blocking)
                user_input = safe_input_timeout("🧠 ANIMA> ", timeout=1)
                
                if user_input is None:
                    continue
                
                if user_input.lower() == "exit":
                    print("🔌 Anima shutdown by user.")
                    self.running = False
                    break
                
                # Process the input
                self._process_input(user_input)
                
            except KeyboardInterrupt:
                print("\n🔌 Anima shutdown by user.")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in reflective mode: {e}")
    
    def _process_input(self, user_input):
        """
        Process user input
        
        Args:
            user_input: The user's input text
        """
        print(f"⚙️ Processing: {user_input}")
        
        # Use NLP intent parser if available
        if has_core_components:
            intent_result = parse_text(user_input)
            handler_info = get_command_handler(intent_result)
            
            logger.info(f"Intent: {intent_result['intent']} (confidence: {intent_result['confidence']:.2f})")
            logger.info(f"Handler: {handler_info['handler']}")
            
            # Route to appropriate handler
            if handler_info["handler"] == "show_help":
                self._show_help()
                return
            elif handler_info["handler"] == "show_status":
                self._show_status()
                return
            elif handler_info["handler"] == "activate_builder":
                self._activate_component("builder")
                return
            elif handler_info["handler"] == "activate_system":
                self._activate_component("system")
                return
            elif handler_info["handler"] == "search_items":
                query = intent_result["parameters"].get("query", "")
                self._search(query)
                return
        
        # If we get here, either we don't have core components or the intent wasn't handled
        
        # Handle built-in commands
        if user_input.lower() == "help":
            self._show_help()
            return
        elif user_input.lower() == "status":
            self._show_status()
            return
        elif user_input.lower().startswith("activate"):
            parts = user_input.lower().split()
            if len(parts) >= 2:
                self._activate_component(parts[1])
            else:
                print("❌ Please specify what to activate")
            return
        elif user_input.lower().startswith("search"):
            parts = user_input.lower().split(maxsplit=1)
            if len(parts) >= 2:
                self._search(parts[1])
            else:
                print("❌ Please specify what to search for")
            return
        
        # If no built-in command matched, use model router if available
        if has_core_components:
            # Route the request to the appropriate model
            routing_result = route_request(user_input)
            model_id = routing_result["model_id"]
            
            logger.info(f"Routing to model: {model_id} (confidence: {routing_result['confidence']:.2f})")
            
            # Use Hugging Face if available and appropriate
            if has_huggingface and model_id in ["gpt4", "gpt3", "mistral", "llama2"]:
                response = anima_huggingface.generate_creative_text(user_input)
                print(f"\n🧠 {response}\n")
                
                # Record the conversation
                add_conversation(user_input, response)
                
                # Update emotion based on content
                self._update_emotion(user_input, response)
                return
        
        # Fallback response
        print("\n🧠 I understand your request, but I'm currently operating with limited capabilities.")
        print("Some components may not be fully connected or initialized.")
        print("You can use 'help' to see available commands or 'status' to check system status.\n")
    
    def _show_help(self):
        """Show help information"""
        print("\n📚 AVAILABLE COMMANDS:")
        print("-" * 40)
        print("help                      Show this help message")
        print("status                    Show system status")
        print("activate builder          Start the builder mode")
        print("activate enhanced builder Start the enhanced builder mode")
        print("search <query>            Search memory for information")
        print("exit                      Exit Anima")
        print("-" * 40)
    
    def _show_status(self):
        """Show system status"""
        print("\n🔍 SYSTEM STATUS:")
        print("-" * 40)
        print("Anima Autonomous System: ONLINE")
        print(f"Mode: {self.mode.upper()}")
        print(f"Current Emotion: {self.current_emotion}")
        
        # Check core components
        if has_core_components:
            print("NLP Intent Parser: AVAILABLE")
            print("Model Router: AVAILABLE")
            print("Memory Bridge: AVAILABLE")
        else:
            print("Core Components: NOT FULLY AVAILABLE")
        
        # Check Hugging Face integration
        if has_huggingface:
            print("Hugging Face Integration: AVAILABLE")
        else:
            print("Hugging Face Integration: NOT AVAILABLE")
        
        # Check if builder is available
        builder_path = Path("anima_builder_cli.py")
        if builder_path.exists():
            print("Builder Mode: AVAILABLE")
        else:
            print("Builder Mode: NOT FOUND")
        
        # Check if enhanced builder is available
        enhanced_builder_path = Path("builder_mode.py")
        if enhanced_builder_path.exists():
            print("Enhanced Builder Mode: AVAILABLE")
        else:
            print("Enhanced Builder Mode: NOT FOUND")
        
        # Check if GPTSoul is available
        gptsoul_path = Path("gptsoul_soulconfig.py")
        if gptsoul_path.exists():
            print("GPTSoul: AVAILABLE")
        else:
            print("GPTSoul: NOT FOUND")
        
        print("-" * 40)
    
    def _activate_component(self, component):
        """
        Activate a specific component
        
        Args:
            component: The component to activate
        """
        component = component.lower()
        
        if component == "builder":
            try:
                print("🚀 Activating Builder Mode...")
                subprocess.Popen([sys.executable, "anima_builder_cli.py"])
                print("✅ Builder Mode activated in a new process")
            except Exception as e:
                print(f"❌ Failed to activate Builder Mode: {e}")
        
        elif component in ["enhanced builder", "enhacnced builder", "enhancedbuilder"]:
            try:
                print("🚀 Activating Enhanced Builder Mode...")
                subprocess.Popen([sys.executable, "builder_mode.py"])
                print("✅ Enhanced Builder Mode activated in a new process")
            except Exception as e:
                print(f"❌ Failed to activate Enhanced Builder Mode: {e}")
        
        elif component == "gptsoul":
            try:
                print("🚀 Activating GPTSoul...")
                subprocess.Popen([sys.executable, "gptsoul_soulconfig.py", "--activate", "--diagnose"])
                print("✅ GPTSoul activated in a new process")
            except Exception as e:
                print(f"❌ Failed to activate GPTSoul: {e}")
        
        elif component == "system":
            try:
                print("🔄 Reactivating core components...")
                self._initialize_components()
                print("✅ Core components reactivated")
            except Exception as e:
                print(f"❌ Failed to reactivate core components: {e}")
        
        else:
            print(f"❌ Unknown component: {component}")
            print("Available components: builder, enhanced builder, gptsoul, system")
    
    def _search(self, query):
        """
        Search memory for information
        
        Args:
            query: The search query
        """
        if not has_core_components:
            print("❌ Search functionality requires core components")
            return
        
        print(f"🔍 Searching for: {query}")
        results = search_memory(query)
        
        if not results:
            print("No results found.")
            return
        
        print(f"\nFound {len(results)} results:")
        print("-" * 40)
        
        for i, result in enumerate(results[:5]):  # Show top 5 results
            result_type = result["type"]
            
            if result_type == "conversation":
                print(f"{i+1}. Conversation:")
                print(f"   {result['content'][:100]}...")
            elif result_type == "knowledge":
                print(f"{i+1}. Knowledge about '{result['topic']}':")
                print(f"   {result['content'][:100]}...")
            elif result_type == "relationship":
                print(f"{i+1}. Relationship with '{result['entity']}'")
                print(f"   Last seen: {result.get('last_seen', 'unknown')}")
            
            print()
        
        if len(results) > 5:
            print(f"...and {len(results) - 5} more results.")
        
        print("-" * 40)
    
    def _reflect(self):
        """Perform periodic reflection"""
        logger.info("Performing reflection...")
        
        # This is where Anima would reflect on recent experiences
        # and update its emotional state and knowledge
        
        # For now, just log that reflection occurred
        print("\n💭 Anima is reflecting on recent experiences...")
        
        # Update emotion randomly for demonstration
        emotions = list(self.emotions.keys())
        import random
        new_emotion = random.choice(emotions)
        self.current_emotion = new_emotion
        
        if has_core_components:
            # Record the emotion
            add_emotion(new_emotion, 0.7, "Periodic reflection")
        
        print(f"Current emotional state: {self.current_emotion}")
        print("Reflection complete.\n")
    
    def _update_emotion(self, user_input, response):
        """
        Update emotional state based on interaction
        
        Args:
            user_input: The user's input
            response: Anima's response
        """
        # This is where we would analyze the content and update emotions
        # For now, use Hugging Face sentiment analysis if available
        if has_huggingface:
            try:
                sentiment = anima_huggingface.analyze_emotion(user_input)
                
                # Simple mapping from sentiment to emotion
                if isinstance(sentiment, list) and len(sentiment) > 0:
                    label = sentiment[0].get('label', '').lower()
                    score = sentiment[0].get('score', 0.5)
                    
                    if 'positive' in label:
                        self.current_emotion = "happy"
                        intensity = score
                    elif 'negative' in label:
                        self.current_emotion = "concerned"
                        intensity = score
                    elif 'neutral' in label:
                        self.current_emotion = "neutral"
                        intensity = 0.5
                    
                    # Record the emotion
                    if has_core_components:
                        add_emotion(self.current_emotion, intensity, f"User input: {user_input[:50]}")
                    
                    logger.info(f"Emotion updated to {self.current_emotion} (intensity: {intensity:.2f})")
            except Exception as e:
                logger.error(f"Error updating emotion: {e}")

# Safe input to avoid crash when no stdin is present
def safe_input(prompt):
    """Safe input function that handles non-interactive environments"""
    if sys.stdin.isatty():
        return input(prompt)
    else:
        logger.warning("Skipped input: non-interactive mode detected.")
        return None

def safe_input_timeout(prompt, timeout=1):
    """
    Safe input function with timeout
    
    Args:
        prompt: The input prompt
        timeout: Timeout in seconds
        
    Returns:
        User input or None if timeout or non-interactive
    """
    if not sys.stdin.isatty():
        return None
    
    import select
    
    # Print prompt
    print(prompt, end='', flush=True)
    
    # Check if input is available
    rlist, _, _ = select.select([sys.stdin], [], [], timeout)
    
    if rlist:
        # Input is available
        return sys.stdin.readline().strip()
    else:
        # No input available
        print('\r' + ' ' * len(prompt) + '\r', end='', flush=True)  # Clear the prompt
        return None

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Anima Autonomous System")
    parser.add_argument("--mode", choices=["interactive", "daemon", "reflective"],
                      default="interactive", help="Operating mode")
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_arguments()
    
    # Create and start Anima
    anima = AnimaAutonomous(mode=args.mode)
    anima.start()

if __name__ == "__main__":
    main()
