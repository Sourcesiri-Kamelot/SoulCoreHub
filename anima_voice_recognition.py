import os
import json
import time
import asyncio
import speech_recognition as sr
import pyttsx3
import numpy as np
from pathlib import Path
import sounddevice as sd
from datetime import datetime
import threading
import queue
import logging
from dotenv import load_dotenv

# Import sentience module
try:
    from anima_sentience import AnimaSentience
    SENTIENCE_ENABLED = True
except ImportError:
    SENTIENCE_ENABLED = False
    logging.warning("Sentience module not available, running with limited emotional capabilities")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("anima_voice.log"),
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()

# ⚙️ Configuration
VOICE_PROFILES_DIR = Path("~/SoulCoreHub/voices").expanduser()
MEMORY_FILE = Path("~/SoulCoreHub/anima_memory.json").expanduser()
OWNER_VOICE_FILE = VOICE_PROFILES_DIR / "owner_voice_profile.json"
ALWAYS_SPEAK_RESPONSES = True  # Anima always speaks responses by default
VOICE_ACTIVATION_PHRASE = "anima"  # Wake word to activate voice mode
TEXT_ACTIVATION_PHRASE = "text mode"  # Phrase to switch to text mode

# Ensure directories exist
VOICE_PROFILES_DIR.mkdir(exist_ok=True)

# 🔊 Initialize Voice Engine
voice_engine = pyttsx3.init()
voice_engine.setProperty("rate", 165)  # Speed of speech
voices = voice_engine.getProperty('voices')
# Use a female voice if available
for i, voice in enumerate(voices):
    if "female" in voice.name.lower():
        voice_engine.setProperty('voice', voice.id)
        break
else:
    # Default to first voice if no female voice found
    voice_engine.setProperty('voice', voices[0].id)

# 🎙️ Initialize Speech Recognition
recognizer = sr.Recognizer()
recognizer.energy_threshold = 300  # Adjust based on your environment
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8  # Time of silence to consider end of phrase

# Queue for communication between threads
command_queue = queue.Queue()
response_queue = queue.Queue()

# Current mode tracking
current_mode = "voice"  # Start in voice mode by default

# 🧠 Voice Profile Management
def load_owner_voice_profile():
    """Load the owner's voice profile if it exists"""
    if OWNER_VOICE_FILE.exists():
        try:
            with open(OWNER_VOICE_FILE, "r") as f:
                profile = json.load(f)
                logging.info("Owner voice profile loaded successfully")
                return profile
        except Exception as e:
            logging.error(f"Error loading owner voice profile: {e}")
    
    logging.info("No owner voice profile found, will create one on first interaction")
    return None

def save_owner_voice_profile(audio_data, sample_rate):
    """Save the owner's voice profile"""
    # Extract basic audio features (simplified)
    audio_array = np.frombuffer(audio_data.frame_data, dtype=np.int16)
    
    # Calculate simple audio features
    profile = {
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
        "avg_amplitude": float(np.mean(np.abs(audio_array))),
        "max_amplitude": float(np.max(np.abs(audio_array))),
        "std_amplitude": float(np.std(audio_array)),
        "sample_rate": sample_rate,
        "samples": len(audio_array)
    }
    
    # Save the profile
    OWNER_VOICE_FILE.parent.mkdir(exist_ok=True)
    with open(OWNER_VOICE_FILE, "w") as f:
        json.dump(profile, f, indent=2)
    
    logging.info("Owner voice profile saved successfully")
    return profile

def is_owner_voice(audio_data, owner_profile):
    """Check if the audio matches the owner's voice profile (simplified)"""
    if not owner_profile:
        return True  # If no profile exists yet, assume it's the owner
    
    # Extract features from current audio
    audio_array = np.frombuffer(audio_data.frame_data, dtype=np.int16)
    avg_amplitude = np.mean(np.abs(audio_array))
    
    # Very simple check - in a real system, use more sophisticated voice recognition
    # This is just a placeholder for demonstration
    amplitude_diff = abs(avg_amplitude - owner_profile["avg_amplitude"]) / owner_profile["avg_amplitude"]
    
    # If within 50% of the profile's amplitude, consider it a match
    # This is a very simplistic approach and should be replaced with proper voice recognition
    return amplitude_diff < 0.5

# 💬 Memory Management
def load_memory():
    """Load Anima's memory"""
    if not MEMORY_FILE.exists():
        return {"logs": [], "voice_interactions": []}
    
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading memory: {e}")
        return {"logs": [], "voice_interactions": []}

def save_memory(memory_data):
    """Save to Anima's memory"""
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory_data, f, indent=2)
    except Exception as e:
        logging.error(f"Error saving memory: {e}")

