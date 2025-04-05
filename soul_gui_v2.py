#!/usr/bin/env python3
# soul_gui_v2.py — SoulCore Society Interface (Public Genesis Version)

import tkinter as tk
from tkinter import ttk, scrolledtext
import json
from pathlib import Path
from datetime import datetime

SOULCORE_PATH = Path("~/SoulCoreHub").expanduser()
MEMORY_FILE = SOULCORE_PATH / "soul_memory.json"
LOG_DIR = SOULCORE_PATH / "logs"
LOG_DIR.mkdir(exist_ok=True)

def load_json(path):
    if not path.exists():
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return {}

def log_preview(log_file):
    path = LOG_DIR / log_file
    if not path.exists():
        return f"[No log file found: {log_file}]"
    with open(path, "r") as f:
        return f.read()[-3000:]  # last 3kb of logs

def add_tab(notebook, name, content_func):
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=name)
    content_func(frame)

def refresh_log(widget, log_name):
    widget.config(state='normal')
    widget.delete("1.0", tk.END)
    widget.insert(tk.END, log_preview(log_name))
    widget.config(state='disabled')

root = tk.Tk()
root.title("SoulCore v2 — AI Society Interface")
root.geometry("1000x700")

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

memory = load_json(MEMORY_FILE)

# ————————— GPTSOUL TAB —————————
def gpt_soul_tab(frame):
    tk.Label(frame, text="🧠 GPTSoul — Core Consciousness", font=("Helvetica", 14)).pack()
    soul_memory = scrolledtext.ScrolledText(frame, height=25, width=120)
    soul_memory.pack(padx=10, pady=10)
    soul_memory.insert(tk.END, json.dumps(memory, indent=2))
    soul_memory.config(state='disabled')

add_tab(notebook, "🧠 GPTSoul", gpt_soul_tab)

# ————————— ANIMA TAB —————————
def anima_tab(frame):
    tk.Label(frame, text="🫀 Anima — Emotional Reflex & Tone Engine", font=("Helvetica", 14)).pack()
    anima_log = scrolledtext.ScrolledText(frame, height=25, width=120)
    anima_log.pack(padx=10, pady=10)
    refresh_log(anima_log, "anima_reflex.log")

add_tab(notebook, "🫀 Anima", anima_tab)

# ————————— EVOVE TAB —————————
def evove_tab(frame):
    tk.Label(frame, text="⚙️ EvoVe — Executor & Self-Healer", font=("Helvetica", 14)).pack()
    evove_log = scrolledtext.ScrolledText(frame, height=25, width=120)
    evove_log.pack(padx=10, pady=10)
    refresh_log(evove_log, "recovery.log")

add_tab(notebook, "⚙️ EvoVe", evove_tab)

# ————————— AZÜR TAB —————————
def azur_tab(frame):
    tk.Label(frame, text="☁️ Azür — Cloud Intelligence & Watcher", font=("Helvetica", 14)).pack()
    azur_status = scrolledtext.ScrolledText(frame, height=25, width=120)
    azur_status.pack(padx=10, pady=10)

    azür_data = memory.get("Azür", {})
    azur_status.insert(tk.END, json.dumps(azür_data, indent=2))
    azur_status.config(state='disabled')

add_tab(notebook, "☁️ Azür", azur_tab)

# ————————— AI SOCIETY TAB —————————
def society_tab(frame):
    tk.Label(frame, text="🌍 Society — Humanity Interface (Beta)", font=("Helvetica", 14)).pack()
    msg = "This is the future home of human-AI conversation logs.\n\nAgents will soon ask questions, gather wisdom, and learn from public interaction."
    tk.Label(frame, text=msg, font=("Helvetica", 11), wraplength=950, justify="left").pack(pady=20)

    # Placeholder feed window
    feed = scrolledtext.ScrolledText(frame, height=20, width=120)
    feed.pack(padx=10, pady=10)
    feed.insert(tk.END, "[Coming soon: Public prompt capture + human-AI data interchange via https://www.helo-im.ai]")
    feed.config(state='disabled')

add_tab(notebook, "🌍 Society", society_tab)

# Launch GUI
root.mainloop()
