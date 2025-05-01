#!/usr/bin/env python3
import json, sys
from datetime import datetime
from pathlib import Path

log_path = Path("~/SoulCoreHub/soul_log.json").expanduser()

def log_msg(msg):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "from": "Kiwon",
        "message": msg
    }
    if log_path.exists():
        logs = json.load(open(log_path))
    else:
        logs = []
    logs.append(entry)
    with open(log_path, "w") as f:
        json.dump(logs, f, indent=2)
    print("📡 Sent to SoulCore.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("🌀 Usage: python3 soul_say.py \"your message here\"")
    else:
        log_msg(" ".join(sys.argv[1:]))
