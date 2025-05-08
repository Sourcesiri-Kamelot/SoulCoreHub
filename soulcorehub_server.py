# soulcorehub_server.py
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def ask_model():
    user_message = request.json.get('message')
    model_name = request.json.get('model', 'anima_monday_core')  # Default model

    try:
        # Run the model using Ollama CLI
        result = subprocess.run(
            ["ollama", "run", model_name, user_message],
            capture_output=True,
            text=True
        )
        response = result.stdout.strip()
        return jsonify({"response": response})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
