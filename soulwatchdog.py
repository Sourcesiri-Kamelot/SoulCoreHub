import os, time, hashlib, shutil

watch_files = [
    "soulcore.py",
    "soulmemory.json",
    "soul_prompt.txt",
    "soulconfig.json"
]
file_hashes = {}

def hash_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def backup_file(path):
    backup_path = path + ".bak"
    shutil.copy(path, backup_path)

while True:
    for file in watch_files:
        full_path = os.path.expanduser(f"~/SoulCoreHub/{file}")
        if os.path.exists(full_path):
            new_hash = hash_file(full_path)
            old_hash = file_hashes.get(file)
            if old_hash and new_hash != old_hash:
                print(f"⚠️ Change detected in {file}! Backing up…")
                backup_file(full_path)
            file_hashes[file] = new_hash
    time.sleep(60)
