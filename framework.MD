Auto Trader

Autonomous Crypto Paper Trading Lab

Project Goal

A personal-use cryptocurrency paper trading simulator powered by autonomous AI agents.
The system executes simulated trades using rule-based strategies and risk constraints.
The interface is a web dashboard (Streamlit) with future mobile monitoring support.

Core Principles

– Paper trading only (no real money)
– Stability over sophistication
– Modular architecture
– Transparent agent decisions
– Deterministic strategies first
– API-first backend design

System Architecture

Backend: Python
Frontend: Streamlit
Data Source: Binance API (or interchangeable)

Core Modules

1. data_engine.py
– Fetch market data
– Handle API calls
– Normalize price data

2. strategy_engine.py
– Trading logic
– Rule-based strategies
– Signal generation

3. risk_engine.py
– Position sizing
– Exposure limits
– Stop-loss rules

4. portfolio_engine.py
– Track balance
– Track positions
– PnL calculations

5. execution_engine.py
– Simulated trade execution
– Slippage simulation (optional later)
– Trade logging

6. agent_engine.py
– Agent cycle orchestration
– Agent communication

Agents (Initial Design)

Market Scanner Agent
→ Identifies candidate assets

Strategy Agent
→ Generates buy/sell signals

Risk Manager Agent
→ Approves/modifies/rejects trades

Execution Agent
→ Simulates trades

Narrator Agent (Optional Phase 2)
→ Explains system behavior

Trading Behavior

– Timed decision cycle (default: every 5 min)
– Active day/swing trading style
– Max trades per cycle/day
– Risk-constrained decisions

Dashboard Requirements

Display:

✔ Price chart
✔ Portfolio value
✔ Open positions
✔ Trade history
✔ Agent activity feed
✔ Risk metrics

User Controls

Allow adjustment of:

– Risk level
– Max position size
– Max exposure
– Trade frequency
– Stop-loss sensitivity

Future Expansion (Not MVP)

– Mobile companion app
– Real trading integration
– ML-based strategies
– Multi-strategy competition