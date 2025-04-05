from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Soul Flask Server is running."

@app.route('/run_command', methods=['POST'])
def run_command():
    data = request.get_json()
    command = data.get("command")

    if not command:
        return jsonify({"status": "error", "message": "No command sent"})

    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return jsonify({"status": "success", "output": output.decode('utf-8')})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "output": e.output.decode('utf-8')})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5007)
