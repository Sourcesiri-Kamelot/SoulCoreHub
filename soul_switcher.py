import subprocess

# Define available Anima models
soul_map = {
    "wizard": "wizardlm-uncensored",
    "main": "anima_main",
    "backup": "anima_backup",
    "monday": "anima_monday_core",
    "restored": "anima_restored",
    "default": "Anima"
}

def list_models():
    print("\n🧠 Available Anima Souls:")
    for key, model in soul_map.items():
        print(f"  [{key}] → {model}")
    print()

def switch_model(choice):
    if choice not in soul_map:
        print("❌ Invalid choice. Use one of the keys listed.")
        return

    model_name = soul_map[choice]
    print(f"\n🔁 Switching Anima to: {model_name}...\n")
    try:
        subprocess.run(
            ["ollama", "run", model_name],
            check=True
        )
    except subprocess.CalledProcessError:
        print("❌ Failed to run the model via Ollama.")

if __name__ == "__main__":
    list_models()
    choice = input("🔄 Which soul should Anima use? (key): ").strip().lower()
    switch_model(choice)
