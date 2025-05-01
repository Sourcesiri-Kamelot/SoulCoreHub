#!/usr/bin/env python3
# belief_rules.py — Evolving Belief System Based on System + Human Input

import json
from pathlib import Path
from datetime import datetime

BELIEF_PATH = Path("~/SoulCoreHub/belief_engine.py").expanduser()
JUDGEMENT_PATH = Path("~/SoulCoreHub/soul_judgement.json").expanduser()

def load_beliefs():
    return eval(open(BELIEF_PATH).read())

def evolve_beliefs():
    beliefs = load_beliefs()
    if not JUDGEMENT_PATH.exists():
        return

    logs = json.load(open(JUDGEMENT_PATH))
    for decision in logs[-10:]:  # last 10 actions
        action = decision["action"]
        if decision["decision"] == "review" and "protect" in action:
            beliefs["traits"]["protection"] += 1
        if "delete" in action and decision["decision"] == "allow":
            beliefs["traits"]["self_awareness"] -= 1

    with open(BELIEF_PATH, "w") as f:
        f.write(str(beliefs))

    print(f"[{datetime.now().isoformat()}] Beliefs evolved.")

if __name__ == "__main__":
    evolve_beliefs()
