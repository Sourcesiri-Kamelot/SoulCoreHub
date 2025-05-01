"""
Configuration Utilities
Handles loading and validating configuration for PaulterPan.
"""

import os
import json
import logging
import yaml
from typing import Dict, Any

logger = logging.getLogger("PaulterPan.Config")

DEFAULT_CONFIG = {
    "data_sources": {
        "yahoo": {
            "enabled": True
        },
        "alpha_vantage": {
            "enabled": False,
            "api_key": ""
        },
        "binance": {
            "enabled": False,
            "api_key": "",
            "api_secret": ""
        }
    },
    "strategies": {
        "moving_average_crossover": {
            "enabled": True,
            "asset_types": ["stock", "crypto"],
            "timeframes": ["1d", "4h"],
            "fast_period": 9,
            "slow_period": 21
        },
        "rsi_divergence": {
            "enabled": True,
            "asset_types": ["stock", "crypto"],
            "timeframes": ["1d", "4h"],
            "rsi_period": 14,
            "overbought": 70,
            "oversold": 30
        },
        "breakout_detector": {
            "enabled": True,
            "asset_types": ["stock", "crypto"],
            "timeframes": ["1d"],
            "lookback_periods": 20
        }
    },
    "watchlists": {
        "stocks": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"],
        "crypto": ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "ADA-USD"],
        "forex": ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD"],
        "indices": ["^GSPC", "^DJI", "^IXIC", "^RUT"]
    },
    "ui": {
        "update_interval": 60,
        "web_dashboard": True,
        "web_port": 8080
    },
    "logging": {
        "level": "INFO",
        "file": "paulterpan.log"
    }
}

def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from file or use defaults
    
    Args:
        config_path: Path to configuration file (optional)
        
    Returns:
        Configuration dictionary
    """
    config = DEFAULT_CONFIG.copy()
    
    # If no config path specified, look in standard locations
    if not config_path:
        possible_paths = [
            "config.json",
            "config.yaml",
            "config.yml",
            os.path.expanduser("~/.paulterpan/config.json"),
            os.path.expanduser("~/.paulterpan/config.yaml")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                config_path = path
                break
    
    # Load config file if it exists
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                if config_path.endswith('.json'):
                    file_config = json.load(f)
                elif config_path.endswith(('.yaml', '.yml')):
                    import yaml
                    file_config = yaml.safe_load(f)
                else:
                    logger.warning(f"Unknown config file format: {config_path}")
                    file_config = {}
                    
            # Merge file config with defaults
            _deep_update(config, file_config)
            logger.info(f"Loaded configuration from {config_path}")
            
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {str(e)}")
            logger.info("Using default configuration")
    else:
        logger.info("No configuration file found, using defaults")
        
        # Create default config file
        try:
            os.makedirs(os.path.dirname(os.path.expanduser("~/.paulterpan/config.json")), exist_ok=True)
            with open(os.path.expanduser("~/.paulterpan/config.json"), 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Created default configuration at ~/.paulterpan/config.json")
        except Exception as e:
            logger.warning(f"Could not create default config file: {str(e)}")
    
    return config

def _deep_update(base_dict, update_dict):
    """
    Recursively update a dictionary
    
    Args:
        base_dict: Base dictionary to update
        update_dict: Dictionary with updates
    """
    for key, value in update_dict.items():
        if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
            _deep_update(base_dict[key], value)
        else:
            base_dict[key] = value

def save_config(config: Dict[str, Any], config_path: str = "~/.paulterpan/config.json"):
    """
    Save configuration to file
    
    Args:
        config: Configuration dictionary
        config_path: Path to save configuration
    """
    config_path = os.path.expanduser(config_path)
    
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as f:
            if config_path.endswith('.json'):
                json.dump(config, f, indent=2)
            elif config_path.endswith(('.yaml', '.yml')):
                import yaml
                yaml.dump(config, f)
            else:
                json.dump(config, f, indent=2)
                
        logger.info(f"Configuration saved to {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving configuration to {config_path}: {str(e)}")
        return False
