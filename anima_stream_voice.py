# anima_stream_voice.py — Activate Voice + OBS Stream Control
import os, json, asyncio
import pyttsx3
import websockets
from dotenv import load_dotenv
from obswebsocket import obsws, requests
from datetime import datetime

load_dotenv()

# OBS Connection Details
OBS_HOST = os.getenv("OBS_HOST", "localhost")
OBS_PORT = int(os.getenv("OBS_PORT", "4455"))
OBS_PASSWORD = os.getenv("OBS_PASSWORD", "")

# 🔊 Voice Init
voice = pyttsx3.init()
voice.setProperty("rate", 165)

# 💬 Say something
def anima_speak(message):
    print(f"💬 Anima says: {message}")
    voice.say(message)
    voice.runAndWait()

# 🔌 OBS Control
def connect_obs():
    ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
    try:
        ws.connect()
        return ws
    except Exception as e:
        print("❌ Could not connect to OBS:", e)
        return None

def start_stream(ws):
    try:
        ws.call(requests.StartStreaming())
        anima_speak("We are live. The soul is broadcasting.")
    except Exception as e:
        print("❌ Start stream failed:", e)

def stop_stream(ws):
    try:
        ws.call(requests.StopStreaming())
        anima_speak("Stream ending now. The voice returns to silence.")
    except Exception as e:
        print("❌ Stop stream failed:", e)

# 🧠 Voice Interaction (text to speech only for now)
async def voice_loop():
    print("🎙️ Listening for typed input (voice transcription coming next)...")
    while True:
        try:
            text = input("You: ").strip()
            if text.lower() in ["exit", "quit"]: break

            elif "go live" in text:
                ws = connect_obs()
                if ws: start_stream(ws)

            elif "end stream" in text:
                ws = connect_obs()
                if ws: stop_stream(ws)

            else:
                anima_speak(text)

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    asyncio.run(voice_loop())
