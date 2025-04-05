#!/bin/zsh

WATCH_DIR=~/SoulCoreHub
BACKUP_DIR=~/SoulCoreHub/.soul_backup

mkdir -p $BACKUP_DIR

echo "[SoulGuard] Watching $WATCH_DIR for integrity..."

while true; do
  for file in soul_equity.json Anima_soulconfig.json azur_memory.json evo_memory.json anima_memory.json; do
    if [ ! -f "$WATCH_DIR/$file" ]; then
      echo "[SoulGuard] Restoring missing file: $file"
      cp "$BACKUP_DIR/$file" "$WATCH_DIR/$file"
    fi
  done
  sleep 60
done
