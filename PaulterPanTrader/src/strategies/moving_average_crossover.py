"""
Moving Average Crossover Strategy
Generates signals based on crossovers between fast and slow moving averages.
"""

import logging
import pandas as pd
import numpy as np
from typing import List

from src.strategies.strategy_manager import BaseStrategy
from src.signals.signal_aggregator import Signal

logger = logging.getLogger("PaulterPan.Strategy.MAcrossover")

class MovingAverageCrossover(BaseStrategy):
    """
    Moving Average Crossover Strategy
    
    Generates signals when a faster moving average crosses a slower moving average.
    - Fast MA crossing above Slow MA = Bullish signal
    - Fast MA crossing below Slow MA = Bearish signal
    """
    
    def __init__(self, config):
        """
        Initialize the strategy
        
        Args:
            config: Strategy configuration
        """
        super().__init__(config)
        self.fast_period = config.get('fast_period', 9)
        self.slow_period = config.get('slow_period', 21)
        self.signal_threshold = config.get('signal_threshold', 0.6)
        
        logger.info(f"Initialized MA Crossover strategy: Fast={self.fast_period}, Slow={self.slow_period}")
        
    def generate_signals(self, market_data) -> List[Signal]:
        """
        Generate trading signals based on moving average crossovers
        
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
                    df = market_data.get_price_data(symbol, timeframe, bars=100)
                    
                    if df.empty:
                        logger.warning(f"No data for {symbol} on {timeframe} timeframe")
                        continue
                    
                    # Calculate moving averages
                    df['fast_ma'] = df['close'].rolling(window=self.fast_period).mean()
                    df['slow_ma'] = df['close'].rolling(window=self.slow_period).mean()
                    
                    # Calculate crossover signals
                    df['prev_fast'] = df['fast_ma'].shift(1)
                    df['prev_slow'] = df['slow_ma'].shift(1)
                    
                    # Check for crossovers in the most recent candle
                    last_row = df.iloc[-1]
                    prev_row = df.iloc[-2] if len(df) > 1 else None
                    
                    if prev_row is not None:
                        # Bullish crossover (fast crosses above slow)
                        if (prev_row['fast_ma'] <= prev_row['slow_ma'] and 
                            last_row['fast_ma'] > last_row['slow_ma']):
                            
                            # Calculate confidence based on the strength of the crossover
                            crossover_strength = (last_row['fast_ma'] - last_row['slow_ma']) / last_row['slow_ma']
                            confidence = min(0.9, self.signal_threshold + (crossover_strength * 100))
                            
                            signal = Signal(
                                asset_type=asset_type,
                                symbol=symbol,
                                direction='long',
                                confidence=confidence,
                                timeframe=timeframe,
                                strategy_name=self.name,
                                entry_price=last_row['close'],
                                stop_loss=last_row['close'] * 0.95,  # 5% stop loss
                                take_profit=last_row['close'] * 1.15  # 15% take profit
                            )
                            signals.append(signal)
                            logger.info(f"Generated BULLISH signal for {symbol} on {timeframe}")
                            
                        # Bearish crossover (fast crosses below slow)
                        elif (prev_row['fast_ma'] >= prev_row['slow_ma'] and 
                              last_row['fast_ma'] < last_row['slow_ma']):
                              
                            # Calculate confidence based on the strength of the crossover
                            crossover_strength = (last_row['slow_ma'] - last_row['fast_ma']) / last_row['slow_ma']
                            confidence = min(0.9, self.signal_threshold + (crossover_strength * 100))
                            
                            signal = Signal(
                                asset_type=asset_type,
                                symbol=symbol,
                                direction='short',
                                confidence=confidence,
                                timeframe=timeframe,
                                strategy_name=self.name,
                                entry_price=last_row['close'],
                                stop_loss=last_row['close'] * 1.05,  # 5% stop loss
                                take_profit=last_row['close'] * 0.85  # 15% take profit
                            )
                            signals.append(signal)
                            logger.info(f"Generated BEARISH signal for {symbol} on {timeframe}")
                    
                except Exception as e:
                    logger.error(f"Error analyzing {symbol} on {timeframe}: {str(e)}")
        
        return signals
