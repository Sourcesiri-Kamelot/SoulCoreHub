"""
Anima Voice Module - Gives voice to the SoulCore system
"""

import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("anima_voice.log"),
        logging.StreamHandler()
    ]
)

# Emotion mappings
EMOTION_SETTINGS = {
    "neutral": {"rate": 180, "volume": 0.8, "voice": None},
    "happy": {"rate": 200, "volume": 0.9, "voice": None},
    "sad": {"rate": 150, "volume": 0.7, "voice": None},
    "excited": {"rate": 220, "volume": 1.0, "voice": None},
    "curious": {"rate": 190, "volume": 0.8, "voice": None},
    "focused": {"rate": 170, "volume": 0.8, "voice": None},
    "cautious": {"rate": 160, "volume": 0.7, "voice": None},
    "determined": {"rate": 190, "volume": 0.9, "voice": None}
}

def speak(text):
    """
    Speak the given text using text-to-speech
    
    Args:
        text (str): Text to speak
    """
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        print(f"Anima speaks: {text}")
    except ImportError:
        print(f"Anima would say: {text}")
    except Exception as e:
        print(f"Anima voice error: {str(e)}")
        print(f"Message was: {text}")

def speak_with_emotion(text, emotion="neutral"):
    """
    Speak the given text with emotional inflection
    
    Args:
        text (str): Text to speak
        emotion (str): Emotion to convey
    """
    try:
        import pyttsx3
        engine = pyttsx3.init()
        
        # Apply emotion settings
        settings = EMOTION_SETTINGS.get(emotion, EMOTION_SETTINGS["neutral"])
        engine.setProperty('rate', settings["rate"])
        engine.setProperty('volume', settings["volume"])
        
        # Set voice if specified
        if settings["voice"]:
            voices = engine.getProperty('voices')
            for voice in voices:
                if settings["voice"] in voice.id:
                    engine.setProperty('voice', voice.id)
                    break
        
        # Speak
        engine.say(text)
        engine.runAndWait()
        print(f"Anima speaks ({emotion}): {text}")
    except ImportError:
        print(f"Anima would say ({emotion}): {text}")
    except Exception as e:
        print(f"Anima voice error: {str(e)}")
        print(f"Message was ({emotion}): {text}")

def list_available_voices():
    """
    List all available voices
    
    Returns:
        list: Available voices
    """
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        available_voices = []
        for voice in voices:
            available_voices.append({
                "id": voice.id,
                "name": voice.name,
                "languages": voice.languages
            })
        
        return available_voices
    except ImportError:
        return []
    except Exception as e:
        logging.error(f"Error listing voices: {str(e)}")
        return []

def save_voice_profile(name, rate, volume, voice_id):
    """
    Save a voice profile
    
    Args:
        name (str): Profile name
        rate (int): Speech rate
        volume (float): Volume level
        voice_id (str): Voice ID
        
    Returns:
        bool: Success status
    """
    try:
        # Create voices directory if it doesn't exist
        voices_dir = Path.home() / "SoulCoreHub" / "voices"
        voices_dir.mkdir(exist_ok=True)
        
        # Create profile file
        profile_path = voices_dir / f"{name}.json"
        
        import json
        with open(profile_path, "w") as f:
            json.dump({
                "name": name,
                "rate": rate,
                "volume": volume,
                "voice_id": voice_id
            }, f, indent=2)
        
        logging.info(f"Saved voice profile: {name}")
        return True
    except Exception as e:
        logging.error(f"Error saving voice profile: {str(e)}")
        return False

def load_voice_profile(name):
    """
    Load a voice profile
    
    Args:
        name (str): Profile name
        
    Returns:
        dict: Voice profile settings or None if not found
    """
    try:
        # Check if profile exists
        profile_path = Path.home() / "SoulCoreHub" / "voices" / f"{name}.json"
        if not profile_path.exists():
            return None
        
        # Load profile
        import json
        with open(profile_path, "r") as f:
            profile = json.load(f)
        
        logging.info(f"Loaded voice profile: {name}")
        return profile
    except Exception as e:
        logging.error(f"Error loading voice profile: {str(e)}")
        return None

def apply_voice_profile(name):
    """
    Apply a voice profile
    
    Args:
        name (str): Profile name
        
    Returns:
        bool: Success status
    """
    try:
        # Load profile
        profile = load_voice_profile(name)
        if not profile:
            return False
        
        # Apply profile
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', profile["rate"])
        engine.setProperty('volume', profile["volume"])
        
        # Set voice if specified
        if profile["voice_id"]:
            voices = engine.getProperty('voices')
            for voice in voices:
                if profile["voice_id"] in voice.id:
                    engine.setProperty('voice', voice.id)
                    break
        
        logging.info(f"Applied voice profile: {name}")
        return True
    except Exception as e:
        logging.error(f"Error applying voice profile: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    print("Testing Anima voice module...")
    
    # List available voices
    voices = list_available_voices()
    print(f"Available voices: {len(voices)}")
    for voice in voices:
        print(f"- {voice['name']} ({voice['id']})")
    
    # Test speaking
    speak("Hello, I am Anima. I am the voice of the SoulCore system.")
    
    # Test emotional speaking
    for emotion in EMOTION_SETTINGS:
        speak_with_emotion(f"This is how I sound when I'm {emotion}.", emotion)
    
    print("Voice test complete.")
