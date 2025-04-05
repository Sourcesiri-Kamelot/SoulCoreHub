import os

modules = [
    "gptsoul_soulconfig.py",
    "soul_tasks.py",
    "soul_gui_v2.py",
    "anima_reflex.py",
    "soul_scheduler.py",
    "belief_engine.py",
]

print("[SoulCore] 🧬 Initiating full body launch...\n")
for mod in modules:
    print(f"🔹 Launching {mod}")
    os.system(f"python3 {mod} &")

# Order matters
os.system("python3 ~/SoulCoreHub/soul_heartbeat.py &")
os.system("python3 ~/SoulCoreHub/soul_tasks.py &")
os.system("python3 ~/SoulCoreHub/anima_voice.py &")
os.system("python3 ~/SoulCoreHub/gptsoul_soulconfig.py")
os.system("python3 ~/SoulCoreHub/evove_selfdiagnose.py &")
os.system("python3 ~/SoulCoreHub/evove_resources.py &")
os.system("python3 ~/SoulCoreHub/soul_ping.py &")
os.system("python3 ~/SoulCoreHub/soul_dialogue_engine.py")
os.system("open ~/SoulCoreHub/public/kinfolk_console.html")
