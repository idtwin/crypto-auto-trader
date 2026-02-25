class RiskEngine:
    """
    Enforces risk rules based on max position size and maximum portfolio exposure.
    """
    def __init__(self, max_position_pct: float = 0.2, max_exposure_pct: float = 0.8):
        # Maximum percentage of the total portfolio value allocated to a single trade
        self.max_position_pct = max_position_pct
        # Maximum percentage of the total portfolio value that can be exposed in open positions
        self.max_exposure_pct = max_exposure_pct
    
    def validate_position_size(self, current_portfolio_value: float, proposed_trade_value: float) -> bool:
        """
        Validates whether a proposed trade value exceeds the maximum allowable position size.
        """
        max_allowed_value = current_portfolio_value * self.max_position_pct
        return proposed_trade_value <= max_allowed_value
        
    def validate_exposure(self, current_portfolio_value: float, total_open_positions_value: float, proposed_trade_value: float) -> bool:
        """
        Validates whether opening a new trade would exceed the total maximum allowable exposure.
        """
        max_allowed_exposure = current_portfolio_value * self.max_exposure_pct
        return (total_open_positions_value + proposed_trade_value) <= max_allowed_exposure
    
    def calculate_position_size(self, current_portfolio_value: float, current_price: float) -> float:
        """
        Calculates a safe position size (in asset amount) that adheres to the max_position_pct constraint.
        Assuming it passes the validate_exposure check.
        """
        trade_value = current_portfolio_value * self.max_position_pct
        return trade_value / current_price
    
    def update_risk_parameters(self, max_position_pct: float, max_exposure_pct: float):
        """
        Allows dynamic updating of risk parameters.
        """
        if 0 < max_position_pct <= 1.0:
             self.max_position_pct = max_position_pct
        
        if 0 < max_exposure_pct <= 1.0:
             self.max_exposure_pct = max_exposure_pct
