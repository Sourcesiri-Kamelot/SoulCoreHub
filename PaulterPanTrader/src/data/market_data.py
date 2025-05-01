"""
Market Data Manager
Handles fetching, caching, and providing market data from various sources.
"""

import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import time
import os
import json

logger = logging.getLogger("PaulterPan.MarketData")

class MarketDataManager:
    """Manages market data from various sources and provides unified access"""
    
    def __init__(self, config):
        """
        Initialize the market data manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.data_cache = {}
        self.cache_expiry = {}
        self.default_cache_time = 300  # 5 minutes in seconds
        
        # Data source connectors
        self.connectors = {}
        self._initialize_connectors()
        
        logger.info("Market Data Manager initialized")
        
    def _initialize_connectors(self):
        """Initialize data source connectors based on configuration"""
        # Initialize connectors based on config
        if self.config.get('data_sources', {}).get('alpha_vantage', {}).get('enabled', False):
            from src.data.connectors.alpha_vantage import AlphaVantageConnector
            self.connectors['alpha_vantage'] = AlphaVantageConnector(
                self.config['data_sources']['alpha_vantage']
            )
            
        if self.config.get('data_sources', {}).get('binance', {}).get('enabled', False):
            from src.data.connectors.binance import BinanceConnector
            self.connectors['binance'] = BinanceConnector(
                self.config['data_sources']['binance']
            )
            
        if self.config.get('data_sources', {}).get('yahoo', {}).get('enabled', False):
            from src.data.connectors.yahoo import YahooFinanceConnector
            self.connectors['yahoo'] = YahooFinanceConnector()
            
        # Add more connectors as needed
        
        logger.info(f"Initialized {len(self.connectors)} data connectors")
        
    def get_price_data(self, symbol: str, timeframe: str = '1d', 
                      bars: int = 100, source: str = None) -> pd.DataFrame:
        """
        Get historical price data for a symbol
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe/interval for the data
            bars: Number of bars/candles to retrieve
            source: Specific data source to use (optional)
            
        Returns:
            DataFrame with OHLCV data
        """
        cache_key = f"{symbol}_{timeframe}_{bars}"
        
        # Check if we have cached data that's still valid
        if (cache_key in self.data_cache and 
            cache_key in self.cache_expiry and 
            time.time() < self.cache_expiry[cache_key]):
            logger.debug(f"Using cached data for {cache_key}")
            return self.data_cache[cache_key]
        
        # Determine which connector to use
        if source and source in self.connectors:
            connector = self.connectors[source]
        else:
            # Choose appropriate connector based on symbol and available connectors
            connector = self._select_connector(symbol)
            
        if not connector:
            logger.error(f"No suitable connector found for {symbol}")
            return pd.DataFrame()
            
        try:
            # Fetch data from the connector
            data = connector.get_historical_data(symbol, timeframe, bars)
            
            # Cache the data
            self.data_cache[cache_key] = data
            self.cache_expiry[cache_key] = time.time() + self.default_cache_time
            
            return data
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def _select_connector(self, symbol):
        """Select appropriate connector based on symbol"""
        # Simple logic - can be expanded
        if symbol.endswith('USDT') and 'binance' in self.connectors:
            return self.connectors['binance']
        elif 'yahoo' in self.connectors:
            return self.connectors['yahoo']
        elif len(self.connectors) > 0:
            # Just use the first available connector
            return list(self.connectors.values())[0]
        return None
    
    def get_market_sentiment(self, symbol: str) -> Dict:
        """Get market sentiment data for a symbol"""
        # Implementation depends on available data sources
        # This is a placeholder
        return {
            'symbol': symbol,
            'sentiment': 'neutral',
            'fear_greed_index': 50,
            'social_sentiment': 0,
            'timestamp': datetime.now()
        }
    
    def get_options_chain(self, symbol: str) -> pd.DataFrame:
        """Get options chain data for a stock symbol"""
        # Implementation for options data
        # This is a placeholder
        return pd.DataFrame()
    
    def get_crypto_orderbook(self, symbol: str, depth: int = 10) -> Dict:
        """Get crypto orderbook data"""
        if 'binance' in self.connectors:
            try:
                return self.connectors['binance'].get_orderbook(symbol, depth)
            except Exception as e:
                logger.error(f"Error fetching orderbook for {symbol}: {str(e)}")
        
        return {'bids': [], 'asks': []}
    
    def clear_cache(self):
        """Clear the data cache"""
        self.data_cache = {}
        self.cache_expiry = {}
        logger.info("Market data cache cleared")
