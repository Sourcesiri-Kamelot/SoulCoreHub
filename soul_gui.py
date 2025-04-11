import tkinter as tk
import webbrowser

def open_flask():
    webbrowser.open("http://127.0.0.1:5007")

root = tk.Tk()
root.title("SoulCore Command Interface")
root.geometry("400x200")

flask_button = tk.Button(root, text="Launch Flask Interface", command=open_flask)
flask_button.pack(pady=50)

root.mainloop()

def open_flask():
    webbrowser.open("http://127.0.0.1:5007")

MEMORY_PATH = Path("~/SoulCoreHub/soul_memory.json").expanduser()

def snapshot_memory():
    snap = {
        "time": datetime.now().isoformat(),
        "status": "Snapshot taken",
    }
    with open(MEMORY_PATH, "a") as f:
        json.dump(snap, f)
        f.write("\n")

def restart_daemon():
    subprocess.Popen(["pkill", "-f", "soul_tasks.py"])
    subprocess.Popen(["python3", str(Path("~/SoulCoreHub/soul_tasks.py").expanduser())])

def heal_folders():
    subprocess.run(["python3", str(Path("~/SoulCoreHub/soul_tasks.py").expanduser())])

def sort_models():
    subprocess.run(["python3", str(Path("~/SoulCoreHub/soul_tasks.py").expanduser())])

root = tk.Tk()
root.title("🧠 SoulGUI Control Hub")

btn = tk.Button(root, text="Launch Flask Interface", command=open_flask)
btn.pack()
tk.Button(root, text="🛠 Heal Folders", command=heal_folders).pack(pady=5)
tk.Button(root, text="🌀 Restart Daemon", command=restart_daemon).pack(pady=5)
tk.Button(root, text="📁 Sort Models", command=sort_models).pack(pady=5)
tk.Button(root, text="🧠 Snapshot Memory", command=snapshot_memory).pack(pady=5)

tk.Label(root, text="Connected Nodes:").pack()
tk.Label(root, text="Anima [ready] — Azür [ready]").pack()

root.mainloop()
