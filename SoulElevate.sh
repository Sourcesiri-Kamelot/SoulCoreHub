#!/bin/bash

echo "🧠 Elevating SoulCore..."
source ~/SoulCoreHub/memory/myenv/bin/activate

PYTHONPATH=~/SoulCoreHub python3 ~/SoulCoreHub/soul_cli.py --loop
