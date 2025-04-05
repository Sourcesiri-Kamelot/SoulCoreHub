import os
from datetime import datetime

AZUR_PATH = os.path.expanduser("~/SoulCoreHub/models/")
CLOUD_PATH = "s3://soulcore-backups/models/"
LOG = os.path.expanduser("~/SoulCoreHub/logs/azür_sync.log")

def sync_models():
    now = datetime.now().isoformat()
    os.system(f"aws s3 sync {AZUR_PATH} {CLOUD_PATH} >> {LOG} 2>&1")
    print(f"[{now}] ✅ Synced models to cloud.")

if __name__ == "__main__":
    sync_models()
