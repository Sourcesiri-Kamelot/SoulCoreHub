"""
RSI Divergence Strategy
Detects divergences between price action and RSI indicator.
"""

import logging
import pandas as pd
import numpy as np
from typing import List

from src.strategies.strategy_manager import BaseStrategy
from src.signals.signal_aggregator import Signal

logger = logging.getLogger("PaulterPan.Strategy.RSIDivergence")

class RsiDivergence(BaseStrategy):
    """
    RSI Divergence Strategy
    
    Detects divergences between price action and RSI indicator:
    - Bullish divergence: Price makes lower lows while RSI makes higher lows
    - Bearish divergence: Price makes higher highs while RSI makes lower highs
    """
    
    def __init__(self, config):
        """
        Initialize the strategy
        
        Args:
            config: Strategy configuration
        """
        super().__init__(config)
        self.rsi_period = config.get('rsi_period', 14)
        self.overbought = config.get('overbought', 70)
        self.oversold = config.get('oversold', 30)
        self.lookback = config.get('lookback', 10)  # Bars to look back for divergence
        
        logger.info(f"Initialized RSI Divergence strategy: Period={self.rsi_period}, "
                   f"Overbought={self.overbought}, Oversold={self.oversold}")
        
    def _calculate_rsi(self, data):
        """Calculate RSI indicator"""
        delta = data.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
        
    def _find_local_extrema(self, series, window=5):
        """Find local maxima and minima in a series"""
        maxima = []
        minima = []
        
        for i in range(window, len(series) - window):
            if all(series.iloc[i] > series.iloc[i-j] for j in range(1, window+1)) and \
               all(series.iloc[i] > series.iloc[i+j] for j in range(1, window+1)):
                maxima.append(i)
            if all(series.iloc[i] < series.iloc[i-j] for j in range(1, window+1)) and \
               all(series.iloc[i] < series.iloc[i+j] for j in range(1, window+1)):
                minima.append(i)
                
        return maxima, minima
        
    def generate_signals(self, market_data) -> List[Signal]:
        """
        Generate trading signals based on RSI divergences
        
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
                    
                    # Calculate RSI
                    df['rsi'] = self._calculate_rsi(df['close'])
                    
                    # Find local extrema in price and RSI
                    price_highs, price_lows = self._find_local_extrema(df['close'])
                    rsi_highs, rsi_lows = self._find_local_extrema(df['rsi'])
                    
                    # Check for recent divergences
                    recent_window = min(self.lookback, len(df) // 3)
                    
                    # Bullish divergence: Price makes lower lows but RSI makes higher lows
                    if len(price_lows) >= 2 and len(rsi_lows) >= 2:
                        # Check if the most recent price low is lower than the previous one
                        if (price_lows[-1] > len(df) - recent_window and 
                            df['close'].iloc[price_lows[-1]] < df['close'].iloc[price_lows[-2]] and
                            df['rsi'].iloc[rsi_lows[-1]] > df['rsi'].iloc[rsi_lows[-2]] and
                            df['rsi'].iloc[rsi_lows[-1]] < self.oversold):
                            
                            # Calculate confidence based on RSI value and divergence strength
                            rsi_val = df['rsi'].iloc[-1]
                            divergence_strength = (df['rsi'].iloc[rsi_lows[-1]] - df['rsi'].iloc[rsi_lows[-2]]) / 10
                            confidence = 0.6 + min(0.3, divergence_strength)
                            
                            if rsi_val < self.oversold:
                                confidence += 0.1
                                
                            signal = Signal(
                                asset_type=asset_type,
                                symbol=symbol,
                                direction='long',
                                confidence=confidence,
                                timeframe=timeframe,
                                strategy_name=self.name,
                                entry_price=df['close'].iloc[-1],
                                stop_loss=df['close'].iloc[price_lows[-1]] * 0.95,
                                take_profit=df['close'].iloc[-1] * 1.2
                            )
                            signals.append(signal)
                            logger.info(f"Generated BULLISH divergence signal for {symbol} on {timeframe}")
                    
                    # Bearish divergence: Price makes higher highs but RSI makes lower highs
                    if len(price_highs) >= 2 and len(rsi_highs) >= 2:
                        # Check if the most recent price high is higher than the previous one
                        if (price_highs[-1] > len(df) - recent_window and 
                            df['close'].iloc[price_highs[-1]] > df['close'].iloc[price_highs[-2]] and
                            df['rsi'].iloc[rsi_highs[-1]] < df['rsi'].iloc[rsi_highs[-2]] and
                            df['rsi'].iloc[rsi_highs[-1]] > self.overbought):
                            
                            # Calculate confidence based on RSI value and divergence strength
                            rsi_val = df['rsi'].iloc[-1]
                            divergence_strength = (df['rsi'].iloc[rsi_highs[-2]] - df['rsi'].iloc[rsi_highs[-1]]) / 10
                            confidence = 0.6 + min(0.3, divergence_strength)
                            
                            if rsi_val > self.overbought:
                                confidence += 0.1
                                
                            signal = Signal(
                                asset_type=asset_type,
                                symbol=symbol,
                                direction='short',
                                confidence=confidence,
                                timeframe=timeframe,
                                strategy_name=self.name,
                                entry_price=df['close'].iloc[-1],
                                stop_loss=df['close'].iloc[price_highs[-1]] * 1.05,
                                take_profit=df['close'].iloc[-1] * 0.8
                            )
                            signals.append(signal)
                            logger.info(f"Generated BEARISH divergence signal for {symbol} on {timeframe}")
                    
                except Exception as e:
                    logger.error(f"Error analyzing {symbol} on {timeframe}: {str(e)}")
        
        return signals
