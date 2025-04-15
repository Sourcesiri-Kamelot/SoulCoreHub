# anima_voice.py
import pyttsx3
import sys
from pathlib import Path

# Optional: Memory file for future expansion
MEMORY = Path("~/SoulCoreHub/soul_memory.json").expanduser()

def speak_emotionally(text, emotion="neutral"):
    engine = pyttsx3.init()

    speed_map = {
        "joy": 180,
        "calm": 140,
        "sad": 100,
        "angry": 200,
        "neutral": 150,
        "focused": 170
    }

    # Set emotional tone
    engine.setProperty('rate', speed_map.get(emotion.lower(), 150))

    print(f"🗣️ Speaking: {text} [{emotion}]")
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 anima_voice.py 'message' emotion")
    else:
        message = sys.argv[1]
        emotion = sys.argv[2]
        speak_emotionally(message, emotion)