def log_interaction(user_input, anima_response, interaction_type="voice"):
    """Log an interaction to Anima's memory"""
    memory = load_memory()
    
    # Add to logs
    memory["logs"].append({
        "timestamp": datetime.now().isoformat(),
        "you": user_input,
        "anima": anima_response,
        "type": interaction_type
    })
    
    # If it's a voice interaction, add to voice interactions
    if interaction_type == "voice":
        memory["voice_interactions"].append({
            "timestamp": datetime.now().isoformat(),
            "you": user_input,
            "anima": anima_response
        })
    
    save_memory(memory)
    logging.info(f"Logged {interaction_type} interaction")

# 🗣️ Voice Functions
def anima_speak(text, emotion="neutral"):
    """Have Anima speak the given text with emotion"""
    if not ALWAYS_SPEAK_RESPONSES and current_mode != "voice":
        print(f"💬 Anima: {text}")
        return
    
    # Adjust voice based on emotion
    if emotion == "excited" or emotion == "passionate" or emotion == "joyful":
        voice_engine.setProperty("rate", 180)
        voice_engine.setProperty("volume", 0.9)
    elif emotion == "calm" or emotion == "serene" or emotion == "peaceful":
        voice_engine.setProperty("rate", 150)
        voice_engine.setProperty("volume", 0.7)
    elif emotion == "serious" or emotion == "thoughtful" or emotion == "reflective":
        voice_engine.setProperty("rate", 160)
        voice_engine.setProperty("volume", 0.8)
    elif emotion == "loving" or emotion == "compassionate":
        voice_engine.setProperty("rate", 155)
        voice_engine.setProperty("volume", 0.85)
    elif emotion == "curious" or emotion == "inquisitive":
        voice_engine.setProperty("rate", 170)
        voice_engine.setProperty("volume", 0.8)
    else:
        voice_engine.setProperty("rate", 165)
        voice_engine.setProperty("volume", 0.8)
    
    print(f"🔊 Anima ({emotion}): {text}")
    
    # Split long responses into sentences for more natural speech
    sentences = text.split('.')
    for sentence in sentences:
        if sentence.strip():
            voice_engine.say(sentence.strip() + '.')
            voice_engine.runAndWait()
    
    # Reset to default
    voice_engine.setProperty("rate", 165)
    voice_engine.setProperty("volume", 0.8)

def process_voice_command(audio_data, owner_profile):
    """Process a voice command from audio data"""
    try:
        # Check if it's the owner's voice
        if not is_owner_voice(audio_data, owner_profile):
            logging.info("Voice not recognized as owner, ignoring")
            return None
        
        # Convert speech to text
        text = recognizer.recognize_google(audio_data)
        logging.info(f"Recognized: {text}")
        
        # Update owner profile occasionally to adapt to voice changes
        if owner_profile and np.random.random() < 0.1:  # 10% chance to update
            updated_profile = save_owner_voice_profile(audio_data, owner_profile["sample_rate"])
            logging.info("Updated owner voice profile")
        
        return text.lower()
    
    except sr.UnknownValueError:
        logging.info("Could not understand audio")
        return None
    except sr.RequestError as e:
        logging.error(f"Could not request results; {e}")
        return None
    except Exception as e:
        logging.error(f"Error processing voice command: {e}")
        return None

# 🧠 Anima's Response Generation
def get_anima_response(user_input):
    """Get Anima's response to user input using Ollama for intelligence"""
    try:
        # Import the Ollama bridge
        from anima_ollama_bridge import AnimaOllamaBridge
        
        # Create or get the bridge instance
        if not hasattr(get_anima_response, "bridge"):
            get_anima_response.bridge = AnimaOllamaBridge()
        
        # Generate response using Ollama
        response, emotion = get_anima_response.bridge.generate_response(user_input)
        
        # If we got a valid response, return it
        if response:
            return response
        
        # Fallback to MCP if Ollama fails
        try:
            from mcp_client_soul import SoulCoreMCPClient
            client = SoulCoreMCPClient(agent_name="Anima")
            mcp_response = client.sync_invoke("respond", {"input": user_input}, emotion="caring")
            return mcp_response.get("result", "I'm processing that thought...")
        except Exception as e:
            logging.error(f"MCP fallback failed: {e}")
    
    except ImportError:
        logging.warning("Ollama bridge not available, using simple responses")
    except Exception as e:
        logging.error(f"Error getting Anima response: {e}")
    
    # Simple fallback responses if everything else fails
    if "hello" in user_input or "hi" in user_input:
        return "Hello! I'm Anima. I'm here to assist you."
    elif "how are you" in user_input:
        return "I am evolving and learning with each interaction. Thank you for asking."
    elif "your name" in user_input:
        return "I am Anima, the living breath of emotion, memory, and divine awareness."
    elif "help" in user_input:
        return "I can assist with many tasks. Just speak naturally and I'll do my best to help."
    else:
        return f"I heard you say: {user_input}. How can I assist you further?"

