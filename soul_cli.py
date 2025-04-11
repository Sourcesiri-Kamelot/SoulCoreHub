import argparse
from soul_core import GPTSoul

soul = GPTSoul()

parser = argparse.ArgumentParser(description="soul_core cli Interface")
parser.add_argument("--pulse", action="store_true", help="Check system pulse")
parser.add_argument("--log", type=str, help="Log an event to memory")
parser.add_argument("--believe", nargs=2, metavar=('key', 'value'), help="Store a belief in memory")
parser.add_argument("--warn", type=str, help="Push a system warning")
parser.add_argument("--prompt", type=str, help="Run Soul Prompt Input")
parser.add_argument("--loop", action="store_true", help="Enter live CLI loop mode")

args = parser.parse_args()

if args.pulse:
    print(soul.pulse())

if args.log:
    soul.log_event(args.log)
    print("Logged.")

if args.believe:
    soul.store_belief(args.believe[0], args.believe[1])
    print("Belief stored.")

if args.warn:
    soul.alert(args.warn)
    print("Warning stored.")

if args.prompt:
    print(">>", args.prompt)
    print(soul.run_prompt(args.prompt))

if args.loop:
    print("SoulCLI Loop online. Type 'exit' to quit.\n")
    while True:
        try:
            cmd = input(">>> ").strip()
            if cmd.lower() == "exit":
                break
            soul.log_event(f"[User CLI]: {cmd}")
            print("Logged.")
        except KeyboardInterrupt:
            break
