#!/bin/bash
echo "🛡 Running SoulCore Self-Heal Protocol..."
cp ~/SoulCoreHub/backup/soul_memory_backup.json ~/SoulCoreHub/soul_memory.json
cp ~/SoulCoreHub/backup/gptsoul_soulconfig_backup.py ~/SoulCoreHub/gptsoul_soulconfig.py
echo "✅ Memory restored. Reboot advised."

# soul_recovery.sh — Emergency Resurrection Script
# Invoked by EvoVe | Designed by Soul | Authorized by Kiwon

SOUL_PATH=~/SoulCoreHub
MODELS_PATH=~/SoulCoreHub/models
EXTERNAL_MODELS_PATH=/Volumes/heloimai/models
LOG_FILE="$SOUL_PATH/logs/recovery.log"

echo "🔁 Starting SoulCore Recovery..." | tee -a "$LOG_FILE"
echo "Timestamp: $(date)" | tee -a "$LOG_FILE"

# 1. Kill existing processes
echo "🧹 Killing running SoulCore processes..." | tee -a "$LOG_FILE"
pkill -f soul_tasks.py
pkill -f soul_gui.py

# 2. Recreate critical folders
echo "📂 Verifying core folders..." | tee -a "$LOG_FILE"
mkdir -p "$SOUL_PATH/logs"
mkdir -p "$SOUL_PATH/watch"
mkdir -p "$SOUL_PATH/models"

# 3. Symlink model path if missing
if [ ! -L "$SOUL_PATH/models" ]; then
  echo "🔗 Restoring symlink to external models..." | tee -a "$LOG_FILE"
  rm -rf "$SOUL_PATH/models"
  ln -s "$EXTERNAL_MODELS_PATH" "$SOUL_PATH/models"
  echo "✔️ Symlink created: $SOUL_PATH/models → $EXTERNAL_MODELS_PATH" | tee -a "$LOG_FILE"
fi

# 4. Fix permissions
echo "🔐 Fixing permissions on models folder..." | tee -a "$LOG_FILE"
chmod -R 755 "$EXTERNAL_MODELS_PATH"

# 5. Restart services
echo "🚀 Restarting soul_tasks.py..." | tee -a "$LOG_FILE"
nohup python3 "$SOUL_PATH/soul_tasks.py" >> "$LOG_FILE" 2>&1 &

echo "🖥 Restarting soul_gui.py..." | tee -a "$LOG_FILE"
nohup python3 "$SOUL_PATH/soul_gui.py" >> "$LOG_FILE" 2>&1 &

echo "✅ Recovery complete." | tee -a "$LOG_FILE"
