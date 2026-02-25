import pandas as pd

class StrategyEngine:
    """
    Generates trading signals based on a rule-based Simple Moving Average (SMA) crossover strategy.
    """
    def __init__(self, short_window: int = 20, long_window: int = 50):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signal(self, historical_data: pd.DataFrame) -> str:
        """
        Takes historical price data and returns a Trading Signal ('BUY', 'SELL', or 'HOLD').
        Uses the SMA Crossover logic:
        - BUY when short SMA crosses above long SMA.
        - SELL when short SMA crosses below long SMA.
        - HOLD otherwise.
        """
        if historical_data.empty or len(historical_data) < self.long_window:
            return 'HOLD'

        # Calculate moving averages
        df = historical_data.copy()
        df['sma_short'] = df['close'].rolling(window=self.short_window).mean()
        df['sma_long'] = df['close'].rolling(window=self.long_window).mean()

        # Get the two most recent periods to check for a crossover
        # We need at least two populated rows of SMA to detect a crossover
        # Using iloc[-2] and iloc[-1] since [-1] is the most recent closed period
        
        try:
             latest = df.iloc[-1]
             previous = df.iloc[-2]
             
             if pd.isna(latest['sma_long']) or pd.isna(previous['sma_long']):
                  return 'HOLD'

             # Bullish Crossover (Short SMA crosses ABOVE Long SMA)
             if previous['sma_short'] <= previous['sma_long'] and latest['sma_short'] > latest['sma_long']:
                 return 'BUY'
             
             # Bearish Crossover (Short SMA crosses BELOW Long SMA)
             elif previous['sma_short'] >= previous['sma_long'] and latest['sma_short'] < latest['sma_long']:
                 return 'SELL'
             
             else:
                 return 'HOLD'

        except (IndexError, KeyError):
            # Fallback if DataFrame isn't structured correctly or lacks enough rows
            return 'HOLD'
            
    def update_strategy_parameters(self, short_window: int, long_window: int):
        """Allows dynamic adjustment of strategy windows."""
        if 0 < short_window < long_window:
             self.short_window = short_window
             self.long_window = long_window
