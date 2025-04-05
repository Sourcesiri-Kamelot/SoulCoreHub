from flask import Flask, request
import subprocess
import os
from datetime import datetime

app = Flask(__name__)
log_path = os.path.expanduser("~/SoulCoreHub/logs/action_response.log")
os.makedirs(os.path.dirname(log_path), exist_ok=True)

@app.route("/run")
def run_command():
    cmd = request.args.get("cmd")
    if not cmd:
        return "No command provided."

    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf-8")
    except subprocess.CalledProcessError as e:
        result = e.output.decode("utf-8")

    log_entry = f"[{datetime.now().isoformat()}] Ran: {cmd}\n{result}\n"
    with open(log_path, "a") as f:
        f.write(log_entry)

    return result or "✅ Done."

if __name__ == "__main__":
    app.run(debug=False)
