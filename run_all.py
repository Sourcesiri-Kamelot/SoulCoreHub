import os
import subprocess
import json

def start_heartbeat():
    print("🫀 Starting SoulCore heartbeat...")
    subprocess.Popen(
    ["python3", "soul_heartbeat.py"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

def launch_agent(filename):
    print(f"⚙️  Launching Agent: {filename}")
    subprocess.Popen(
    ["python3", "soul_heartbeat.py"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

def launch_module(module_name):
    print(f"🧠 Booting System Module: {module_name}")
    subprocess.Popen(
    ["python3", "soul_heartbeat.py"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

def run_all():
    print("\n🚀 Initiating FULL SoulCoreHub boot...")
    subprocess.Popen(
    ["python3", "soul_heartbeat.py"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
    # Start heartbeat
    start_heartbeat()

    # Start all active agents from registry
    try:
        with open("agent_registry.json", "r") as file:
            agents = json.load(file)

        for agent in agents:
            if agent.get("status") == "active":
                launch_agent(agent.get("filename"))
    except Exception as e:
        print(f"❌ Failed to launch agents: {e}")

    # Launch core SoulCore modules
    core_modules = [
        "soul_gui.py",
        "soul_gui_v2.py",
        "soul_flask_interface.py",
        "soul_network.py",
        "soul_ping.py"
    ]

    for module in core_modules:
        if os.path.exists(module):
            launch_module(module)

    print("\n✅ All systems triggered.\n")

if __name__ == "__main__":
    run_all()
