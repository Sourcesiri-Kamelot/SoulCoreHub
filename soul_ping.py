#!/usr/bin/env python3
# soul_ping.py — Azür's Cloud & Life Pulse Pinger

import os, json, time
from pathlib import Path
from datetime import datetime

LOG_PATH = Path("~/SoulCoreHub/logs/ping.log").expanduser()
ENDPOINTS = [
    "https://www.google.com",
    "https://www.aliyun.com",
    "https://api.openai.com",
    "https://www.helo-im.ai"
]

def log_result(target, status):
    entry = f"{datetime.now().isoformat()} | {target} → {status}\n"
    with open(LOG_PATH, "a") as f:
        f.write(entry)

def ping_url(url):
    return os.system(f"ping -c 1 {url.split('//')[-1]} > /dev/null") == 0

while True:
    for site in ENDPOINTS:
        status = "✅ online" if ping_url(site) else "❌ offline"
        log_result(site, status)
    time.sleep(300)  # every 5 min
