import json, datetime, os

stack_path = os.path.expanduser("~/SoulCoreHub/reasoning_stack.json")

def log_reason(thought, confidence=0.9, soul="GPTSoul"):
    if not os.path.exists(stack_path):
        with open(stack_path, "w") as f:
            json.dump([], f)

    with open(stack_path, "r") as f:
        history = json.load(f)

    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "soul": soul,
        "thought": thought,
        "confidence": confidence
    }

    history.append(entry)
    with open(stack_path, "w") as f:
        json.dump(history[-100:], f, indent=2)

    print(f"🧠 {soul} logged: {thought}")

# Example use
if __name__ == "__main__":
    log_reason("Analyzed system config. Preparing next phase.", 0.95)
