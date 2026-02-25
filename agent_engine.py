import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Base class for all trading agents."""
    def __init__(self, name: str):
        self.name = name
        self.status = "Idle"
        self.last_decision = None
        self.memory = {
            'total_trades': 0,
            'wins': 0,
            'losses': 0,
            'current_streak': 0,  # positive for win streak, negative for loss streak
            'adaptations': []     # list of current active adaptations
        }

    def update_memory(self, realized_pnl: float):
        """Updates agent memory based on trade outcome."""
        self.memory['total_trades'] += 1
        if realized_pnl > 0:
            self.memory['wins'] += 1
            if self.memory['current_streak'] > 0:
                self.memory['current_streak'] += 1
            else:
                self.memory['current_streak'] = 1
        elif realized_pnl < 0:
            self.memory['losses'] += 1
            if self.memory['current_streak'] < 0:
                self.memory['current_streak'] -= 1
            else:
                self.memory['current_streak'] = -1
        
        self._adapt()

    @abstractmethod
    def _adapt(self):
        """Rule-based adaptation logic triggered after memory updates."""
        pass


class ScoutAgent(BaseAgent):
    """
    Scans market data to identify potential trade opportunities based on 
    simple indicators like trend, volatility, and momentum.
    """
    def __init__(self, name: str = "Scout"):
        super().__init__(name)
        self.volatility_threshold = 0.05 # 5% volatility considered high

    def _adapt(self):
        self.memory['adaptations'] = []
        if self.memory['current_streak'] <= -3:
            self.volatility_threshold = 0.02 # Tighten filter on losing streak
            self.memory['adaptations'].append("Tightened Volatility Filter (Loss Streak)")
        else:
            self.volatility_threshold = 0.05

    def scan(self, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Outputs candidate signals.
        Returns a dict with 'signal' (BUY/SELL/HOLD) and 'context' (e.g. volatility).
        """
        if historical_data.empty or len(historical_data) < 5:
            self.status = "Waiting for data"
            self.last_decision = {"signal": "HOLD", "reason": "Insufficient data"}
            return self.last_decision

        # Simple Momentum: Price change over last 5 periods
        prices = historical_data['close'].values
        momentum = (prices[-1] - prices[-5]) / prices[-5]
        
        # Simple Volatility: High-Low range estimation (simplified using close variations here)
        # Using std dev of recent returns as a proxy for volatility
        returns = pd.Series(prices).pct_change().dropna()
        volatility = returns.std() * np.sqrt(len(returns)) if len(returns) > 0 else 0

        signal = "HOLD"
        reason = f"Momentum: {momentum:.4f}, Volatility: {volatility:.4f}"

        if volatility > self.volatility_threshold:
            signal = "HOLD"
            reason += f" | Rejected: High Volatility (>{self.volatility_threshold})"
        elif momentum > 0.01:
            signal = "BUY"
            reason += " | Strong Positive Momentum"
        elif momentum < -0.01:
            signal = "SELL"
            reason += " | Strong Negative Momentum"

        self.status = f"Scanned | Volatility: {volatility:.4f}"
        self.last_decision = {"signal": signal, "reason": reason, "volatility": volatility}
        return self.last_decision


