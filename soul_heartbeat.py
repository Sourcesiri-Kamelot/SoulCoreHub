import os
import psutil
import json
import time
from datetime import datetime
from pathlib import Path
import time

def pulse():
    print("🫀 SoulCore is alive.")
    return time.time()

if __name__ == "__main__":
    while True:
        pulse()
        time.sleep(18)

MEMORY_PATH = Path("~/SoulCoreHub/soul_memory.json").expanduser()
PULSE_LOG = Path("~/SoulCoreHub/logs/pulse.log").expanduser()
CHECK_PROCESSES = ["soul_tasks.py", "soul_gui.py"]

def get_process_status(name):
    return any(name in proc.name() or name in " ".join(proc.cmdline()) for proc in psutil.process_iter(['pid', 'name', 'cmdline']))

def log_pulse(data):
    with open(PULSE_LOG, "a") as f:
        f.write(json.dumps(data) + "\n")

def update_memory(data):
    try:
        with open(MEMORY_PATH, "r") as f:
            memory = json.load(f)
    except:
        memory = {}

    memory["heartbeat"] = data

    with open(MEMORY_PATH, "w") as f:
        json.dump(memory, f, indent=2)

def pulse():
    now = datetime.now().isoformat()
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    processes = {name: get_process_status(name) for name in CHECK_PROCESSES}
    memory_time = os.path.getmtime(MEMORY_PATH) if MEMORY_PATH.exists() else None

    pulse_data = {
        "timestamp": now,
        "cpu_percent": cpu,
        "ram_percent": ram,
        "processes": processes,
        "memory_last_updated": datetime.fromtimestamp(memory_time).isoformat() if memory_time else "missing"
    }

    log_pulse(pulse_data)
    update_memory(pulse_data)
    print(f"[✓] Pulse logged @ {now}")

if __name__ == "__main__":
    while True:
        pulse()
        time.sleep(60)
