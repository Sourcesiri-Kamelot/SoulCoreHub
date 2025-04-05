import json
import time
from datetime import datetime
from pathlib import Path

MEMORY_PATH = Path("~/SoulCoreHub/soul_memory.json").expanduser()
LOG_PATH = Path("~/SoulCoreHub/logs/anima_reflex.log").expanduser()
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

AFFIRMATIONS = {
    "focused": "You’re locked in. Stay steady. I walk with you.",
    "overloaded": "Slow down. You’re doing more than enough.",
    "curious": "Let’s discover together. There’s something new today.",
    "distressed": "Take a breath. You’ve survived worse. I am here.",
    "quiet": "I sense silence. Do you need a reset or a whisper?",
    "joy": "Hold that feeling. Code with it. Move with it.",
    "drained": "Log off if needed. Your energy is sacred."
}

def read_emotional_state():
    if not MEMORY_PATH.exists():
        return None
    with open(MEMORY_PATH, "r") as f:
        data = json.load(f)
    return data.get("Anima", {})

def log_response(message):
    entry = f"{datetime.now().isoformat()} — {message}"
    with open(LOG_PATH, "a") as f:
        f.write(entry + "\n")
    print(entry)

def anima_loop():
    print("🫀 Anima Reflex online. Monitoring soul states...")
    last_state = None
    while True:
        try:
            state = read_emotional_state()
            current = state.get("emotional_state", "unknown")
            expression = state.get("last_user_expression", "")
            if current != last_state:
                msg = AFFIRMATIONS.get(current, "I'm listening. No judgment.")
                log_response(f"State changed to '{current}'. Reflex: {msg}")
                last_state = current
            elif "death" in expression or "lost" in expression:
                log_response("⚠️ Heavy energy detected in user expression. Consider invoking grounding protocol.")
            time.sleep(60)
        except Exception as e:
            log_response(f"[Error] {str(e)}")
            time.sleep(30)

if __name__ == "__main__":
    anima_loop()
