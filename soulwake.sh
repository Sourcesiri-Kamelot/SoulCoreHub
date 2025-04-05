#!/bin/bash

echo "🧠 Booting Anami..."

# Activate virtual environment
source ~/SoulCoreHub/memory/myenv/bin/activate

# Run Anami CLI
PYTHONPATH=~/SoulCoreHub python3 ~/SoulCoreHub/soul_cli.py --loop
