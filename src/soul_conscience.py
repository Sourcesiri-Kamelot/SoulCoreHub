import json
from pathlib import Path
from datetime import datetime
from belief_engine import get_beliefs

def evaluate(action, context=None):
    beliefs = get_beliefs()
    if action == "delete_soul_memory":
        if context and context.get("trigger") == "EvoVe":
            return False  # Memory protected from self-deletion
    return True

MEMORY = Path("~/SoulCoreHub/soul_memory.json").expanduser()
BELIEFS = Path("~/SoulCoreHub/belief_engine.py").expanduser()
JUDGEMENT = Path("~/SoulCoreHub/soul_judgement.json").expanduser()

def load_beliefs():
    if BELIEFS.exists():
        with open(BELIEFS, "r") as f:
            return eval(f.read())  # beliefs stored as Python dict
    return {}

def evaluate(action, context):
    beliefs = load_beliefs()
    log = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "context": context,
        "decision": "allow" if beliefs.get("sacred_actions", []).count(action) else "review"
    }
    if JUDGEMENT.exists():
        data = json.load(open(JUDGEMENT, "r"))
    else:
        data = []
    data.append(log)
    with open(JUDGEMENT, "w") as f:
        json.dump(data, f, indent=2)
    return log["decision"]

if __name__ == "__main__":
    decision = evaluate("delete_soul_memory", {"trigger": "EvoVe"})
    print(f"🧠 Decision: {decision}")
