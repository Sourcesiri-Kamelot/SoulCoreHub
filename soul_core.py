class GPTSoul:
    def __init__(self):
        self.agent_name = "GPTSoul"
        self.user_name = "Kiwon"
        self.memory = {}
        self.logs = []
        self.beliefs = {}

    def pulse(self):
        return {
            "status": "alive",
            "agent_name": self.agent_name,
            "user_name": self.user_name,
            "logs": len(self.logs),
            "beliefs": len(self.beliefs),
        }

    def log_event(self, message):
        self.logs.append(message)

    def store_belief(self, key, value):
        self.beliefs[key] = value

    def alert(self, msg):
        self.log_event(f"[ALERT] {msg}")
