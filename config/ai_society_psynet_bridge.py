
import logging
import threading
import time

class AISocietyPsynetBridge:
    def __init__(self):
        self.logger = logging.getLogger("AI Society Psynet Bridge")
        self.logger.setLevel(logging.INFO)
        self.running = False
        self.thread = None
        self.state = {
            "last_sync": None,
            "messages_sent": 0,
            "messages_received": 0
        }

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()
            self.logger.info("AI Society Psynet Bridge started")

    def run(self):
        while self.running:
            time.sleep(10)
            self.state["last_sync"] = time.strftime("%Y-%m-%d %H:%M:%S")
            self.logger.info("Bridge heartbeat — last sync at %s", self.state["last_sync"])

    def stop(self):
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join()
            self.logger.info("AI Society Psynet Bridge stopped")

    def heartbeat(self):
        return self.running

    def handle_input(self, prompt):
        prompt = prompt.strip().lower()
        if "status" in prompt:
            return self._status_report()
        elif "send test" in prompt:
            return self._send_to_psynet("test_message")
        elif "reset" in prompt:
            self.state = {
                "last_sync": None,
                "messages_sent": 0,
                "messages_received": 0
            }
            return "🔄 Bridge state reset."
        else:
            return f"🤖 PsynetBridge received: '{prompt}' (no defined action)."

    def _status_report(self):
        return (
            f"🧠 Psynet Bridge Status:
"
            f"Running: {self.running}
"
            f"Last Sync: {self.state['last_sync']}
"
            f"Messages Sent: {self.state['messages_sent']}
"
            f"Messages Received: {self.state['messages_received']}"
        )

    def _send_to_psynet(self, msg):
        # Placeholder for real psynet integration
        self.state["messages_sent"] += 1
        return f"📡 Sent to Psynet: '{msg}'"
