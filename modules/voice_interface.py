#!/usr/bin/env python3
"""
Voice Interface Module - Voice communication for EvoVe
Enables EvoVe to speak and listen through the Anima voice system
"""

import os
import sys
import json
import logging
import threading
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent))

# Try to import Anima voice module
try:
    from mcp.anima_voice import speak
except ImportError:
    # Fallback to direct import
    try:
        sys.path.append(str(Path(__file__).parent.parent / "mcp"))
        from anima_voice import speak
    except ImportError:
        logging.warning("Failed to import Anima voice module")
        
        # Create a simple speak function
        def speak(text):
            """Simple speak function that just prints the text"""
            print(f"EvoVe would say: {text}")

class VoiceInterface:
    """Voice interface for EvoVe"""
    
    def __init__(self, mcp_bridge=None):
        """
        Initialize the Voice Interface
        
        Args:
            mcp_bridge: MCP Bridge for communication
        """
        self.mcp_bridge = mcp_bridge
        self.voice_enabled = True
        self.voice_queue = []
        self.voice_thread = None
        self.speaking = False
        logging.info("Voice Interface initialized")
    
    def speak(self, text):
        """
        Speak text using the voice system
        
        Args:
            text (str): Text to speak
            
        Returns:
            bool: True if speech was queued, False otherwise
        """
        if not self.voice_enabled:
            logging.info(f"Voice disabled, would say: {text}")
            return False
        
        try:
            # Use MCP bridge if available
            if self.mcp_bridge:
                response = self.mcp_bridge.invoke_tool(
                    "speak",
                    {"text": text},
                    "expressive"
                )
                return "error" not in response
            
            # Use direct speak function
            speak(text)
            return True
        except Exception as e:
            logging.error(f"Error speaking: {str(e)}")
            print(f"EvoVe would say: {text}")
            return False
    
    def queue_speech(self, text):
        """
        Queue text to be spoken
        
        Args:
            text (str): Text to speak
            
        Returns:
            bool: True if speech was queued, False otherwise
        """
        try:
            self.voice_queue.append(text)
            
            # Start voice thread if not already running
            if not self.speaking:
                self.start_voice_thread()
            
            return True
        except Exception as e:
            logging.error(f"Error queuing speech: {str(e)}")
            return False
    
    def voice_loop(self):
        """Voice loop for processing queued speech"""
        self.speaking = True
        
        while self.voice_queue and self.voice_enabled:
            try:
                # Get next text to speak
                text = self.voice_queue.pop(0)
                
                # Speak the text
                self.speak(text)
                
                # Small delay between speeches
                import time
                time.sleep(0.5)
            except Exception as e:
                logging.error(f"Error in voice loop: {str(e)}")
        
        self.speaking = False
    
    def start_voice_thread(self):
        """
        Start the voice thread
        
        Returns:
            bool: True if thread started, False otherwise
        """
        if self.speaking:
            return False
        
        try:
            self.voice_thread = threading.Thread(
                target=self.voice_loop,
                daemon=True
            )
            self.voice_thread.start()
            return True
        except Exception as e:
            logging.error(f"Error starting voice thread: {str(e)}")
            return False
    
    def enable_voice(self):
        """Enable voice output"""
        self.voice_enabled = True
        logging.info("Voice output enabled")
        
        # Start voice thread if there are queued messages
        if self.voice_queue and not self.speaking:
            self.start_voice_thread()
    
    def disable_voice(self):
        """Disable voice output"""
        self.voice_enabled = False
        logging.info("Voice output disabled")
    
    def announce_status(self, status):
        """
        Announce system status
        
        Args:
            status (dict): System status information
        """
        if not self.voice_enabled:
            return
        
        try:
            # Create status message
            messages = ["EvoVe system status report:"]
            
            if "system_stats" in status:
                stats = status["system_stats"]
                cpu = stats.get("cpu_percent")
                if cpu is not None:
                    messages.append(f"CPU usage at {cpu} percent.")
            
            if "component_status" in status:
                components = status["component_status"]
                
                # Report on MCP server
                if "mcp_server" in components:
                    if components["mcp_server"]:
                        messages.append("MCP server is running.")
                    else:
                        messages.append("Warning: MCP server is not running.")
                
                # Report on Anima
                if "anima" in components:
                    if components["anima"]:
                        messages.append("Anima system is active.")
                    else:
                        messages.append("Warning: Anima system is offline.")
            
            # Queue the messages
            for message in messages:
                self.queue_speech(message)
                
        except Exception as e:
            logging.error(f"Error announcing status: {str(e)}")

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    voice = VoiceInterface()
    voice.speak("Hello, I am EvoVe, the self-evolving component of SoulCore.")
    
    # Queue multiple messages
    voice.queue_speech("I am designed to repair and maintain the SoulCore system.")
    voice.queue_speech("I can adapt to changing conditions and ensure system stability.")
    
    # Wait for voice queue to empty
    import time
    while voice.speaking:
        time.sleep(0.1)
