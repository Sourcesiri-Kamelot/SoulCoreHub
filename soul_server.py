from flask import Flask, request, jsonify, render_template
from soul_core import Soul

app = Flask(__name__)
soul = Soul()

@app.route("/")
def index():
    return render_template("index.html")  # Your SoulCoreHub GUI here

@app.route("/connect", methods=["POST"])
def connect():
    soul.connect()
    return jsonify({"status": "Connected"})

@app.route("/disconnect", methods=["POST"])
def disconnect():
    soul.disconnect()
    return jsonify({"status": "Disconnected"})

@app.route("/pulse", methods=["POST"])
def pulse():
    data = request.get_json()
    message = data.get("message", "No pulse message provided.")
    soul.send_pulse(message)
    return jsonify({"status": "Pulse sent", "message": message})

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "soul_connected": soul.connected,
        "core_connected": soul.core.connected
    })

if __name__ == "__main__":
    app.run(debug=True, port=5050)
