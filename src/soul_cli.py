import argparse
import json
from soul_core import GPTSoul

soul = GPTSoul()

parser = argparse.ArgumentParser(description="SoulCore CLI Interface")

# Core commands
parser.add_argument("--pulse", action="store_true", help="Check system pulse")
parser.add_argument("--log", type=str, help="Log an event to memory")
parser.add_argument("--believe", nargs=2, metavar=('key', 'value'), help="Store a belief in memory")
parser.add_argument("--warn", type=str, help="Push a system warning")
parser.add_argument("--prompt", type=str, help="Run Soul Prompt Input")
parser.add_argument("--loop", action="store_true", help="Enter live CLI loop mode")

# --- QRDS Commands ---
parser.add_argument("--store_resonance", nargs=3, metavar=('data_point', 'emotion', 'value'), help="Store emotional resonance data")
parser.add_argument("--get_resonance", type=str, metavar='emotion', help="Get emotional resonance data for an emotion")
parser.add_argument("--get_all_resonance", action="store_true", help="Get all emotional resonance data")

# --- Psynet Commands ---
parser.add_argument("--store_prediction", nargs=3, metavar=('data_point', 'prediction', 'confidence'), help="Store future prediction data")
parser.add_argument("--get_prediction", type=str, metavar='data_point', help="Get prediction for a data point")
parser.add_argument("--get_all_predictions", action="store_true", help="Get all future prediction data")

args = parser.parse_args()

# Core functionality
if args.pulse:
    print(json.dumps(soul.pulse(), indent=2))

if args.log:
    soul.log_event(args.log)
    print("Event logged.")

if args.believe:
    soul.store_belief(args.believe[0], args.believe[1])
    print("Belief stored.")

if args.warn:
    soul.alert(args.warn)
    print("Warning issued and logged.")

if args.prompt:
    print("Prompt:", args.prompt)
    # Placeholder for real prompt execution
    print("Prompt executed (placeholder).")

if args.loop:
    print("🔄 SoulCLI Loop online. Type 'exit' to quit.\n")
    while True:
        try:
            cmd = input(">>> ").strip()
            if cmd.lower() == "exit":
                break
            soul.log_event(f"[User CLI]: {cmd}")
            print("Command logged.")
        except KeyboardInterrupt:
            print("\nCLI loop exited.")
            break

# --- QRDS functionality ---
if args.store_resonance:
    data_point, emotion, value = args.store_resonance
    soul.store_resonance_data(data_point, emotion, float(value))
    print("Resonance data stored.")

if args.get_resonance:
    data = soul.get_resonance_data(args.get_resonance)
    print(json.dumps(data, indent=2))

if args.get_all_resonance:
    data = soul.get_resonance_data()
    print(json.dumps(data, indent=2))

# --- Psynet functionality ---
if args.store_prediction:
    data_point, prediction, confidence = args.store_prediction
    soul.store_prediction(data_point, prediction, float(confidence))
    print("Prediction data stored.")

if args.get_prediction:
    data = soul.get_prediction(args.get_prediction)
    print(json.dumps(data, indent=2))

if args.get_all_predictions:
    data = soul.get_all_predictions()
    print(json.dumps(data, indent=2))
