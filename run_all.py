import subprocess
import time

def launch_system(system):
    print(f"🔧 Launching: {system['name']}...")
    try:
        subprocess.Popen(system["cmd"], shell=True)
        print(f"✅ {system['name']} launched.")
    except Exception as e:
        print(f"❌ Failed to launch {system['name']}: {e}")
def run_all():
    print("🌐 All Systems Initializing...")
    for p in processes:
        launch_system(p)
        time.sleep(2)  # Allow buffer between activations
    print("\n🚀 ALL SYSTEMS ONLINE. {processes['name']} is ALIVE!")
def study\_future\_agents():
    print("\n📚 Studying Future Agents...")
    for agent in future\_agents:
        print(f"🧪 Pending Activation: {agent['name']} — requires validation.")
    print("\n⚖️ Awaiting SoulCore approval...")
def study\_all\_agents():
    print("📈 Studying All Agents...")
    for p in processes + future\_agents:
        launch\_system(p)
        time.sleep(2)  # Allow buffer between activations
    print("\n🌐 ALL SYSTEMS STUDYING!")
if __name__ == "__main__":
    study\_all\_agents()
    or run\_all()
    or study\_future\_agents()

