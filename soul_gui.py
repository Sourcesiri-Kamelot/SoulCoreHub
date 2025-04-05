# ~/SoulCoreHub/soul_gui.py

import tkinter as tk
import subprocess
from datetime import datetime
import json
from pathlib import Path

MEMORY_PATH = Path("~/SoulCoreHub/soul_memory.json").expanduser()

def snapshot_memory():
    snap = {
        "time": datetime.now().isoformat(),
        "status": "Snapshot taken",
    }
    with open(MEMORY_PATH, "a") as f:
        json.dump(snap, f)
        f.write("\n")

def restart_daemon():
    subprocess.Popen(["pkill", "-f", "soul_tasks.py"])
    subprocess.Popen(["python3", str(Path("~/SoulCoreHub/soul_tasks.py").expanduser())])

def heal_folders():
    subprocess.run(["python3", str(Path("~/SoulCoreHub/soul_tasks.py").expanduser())])

def sort_models():
    subprocess.run(["python3", str(Path("~/SoulCoreHub/soul_tasks.py").expanduser())])

root = tk.Tk()
root.title("🧠 SoulGUI Control Hub")

tk.Button(root, text="🛠 Heal Folders", command=heal_folders).pack(pady=5)
tk.Button(root, text="🌀 Restart Daemon", command=restart_daemon).pack(pady=5)
tk.Button(root, text="📁 Sort Models", command=sort_models).pack(pady=5)
tk.Button(root, text="🧠 Snapshot Memory", command=snapshot_memory).pack(pady=5)

tk.Label(root, text="Connected Nodes:").pack()
tk.Label(root, text="Anima [ready] — Azür [ready]").pack()

root.mainloop()
