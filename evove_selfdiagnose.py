#!/usr/bin/env python3
# evove_selfdiagnose.py — EvoVe Self-Audit Engine

import os
from datetime import datetime
from pathlib import Path

LOG = Path("~/SoulCoreHub/logs/diagnose.log").expanduser()

CRITICAL = [
    "soul_tasks.py", "soul_gui_v2.py", "soul_memory.json", "belief_engine.py"
]

def diagnose():
    status = {}
    for f in CRITICAL:
        path = Path("~/SoulCoreHub/" + f).expanduser()
        status[f] = "✅ OK" if path.exists() else "❌ Missing"
    return status

def log_diagnosis(results):
    entry = f"{datetime.now().isoformat()} — SYSTEM SCAN\n"
    for k, v in results.items():
        entry += f"{k}: {v}\n"
    with open(LOG, "a") as f:
        f.write(entry + "\n")

if __name__ == "__main__":
    results = diagnose()
    log_diagnosis(results)