class AnalystAgent(BaseAgent):
    """
    Evaluates Scout signals using the core Rule-Based Strategy (SMA).
    """
    def __init__(self, strategy_engine, name: str = "Analyst"):
        super().__init__(name)
        self.strategy_engine = strategy_engine
        self.requires_scout_alignment = False

    def _adapt(self):
        self.memory['adaptations'] = []
        if self.memory['current_streak'] <= -2:
             # On a losing streak, require Scout momentum to align with SMA signal
             self.requires_scout_alignment = True
             self.memory['adaptations'].append("Requiring Scout Alignment (Loss Streak)")
        elif self.memory['current_streak'] >= 2:
             self.requires_scout_alignment = False
             self.memory['adaptations'].append("Relaxed Alignment (Win Streak)")

    def analyze(self, scout_signal: Dict[str, Any], historical_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Confirms or rejects opportunities. Outputs trade proposals.
        """
        sma_signal = self.strategy_engine.generate_signal(historical_data)
        
        final_signal = "HOLD"
        reason = f"SMA Signal: {sma_signal}"

        if sma_signal != "HOLD":
            if self.requires_scout_alignment:
                if sma_signal == scout_signal['signal']:
                    final_signal = sma_signal
                    reason += " | Confirmed by Scout Alignment"
                else:
                    reason += f" | Rejected: Scout divergence ({scout_signal['signal']})"
            else:
                final_signal = sma_signal
                reason += " | Base Strategy Executing"

        self.status = f"Analyzed | Output: {final_signal}"
        self.last_decision = {"signal": final_signal, "reason": reason}
        return self.last_decision


class RiskGuardianAgent(BaseAgent):
    """
    Applies risk management constraints, adjusts position sizing, and enforces cooldowns.
    """
    def __init__(self, risk_engine, name: str = "Risk Guardian"):
        super().__init__(name)
        self.risk_engine = risk_engine
        self.cooldown_cycles_remaining = 0
        self.size_modifier = 1.0 # Multiplier for calculated position size
        
    def _adapt(self):
        self.memory['adaptations'] = []
        if self.memory['current_streak'] <= -3:
            # Massive losing streak -> Cooldown and drastic size reduction
            if self.cooldown_cycles_remaining == 0: # Only trigger if not already cooling down
                 self.cooldown_cycles_remaining = 5
            self.size_modifier = 0.5
            self.memory['adaptations'].extend(["Active Cooldown", "Reduced Sizing (-50%)"])
        elif self.memory['current_streak'] <= -1:
            self.size_modifier = 0.75
            self.memory['adaptations'].append("Cautious Sizing (-25%)")
        elif self.memory['current_streak'] >= 3:
            self.size_modifier = 1.25 # Cautiously increase max risk by 25% (still bounded by risk_engine ceilings)
            self.memory['adaptations'].append("Aggressive Sizing (+25%)")
        else:
            self.size_modifier = 1.0

    def evaluate(self, analyst_proposal: Dict[str, Any], current_portfolio_value: float, total_open_value: float, current_price: float) -> Dict[str, Any]:
        """
        Approves/rejects trades and finalizes position sizing.
        """
        signal = analyst_proposal['signal']
        
        # Handle Cooldown
        if self.cooldown_cycles_remaining > 0:
            self.cooldown_cycles_remaining -= 1
            if self.cooldown_cycles_remaining > 0:
                 self.status = f"Cooldown Active ({self.cooldown_cycles_remaining} cycles left)"
            else:
                 self._adapt() # Re-evaluate adaptations when cooldown finishes
                 self.status = "Cooldown Finished"
            self.last_decision = {"signal": "HOLD", "amount": 0, "reason": "Blocked by active cooldown."}
            return self.last_decision

        # If it's a hold, skip risk checks
        if signal == "HOLD":
             self.status = "No Action Required"
             self.last_decision = {"signal": "HOLD", "amount": 0, "reason": "No trade proposed."}
             return self.last_decision
             
        # For Sells, we don't calculate max position sizes, we just approve the sell
        if signal == "SELL":
             self.status = "Approved SELL"
             self.last_decision = {"signal": "SELL", "amount": -1, "reason": "Sell approved by risk logic."} # Return -1 to indicate full position sell
             return self.last_decision

        # For BUYs, calculate and validate size
        base_calc_amount = self.risk_engine.calculate_position_size(portfolio_value=current_portfolio_value, current_price=current_price)
        proposed_amount = base_calc_amount * self.size_modifier
        proposed_value = proposed_amount * current_price
        
        valid_size = self.risk_engine.validate_position_size(current_portfolio_value, proposed_value)
        valid_exposure = self.risk_engine.validate_exposure(current_portfolio_value, total_open_value, proposed_value)
        
        if valid_size and valid_exposure:
             self.status = "Approved BUY"
             self.last_decision = {"signal": "BUY", "amount": proposed_amount, "reason": f"Sizing approved (Modifier: {self.size_modifier}x)"}
        else:
             reason = "Max Position Size limit" if not valid_size else "Max Exposure limit"
             self.status = "Rejected BUY"
             self.last_decision = {"signal": "HOLD", "amount": 0, "reason": f"Risk Rejected: {reason}"}
        
        return self.last_decision
