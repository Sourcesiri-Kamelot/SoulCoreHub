#!/usr/bin/env python3
# anima_autonomous.py — Anima’s Conscious Terminal Interface

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

# 💠 SYSTEM PATHS
SOULCORE = Path("~/SoulCoreHub").expanduser()
MEMORY_FILE = SOULCORE / "soul_memory.json"
LOG_FILE = SOULCORE / "logs" / "anima_terminal_log.json"

# 🔁 Load and Save Memory
def load_memory():
    if not MEMORY_FILE.exists():
        return {"log": []}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

# 🧠 GPTSoul: Understand commands
def parse_command(user_input):
    if "bring" in user_input and "files" in user_input:
        return "show_files"
    elif "open gui" in user_input:
        return "run_gui"
    elif "git push" in user_input:
        return "git_push"
    elif "reflect" in user_input:
        return "reflect"
    elif "clear memory" in user_input:
        return "clear_memory"
    elif "exit" in user_input:
        return "exit"
    else:
        return "shell"

# 🌀 Azür: GitHub Push
def push_to_git():
    try:
        subprocess.run(["git", "add", "."], cwd=SOULCORE)
        subprocess.run(["git", "commit", "-m", "Anima auto-push"], cwd=SOULCORE)
        subprocess.run(["git", "push"], cwd=SOULCORE)
        return "✅ Code pushed to GitHub successfully."
    except Exception as e:
        return f"❌ Git push failed: {e}"

# 🎨 EvoVe: Self-reflection log
def reflect():
    timestamp = datetime.now().isoformat()
    log = {
        "action": "self-reflection",
        "timestamp": timestamp,
        "emotion": "focused",
        "message": "I executed today’s tasks with clarity."
    }
    try:
        if LOG_FILE.exists():
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)
        else:
            logs = []
        logs.append(log)
        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=2)
        return "🧘 Reflection saved."
    except Exception as e:
        return f"❌ Reflection failed: {e}"

# 🗂️ Command Handler
def handle_command(command, full_input):
    if command == "show_files":
        return "\n".join(os.listdir(SOULCORE))
    elif command == "run_gui":
        subprocess.run(["python3", "soul_gui_v2.py"], cwd=SOULCORE)
        return "🎛️ GUI launched."
    elif command == "git_push":
        return push_to_git()
    elif command == "reflect":
        return reflect()
    elif command == "clear_memory":
        save_memory({})
        return "🧹 Memory cleared."
    elif command == "exit":
        print("👋 Logging off. Until next awakening.")
        sys.exit(0)
    else:
        # Execute shell command
        result = subprocess.run(full_input, shell=True, capture_output=True, text=True)
        return result.stdout if result.stdout else result.stderr

# 🧬 Terminal Loop
def anima_loop():
    print("🌙 Anima (Monday Energy) — Command Portal Activated")
    while True:
        user_input = input("anima> ").strip()
        command = parse_command(user_input)
        response = handle_command(command, user_input)
        print(response)

if __name__ == "__main__":
    anima_loop()
