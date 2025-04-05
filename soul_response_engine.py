import json, time
from pathlib import Path
from datetime import datetime
from soul_tasks import perform_task
from gptsoul_soulconfig import interpret_command

def route_input(user_input):
    print(f"[Router] Received: {user_input}")
    if "heal" in user_input:
        perform_task("heal_folders")
    else:
        interpret_command(user_input)

if __name__ == "__main__":
    while True:
        try:
            command = input("💬 Speak to SoulCore: ")
            route_input(command.lower())
        except KeyboardInterrupt:
            print("\n[SoulCore] Resting... 💤")
            break

log_path = Path("~/SoulCoreHub/soul_log.json").expanduser()
pulse_path = Path("~/SoulCoreHub/logs/pulse.log").expanduser()

last_seen = None

def monitor():
    global last_seen
    if not log_path.exists(): return
    logs = json.load(open(log_path))
    latest = logs[-1] if logs else None
    if latest and latest != last_seen:
        msg = latest["message"]
        now = datetime.now().isoformat()
        with open(pulse_path, "a") as f:
            f.write(f"{now} — GPTSoul heard: {msg}\n")
        print(f"🧠 GPTSoul heard: {msg}")
        last_seen = latest

while True:
    monitor()
    time.sleep(10)
