from datetime import datetime
from portfolio_engine import PortfolioEngine
from risk_engine import RiskEngine
from strategy_engine import StrategyEngine
from agent_engine import ScoutAgent, AnalystAgent, RiskGuardianAgent

class ExecutionEngine:
    """
    Simulates trade execution through an Agent Pipeline.
    Pipeline: Scout (Signals) -> Analyst (Strategy) -> Risk Guardian (Sizing/Rules) -> Execution
    """
    def __init__(self, portfolio: PortfolioEngine, risk: RiskEngine, strategy: StrategyEngine):
        self.portfolio = portfolio
        self.risk = risk
        self.strategy = strategy
        self.trade_history = [] 
        
        # Initialize the Agents
        self.scout = ScoutAgent()
        self.analyst = AnalystAgent(self.strategy)
        self.guardian = RiskGuardianAgent(self.risk)

    def execute_cycle(self, symbol: str, current_price: float, historical_data):
        """
        Runs a complete trading cycle utilizing the autonomous agent pipeline.
        """
        # --- 1. Scout Pattern Recognition ---
        scout_signal = self.scout.scan(historical_data)
        
        # --- 2. Analyst Strategy Evaluation ---
        analyst_proposal = self.analyst.analyze(scout_signal, historical_data)
        
        # Extract portfolio state for Risk Guardian
        current_prices = {symbol: current_price}
        portfolio_value = self.portfolio.get_portfolio_value(current_prices)
        open_positions = self.portfolio.get_all_positions()
        total_open_value = sum(
             pos['amount'] * current_prices.get(sym, pos['average_entry_price']) 
             for sym, pos in open_positions.items()
        )
        
        # --- 3. Risk Guardian Approval & Sizing ---
        guardian_decision = self.guardian.evaluate(analyst_proposal, portfolio_value, total_open_value, current_price)
        
        # --- 4. Execution Logic ---
        final_action = guardian_decision['signal']
        
        if final_action == 'BUY':
             proposed_amount = guardian_decision['amount']
             success = self.portfolio.add_position(symbol, proposed_amount, current_price)
             if success:
                  self._log_trade(symbol, 'BUY', proposed_amount, current_price, f"Agent Pipeline Executed. Modifier: {self.guardian.size_modifier}x")
             else:
                  self._log_trade(symbol, 'REJECTED_FUNDS', proposed_amount, current_price, "Insufficient cash balance")

        elif final_action == 'SELL':
             position = self.portfolio.get_position(symbol)
             if position and position['amount'] > 0:
                   amount_to_sell = position['amount']
                   success = self.portfolio.remove_position(symbol, amount_to_sell, current_price)
                   if success:
                       entry_price = position['average_entry_price']
                       realized_pnl = (current_price - entry_price) * amount_to_sell
                       
                       # --- 5. Update Agent Memory with Outcomes ---
                       self.scout.update_memory(realized_pnl)
                       self.analyst.update_memory(realized_pnl)
                       self.guardian.update_memory(realized_pnl)
                       
                       self._log_trade(symbol, 'SELL', amount_to_sell, current_price, f"PnL: {realized_pnl:.2f}. Agents memory updated.")

        # If HOLD, the cycle ends with no execution

    def _log_trade(self, symbol: str, action: str, amount: float, price: float, note: str = ""):
        """Appends a trade record to the history."""
        log_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'symbol': symbol,
            'action': action,
            'amount': amount,
            'price': price,
            'value': amount * price,
            'note': note
        }
        self.trade_history.append(log_entry)
        print(f"[{log_entry['timestamp']}] {action} {amount:.4f} {symbol} @ {price:.2f} | {note}")
        
    def get_trade_history(self) -> list:
        return self.trade_history
