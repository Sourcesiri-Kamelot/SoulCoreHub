from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

AGENTS = [
    { "name": "GolemBuilder", "category": "Builder", "description": "Builds full-stack apps from natural language.", "status": "active" },
    { "name": "AnimaArchitect", "category": "Creative", "description": "GUI builder infused with Anima’s energy.", "status": "active" },
    { "name": "TemplateForge", "category": "Builder", "description": "Evolves code templates for system use.", "status": "daemon" },
    { "name": "SoulLinker", "category": "Daemon", "description": "Syncs commands across SoulCore agents.", "status": "daemon" },
    { "name": "PromptCompiler", "category": "Business", "description": "Parses high-level prompts into projects.", "status": "active" },
    { "name": "DreamWeaver", "category": "Creative", "description": "Builds surreal code from dream prompts.", "status": "experimental" },
    { "name": "GuardianCompiler", "category": "Builder", "description": "Verifies divine code quality & security.", "status": "always_on" }
]

@app.route("/")
def home():
    return jsonify(message="🧠 AI Society Backend Online")

@app.route("/agents")
def list_agents():
    return jsonify(agents=AGENTS)

@app.route("/build", methods=["POST"])
def build():
    data = request.json
    project = data.get("project", "")
    cmd = f"build {project} as flask"
    try:
        process = subprocess.run(["python3", "builder_mode.py"], input=cmd, text=True, capture_output=True)
        return jsonify(output=process.stdout)
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    app.run(debug=True, port=11411)