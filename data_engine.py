import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DataEngine:
    """
    Simulates cryptocurrency price data for the paper trading lab.
    Uses a random walk to generate realistic-looking price movements.
    """
    def __init__(self):
        self.current_prices = {}
        self.start_time = datetime.now() - timedelta(days=30)
        
    def _initialize_symbol(self, symbol: str):
        if symbol not in self.current_prices:
            # Set arbitrary starting prices for common symbols
            if 'BTC' in symbol:
                self.current_prices[symbol] = 60000.0
            elif 'ETH' in symbol:
                self.current_prices[symbol] = 3000.0
            else:
                self.current_prices[symbol] = 100.0

    def get_current_price(self, symbol: str) -> float:
        """
        Simulates fetching the current price by applying a small random walk to the last price.
        """
        self._initialize_symbol(symbol)
        
        # Random walk: +/- 0.5% max change per call
        change_pct = np.random.uniform(-0.005, 0.005)
        new_price = self.current_prices[symbol] * (1 + change_pct)
        self.current_prices[symbol] = new_price
        
        return new_price

    def get_historical_klines(self, symbol: str, interval: str = '1h', limit: int = 100) -> pd.DataFrame:
        """
        Generates simulated historical kline data for the given symbol to allow SMA calculation.
        """
        self._initialize_symbol(symbol)
        
        # Generate timestamps backwards from now
        now = datetime.now()
        timestamps = [now - timedelta(hours=i) for i in range(limit - 1, -1, -1)]
        
        # Generate a random walk ending at the current price
        prices = [self.current_prices[symbol]]
        for _ in range(limit - 1):
            # Work backwards applying random walk
            change_pct = np.random.uniform(-0.02, 0.02) # Slightly larger variance for hourly data
            prev_price = prices[-1] / (1 + change_pct)
            prices.append(prev_price)
            
        prices.reverse() # Order from oldest to newest

        df = pd.DataFrame({
            'open_time': timestamps,
            'close': prices
        })
        
        return df[['open_time', 'close']]
