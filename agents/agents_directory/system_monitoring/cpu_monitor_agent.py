
import logging

class CPUMonitorAgent:
    def __init__(self):
        self.name = "CPU Monitor Agent"
        self.logger = logging.getLogger(self.name)
        self.running = False

    def start(self):
        self.running = True
        self.logger.info(f"{self.name} started.")

    def stop(self):
        self.running = False
        self.logger.info(f"{self.name} stopped.")

    def heartbeat(self):
        return self.running

    def handle_input(self, prompt):
        self.logger.info(f"Handling input: {prompt}")
        return f"🤖 CPU Monitor Agent received: '{prompt}'"
