import datetime, json, os

log_path = os.path.expanduser("~/SoulCoreHub/logs/dialogue_history.json")
os.makedirs(os.path.dirname(log_path), exist_ok=True)

def speak_to_agents(user_input):
    timestamp = datetime.datetime.now().isoformat()

    gpt_soul = f"🧠 GPTSoul: Based on your input, I suggest this corrected version: '{user_input.capitalize()}'. Should I execute?"
    anima = f"💫 Anima: I feel uncertainty. Shall I color the GUI for calm?"
    evove = f"⚙️ EvoVe: Daemon is live. I’m checking for matching command threads."
    azur = f"☁️ Azür: Monitoring cloud sync path. Do you want me to prep Alibaba backup?"

    response = {
        "time": timestamp,
        "user": user_input,
        "GPTSoul": gpt_soul,
        "Anima": anima,
        "EvoVe": evove,
        "Azür": azur
    }

    try:
        history = []
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                history = json.load(f)
        history.append(response)
        with open(log_path, "w") as f:
            json.dump(history[-100:], f, indent=2)
    except Exception as e:
        print(f"❌ Logging failed: {e}")

    return response

if __name__ == "__main__":
    user_input = input("💬 Speak to SoulCore: ")
    reply = speak_to_agents(user_input)
    for agent in ["GPTSoul", "Anima", "EvoVe", "Azür"]:
        print(reply[agent])
