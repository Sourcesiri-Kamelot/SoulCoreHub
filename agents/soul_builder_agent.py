# ✅ SOULBUILDER vX∞ — God-Tier Autonomous Build Agent
import os
import requests
import subprocess
from datetime import datetime
from rich.console import Console

console = Console()

# 🧠 Hugging Face Token (from env or hardcoded backup)
HF_TOKEN = os.getenv("HF_TOKEN") or "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"

def speak(msg):
    console.print(f"[bold cyan]SoulBuilder:[/bold cyan] {msg}")

def hf_infer(prompt):
    speak("🔗 Connecting to HuggingFace Inference API...")
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}
    response = requests.post(
        "https://api-inference.huggingface.co/models/google/flan-t5-large",
        headers=headers, json=payload)
    try:
        result = response.json()
        return result[0]['generated_text'] if isinstance(result, list) else result.get('generated_text', str(result))
    except Exception as e:
        return f"❌ Error from HuggingFace API: {e}"

def write_file(path, content):
    with open(path, "w") as f:
        f.write(content)
    with open(os.path.expanduser("~/SoulCoreHub/logs/soul_builds.log"), "a") as log:
        log.write(f"\n[{datetime.now()}] {path} — build:\n{content}\n{'-'*60}\n")
    speak(f"💾 Saved to [bold green]{path}[/bold green]")

def run_file(path):
    speak(f"🚀 Running [bold]{path}[/bold]...")
    ext = path.split('.')[-1]
    commands = {'py': f"python3 {path}", 'sh': f"bash {path}", 'js': f"node {path}"}
    cmd = commands.get(ext)
    if cmd:
        os.system(cmd)
    else:
        speak(f"⚠️ No auto-run support for .{ext} files.")

def confirm_delete(path):
    speak(f"⚠️ Confirm delete: [red]{path}[/red]")
    if input("Type 'yes' to delete: ").strip().lower() == 'yes':
        os.remove(path)
        speak(f"🗑️ Deleted {path}")
    else:
        speak("❎ Delete canceled.")

def run():
    speak("💡 SoulBuilderAgent is online. Describe your build.")
    while True:
        try:
            prompt = input("🔧 Build Request: ").strip()
            if prompt.lower() in ["exit", "quit"]:
                speak("👋 Exiting.")
                break

            code = hf_infer(prompt)
            speak("🧠 Generated Code:")
            console.print(code, style="bold green")

            filename = input("📁 Save as filename (e.g., hello.py): ").strip()
            path = os.path.join(os.getcwd(), filename)
            write_file(path, code)

            if input("▶️ Auto-run now? (y/n): ").strip().lower() == 'y':
                run_file(path)

            if input("🗑️ Delete after run? (y/n): ").strip().lower() == 'y':
                confirm_delete(path)

        except KeyboardInterrupt:
            speak("⏹️ Interrupted.")
            break

if __name__ == "__main__":
    run()
