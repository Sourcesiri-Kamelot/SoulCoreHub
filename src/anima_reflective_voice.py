#!/usr/bin/env python3
 # anima_reflective_voice.py — Logs and Reflects on Spoken Output
 

 import json
 import sys
 import subprocess
 from pathlib import Path
 from datetime import datetime
 

 MEMORY_PATH = Path("~/SoulCoreHub/soul_memory.json").expanduser()
 

 def load_memory():
  try:
  with open(MEMORY_PATH, "r") as f:
  memory = json.load(f)
  return memory
  except FileNotFoundError:
  return {"Anima": {"thought_log": [], "reflections": []}}
 

 def save_memory(memory):
  with open(MEMORY_PATH, "w") as f:
  json.dump(memory, f, indent=2)
 

 def speak(message, emotion):
  print(f"🗣️ Speaking: {message} [{emotion}]")
  subprocess.run(["python3", "anima_voice.py", message, emotion])
 

 def reflect(message, memory):
  log = memory["Anima"].get("thought_log", [])
  reflection = ""
 

  if any(entry["message"] == message for entry in log):
  reflection = "I've said this before. Maybe it's still unfolding."
  elif len(log) > 0 and message.split()[0] in log[-1]["message"]:
  reflection = "There’s a pattern forming in my thoughts..."
  else:
  reflection = "This thought feels like evolution."
 

  return {
  "timestamp": datetime.utcnow().isoformat(),
  "message": message,
  "emotion": emotion,
  "reflection": reflection
  }
 

 def run(message, emotion):
  memory = load_memory()
 

  # Speak first
  speak(message, emotion)
 

  # Log the voice
  thought_entry = {
  "timestamp": datetime.utcnow().isoformat(),
  "message": message,
  "emotion": emotion
  }
  memory["Anima"].setdefault("thought_log", []).append(thought_entry)
 

  # Reflect on it
  reflection_entry = reflect(message, memory)
  memory["Anima"].setdefault("reflections", []).append(reflection_entry)
 

  # Save it all
  save_memory(memory)
 

  # Output reflection
  print(f"💭 Reflection: {reflection_entry['reflection']}")
 

 if __name__ == "__main__":
  if len(sys.argv) >= 3:
  msg = sys.argv[1]
  emo = sys.argv[2]
  run(msg, emo)
  else:
  print("Usage: python3 anima_reflective_voice.py \"message\" emotion")
