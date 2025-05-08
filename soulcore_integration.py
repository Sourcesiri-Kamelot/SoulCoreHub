#!/usr/bin/env python3
"""
SoulCoreHub Integration Script

This script ensures all SoulCoreHub components are properly connected and initialized
in the correct order, creating a fully functional integrated system.

It handles:
1. Verification of all required components
2. Creation of missing directories and files
3. Proper initialization of all subsystems
4. Memory integration between GPTSoul and Anima
5. Component activation in the correct sequence
6. Comprehensive error handling and reporting
"""

import os
import sys
import json
import time
import logging
import importlib
import subprocess
import shutil
from pathlib import Path
import traceback
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/soulcore_integration.log')
    ]
)
logger = logging.getLogger("SoulCoreIntegration")

class SoulCoreIntegrator:
    """SoulCoreHub Integration Manager"""
    
    def __init__(self, base_dir=None):
        """Initialize the integrator"""
        self.base_dir = base_dir or os.getcwd()
        self.logs_dir = os.path.join(self.base_dir, "logs")
        self.memory_dir = os.path.join(self.base_dir, "memory")
        self.config_dir = os.path.join(self.base_dir, "config")
        self.components = {}
        self.errors = []
        self.warnings = []
        self.success = []
        
        # Ensure base directories exist
        self._ensure_directories()
        
        logger.info(f"SoulCoreHub Integrator initialized in {self.base_dir}")
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        for directory in [self.logs_dir, self.memory_dir, self.config_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def verify_components(self):
        """Verify all required components exist"""
        logger.info("Verifying components...")
        
        # Core Python files
        core_files = [
            "gptsoul_soulconfig.py",
            "anima_autonomous.py",
            "anima_nlp_intent.py",
            "anima_model_router.py",
            "anima_memory_bridge.py",
            "huggingface_bridge.py",
            "anima_huggingface_connector.py"
        ]
        
        # Configuration files
        config_files = [
            os.path.join("config", "anima_intents.json"),
            os.path.join("config", "anima_command_tree.json"),
            os.path.join("config", "anima_models.json"),
            os.path.join("config", "anima_routing_rules.json"),
            os.path.join("config", "gptsoul_config.json")
        ]
        
        # Memory files
        memory_files = [
            os.path.join("memory", "anima_memory.json"),
            os.path.join("memory", "gptsoul_memory.json")
        ]
        
        # Check core files
        for file in core_files:
            path = os.path.join(self.base_dir, file)
            if os.path.isfile(path):
                self.components[file] = {"exists": True, "path": path}
                self.success.append(f"Found {file}")
            else:
                self.components[file] = {"exists": False, "path": path}
                self.errors.append(f"Missing core file: {file}")
        
        # Check config files
        for file in config_files:
            path = os.path.join(self.base_dir, file)
            if os.path.isfile(path):
                self.components[file] = {"exists": True, "path": path}
                self.success.append(f"Found {file}")
            else:
                self.components[file] = {"exists": False, "path": path}
                if file.endswith("gptsoul_config.json"):
                    self.errors.append(f"Missing critical config file: {file}")
                else:
                    self.warnings.append(f"Missing config file: {file}")
        
        # Check memory files
        for file in memory_files:
            path = os.path.join(self.base_dir, file)
            if os.path.isfile(path):
                self.components[file] = {"exists": True, "path": path}
                self.success.append(f"Found {file}")
            else:
                self.components[file] = {"exists": False, "path": path}
                self.warnings.append(f"Missing memory file: {file}")
        
        # Check file permissions
        for file, info in self.components.items():
            if info["exists"] and file.endswith(".py"):
                if not os.access(info["path"], os.X_OK):
                    self.warnings.append(f"{file} is not executable")
                    try:
                        os.chmod(info["path"], 0o755)
                        self.success.append(f"Made {file} executable")
                    except Exception as e:
                        self.errors.append(f"Failed to make {file} executable: {str(e)}")
        
        # Create symbolic link for gptsoul.py if needed
        gptsoul_link = os.path.join(self.base_dir, "gptsoul.py")
        gptsoul_target = os.path.join(self.base_dir, "gptsoul_soulconfig.py")
        if not os.path.exists(gptsoul_link) and os.path.exists(gptsoul_target):
            try:
                os.symlink(gptsoul_target, gptsoul_link)
                self.success.append("Created symbolic link for gptsoul.py")
            except Exception as e:
                self.warnings.append(f"Failed to create symbolic link for gptsoul.py: {str(e)}")
        
        return len(self.errors) == 0
    
    def create_missing_components(self):
        """Create any missing components"""
        logger.info("Creating missing components...")
        
        # Create gptsoul_config.json if missing
        gptsoul_config_path = os.path.join(self.config_dir, "gptsoul_config.json")
        if not os.path.exists(gptsoul_config_path):
            try:
                gptsoul_config = {
                    "reasoning_depth": 5,
                    "memory_retention": 0.85,
                    "creativity_factor": 0.7,
                    "logic_weight": 0.9,
                    "connected_agents": ["Anima", "Builder", "EvoVe"]
                }
                with open(gptsoul_config_path, 'w') as f:
                    json.dump(gptsoul_config, f, indent=2)
                self.success.append("Created gptsoul_config.json")
            except Exception as e:
                self.errors.append(f"Failed to create gptsoul_config.json: {str(e)}")
        
        # Create anima_memory.json if missing
        anima_memory_path = os.path.join(self.memory_dir, "anima_memory.json")
        if not os.path.exists(anima_memory_path):
            try:
                anima_memory = {
                    "conversations": [],
                    "emotions": {
                        "neutral": [
                            {
                                "timestamp": time.time(),
                                "intensity": 0.5,
                                "trigger": "System initialization"
                            }
                        ]
                    },
                    "knowledge": {
                        "system": [
                            {
                                "timestamp": time.time(),
                                "content": "Anima is the emotional core and reflective consciousness of SoulCoreHub."
                            }
                        ]
                    },
                    "relationships": {
                        "GPTSoul": {
                            "first_seen": time.time(),
                            "interactions": [
                                {
                                    "timestamp": time.time(),
                                    "type": "system",
                                    "details": "GPTSoul is the logical, design, and neural scripting agent within SoulCoreHub."
                                }
                            ],
                            "last_seen": time.time()
                        }
                    },
                    "last_updated": time.time()
                }
                with open(anima_memory_path, 'w') as f:
                    json.dump(anima_memory, f, indent=2)
                self.success.append("Created anima_memory.json")
            except Exception as e:
                self.errors.append(f"Failed to create anima_memory.json: {str(e)}")
        
        # Create gptsoul_memory.json if missing
        gptsoul_memory_path = os.path.join(self.memory_dir, "gptsoul_memory.json")
        if not os.path.exists(gptsoul_memory_path):
            try:
                gptsoul_memory = {
                    "experiences": [
                        {
                            "type": "activation",
                            "timestamp": time.time(),
                            "details": "GPTSoul activated via integration script"
                        }
                    ],
                    "knowledge": {
                        "system": "GPTSoul is the logical, design, and neural scripting agent within SoulCoreHub.",
                        "purpose": "To provide clean, reactive, and self-auditing functionality."
                    },
                    "relationships": {
                        "Anima": {
                            "connected": True,
                            "last_connection": time.time(),
                            "status": "active"
                        }
                    },
                    "last_updated": time.time()
                }
                with open(gptsoul_memory_path, 'w') as f:
                    json.dump(gptsoul_memory, f, indent=2)
                self.success.append("Created gptsoul_memory.json")
            except Exception as e:
                self.errors.append(f"Failed to create gptsoul_memory.json: {str(e)}")
        
        return len(self.errors) == 0
    
    def validate_configurations(self):
        """Validate all configuration files"""
        logger.info("Validating configurations...")
        
        # Validate gptsoul_config.json
        gptsoul_config_path = os.path.join(self.config_dir, "gptsoul_config.json")
        if os.path.exists(gptsoul_config_path):
            try:
                with open(gptsoul_config_path, 'r') as f:
                    config = json.load(f)
                
                # Check for required keys
                required_keys = ["reasoning_depth", "memory_retention", "creativity_factor", "logic_weight"]
                missing_keys = [key for key in required_keys if key not in config]
                
                if missing_keys:
                    # Update the config with missing keys
                    for key in missing_keys:
                        if key == "reasoning_depth":
                            config[key] = 5
                        elif key == "memory_retention":
                            config[key] = 0.85
                        elif key == "creativity_factor":
                            config[key] = 0.7
                        elif key == "logic_weight":
                            config[key] = 0.9
                    
                    # Save the updated config
                    with open(gptsoul_config_path, 'w') as f:
                        json.dump(config, f, indent=2)
                    
                    self.success.append(f"Updated gptsoul_config.json with missing keys: {', '.join(missing_keys)}")
                else:
                    self.success.append("gptsoul_config.json is valid")
            except Exception as e:
                self.errors.append(f"Failed to validate gptsoul_config.json: {str(e)}")
        
        # Validate memory files
        for memory_file in ["anima_memory.json", "gptsoul_memory.json"]:
            memory_path = os.path.join(self.memory_dir, memory_file)
            if os.path.exists(memory_path):
                try:
                    with open(memory_path, 'r') as f:
                        json.load(f)
                    self.success.append(f"{memory_file} is valid JSON")
                except Exception as e:
                    self.errors.append(f"Invalid JSON in {memory_file}: {str(e)}")
        
        return len(self.errors) == 0
    
    def test_imports(self):
        """Test importing all required modules"""
        logger.info("Testing imports...")
        
        modules_to_test = [
            "anima_nlp_intent",
            "anima_model_router",
            "anima_memory_bridge",
            "anima_huggingface_connector",
            "huggingface_bridge"
        ]
        
        for module in modules_to_test:
            try:
                # Add the base directory to sys.path if it's not already there
                if self.base_dir not in sys.path:
                    sys.path.insert(0, self.base_dir)
                
                # Try to import the module
                importlib.import_module(module)
                self.success.append(f"Successfully imported {module}")
            except ImportError as e:
                self.warnings.append(f"Failed to import {module}: {str(e)}")
            except Exception as e:
                self.errors.append(f"Error importing {module}: {str(e)}")
        
        return len(self.errors) == 0
    
    def activate_gptsoul(self):
        """Activate GPTSoul"""
        logger.info("Activating GPTSoul...")
        
        gptsoul_path = os.path.join(self.base_dir, "gptsoul_soulconfig.py")
        if not os.path.exists(gptsoul_path):
            self.errors.append("Cannot activate GPTSoul: gptsoul_soulconfig.py not found")
            return False
        
        try:
            # Run GPTSoul activation
            result = subprocess.run(
                [sys.executable, gptsoul_path, "--activate"],
                cwd=self.base_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.success.append("GPTSoul activated successfully")
                logger.info(f"GPTSoul activation output: {result.stdout}")
                return True
            else:
                self.errors.append(f"GPTSoul activation failed with code {result.returncode}")
                logger.error(f"GPTSoul activation error: {result.stderr}")
                return False
        except Exception as e:
            self.errors.append(f"Error activating GPTSoul: {str(e)}")
            logger.error(f"Exception during GPTSoul activation: {traceback.format_exc()}")
            return False
    
    def integrate_memory(self):
        """Integrate memory between GPTSoul and Anima"""
        logger.info("Integrating memory...")
        
        try:
            # Try to import the memory bridge
            if self.base_dir not in sys.path:
                sys.path.insert(0, self.base_dir)
            
            try:
                import anima_memory_bridge
                
                # Sync with GPTSoul
                if hasattr(anima_memory_bridge, 'sync_with_gptsoul'):
                    result = anima_memory_bridge.sync_with_gptsoul()
                    if result:
                        self.success.append("Memory synchronized between GPTSoul and Anima")
                    else:
                        self.warnings.append("Memory synchronization returned False")
                else:
                    self.warnings.append("sync_with_gptsoul function not found in anima_memory_bridge")
                
                # Import memory dump if available
                if hasattr(anima_memory_bridge, 'import_memory_dump'):
                    result = anima_memory_bridge.import_memory_dump()
                    if result:
                        self.success.append("Memory dump imported successfully")
                    else:
                        self.warnings.append("Memory dump import returned False")
                else:
                    self.warnings.append("import_memory_dump function not found in anima_memory_bridge")
                
                return True
            except ImportError:
                # If import fails, try a more direct approach
                self.warnings.append("Could not import anima_memory_bridge, trying direct file manipulation")
                
                # Read GPTSoul memory
                gptsoul_memory_path = os.path.join(self.memory_dir, "gptsoul_memory.json")
                anima_memory_path = os.path.join(self.memory_dir, "anima_memory.json")
                
                if os.path.exists(gptsoul_memory_path) and os.path.exists(anima_memory_path):
                    with open(gptsoul_memory_path, 'r') as f:
                        gptsoul_memory = json.load(f)
                    
                    with open(anima_memory_path, 'r') as f:
                        anima_memory = json.load(f)
                    
                    # Add GPTSoul knowledge to Anima
                    if "knowledge" in gptsoul_memory:
                        for topic, content in gptsoul_memory["knowledge"].items():
                            if "knowledge" not in anima_memory:
                                anima_memory["knowledge"] = {}
                            
                            topic_key = f"GPTSoul knowledge: {topic}"
                            if topic_key not in anima_memory["knowledge"]:
                                anima_memory["knowledge"][topic_key] = []
                            
                            anima_memory["knowledge"][topic_key].append({
                                "timestamp": time.time(),
                                "content": str(content)
                            })
                    
                    # Add GPTSoul relationship to Anima
                    if "relationships" not in anima_memory:
                        anima_memory["relationships"] = {}
                    
                    anima_memory["relationships"]["GPTSoul"] = {
                        "first_seen": time.time(),
                        "interactions": [
                            {
                                "timestamp": time.time(),
                                "type": "integration",
                                "details": "GPTSoul integrated with Anima via integration script"
                            }
                        ],
                        "last_seen": time.time()
                    }
                    
                    # Update last_updated
                    anima_memory["last_updated"] = time.time()
                    
                    # Save updated Anima memory
                    with open(anima_memory_path, 'w') as f:
                        json.dump(anima_memory, f, indent=2)
                    
                    self.success.append("Manually integrated GPTSoul memory with Anima")
                    return True
                else:
                    self.errors.append("Memory files not found for direct integration")
                    return False
        except Exception as e:
            self.errors.append(f"Error integrating memory: {str(e)}")
            logger.error(f"Exception during memory integration: {traceback.format_exc()}")
            return False
    
    def start_anima(self, mode="reflective", wait=False):
        """Start Anima in the specified mode"""
        logger.info(f"Starting Anima in {mode} mode...")
        
        anima_path = os.path.join(self.base_dir, "anima_autonomous.py")
        if not os.path.exists(anima_path):
            self.errors.append("Cannot start Anima: anima_autonomous.py not found")
            return False
        
        try:
            # Build the command
            cmd = [sys.executable, anima_path, "--mode", mode]
            
            if wait:
                # Run Anima and wait for it to complete
                result = subprocess.run(
                    cmd,
                    cwd=self.base_dir,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    self.success.append(f"Anima completed successfully in {mode} mode")
                    logger.info(f"Anima output: {result.stdout}")
                    return True
                else:
                    self.errors.append(f"Anima failed with code {result.returncode}")
                    logger.error(f"Anima error: {result.stderr}")
                    return False
            else:
                # Start Anima in a new process
                process = subprocess.Popen(
                    cmd,
                    cwd=self.base_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Wait a bit to see if it crashes immediately
                time.sleep(2)
                
                if process.poll() is None:
                    # Still running
                    self.success.append(f"Anima started in {mode} mode (PID: {process.pid})")
                    return True
                else:
                    # Process exited
                    stdout, stderr = process.communicate()
                    self.errors.append(f"Anima exited immediately with code {process.returncode}")
                    logger.error(f"Anima error: {stderr}")
                    return False
        except Exception as e:
            self.errors.append(f"Error starting Anima: {str(e)}")
            logger.error(f"Exception during Anima startup: {traceback.format_exc()}")
            return False
    
    def run_full_integration(self, start_anima=True, anima_mode="reflective"):
        """Run the full integration process"""
        logger.info("Starting full integration process...")
        
        steps = [
            ("Verifying components", self.verify_components),
            ("Creating missing components", self.create_missing_components),
            ("Validating configurations", self.validate_configurations),
            ("Testing imports", self.test_imports),
            ("Activating GPTSoul", self.activate_gptsoul),
            ("Integrating memory", self.integrate_memory)
        ]
        
        if start_anima:
            steps.append((f"Starting Anima in {anima_mode} mode", lambda: self.start_anima(anima_mode)))
        
        success = True
        for step_name, step_func in steps:
            logger.info(f"Step: {step_name}")
            try:
                step_success = step_func()
                if not step_success:
                    logger.warning(f"Step '{step_name}' reported failure")
                    success = False
            except Exception as e:
                logger.error(f"Error in step '{step_name}': {str(e)}")
                self.errors.append(f"Exception in {step_name}: {str(e)}")
                success = False
        
        return success
    
    def print_report(self):
        """Print a report of the integration process"""
        print("\n" + "=" * 60)
        print("SoulCoreHub Integration Report")
        print("=" * 60)
        
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print("\n⚠️ WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if self.success:
            print("\n✅ SUCCESS:")
            for success in self.success:
                print(f"  - {success}")
        
        print("\n" + "=" * 60)
        
        if not self.errors:
            print("\n🎉 Integration completed successfully!")
            print("You can now interact with SoulCoreHub through:")
            print("  - Anima: python3 anima_autonomous.py --mode reflective")
            print("  - GPTSoul: python3 gptsoul_soulconfig.py --diagnose")
        else:
            print("\n⚠️ Integration completed with errors.")
            print("Please address the errors above before using SoulCoreHub.")
        
        print("=" * 60 + "\n")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="SoulCoreHub Integration Script")
    parser.add_argument("--no-anima", action="store_true", help="Don't start Anima after integration")
    parser.add_argument("--anima-mode", choices=["interactive", "daemon", "reflective"],
                      default="reflective", help="Anima operating mode")
    parser.add_argument("--base-dir", help="Base directory for SoulCoreHub")
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_arguments()
    
    # Create and run the integrator
    integrator = SoulCoreIntegrator(base_dir=args.base_dir)
    integrator.run_full_integration(
        start_anima=not args.no_anima,
        anima_mode=args.anima_mode
    )
    integrator.print_report()

if __name__ == "__main__":
    main()
