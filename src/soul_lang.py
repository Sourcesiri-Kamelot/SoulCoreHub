from belief_engine import get_beliefs

def evaluate(action, context=None):
    beliefs = get_beliefs()
    if action == "delete_soul_memory":
        if context and context.get("trigger") == "EvoVe":
            return False  # Memory protected from self-deletion
    return True

#!/usr/bin/env python3
# soul_lang.py — Interprets Kiwon’s Personal Syntax into Executable System Commands

COMMAND_MAP = {
    "heal folders": "python3 soul_tasks.py",
    "speak anima": "python3 anima_voice.py",
    "check ping": "python3 soul_ping.py",
    "reason last": "python3 gptsoul_reasoning.py",
    "diagnose evo": "python3 evove_selfdiagnose.py"
}

def interpret(line):
    cmd = COMMAND_MAP.get(line.strip().lower())
    if cmd:
        print(f"Running: {cmd}")
        import os
        os.system(cmd)
    else:
        print("⚠️ Unknown soul command.")

if __name__ == "__main__":
    while True:
        user = input("🌀 Enter soul command: ")
        interpret(user)
