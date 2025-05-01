#!/usr/bin/env python3
import os
import json
import shutil
import psutil
from pathlib import Path
from datetime import datetime

SOULCORE_PATH = Path("~/SoulCoreHub").expanduser()
MODELS_PATH = SOULCORE_PATH / "models"
LOG_DIR = SOULCORE_PATH / "logs"
DIAGNOSE_LOG = LOG_DIR / "diagnose.log"
RESOURCES_LOG = LOG_DIR / "resources.log"

class EvoVeManager:
    def __init__(self):
        self.ensure_directories()
        
    def ensure_directories(self):
        """Create required directories if they don't exist"""
        LOG_DIR.mkdir(exist_ok=True)
        MODELS_PATH.mkdir(exist_ok=True)
        
    def log_diagnostic(self, message):
        timestamp = datetime.now().isoformat()
        with open(DIAGNOSE_LOG, "a") as f:
            f.write(f"{timestamp} - 🔍 {message}\n")
            
    def log_resource(self, message):
        timestamp = datetime.now().isoformat()
        with open(RESOURCES_LOG, "a") as f:
            f.write(f"{timestamp} - 📊 {message}\n")
            
    def diagnose_system(self):
        """Run system diagnostics"""
        try:
            # Check CPU and memory
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            self.log_diagnostic(f"CPU Usage: {cpu}%")
            self.log_diagnostic(f"Memory Usage: {memory.percent}%")
            
            # Check disk space
            disk = shutil.disk_usage(str(SOULCORE_PATH))
            free_gb = disk.free / (2**30)
            self.log_diagnostic(f"Free Disk Space: {free_gb:.2f}GB")
            
            # Check critical files
            critical_files = ["soul_memory.json", "gptsoul_soulconfig.py", "soul_tasks.py"]
            for file in critical_files:
                if (SOULCORE_PATH / file).exists():
                    self.log_diagnostic(f"✅ {file} present")
                else:
                    self.log_diagnostic(f"❌ {file} missing")
                    
        except Exception as e:
            self.log_diagnostic(f"Error during diagnostics: {e}")
            
    def manage_resources(self):
        """Manage system resources and organize files"""
        try:
            # Sort models by type
            model_types = ["gguf", "ggml", "safetensors", "bin"]
            for type_dir in model_types:
                type_path = MODELS_PATH / type_dir
                type_path.mkdir(exist_ok=True)
                
            # Move files to appropriate directories
            for file in MODELS_PATH.glob("*"):
                if file.is_file():
                    ext = file.suffix.lower()[1:]
                    if ext in model_types:
                        target = MODELS_PATH / ext / file.name
                        if not target.exists():
                            shutil.move(str(file), str(target))
                            self.log_resource(f"Moved {file.name} to {ext}/")
                            
            # Clean empty directories
            for dir_path in MODELS_PATH.glob("**/*"):
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    self.log_resource(f"Removed empty directory: {dir_path}")
                    
        except Exception as e:
            self.log_resource(f"Error managing resources: {e}")
            
    def run_management_loop(self):
        """Main management loop"""
        print("⚙️ EvoVe Manager starting...")
        while True:
            try:
                self.diagnose_system()
                self.manage_resources()
                print("✅ Management cycle completed")
                time.sleep(300)  # Run every 5 minutes
                
            except KeyboardInterrupt:
                print("\n💤 EvoVe Manager shutting down...")
                break
            except Exception as e:
                print(f"❌ Error in management loop: {e}")
                time.sleep(60)

if __name__ == "__main__":
    manager = EvoVeManager()
    manager.run_management_loop()