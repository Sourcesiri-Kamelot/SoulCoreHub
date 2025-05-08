import os
import json
import re
import asyncio
from datetime import datetime
from pathlib import Path
import subprocess
from jsonrpcserver import method, serve
import sys

def read_file(path):
    from pathlib import Path
    return Path(path).read_text()

def write_file(path, content):
    from pathlib import Path
    Path(path).write_text(content)

PROJECTS_DIR = Path("~/SoulCoreHub/projects").expanduser()
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

def gptsoul_nlp(prompt):
    try:
        injected = f"""
You are SoulBuilder. Return ONLY valid JSON like this:

{{
  "name": "project_name",
  "type": "flask",
  "features": ["login", "upload"]
}}

Prompt: {prompt}
Only return JSON. No explanation.
"""
        result = subprocess.run(
            ["ollama", "run", "gpt-soul", injected],
            capture_output=True,
            text=True
        )
        raw = result.stdout.strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1
        json_data = raw[start:end]
        return json.loads(json_data)
    except Exception as e:
        print(f"❌ GPTSoul NLP failed: {e}")
        return {"name": "project", "type": "python", "features": []}

def scaffold_project(name, kind, features):
    folder = PROJECTS_DIR / name
    folder.mkdir(parents=True, exist_ok=True)

    ext = {"flask": "py", "html": "html", "python": "py", "node": "js"}.get(kind, "txt")
    main_file = folder / f"{name}.{ext}"
    content = TEMPLATES.get(kind, "").strip().format(name=name)
    main_file.write_text(content)

    for feat in features:
        (folder / f"{feat}.py").write_text(f"# {feat.title()} feature\n")

    (folder / "manifest.json").write_text(json.dumps({
        "name": name,
        "type": kind,
        "features": features,
        "created": datetime.now().isoformat()
    }, indent=2))

    # ✅ Now correctly placed
    build_log = folder / "build_log.txt"
    build_log.write_text(
        f"🔧 Project: {name}\n🧠 Type: {kind}\n🧩 Features: {', '.join(features)}\n🕒 Created: {datetime.now().isoformat()}"
    )

    print(f"\n✅ Built {kind} project: {name}")
    print("🧩 Features:", ", ".join(features))

def soul_cli():
    print("\n⚡ SoulBuilder CLI Online.")
    print("Type 'build [idea]' or 'exit'\n")

    while True:
        try:
            user_input = input("🛠️  > ").strip().lower()

            if user_input in ["exit", "quit"]:
                break

            elif user_input.startswith("build "):
                prompt = user_input.replace("build ", "")
                nlp = gptsoul_nlp(prompt)
                name = re.sub(r"[^\w]", "", nlp.get("name", "project"))
                kind = nlp.get("type", "python")
                features = nlp.get("features", [])
                scaffold_project(name, kind, features)

            elif user_input.startswith("design"):
                print("🎨 UX design initialized (placeholder)")

            elif user_input.startswith("summon"):
                agent = user_input.split(" ")[-1]
                print(f"🌀 Summoning agent: {agent}...")

            elif user_input.startswith("connect"):
                print("🔌 Connecting to backend or DB (mock)")

            elif user_input.startswith("deploy"):
                print("🚀 Deploying project (mock)")

            elif user_input.startswith("doc"):
                print("📄 Generating documentation...")

            elif user_input.startswith("refactor"):
                print("🔧 Refactoring codebase...")

            elif user_input in ["help", "commands"]:
                print("""
📜 SoulBuilder CLI Commands:
  build [prompt]      → Natural language build
  design              → UX sketch (stub)
  summon [agent]      → Activate SoulCore agent
  connect             → Connect DB/API
  deploy              → Launch app (stub)
  doc                 → Document project
  refactor            → Rebuild structure
  exit                → Exit CLI
""")

            else:
                print("❌ Unknown command. Type 'help'.")

        except KeyboardInterrupt:
            print("\n👋 Exiting SoulBuilder.")
            break

#🧠 MCP Server: SoulBuilder as a Remote Tool
@method
def build_app(prompt: str):
    from builder_mode import gptsoul_nlp, scaffold_project
    nlp = gptsoul_nlp(prompt)
    name = re.sub(r"[^\w]", "", nlp.get("name", "project"))
    kind = nlp.get("type", "python")
    features = nlp.get("features", [])
    scaffold_project(name, kind, features)
    return {"status": "success", "project": name, "features": features}

if __name__ == "__main__":
    if "--mode" in sys.argv and "mcp" in sys.argv:
        print("🧠 SoulBuilder JSON-RPC Server Online. Send build_app requests.")
        serve()  # Listens to stdin like MCP
    else:
        soul_cli()

