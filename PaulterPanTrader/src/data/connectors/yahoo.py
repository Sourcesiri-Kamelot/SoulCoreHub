"""
Yahoo Finance Connector
Fetches market data from Yahoo Finance.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

logger = logging.getLogger("PaulterPan.Connector.Yahoo")

class YahooFinanceConnector:
    """Connector for Yahoo Finance data"""
    
    def __init__(self):
        """Initialize the Yahoo Finance connector"""
        try:
            import yfinance as yf
            self.yf = yf
            self.available = True
            logger.info("Yahoo Finance connector initialized")
        except ImportError:
            self.available = False
            logger.warning("yfinance package not found. Install with: pip install yfinance")
    
    def get_historical_data(self, symbol, timeframe='1d', bars=100):
        """
        Get historical price data from Yahoo Finance
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe/interval for the data
            bars: Number of bars/candles to retrieve
            
        Returns:
            DataFrame with OHLCV data
        """
        if not self.available:
            logger.error("Yahoo Finance connector not available")
            return pd.DataFrame()
            
        try:
            # Convert timeframe to yfinance interval format
            interval = self._convert_timeframe(timeframe)
            
            # Calculate start date based on bars and timeframe
            end_date = datetime.now()
            
            # For intraday data, we need to adjust the period
            if interval in ['1m', '2m', '5m', '15m', '30m', '60m', '90m']:
                # Yahoo only provides 7 days of 1-minute data
                if interval == '1m':
                    days_back = min(7, bars // 390 + 1)  # ~390 minutes in a trading day
                elif interval == '5m':
                    days_back = min(60, bars // 78 + 1)  # ~78 5-minute bars in a trading day
                else:
                    days_back = min(60, bars // 20 + 1)  # Approximation for other intervals
                    
                start_date = end_date - timedelta(days=days_back)
                period = None
            else:
                # For daily data and above, we can use period parameter
                period = f"{bars}d" if interval == '1d' else f"{bars*2}d"
                start_date = None
            
            # Fetch data from Yahoo Finance
            data = self.yf.download(
                symbol,
                start=start_date,
                end=end_date,
                interval=interval,
                period=period,
                progress=False,
                show_errors=False
            )
            
            if data.empty:
                logger.warning(f"No data returned for {symbol} on {timeframe} timeframe")
                return pd.DataFrame()
                
            # Rename columns to lowercase
            data.columns = [col.lower() for col in data.columns]
            
            # Make sure we have all required columns
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in data.columns:
                    data[col] = np.nan
            
            # Limit to requested number of bars
            if len(data) > bars:
                data = data.iloc[-bars:]
                
            # Reset index to make datetime a column
            data = data.reset_index()
            data = data.rename(columns={'index': 'datetime', 'date': 'datetime'})
            
            logger.info(f"Retrieved {len(data)} bars for {symbol} on {timeframe} timeframe")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def _convert_timeframe(self, timeframe):
        """Convert internal timeframe format to Yahoo Finance interval format"""
        # Map common timeframe formats to Yahoo Finance intervals
        timeframe_map = {
            '1m': '1m',
            '5m': '5m',
            '15m': '15m',
            '30m': '30m',
            '1h': '60m',
            '4h': '60m',  # Yahoo doesn't have 4h, use 1h and resample
            '1d': '1d',
            'D': '1d',
            'W': '1wk',
            '1w': '1wk',
            'M': '1mo',
            '1M': '1mo'
        }
        
        return timeframe_map.get(timeframe, '1d')
    
    def get_quote(self, symbol):
        """Get current quote for a symbol"""
        if not self.available:
            return None
            
        try:
            ticker = self.yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'price': info.get('regularMarketPrice', None),
                'change': info.get('regularMarketChange', None),
                'change_percent': info.get('regularMarketChangePercent', None),
                'volume': info.get('regularMarketVolume', None),
                'market_cap': info.get('marketCap', None),
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {str(e)}")
            return None
