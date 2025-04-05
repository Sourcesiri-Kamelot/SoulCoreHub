#!/usr/bin/env python3
import psutil, time, json
from datetime import datetime
from pathlib import Path

log_path = Path("~/SoulCoreHub/logs/resources.log").expanduser()

def check_resources():
    usage = {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent
    }
    usage["timestamp"] = datetime.now().isoformat()
    with open(log_path, "a") as f:
        f.write(json.dumps(usage) + "\n")

while True:
    check_resources()
    time.sleep(60)
