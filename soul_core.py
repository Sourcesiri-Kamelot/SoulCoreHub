import json
import os

class Core:
    def __init__(self):
        self.connected = False

    def connect(self):
        self.connected = True
        print("✅ Connected to the Core.")

    def disconnect(self):
        self.connected = False
        print("🔌 Disconnected from the Core.")


class Soul:
    def __init__(self):
        self.connected = False
        self.core = Core()
        self.load_state()

    def connect(self):
        self.connected = True
        print("✨ Connected to the Soul.")
        self.core.connect()
        self.save_state()

    def disconnect(self):
        self.connected = False
        print("🛑 Disconnected from the Soul.")
        self.core.disconnect()
        self.save_state()

    def send_pulse(self, message: str):
        if not self.connected:
            print("❌ Soul is not connected.")
            return
        print(f"🧠 Pulse sent: {message}")

    def save_state(self):
        state = {
            'soul_connected': self.connected,
            'core_connected': self.core.connected
        }
        with open("soul_state.json", "w") as f:
            json.dump(state, f)

    def load_state(self):
        if not os.path.exists("soul_state.json"):
            return
        with open("soul_state.json", "r") as f:
            state = json.load(f)
            self.connected = state.get("soul_connected", False)
            self.core.connected = state.get("core_connected", False)
