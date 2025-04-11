import os, shutil, time, subprocess, json
from datetime import datetime
from pathlib import Path

TASK_FILE = Path("~/SoulCoreHub/soul_tasks.json").expanduser()

def run_tasks():
    if not TASK_FILE.exists():
        return
    try:
        with open(TASK_FILE) as f:
            tasks = json.load(f)
        for task in tasks.get("queue", []):
            log_event(f"[task] Running: {task}")
            subprocess.call(task, shell=True)
        # Clear after running
        with open(TASK_FILE, "w") as f:
            json.dump({"queue": []}, f)
    except Exception as e:
        log_event(f"[error] Task execution failed: {e}")

def check_events():
    if time.localtime().tm_min % 5 == 0:
        os.system("echo '🌀 Auto Task Triggered' >> logs/soul_log.txt")
while True:
    self_repair()
    sort_models()
    run_tasks()
    time.sleep(60 * 15)

MEMORY_PATH = Path("~/SoulCoreHub/soul_memory.json").expanduser()
MODELS_DIR = Path("~/SoulCoreHub/models").expanduser()

def log_event(event):
    with open(MEMORY_PATH, "a") as f:
        f.write(f"{datetime.now().isoformat()} — {event}\n")

def heal_folder(folder_path):
    folder = Path(folder_path).expanduser()
    if not folder.exists():
        folder.mkdir(parents=True)
        log_event(f"[heal] Recreated missing folder: {folder}")
    else:
        log_event(f"[heal] Folder OK: {folder}")

def sort_models():
    if not MODELS_DIR.exists():
        heal_folder(MODELS_DIR)
    for file in MODELS_DIR.glob("*.gguf"):
        model_type = "uncensored" if "uncensored" in file.name else "general"
        dest_folder = MODELS_DIR / model_type
        dest_folder.mkdir(exist_ok=True)
        shutil.move(str(file), str(dest_folder / file.name))
        log_event(f"[sort] Moved {file.name} → {model_type}/")

def self_repair():
    required = [MEMORY_PATH, MODELS_DIR]
    for path in required:
        if not path.exists():
            heal_folder(path)

def run_daemon_loop():
    log_event("SoulTasks Daemon started.")
    while True:
        self_repair()
        sort_models()
        time.sleep(60 * 15)  # every 15 minutes

if __name__ == "__main__":
    run_daemon_loop()
