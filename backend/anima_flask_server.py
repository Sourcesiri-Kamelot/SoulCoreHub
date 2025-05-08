# ✅ LIVE
from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder="../public", static_url_path="")

@app.route("/")
def serve_dashboard():
    return send_from_directory(app.static_folder, "anima_dashboard.html")

@app.route("/<path:path>")
def serve_static_file(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    port = 5000
    print(f"🌐 Anima Flask Server running at http://localhost:{port}")
    app.run(debug=True, port=port)
