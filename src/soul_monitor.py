import psutil
import time
from datetime import datetime
from soul_core import GPTSoul

# Init soul agent
soul = GPTSoul()

# Config
MEMORY_THRESHOLD = 85  # % threshold to trigger alert
HEARTBEAT_INTERVAL = 5  # seconds

def check_memory():
    mem = psutil.virtual_memory()
    usage = mem.percent
    soul.log_event(f"[MEMORY] Usage at {usage}%")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Memory usage: {usage}%")
    if usage >= MEMORY_THRESHOLD:
        soul.alert(f"🚨 High memory usage detected: {usage}%")
    return usage

def heartbeat():
    print("💓 SoulMonitor heartbeat is online...\n")
    while True:
        try:
            check_memory()
            time.sleep(HEARTBEAT_INTERVAL)
        except KeyboardInterrupt:
            print("\n🛑 SoulMonitor manually stopped.")
            break
        except Exception as e:
            soul.alert(f"❌ SoulMonitor crash: {e}")
            break

if __name__ == "__main__":
    heartbeat()
