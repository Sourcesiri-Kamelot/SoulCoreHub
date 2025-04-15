import json
import os

REASONING_PATH = os.path.expanduser("~/SoulCoreHub/reasoning_stack.json")

def add_reason(reason):
    if not os.path.exists(REASONING_PATH):
        stack = []
    else:
        with open(REASONING_PATH, "r") as f:
            stack = json.load(f)

    stack.append({"reason": reason, "source": "gptsoul"})
    with open(REASONING_PATH, "w") as f:
        json.dump(stack, f, indent=4)
    print("🧠 Reason added to GPTSoul's stack.")

if __name__ == "__main__":
    add_reason("Phase 7 initiated. Belief evolution activated.")
