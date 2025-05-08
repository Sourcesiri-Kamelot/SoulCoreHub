# Anima Commands Package
# This package contains command modules for Anima

from importlib import import_module
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/anima_commands.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("anima_commands")

def register_all_commands(command_registry):
    """Register all commands from modules in this package"""
    # Get the directory of this package
    package_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get all Python files in the package
    module_files = [f for f in os.listdir(package_dir) if f.endswith('.py') and f != '__init__.py']
    
    # Import each module and register its commands
    for module_file in module_files:
        module_name = module_file[:-3]  # Remove .py extension
        try:
            # Import the module
            module = import_module(f"anima_commands.{module_name}")
            
            # Register commands if the module has a register_commands function
            if hasattr(module, 'register_commands'):
                module.register_commands(command_registry)
                logger.info(f"Registered commands from {module_name}")
        except Exception as e:
            logger.error(f"Error registering commands from {module_name}: {str(e)}")
    
    return True
