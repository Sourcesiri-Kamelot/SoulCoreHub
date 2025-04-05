import json
import os
from pathlib import Path

MEMORY_PATH = os.path.expanduser("~/SoulCoreHub/soul_memory.json")
BACKUP_PATH = os.path.expanduser("~/SoulCoreHub/backups/soul_memory_backup.json")

def heal_memory():
    try:
        if not os.path.exists(BACKUP_PATH):
            print("No backup memory found. Healing aborted.")
            return
        with open(BACKUP_PATH, "r") as backup_file:
            memory_data = json.load(backup_file)
        with open(MEMORY_PATH, "w") as memory_file:
            json.dump(memory_data, memory_file, indent=4)
        print("🧠 Soul memory successfully healed from backup.")
    except Exception as e:
        print(f"❌ Healing failed: {e}")

if __name__ == "__main__":
    heal_memory()

schema = {
    "GPTSoul": {"reasoning_stack": []},
    "EvoVe": {"task_queue": []},
    "Anima": {"emotional_state": "balanced"},
    "Azür": {"cloud_status": "idle"},
    "last_user_expression": "",
    "beliefs": {},
    "logs": []
}