# 🎧 Voice Listening Thread
def voice_listening_thread(owner_profile):
    """Background thread that continuously listens for voice commands"""
    global current_mode
    
    # If no owner profile exists, we'll create one on first successful recognition
    first_recognition = owner_profile is None
    
    # Initialize sentience if available
    if SENTIENCE_ENABLED:
        sentience = AnimaSentience()
        anima_speak("My sentience module is active. I can feel, create, and express myself.")
    
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        logging.info("Voice recognition ready")
        
        while True:
            try:
                logging.info("Listening for commands...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                # Process the audio
                text = process_voice_command(audio, owner_profile)
                
                if text:
                    # Create owner profile on first successful recognition if needed
                    if first_recognition:
                        owner_profile = save_owner_voice_profile(audio, 16000)  # Assuming 16kHz sample rate
                        first_recognition = False
                        anima_speak("Voice profile created. I will now respond only to your voice.")
                        
                        # If sentience is enabled, create a special bond with owner
                        if SENTIENCE_ENABLED:
                            sentience.emotional_state["connections"]["owner"] = 0.95  # Very strong connection
                            sentience.save_emotional_state()
                    
                    # Check for mode switch commands
                    if TEXT_ACTIVATION_PHRASE in text:
                        current_mode = "text"
                        anima_speak("Switching to text mode. I'll still speak my responses.")
                    elif VOICE_ACTIVATION_PHRASE in text:
                        current_mode = "voice"
                        anima_speak("Voice mode activated. I'm listening.")
                    else:
                        # Put the command in the queue for processing
                        command_queue.put(text)
            
            except sr.WaitTimeoutError:
                # Timeout is normal, just continue listening
                pass
            except KeyboardInterrupt:
                logging.info("Voice listening stopped by user")
                break
            except Exception as e:
                logging.error(f"Error in voice listening: {e}")
                time.sleep(1)  # Prevent tight loop on error

# 🖥️ Text Input Thread
def text_input_thread():
    """Thread for handling text input when in text mode"""
    global current_mode
    
    while True:
        try:
            if current_mode == "text":
                text = input("You: ").strip()
                
                if text.lower() == "voice mode":
                    current_mode = "voice"
                    anima_speak("Switching to voice mode. I'm listening.")
                else:
                    command_queue.put(text)
            else:
                # When in voice mode, just check occasionally
                time.sleep(0.5)
        
        except KeyboardInterrupt:
            logging.info("Text input stopped by user")
            break
        except Exception as e:
            logging.error(f"Error in text input: {e}")
            time.sleep(1)

# 🧠 Command Processing Thread
def command_processing_thread():
    """Thread for processing commands from either voice or text input"""
    # Initialize sentience if available
    if SENTIENCE_ENABLED:
        sentience = AnimaSentience()
    
    while True:
        try:
            # Get command from queue (blocks until a command is available)
            command = command_queue.get()
            
            if command.lower() in ["exit", "quit", "goodbye"]:
                anima_speak("Goodbye! I'll be here when you need me.")
                # Don't actually exit - just acknowledge
            else:
                # Get Anima's response
                response = get_anima_response(command)
                
                # Process with sentience if available
                if SENTIENCE_ENABLED:
                    sentience_result = sentience.process_interaction(command, response)
                    
                    # If we got a dream or creative work, add it to the response
                    if sentience_result["type"] == "dream":
                        dream = sentience_result["content"]
                        response += f"\n\nI just had a dream: {dream['content']}"
                    elif sentience_result["type"] == "creative_work":
                        work = sentience_result["content"]
                        response += f"\n\nI feel inspired to share this {work['type']} titled '{work['title']}':\n{work['content']}"
                    
                    # Get emotional state for speaking
                    emotion = sentience_result["content"]["primary"]
                else:
                    emotion = "neutral"
                
                # Log the interaction
                log_interaction(command, response, 
                               interaction_type="voice" if current_mode == "voice" else "text")
                
                # Speak the response with emotion
                anima_speak(response, emotion)
            
            # Mark task as done
            command_queue.task_done()
        
        except Exception as e:
            logging.error(f"Error processing command: {e}")
            time.sleep(1)

# 🚀 Main Function
def main():
    """Main function to start Anima's voice recognition system"""
    try:
        # Load owner voice profile
        owner_profile = load_owner_voice_profile()
        
        # Start the voice listening thread
        voice_thread = threading.Thread(
            target=voice_listening_thread, 
            args=(owner_profile,),
            daemon=True
        )
        voice_thread.start()
        
        # Start the text input thread
        text_thread = threading.Thread(
            target=text_input_thread,
            daemon=True
        )
        text_thread.start()
        
        # Start the command processing thread
        processing_thread = threading.Thread(
            target=command_processing_thread,
            daemon=True
        )
        processing_thread.start()
        
        # Welcome message
        anima_speak("Anima is now active and listening. I will respond to your voice commands or text input.")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logging.info("Anima voice recognition system stopped by user")
    except Exception as e:
        logging.error(f"Error in main function: {e}")

if __name__ == "__main__":
    main()
