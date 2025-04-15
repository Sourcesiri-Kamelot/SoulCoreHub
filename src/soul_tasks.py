import os, shutil, time, subprocess, json
from datetime import datetime
from pathlib import Path

SOULCORE_PATH = Path("~/SoulCoreHub").expanduser()
MEMORY_PATH = SOULCORE_PATH / "soul_memory.json"
BACKUP_PATH = SOULCORE_PATH / "backups/soul_memory_backup.json"
TASK_FILE = SOULCORE_PATH / "soul_tasks.json"
LOG_DIR = SOULCORE_PATH / "logs"

# Memory schema for repair operations
MEMORY_SCHEMA = {
    "GPTSoul": {"reasoning_stack": []},
    "EvoVe": {"task_queue": []},
    "Anima": {"emotional_state": "balanced"},
    "Azür": {"cloud_status": "idle"},
    "last_user_expression": "",
    "beliefs": {},
    "logs": []
}

def ensure_directories():
    """Create necessary directories"""
    LOG_DIR.mkdir(exist_ok=True)
    BACKUP_PATH.parent.mkdir(exist_ok=True)

def log_event(event):
    """Log an event to the task log"""
    timestamp = datetime.now().isoformat()
    with open(LOG_DIR / "tasks.log", "a") as f:
        f.write(f"{timestamp} - ⚙️ {event}\n")

def heal_memory():
    """Repair or initialize soul memory if corrupted"""
    try:
        # Backup existing memory if it exists
        if MEMORY_PATH.exists():
            shutil.copy(MEMORY_PATH, BACKUP_PATH)
            log_event("Memory backup created")
            
        # Try to load existing memory
        try:
            with open(MEMORY_PATH) as f:
                memory = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            memory = MEMORY_SCHEMA.copy()
            
        # Ensure all required fields exist
        for key, default in MEMORY_SCHEMA.items():
            if key not in memory:
                memory[key] = default
                
        # Write repaired memory
        with open(MEMORY_PATH, "w") as f:
            json.dump(memory, f, indent=2)
        log_event("Memory healed successfully")
        
    except Exception as e:
        log_event(f"Memory healing failed: {e}")

def run_tasks():
    """Execute queued tasks"""
    if not TASK_FILE.exists():
        return
        
    try:
        with open(TASK_FILE) as f:
            tasks = json.load(f)
            
        for task in tasks.get("queue", []):
            log_event(f"Running task: {task}")
            subprocess.call(task, shell=True)
            
        # Clear completed tasks
        with open(TASK_FILE, "w") as f:
            json.dump({"queue": []}, f)
            
    except Exception as e:
        log_event(f"Task execution failed: {e}")

def self_repair():
    """Perform system self-repair operations"""
    ensure_directories()
    heal_memory()
    
def run_daemon_loop():
    """Main daemon loop"""
    print("⚙️ EvoVe task daemon starting...")
    while True:
        try:
            self_repair()
            run_tasks()
            time.sleep(900)  # Run every 15 minutes
        except KeyboardInterrupt:
            print("\n💤 Task daemon shutting down...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_daemon_loop()
