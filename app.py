import streamlit as st
import pandas as pd
import time
from data_engine import DataEngine
from portfolio_engine import PortfolioEngine
from risk_engine import RiskEngine
from strategy_engine import StrategyEngine
from execution_engine import ExecutionEngine

# Set page config for a wider layout
st.set_page_config(page_title="Crypto Auto Trader", layout="wide")

# --- Initialize session state for persistent engines ---
if 'initialized' not in st.session_state:
    st.session_state.data_engine = DataEngine()
    st.session_state.portfolio = PortfolioEngine(initial_balance=10000.0)
    st.session_state.risk = RiskEngine(max_position_pct=0.2, max_exposure_pct=0.8)
    st.session_state.strategy = StrategyEngine(short_window=20, long_window=50)
    st.session_state.execution = ExecutionEngine(
        st.session_state.portfolio, 
        st.session_state.risk, 
        st.session_state.strategy
    )
    st.session_state.cycle_count = 0
    st.session_state.is_running = False
    st.session_state.target_symbol = 'BTCUSDT'
    st.session_state.initialized = True

engines = st.session_state

# --- Sidebar Controls ---
st.sidebar.title("Trader Controls")

# Symbol Selection
engines.target_symbol = st.sidebar.text_input("Target Symbol", value=engines.target_symbol).upper()

st.sidebar.header("Risk Constraints")
max_pos_pct = st.sidebar.slider("Max Position Size (%)", 1, 100, int(engines.risk.max_position_pct * 100)) / 100.0
max_exp_pct = st.sidebar.slider("Max Total Exposure (%)", 1, 100, int(engines.risk.max_exposure_pct * 100)) / 100.0
engines.risk.update_risk_parameters(max_pos_pct, max_exp_pct)

st.sidebar.header("Strategy Settings (SMA)")
short_window = st.sidebar.number_input("Short Window (periods)", min_value=1, value=engines.strategy.short_window)
long_window = st.sidebar.number_input("Long Window (periods)", min_value=2, value=engines.strategy.long_window)
engines.strategy.update_strategy_parameters(short_window, long_window)

st.sidebar.header("Execution")
# Allow user to manually trigger a cycle
if st.sidebar.button("Run Single Cycle Manually"):
    # Fetch Data
    current_price = engines.data_engine.get_current_price(engines.target_symbol)
    historical_data = engines.data_engine.get_historical_klines(engines.target_symbol, limit=long_window + 10)
    
    if current_price > 0 and not historical_data.empty:
        # Run Execution Cycle
        engines.execution.execute_cycle(engines.target_symbol, current_price, historical_data)
        engines.cycle_count += 1
        st.sidebar.success(f"Cycle {engines.cycle_count} executed successfully.")
    else:
        st.sidebar.error("Failed to fetch data for cycle.")

# Simulated Auto-Run Toggle
st.sidebar.markdown("---")
if st.sidebar.button("Toggle Auto-Run (Simulated)"):
    st.session_state.is_running = not st.session_state.is_running
    
st.sidebar.write(f"**Auto-Run Status:** {'🟢 Running' if st.session_state.is_running else '🔴 Stopped'}")


# --- Main Dashboard ---
st.title("Autonomous Crypto Paper Trading Lab")

# Fetch fresh price for display purposes
try:
    display_price = engines.data_engine.get_current_price(engines.target_symbol)
except Exception:
    display_price = 0.0

# Calculate Portfolio Value
current_prices = {engines.target_symbol: display_price} if display_price > 0 else {}
portfolio_value = engines.portfolio.get_portfolio_value(current_prices)

# Top Metrics Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Target Asset", engines.target_symbol, f"${display_price:,.2f}")
col2.metric("Total Portfolio Value", f"${portfolio_value:,.2f}")
col3.metric("Cash Balance", f"${engines.portfolio.get_cash_balance():,.2f}")
col4.metric("Agent Pipeline Status", engines.execution.guardian.status if display_price > 0 else "N/A")

st.markdown("---")

# Agent Layer Status Row
st.subheader("Autonomous Agent Layer")
col_scout, col_analyst, col_guardian = st.columns(3)

def render_agent_card(col, agent_name, agent_obj):
     with col:
          st.markdown(f"**{agent_name}**")
          st.write(f"Status: `{agent_obj.status}`")
          
          streak = agent_obj.memory['current_streak']
          streak_color = "green" if streak > 0 else "red" if streak < 0 else "gray"
          st.markdown(f"Streak: :{streak_color}[{streak}] (W:{agent_obj.memory['wins']} L:{agent_obj.memory['losses']})")
          
          if agent_obj.memory['adaptations']:
               st.caption("Active Adaptations:")
               for adapt in agent_obj.memory['adaptations']:
                    st.caption(f"- {adapt}")
          else:
               st.caption("No active adaptations.")

render_agent_card(col_scout, "Scout Agent", engines.execution.scout)
render_agent_card(col_analyst, "Analyst Agent", engines.execution.analyst)
render_agent_card(col_guardian, "Risk Guardian Agent", engines.execution.guardian)

st.markdown("---")

# Open Positions & History Row
col_pos, col_hist = st.columns(2)

with col_pos:
    st.subheader("Open Positions")
    positions = engines.portfolio.get_all_positions()
    if positions:
        pos_data = []
        for sym, data in positions.items():
            current_sym_price = current_prices.get(sym, data['average_entry_price'])
            current_val = data['amount'] * current_sym_price
            pnl = current_val - (data['amount'] * data['average_entry_price'])
            pos_data.append({
                "Symbol": sym,
                "Amount": round(data['amount'], 4),
                "Avg Entry Price": f"${data['average_entry_price']:,.2f}",
                "Current Value": f"${current_val:,.2f}",
                "Unrealized PnL": f"${pnl:,.2f}"
            })
        st.table(pd.DataFrame(pos_data))
    else:
        st.info("No open positions.")
        
with col_hist:
    st.subheader("Trade History")
    history = engines.execution.get_trade_history()
    if history:
        # Show last 10 trades reversed
        df_hist = pd.DataFrame(history)
        # Reorder columns slightly for better fit
        df_hist = df_hist[['timestamp', 'action', 'symbol', 'amount', 'price', 'note']]
        st.dataframe(df_hist.iloc[::-1].head(10), use_container_width=True)
    else:
        st.info("No trade history available yet.")

# If auto-running, use Streamlit's rerun capability with a delay
if st.session_state.is_running:
    time.sleep(5)  # Simulate a 5-second cycle for the prototype
    
    current_price = engines.data_engine.get_current_price(engines.target_symbol)
    historical_data = engines.data_engine.get_historical_klines(engines.target_symbol, limit=engines.strategy.long_window + 10)
    
    if current_price > 0 and not historical_data.empty:
        engines.execution.execute_cycle(engines.target_symbol, current_price, historical_data)
        engines.cycle_count += 1
    
    st.rerun()
