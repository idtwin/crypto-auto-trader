class PortfolioEngine:
    """
    Manages virtual balance, open positions, and calculates total portfolio value.
    """
    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.cash_balance = initial_balance
        self.positions = {}  # Format: {'BTCUSDT': {'amount': 0.5, 'average_entry_price': 50000.0}}

    def get_portfolio_value(self, current_prices: dict) -> float:
        """
        Calculates total portfolio value (cash + value of all open positions).
        current_prices: dictionary of current market prices, e.g., {'BTCUSDT': 60000.0}
        """
        total_value = self.cash_balance
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                total_value += position['amount'] * current_prices[symbol]
        return total_value

    def add_position(self, symbol: str, amount: float, price: float) -> bool:
        """
        Simulates buying an asset. Reduces cash balance and increases position amount.
        """
        cost = amount * price
        if cost > self.cash_balance:
            print(f"Insufficient funds to buy {amount} of {symbol} at {price}.")
            return False

        self.cash_balance -= cost

        if symbol in self.positions:
            # Calculate new average entry price
            old_amount = self.positions[symbol]['amount']
            old_price = self.positions[symbol]['average_entry_price']
            
            new_amount = old_amount + amount
            new_price = ((old_amount * old_price) + (amount * price)) / new_amount
            
            self.positions[symbol] = {
                'amount': new_amount,
                'average_entry_price': new_price
            }
        else:
            self.positions[symbol] = {
                'amount': amount,
                'average_entry_price': price
            }
        
        return True

    def remove_position(self, symbol: str, amount: float, price: float) -> bool:
        """
        Simulates selling an asset. Increases cash balance and reduces position amount.
        """
        if symbol not in self.positions or self.positions[symbol]['amount'] < amount:
            print(f"Insufficient position size to sell {amount} of {symbol}.")
            return False

        sale_value = amount * price
        self.cash_balance += sale_value

        self.positions[symbol]['amount'] -= amount
        
        # Remove position entirely if amount is negligible (handling float precision)
        if self.positions[symbol]['amount'] < 1e-8:
            del self.positions[symbol]

        return True

    def get_position(self, symbol: str) -> dict:
        """Returns details of a specific position, or None if not held."""
        return self.positions.get(symbol)
    
    def get_all_positions(self) -> dict:
        """Returns all open positions."""
        return self.positions

    def get_cash_balance(self) -> float:
        """Returns current cash balance."""
        return self.cash_balance
