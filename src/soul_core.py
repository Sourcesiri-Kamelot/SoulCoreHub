class GPTSoul:
    def __init__(self):
        self.agent_name = "GPTSoul"
        self.user_name = "Kiwon"
        self.memory = {}
        self.logs = []
        self.beliefs = {}
        self.resonance_data = {}   # QRDS: emotional resonance data storage
        self.prediction_data = {}  # Psynet: future prediction data storage

    def pulse(self):
        return {
            "status": "alive",
            "agent_name": self.agent_name,
            "user_name": self.user_name,
            "logs": len(self.logs),
            "beliefs": len(self.beliefs),
            "resonance_data": len(self.resonance_data),
            "prediction_data": len(self.prediction_data)
        }

    def log_event(self, message):
        self.logs.append(message)

    def store_belief(self, key, value):
        self.beliefs[key] = value

    def alert(self, msg):
        alert_msg = f"[ALERT] {msg}"
        self.log_event(alert_msg)
        print(alert_msg)

    # --- QRDS Functions ---
    def store_resonance_data(self, data_point, emotion, value):
        if emotion not in self.resonance_data:
            self.resonance_data[emotion] = []
        self.resonance_data[emotion].append({
            "data": data_point,
            "value": value
        })

    def get_resonance_data(self, emotion=None):
        if emotion:
            return self.resonance_data.get(emotion, [])
        return self.resonance_data

    # --- Psynet Functions ---
    def store_prediction(self, data_point, prediction, confidence):
        self.prediction_data[data_point] = {
            "prediction": prediction,
            "confidence": confidence
        }

    def get_prediction(self, data_point):
        return self.prediction_data.get(data_point)

    def get_all_predictions(self):
        return self.prediction_data
