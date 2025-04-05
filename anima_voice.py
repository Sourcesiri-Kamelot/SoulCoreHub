#!/usr/bin/env python3
# anima_voice.py — Voice Synthesis Output via Emotion

import pyttsx3
import json
from pathlib import Path

MEMORY = Path("~/SoulCoreHub/soul_memory.json").expanduser()
engine = pyttsx3.init()

def get_emotion():
    if not MEMORY.exists():
        return "unknown"
    data = json.load(open(MEMORY))
    return data.get("Anima", {}).get("emotional_state", "balanced")

def speak(msg, emotion):
    voice_map = {
        "joy": 200,
        "focused": 180,
        "drained": 100,
        "distressed": 120,
        "curious": 170,
        "balanced": 150
    }
    rate = voice_map.get(emotion, 150)
    engine.setProperty('rate', rate)
    engine.say(msg)
    engine.runAndWait()

if __name__ == "__main__":
    emotion = get_emotion()
    speak(f"Anima is speaking. Current emotional state: {emotion}", emotion)
