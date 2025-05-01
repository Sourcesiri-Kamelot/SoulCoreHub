#!/usr/bin/env python3
"""
PaulterPan Trading Signal Bot
Main entry point for the application that aggregates and presents trading signals
across multiple asset classes and trading strategies.
"""

import os
import sys
import logging
from datetime import datetime

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.signals.signal_aggregator import SignalAggregator
from src.data.market_data import MarketDataManager
from src.strategies.strategy_manager import StrategyManager
from src.ui.dashboard import Dashboard
from src.utils.config import load_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("paulterpan.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("PaulterPan")

def main():
    """Main entry point for the PaulterPan Trading Signal Bot"""
    logger.info("Starting PaulterPan Trading Signal Bot")
    
    # Load configuration
    config = load_config()
    
    # Initialize components
    market_data = MarketDataManager(config)
    strategy_manager = StrategyManager(config)
    signal_aggregator = SignalAggregator(market_data, strategy_manager)
    dashboard = Dashboard(signal_aggregator)
    
    # Start the dashboard
    dashboard.start()
    
    logger.info("PaulterPan Trading Signal Bot started successfully")

if __name__ == "__main__":
    main()
