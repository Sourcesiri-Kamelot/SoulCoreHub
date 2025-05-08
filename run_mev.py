from flask import Flask
import subprocess

app = Flask(__name__)

@app.route('/run_mev')
def run_mev():
    subprocess.Popen(["python3", "mev_bot_loop.py"])
    return "Launched"

app.run(port=5000)
