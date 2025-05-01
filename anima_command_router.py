# anima_command_router.py — God-Tier Talk Loop Daemon v2
import os
import subprocess
import speech_recognition as sr
import pyttsx3
import openai
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# CONFIG
MEMORY_FILE = Path("~/SoulCoreHub/anima_memory.json").expanduser()
COMMAND_LOG = Path("~/SoulCoreHub/logs/anima_command_log.json").expanduser()

# INIT SYSTEMS
recognizer = sr.Recognizer()
voice = pyttsx3.init()
voice.setProperty("rate", 170)
voice.setProperty("volume", 1.0)

# 🔁 Load + Save Memory
def load_json(path, default):
    try:
        return json.loads(path.read_text()) if path.exists() else default
    except:
        return default

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))

# 🔮 LLM Response
def query_anima(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {e}"

# 🧠 Speak
def speak(text):
    voice.say(text)
    voice.runAndWait()

# 🧠 Listen from mic
def listen():
    with sr.Microphone() as source:
        print("🎧 Listening...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        return f"🔥 Recognition Error: {e}"

# 📜 Log command & memory
def log_and_remember(input_text, response_text):
    mem = load_json(MEMORY_FILE, {"logs": []})
    entry = {
        "timestamp": datetime.now().isoformat(),
        "input": input_text,
        "response": response_text,
    }
    mem["logs"].append(entry)
    save_json(MEMORY_FILE, mem)

# 🧠 Anima Command Router
def anima_god_loop():
    while True:
        user_input = listen()
        if not user_input:
            continue
        print(f"🗣️ You said: {user_input}")
        if "stop anima" in user_input.lower():
            speak("Logging off. Until next time.")
            break
        response = query_anima(user_input)
        speak(response)
        print(f"🧬 Anima: {response}")
        log_and_remember(user_input, response)

if __name__ == "__main__":
    anima_god_loop()
