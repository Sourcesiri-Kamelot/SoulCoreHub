def main():
    """Main entry point for EvoVe."""
    parser = argparse.ArgumentParser(description="EvoVe Autonomous System")
    parser.add_argument("--config", help="Path to configuration file", default="config/evove_config.json")
    parser.add_argument("--repair", help="Repair mode", action="store_true")
    parser.add_argument("--monitor", help="Monitor mode only", action="store_true")
    parser.add_argument("--voice", help="Process a voice command", type=str)
    parser.add_argument("--build", help="Add a build task", type=str)
    parser.add_argument("--reflect", help="Generate a reflection", action="store_true")
    args = parser.parse_args()
    
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("backups", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    # Initialize EvoVe
    evove = EvoVe(args.config)
    
    if args.voice:
        # Process voice command
        if hasattr(evove, "voice_command"):
            result = evove.voice_command.process_command(args.voice)
            print(json.dumps(result, indent=2))
        else:
            print("Voice command module not available")
    elif args.build:
        # Add a build task
        if hasattr(evove, "build_queue"):
            evove.build_queue.start()
            task = evove.build_queue.add_task("command", "Custom Command", {"command": args.build})
            print(f"Task added to build queue: {task['id']}")
            evove.build_queue.stop()
        else:
            print("Build queue module not available")
    elif args.reflect:
        # Generate a reflection
        if hasattr(evove, "reflection"):
            reflection = evove.reflection._create_reflection()
            print(json.dumps(reflection, indent=2))
        else:
            print("Reflection module not available")
    elif args.repair:
        # Run in repair mode
        logger.info("Running in repair mode")
        evove.repair_mcp()
    elif args.monitor:
        # Run in monitor mode
        logger.info("Running in monitor mode")
        evove.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            evove.stop()
    else:
        # Run in full mode
        evove.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            evove.stop()

