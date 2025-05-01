import argparse
import json
import os
import sys

# Add parent directory to path to import EvoVe modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.quantum_ready import QuantumReady

def main():
    """Main entry point for Quantum CLI."""
    parser = argparse.ArgumentParser(description="EvoVe Quantum CLI")
    parser.add_argument("--state-file", help="Path to quantum state file", default="data/quantum_state.json")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Entangle command
    entangle_parser = subparsers.add_parser("entangle", help="Entangle two agents")
    entangle_parser.add_argument("agent_a", help="First agent")
    entangle_parser.add_argument("agent_b", help="Second agent")
    
    # Disentangle command
    disentangle_parser = subparsers.add_parser("disentangle", help="Disentangle two agents")
    disentangle_parser.add_argument("agent_a", help="First agent")
    disentangle_parser.add_argument("agent_b", help="Second agent")
    
    # Observe command
    observe_parser = subparsers.add_parser("observe", help="Observe a quantum state")
    observe_parser.add_argument("condition", help="Condition to observe")
    
    # Add superposition command
    superposition_parser = subparsers.add_parser("superposition", help="Add a superposition")
    superposition_parser.add_argument("event", help="Event name")
    superposition_parser.add_argument("outcomes", help="Outcomes JSON")
    
    # Get state command
    subparsers.add_parser("state", help="Get quantum state")
    
    # Simulate decision command
    decision_parser = subparsers.add_parser("decide", help="Simulate a quantum decision")
    decision_parser.add_argument("options", help="Options JSON array")
    decision_parser.add_argument("--weights", help="Weights JSON array (optional)")
    
    args = parser.parse_args()
    
    # Create quantum readiness module
    qr = QuantumReady(state_file=args.state_file)
    
    if args.command == "entangle":
        result = qr.entangle(args.agent_a, args.agent_b)
        print(result)
    elif args.command == "disentangle":
        result = qr.disentangle(args.agent_a, args.agent_b)
        print(result)
    elif args.command == "observe":
        result = qr.observe(args.condition)
        print(result)
    elif args.command == "superposition":
        try:
            outcomes = json.loads(args.outcomes)
            result = qr.add_superposition(args.event, outcomes)
            print(result)
        except json.JSONDecodeError:
            print("Error: Outcomes must be valid JSON")
    elif args.command == "state":
        state = qr.get_quantum_state()
        print(json.dumps(state, indent=2))
    elif args.command == "decide":
        try:
            options = json.loads(args.options)
            weights = json.loads(args.weights) if args.weights else None
            result = qr.simulate_quantum_decision(options, weights)
            print(f"Decision: {result}")
        except json.JSONDecodeError:
            print("Error: Options and weights must be valid JSON")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

