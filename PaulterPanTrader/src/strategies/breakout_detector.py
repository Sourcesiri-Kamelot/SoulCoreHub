"""
Breakout Detector Strategy
Identifies price breakouts from consolidation patterns.
"""

import logging
import pandas as pd
import numpy as np
from typing import List

from src.strategies.strategy_manager import BaseStrategy
from src.signals.signal_aggregator import Signal

logger = logging.getLogger("PaulterPan.Strategy.Breakout")

class BreakoutDetector(BaseStrategy):
    """
    Breakout Detector Strategy
    
    Identifies price breakouts from consolidation patterns:
    - Bullish breakout: Price breaks above resistance with increased volume
    - Bearish breakout: Price breaks below support with increased volume
    """
    
    def __init__(self, config):
        """
        Initialize the strategy
        
        Args:
            config: Strategy configuration
        """
        super().__init__(config)
        self.lookback_periods = config.get('lookback_periods', 20)
        self.min_consolidation_bars = config.get('min_consolidation_bars', 5)
        self.volume_factor = config.get('volume_factor', 1.5)  # Volume increase factor for confirmation
        
        logger.info(f"Initialized Breakout Detector strategy: Lookback={self.lookback_periods}")
        
    def _detect_consolidation(self, df):
        """
        Detect price consolidation patterns
        
        Returns tuple of:
        - is_consolidating: True if price is in consolidation
        - support_level: Lower bound of consolidation
        - resistance_level: Upper bound of consolidation
        - consolidation_length: Number of bars in consolidation
        """
        if len(df) < self.lookback_periods:
            return False, None, None, 0
            
        # Get recent price data
        recent_data = df.iloc[-self.lookback_periods:]
        
        # Calculate price range as percentage of average price
        price_range = (recent_data['high'].max() - recent_data['low'].min()) / recent_data['close'].mean()
        
        # Calculate standard deviation of closing prices
        std_dev = recent_data['close'].std() / recent_data['close'].mean()
        
        # Detect consolidation - low volatility period
        is_consolidating = std_dev < 0.03  # Less than 3% standard deviation
        
        if not is_consolidating:
            return False, None, None, 0
            
        # Find support and resistance levels
        support_level = recent_data['low'].min()
        resistance_level = recent_data['high'].max()
        
        # Count bars in consolidation range
        in_range = ((df['high'] <= resistance_level * 1.01) & 
                   (df['low'] >= support_level * 0.99)).rolling(3).sum() >= 2
        
        # Find the start of the current consolidation
        consolidation_start = None
        for i in range(len(in_range) - 1, 0, -1):
            if not in_range.iloc[i]:
                consolidation_start = i + 1
                break
                
        if consolidation_start is None:
            consolidation_length = len(df)
        else:
            consolidation_length = len(df) - consolidation_start
            
        return is_consolidating, support_level, resistance_level, consolidation_length
        
    def generate_signals(self, market_data) -> List[Signal]:
        """
        Generate trading signals based on price breakouts
        
        Args:
            market_data: MarketDataManager instance
            
        Returns:
            List of Signal objects
        """
        signals = []
        
        # Get symbols to analyze
        symbols = self.symbols
        if not symbols:
            # If no specific symbols configured, use watchlists from market data
            for asset_type in self.asset_types:
                if asset_type == 'stock':
                    symbols.extend(market_data.config.get('watchlists', {}).get('stocks', []))
                elif asset_type == 'crypto':
                    symbols.extend(market_data.config.get('watchlists', {}).get('crypto', []))
        
        # Process each symbol and timeframe
        for symbol in symbols:
            for timeframe in self.timeframes:
                try:
                    # Determine asset type from symbol
                    if '-USD' in symbol or symbol.endswith('USDT'):
                        asset_type = 'crypto'
                    else:
                        asset_type = 'stock'
                    
                    # Skip if this asset type is not enabled for this strategy
                    if asset_type not in self.asset_types:
                        continue
                    
                    # Get price data
                    df = market_data.get_price_data(symbol, timeframe, bars=self.lookback_periods * 2)
                    
                    if df.empty:
                        logger.warning(f"No data for {symbol} on {timeframe} timeframe")
                        continue
                    
                    # Check for consolidation pattern
                    is_consolidating, support, resistance, consolidation_length = self._detect_consolidation(df.iloc[:-1])
                    
                    if not is_consolidating or consolidation_length < self.min_consolidation_bars:
                        continue
                        
                    # Get the latest candle
                    latest = df.iloc[-1]
                    prev = df.iloc[-2]
                    
                    # Calculate average volume during consolidation
                    avg_volume = df['volume'].iloc[-consolidation_length-1:-1].mean()
                    
                    # Check for bullish breakout
                    if latest['close'] > resistance and latest['volume'] > avg_volume * self.volume_factor:
                        # Calculate confidence based on breakout strength and volume
                        breakout_strength = (latest['close'] - resistance) / resistance
                        volume_strength = latest['volume'] / avg_volume
                        
                        confidence = 0.6 + min(0.3, breakout_strength * 10 + (volume_strength - 1) * 0.1)
                        
                        signal = Signal(
                            asset_type=asset_type,
                            symbol=symbol,
                            direction='long',
                            confidence=confidence,
                            timeframe=timeframe,
                            strategy_name=self.name,
                            entry_price=latest['close'],
                            stop_loss=support,  # Stop loss at support level
                            take_profit=latest['close'] + (resistance - support) * 2  # 2x the consolidation range
                        )
                        signals.append(signal)
                        logger.info(f"Generated BULLISH breakout signal for {symbol} on {timeframe}")
                    
                    # Check for bearish breakout
                    elif latest['close'] < support and latest['volume'] > avg_volume * self.volume_factor:
                        # Calculate confidence based on breakout strength and volume
                        breakout_strength = (support - latest['close']) / support
                        volume_strength = latest['volume'] / avg_volume
                        
                        confidence = 0.6 + min(0.3, breakout_strength * 10 + (volume_strength - 1) * 0.1)
                        
                        signal = Signal(
                            asset_type=asset_type,
                            symbol=symbol,
                            direction='short',
                            confidence=confidence,
                            timeframe=timeframe,
                            strategy_name=self.name,
                            entry_price=latest['close'],
                            stop_loss=resistance,  # Stop loss at resistance level
                            take_profit=latest['close'] - (resistance - support) * 2  # 2x the consolidation range
                        )
                        signals.append(signal)
                        logger.info(f"Generated BEARISH breakout signal for {symbol} on {timeframe}")
                    
                except Exception as e:
                    logger.error(f"Error analyzing {symbol} on {timeframe}: {str(e)}")
        
        return signals
