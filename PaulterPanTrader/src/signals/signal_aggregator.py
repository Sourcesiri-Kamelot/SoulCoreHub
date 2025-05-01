"""
Signal Aggregator Module
Collects, filters, and prioritizes trading signals from various sources and strategies.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger("PaulterPan.SignalAggregator")

class Signal:
    """Represents a trading signal with metadata and confidence score"""
    
    def __init__(self, 
                 asset_type: str,
                 symbol: str, 
                 direction: str, 
                 confidence: float,
                 timeframe: str,
                 strategy_name: str,
                 entry_price: float = None,
                 stop_loss: float = None,
                 take_profit: float = None,
                 expiration: datetime = None):
        """
        Initialize a new trading signal
        
        Args:
            asset_type: Type of asset (stock, crypto, options, etc.)
            symbol: Trading symbol
            direction: 'long' or 'short'
            confidence: Score from 0.0 to 1.0 indicating signal strength
            timeframe: Trading timeframe (e.g., '1h', '4h', '1d')
            strategy_name: Name of the strategy that generated this signal
            entry_price: Suggested entry price
            stop_loss: Suggested stop loss price
            take_profit: Suggested take profit price
            expiration: When this signal expires
        """
        self.asset_type = asset_type
        self.symbol = symbol
        self.direction = direction
        self.confidence = confidence
        self.timeframe = timeframe
        self.strategy_name = strategy_name
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.expiration = expiration
        self.timestamp = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary format"""
        return {
            'asset_type': self.asset_type,
            'symbol': self.symbol,
            'direction': self.direction,
            'confidence': self.confidence,
            'timeframe': self.timeframe,
            'strategy_name': self.strategy_name,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'expiration': self.expiration,
            'timestamp': self.timestamp
        }
        
    def __str__(self) -> str:
        """String representation of the signal"""
        return (f"{self.asset_type.upper()} SIGNAL: {self.direction.upper()} {self.symbol} "
                f"({self.confidence:.2f}) on {self.timeframe} timeframe "
                f"by {self.strategy_name}")


class SignalAggregator:
    """Aggregates and manages trading signals from multiple sources"""
    
    def __init__(self, market_data, strategy_manager):
        """
        Initialize the signal aggregator
        
        Args:
            market_data: MarketDataManager instance
            strategy_manager: StrategyManager instance
        """
        self.market_data = market_data
        self.strategy_manager = strategy_manager
        self.signals = []
        self.min_confidence_threshold = 0.6  # Minimum confidence to display signals
        logger.info("Signal Aggregator initialized")
        
    def update_signals(self):
        """Update all signals from available strategies"""
        logger.info("Updating signals from all strategies")
        new_signals = []
        
        # Get signals from each strategy
        for strategy in self.strategy_manager.get_active_strategies():
            try:
                strategy_signals = strategy.generate_signals(self.market_data)
                new_signals.extend(strategy_signals)
                logger.debug(f"Got {len(strategy_signals)} signals from {strategy.name}")
            except Exception as e:
                logger.error(f"Error getting signals from {strategy.name}: {str(e)}")
                
        # Filter signals by confidence threshold
        filtered_signals = [s for s in new_signals if s.confidence >= self.min_confidence_threshold]
        
        # Sort by confidence (highest first)
        filtered_signals.sort(key=lambda x: x.confidence, reverse=True)
        
        self.signals = filtered_signals
        logger.info(f"Updated signals: {len(self.signals)} signals after filtering")
        return self.signals
    
    def get_signals(self, asset_type=None, min_confidence=None, limit=None) -> List[Signal]:
        """
        Get filtered signals
        
        Args:
            asset_type: Filter by asset type (optional)
            min_confidence: Minimum confidence threshold (optional)
            limit: Maximum number of signals to return (optional)
            
        Returns:
            List of Signal objects
        """
        filtered = self.signals
        
        if asset_type:
            filtered = [s for s in filtered if s.asset_type == asset_type]
            
        if min_confidence:
            filtered = [s for s in filtered if s.confidence >= min_confidence]
            
        if limit:
            filtered = filtered[:limit]
            
        return filtered
    
    def get_top_signals(self, count=5) -> List[Signal]:
        """Get top signals by confidence score"""
        return self.signals[:count]
