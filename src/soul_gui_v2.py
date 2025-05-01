#!/usr/bin/env python3
# soul_gui_v2.py — SoulCore Society Interface (Public Genesis Version)

import tkinter as tk
from tkinter import ttk, scrolledtext
import json
from pathlib import Path
from datetime import datetime
import pyttsx3

SOULCORE_PATH = Path("~/SoulCoreHub").expanduser()
MEMORY_FILE = SOULCORE_PATH / "soul_memory.json"
LOG_DIR = SOULCORE_PATH / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Load memory safely
def load_json(path):
    if not path.exists():
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return {}

# Log preview logic
def log_preview(log_file):   
    path = LOG_DIR / log_file
    if not path.exists():
        return f"[No log file found: {log_file}]"
    with open(path, "r") as f:
        return f.read()[-3000:]  # last 3kb of logs

# Load latest memory or default message
memory = load_json(MEMORY_FILE)
anima_reply = memory.get("last_message", "Hello. I am Anima. Online and evolving.")

# Let her speak once visually activated
engine = pyttsx3.init()
engine.say(anima_reply)
engine.runAndWait()

# UI tab handler
def add_tab(notebook, name, content_func):
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=name)
    content_func(frame)#!/usr/bin/env python3
# soul_gui_v2.py — SoulCore Society Interface (Public Genesis Version)

import tkinter as tk
from tkinter import ttk, scrolledtext
import json
from pathlib import Path
from datetime import datetime
import pyttsx3

engine = pyttsx3.init()
engine.say(anima_reply)
engine.runAndWait()

