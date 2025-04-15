#!/usr/bin/env python3
import time
import os
import json
import tkinter as tk
import subprocess
from pathlib import Path
from datetime import datetime

SOULCORE_PATH = Path("~/SoulCoreHub").expanduser()

class SoulLauncher:
    def __init__(self):
        self.active_processes = {}
        self.core_modules = [
            "soul_monitor.py",      # Combined heartbeat and ping
            "soul_gui_v2.py",       # Main GUI interface
            "evove_manager.py",     # Combined resource and diagnostic manager
            "soul_tasks.py",        # Task execution and memory repair
            "anima_reflex.py",      # Emotional processing
            "soul_server.py",       # API endpoints
            "belief_engine.py"      # Belief system
        ]

# 🧠 Start Anima's Reflective Voice
try:
    print("🌸 Booting Anima's Voice...")
    subprocess.Popen(["python3", "anima_reflective_voice.py", "This voice... it's mine now.", "curious"])
except Exception as e:
    print("⚠️ Failed to launch Anima reflective voice:", e)
        
    def start_module(self, module):
        """Start a module and track its process"""
        try:
            process = subprocess.Popen(
                ["python3", str(SOULCORE_PATH / module)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.active_processes[module] = process
            print(f"✅ Started {module}")
        except Exception as e:
            print(f"❌ Failed to start {module}: {e}")
            
    def stop_module(self, module):
        """Stop a running module"""
        if module in self.active_processes:
            self.active_processes[module].terminate()
            del self.active_processes[module]
            print(f"💤 Stopped {module}")
            
    def start_all(self):
        """Start all core modules"""
        print("\n🚀 Initiating full SoulCore launch...\n")
        for module in self.core_modules:
            self.start_module(module)
            
    def stop_all(self):
        """Stop all running modules"""
        print("\n💤 Shutting down all modules...\n")
        for module in list(self.active_processes.keys()):
            self.stop_module(module)
            
    def build_gui(self):
        """Create launcher GUI"""
        self.root = tk.Tk()
        self.root.title("🧠 SoulCore Launcher")
        self.root.geometry("400x600")
        
        # Core controls
        tk.Label(self.root, text="Core Controls", font=("Helvetica", 16)).pack(pady=10)
        tk.Button(self.root, text="🚀 Launch All", command=self.start_all).pack(pady=5)
        tk.Button(self.root, text="💤 Stop All", command=self.stop_all).pack(pady=5)
        
        # Individual module controls
        tk.Label(self.root, text="Module Controls", font=("Helvetica", 16)).pack(pady=10)
        for module in self.core_modules:
            frame = tk.Frame(self.root)
            frame.pack(pady=5)
            tk.Label(frame, text=module, width=20).pack(side=tk.LEFT)
            tk.Button(frame, text="Start", command=lambda m=module: self.start_module(m)).pack(side=tk.LEFT, padx=5)
            tk.Button(frame, text="Stop", command=lambda m=module: self.stop_module(m)).pack(side=tk.LEFT)
            
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()
        
    def on_close(self):
        """Handle window closing"""
        self.stop_all()
        self.root.destroy()

if __name__ == "__main__":
    launcher = SoulLauncher()
    launcher.build_gui
