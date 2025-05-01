"""
Strategy Manager
Manages and coordinates different trading strategies.
"""

import logging
import importlib
import os
from typing import List, Dict, Any

logger = logging.getLogger("PaulterPan.StrategyManager")

class BaseStrategy:
    """Base class for all trading strategies"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the strategy
        
        Args:
            config: Strategy-specific configuration
        """
        self.name = self.__class__.__name__
        self.config = config
        self.enabled = config.get('enabled', True)
        self.asset_types = config.get('asset_types', ['stock'])
        self.timeframes = config.get('timeframes', ['1d'])
        self.symbols = config.get('symbols', [])
        
    def generate_signals(self, market_data):
        """
        Generate trading signals based on market data
        
        Args:
            market_data: MarketDataManager instance
            
        Returns:
            List of Signal objects
        """
        raise NotImplementedError("Subclasses must implement generate_signals()")
        
    def __str__(self):
        return f"{self.name} (enabled: {self.enabled})"


class StrategyManager:
    """Manages and coordinates different trading strategies"""
    
    def __init__(self, config):
        """
        Initialize the strategy manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.strategies = []
        self._load_strategies()
        logger.info(f"Strategy Manager initialized with {len(self.strategies)} strategies")
        
    def _load_strategies(self):
        """Load strategies based on configuration"""
        strategy_configs = self.config.get('strategies', {})
        
        # Load built-in strategies
        for strategy_name, strategy_config in strategy_configs.items():
            if not strategy_config.get('enabled', True):
                continue
                
            try:
                # Try to import the strategy module
                module_path = f"src.strategies.{strategy_name.lower()}"
                module = importlib.import_module(module_path)
                
                # Get the strategy class (assume it's named like the module but in CamelCase)
                class_name = ''.join(word.capitalize() for word in strategy_name.split('_'))
                strategy_class = getattr(module, class_name)
                
                # Instantiate the strategy
                strategy = strategy_class(strategy_config)
                self.strategies.append(strategy)
                logger.info(f"Loaded strategy: {strategy}")
                
            except (ImportError, AttributeError, Exception) as e:
                logger.error(f"Failed to load strategy {strategy_name}: {str(e)}")
        
        # Load custom strategies from plugins directory if it exists
        plugins_dir = os.path.join(os.path.dirname(__file__), 'plugins')
        if os.path.exists(plugins_dir) and os.path.isdir(plugins_dir):
            for filename in os.listdir(plugins_dir):
                if filename.endswith('.py') and not filename.startswith('_'):
                    try:
                        module_name = filename[:-3]  # Remove .py extension
                        module_path = f"src.strategies.plugins.{module_name}"
                        module = importlib.import_module(module_path)
                        
                        # Look for classes that inherit from BaseStrategy
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (isinstance(attr, type) and 
                                issubclass(attr, BaseStrategy) and 
                                attr is not BaseStrategy):
                                
                                # Get config for this strategy if available
                                strategy_config = strategy_configs.get(module_name, {})
                                
                                # Instantiate the strategy
                                strategy = attr(strategy_config)
                                self.strategies.append(strategy)
                                logger.info(f"Loaded plugin strategy: {strategy}")
                                
                    except Exception as e:
                        logger.error(f"Failed to load plugin strategy from {filename}: {str(e)}")
    
    def get_active_strategies(self):
        """Get list of active strategies"""
        return [s for s in self.strategies if s.enabled]
    
    def get_strategy_by_name(self, name):
        """Get a strategy by name"""
        for strategy in self.strategies:
            if strategy.name.lower() == name.lower():
                return strategy
        return None
