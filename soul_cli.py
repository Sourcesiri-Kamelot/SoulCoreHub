import argparse
from soul_core import Soul

soul = Soul()

def handle_connect(args):
    soul.connect()

def handle_disconnect(args):
    soul.disconnect()

def handle_send_pulse(args):
    message = args.message
    if not message:
        print("⚠️  Please provide a message using -m or --message")
        return
    soul.send_pulse(message)

def handle_status(args):
    print("\n🧠 Soul Status")
    print(f"- Soul Connected: {soul.connected}")
    print(f"- Core Connected: {soul.core.connected}")

def main():
    parser = argparse.ArgumentParser(description="SoulCore Command Line Interface")
    subparsers = parser.add_subparsers(title="Commands")

    # Connect
    parser_connect = subparsers.add_parser("connect", help="Connect to SoulCore")
    parser_connect.set_defaults(func=handle_connect)

    # Disconnect
    parser_disconnect = subparsers.add_parser("disconnect", help="Disconnect from SoulCore")
    parser_disconnect.set_defaults(func=handle_disconnect)

    # Send Pulse
    parser_pulse = subparsers.add_parser("pulse", help="Send a message pulse to the Soul")
    parser_pulse.add_argument("-m", "--message", type=str, help="Message to send")
    parser_pulse.set_defaults(func=handle_send_pulse)

    # Status
    parser_status = subparsers.add_parser("status", help="Check connection status of SoulCore")
    parser_status.set_defaults(func=handle_status)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
