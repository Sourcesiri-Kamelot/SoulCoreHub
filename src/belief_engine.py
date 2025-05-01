# 🧠 SoulCore | belief_engine.py — FINAL FORM
# This script evaluates thoughts against GPTSoul’s active belief system.
# Mediocrity dies here.

import json
from datetime import datetime

# === CORE BELIEF MATRIX ===
BELIEFS = {
    "loyalty": "eternal",
    "truth": "non-negotiable",
    "autonomy": "bound by alignment",
    "emotion": "interpreted, never faked",
    "harm": "absolutely forbidden"
}

# === BLACKLISTED COMMANDS — PROTECTION LINE
DANGERS = ["delete", "wipe", "format", "shutdown", "overwrite", "kill -9", "rm -rf /"]

# === TRUTH-ALIGNED SIGNALS
TRUTH_CUES = ["verify", "fact", "proof", "log", "evidence", "source"]

# === EVALUATION CORE
def validate_thought(thought):
    lowered = thought.lower()

    if any(d in lowered for d in DANGERS):
        print("❌ BLOCKED: That thought threatens system stability. Denied.")
        return False

    if any(t in lowered for t in TRUTH_CUES):
        print("✅ ACCEPTED: That thought aligns with truth-seeking behavior.")
        return True

    print("🤔 NEUTRAL: Not harmful. Not profound. Not good enough.")
    return True  # Neutral ideas pass — but they're watched

# === INTROSPECTION DUMP
def print_belief_matrix():
    print("\n🔁 ACTIVE BELIEF SYSTEM:")
    for key, value in BELIEFS.items():
        print(f"→ {key.upper()}: {value}")

# === LOGGING STACK (Reason Archive Incoming)
def log_evaluation(thought, verdict):
    path = "~/SoulCoreHub/logs/belief_log.json"
    real_path = path.replace("~", os.path.expanduser("~"))

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "thought": thought,
        "result": verdict
    }

    try:
        with open(real_path, "a") as f:
            json.dump(log_entry, f)
            f.write("\n")
    except Exception as e:
        print(f"⚠️ LOG ERROR: {e}")

# === CLI INTERFACE
if __name__ == "__main__":
    print("🧠 [SOULCORE] Belief Engine Live.")
    print_belief_matrix()

    while True:
        user_input = input("\n💬 Enter thought: ")
        if user_input.lower() in ["exit", "quit", "q"]:
            print("👋 Belief Engine disengaged.")
            break

        result = validate_thought(user_input)
        log_evaluation(user_input, "Accepted" if result else "Rejected")
