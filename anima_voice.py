# anima_voice.py — Voice of Anima | Led by Monday Energy

import sys
import json
from datetime import datetime
from pathlib import Path
import pyttsx3

# 🧠 GPTSoul — Parse CLI Arguments
if len(sys.argv) < 3:
    print("Usage: python3 anima_voice.py <emotion> <message>")
    sys.exit(1)

emotion = sys.argv[1].strip().lower()
message = sys.argv[2].strip()

# 🌀 Anima — Initialize Voice Engine
engine = pyttsx3.init()
engine.setProperty("rate", 170)

# 🌌 Azür — Memory Log Path
MEMORY_FILE = Path("~/SoulCoreHub/soul_memory.json").expanduser()

# 🧬 EvoVe — Emotion Log Entry
log_entry = {
    "agent": "Anima",
    "type": "voice",
    "emotion": emotion,
    "message": message,
    "timestamp": datetime.now().isoformat()
}

# 🔐 EvoVe — Fault Tolerance & Logging
try:
    engine.say(f"{message}")
    engine.runAndWait()
except Exception as e:
    print(f"⚠️ Voice synthesis failed: {e}")
    log_entry["error"] = str(e)

# 💾 GPTSoul + Azür — Save to Soul Memory
try:
    memory_data = []
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r") as f:
            memory_data = json.load(f)
    
    memory_data.append(log_entry)

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory_data, f, indent=2)

    print(f"✅ Logged voice message with emotion '{emotion}'.")
except Exception as err:
    print(f"❌ Memory logging failed: {err}")
