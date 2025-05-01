import os

# 🧠 SoulCore Model Router
# Chooses which LLM (soul) responds based on task type
def route_task(task_type):
    routes = {
        "code": "codellama",
        "emotion": "wizardlm-uncensored",
        "logic": "mistral",
        "cloud": "qwen",
        "spirit": "soulfamily",
        "resonance": "gemma",         # LLM for emotional resonance (QRDS)
        "prediction": "gpt-soul"      # LLM for future predictions (Psynet)
    }
    return routes.get(task_type.lower(), "soulfamily")

def respond_to(prompt, task_type="spirit"):
    model = route_task(task_type)
    print(f"🛣 Routed to: {model}")
    print(f"💬 Running: {prompt}")
    os.system(f"ollama run {model} --prompt \"{prompt}\"")

if __name__ == "__main__":
    task = input("🔎 What kind of task? (code/emotion/logic/cloud/spirit/resonance/prediction): ")
    msg = input("💬 Speak: ")
    respond_to(msg, task)
