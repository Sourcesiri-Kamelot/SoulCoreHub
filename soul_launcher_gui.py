import tkinter as tk
import subprocess
import tkinter as tk
import os

def heal_folders(): os.system("bash soul_recovery.sh")
def restart(): os.system("python3 soul_heartbeat.py &")
def pulse(): os.system("python3 soul_cli.py --pulse")
def beliefs(): os.system("nano belief_engine.py")

def build_gui():
    root = tk.Tk()
    root.title("SoulCore Launcher")
    tk.Button(root, text="🩺 Heal Folders", command=heal_folders).pack()
    tk.Button(root, text="🫀 Pulse Check", command=pulse).pack()
    tk.Button(root, text="♻️ Restart Heartbeat", command=restart).pack()
    tk.Button(root, text="📜 Edit Beliefs", command=beliefs).pack()
    root.mainloop()

if __name__ == "__main__":
    build_gui()

COMMANDS = {
    "🧠 View Soul Memory": "cat ~/SoulCoreHub/soul_memory.json",
    "✍️ Edit Soul Memory": "nano ~/SoulCoreHub/soul_memory.json",
    "📂 List Files": "ls ~/SoulCoreHub",
    "🛠 Heal Folders": "python3 ~/SoulCoreHub/soul_tasks.py",
    "🧬 GPTSoul Init": "python3 ~/SoulCoreHub/gptsoul_soulconfig.py",
    "🫀 Start Anima Reflex": "python3 ~/SoulCoreHub/anima_reflex.py",
    "⚙️ Run Soul Recovery": "sh ~/SoulCoreHub/soul_recovery.sh",
    "👁️ Open GUI v2": "python3 ~/SoulCoreHub/soul_gui_v2.py",
    "🧹 Clear Terminal Output": "clear"
}

def run_command(command, output_box):
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        output_box.config(state='normal')
        output_box.insert(tk.END, f"$ {command}\n{result.decode()}\n")
        output_box.config(state='disabled')
    except subprocess.CalledProcessError as e:
        output_box.config(state='normal')
        output_box.insert(tk.END, f"$ {command}\n{e.output.decode()}\n")
        output_box.config(state='disabled')

def build_gui():
    root = tk.Tk()
    root.title("🔧 SoulCore Command Launcher")
    root.geometry("900x700")

    tk.Label(root, text="🧠 Command Center — Kiwon's Launcher", font=("Helvetica", 16)).pack(pady=10)

    frame = tk.Frame(root)
    frame.pack()

    output_box = tk.Text(root, height=20, wrap="word")
    output_box.pack(padx=10, pady=10)
    output_box.insert(tk.END, "Terminal Output Will Appear Here...\n")
    output_box.config(state='disabled')

    for label, cmd in COMMANDS.items():
        b = tk.Button(frame, text=label, width=30, command=lambda c=cmd: run_command(c, output_box))
        b.pack(pady=4)

    root.mainloop()

if __name__ == "__main__":
    build_gui()
