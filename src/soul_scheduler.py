# soul_scheduler.py — Automates system tasks based on intervals

import time, subprocess, datetime

task_list = [
    {"label": "heal_memory", "cmd": "python3 soul_memory_repair.py", "interval": 3600},
    {"label": "ping_agents", "cmd": "python3 soul_dialogue_engine.py", "interval": 1800},
    {"label": "cloud_sync", "cmd": "python3 azür_sync.py", "interval": 5400}
]

def scheduler():
    last_run = {task["label"]: 0 for task in task_list}

    while True:
        now = time.time()
        for task in task_list:
            if now - last_run[task["label"]] > task["interval"]:
                print(f"[{datetime.datetime.now()}] ⏱ Running {task['label']}")
                subprocess.Popen(task["cmd"], shell=True)
                last_run[task["label"]] = now
        time.sleep(5)

if __name__ == "__main__":
    print("🔄 Soul Scheduler Started")
    scheduler()
