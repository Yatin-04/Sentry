# Interview Prep: Executive Dashboard & UI (Segment 6)

This document covers the frontend architecture and how we handled visualizing massive amounts of financial data efficiently.

## 1. Serialization (Pickling) for UI Speed

**What we did:** We updated `backtester.py` to save `portfolio_daily_values`, `strategy_returns`, and `holdings_history` into a serialized `backtest_results.pkl` file, which `app.py` loads instantly.

> [!TIP]
> **Interview Question:** *If your backtest takes 2-3 minutes to run (due to XGBoost training and CVXPY optimization), how do you ensure the UI is fast and responsive for end users?*
> 
> **Your Answer:** 
> "I decoupled the compute layer from the presentation layer. The heavy backtest runs asynchronously or on a schedule, and serializes its final state objects (Pandas Dataframes, Dictionaries) into a binary `.pkl` file. The Streamlit dashboard exclusively acts as a read-only presentation layer, loading the pre-computed binary file using `@st.cache_data`. This ensures the UI launches and interacts instantly, rather than locking up the browser to compute ML models."

## 2. Institutional Design & Transparency

**What we did:** Engineered a custom CSS theme with glassmorphism and integrated Plotly for interactive charting.

> [!IMPORTANT]
> **Interview Question:** *In quantitative finance, transparency is as important as returns. How does your UI design cater to portfolio managers?*
> 
> **Your Answer:** 
> "Portfolio managers don't just care about the final CAGR; they care about the path taken and the current risk exposure. I designed the dashboard with three core transparency layers:
> 1. **Immediate KPIs**: Large metric cards showing delta against the benchmark to prove relative performance immediately.
> 2. **Historical Pain (Drawdown)**: A dedicated interactive drawdown chart so a PM can see exactly when and how deeply the strategy bled cash during market crashes.
> 3. **Current Exposure (Holdings Table)**: A live view of the *most recent* non-zero portfolio weights so a PM knows exactly what the AI has bought for the current cycle."

## 3. Handling NaN Bugs in the Matrix Multiplication

**What we did:** Fixed a bug where a single missing stock price caused a `NaN` propagation across the entire portfolio value.

> [!WARNING]
> **Interview Question:** *What happens if a stock in your universe is halted or missing price data on a specific day during the holding period? How did you handle that bug?*
> 
> **Your Answer:** 
> "During the holding drift simulation, I used a dot product between the `price_relatives` and `target_weights`. In Pandas, if a stock has a `NaN` price, its price relative is `NaN`. If you dot product that with a 0.0 weight, it yields `NaN`, which poisons the entire portfolio's daily return, cascading to 0.0 metrics for the rest of the simulation. 
> To fix this, I engineered a robust forward-fill (`ffill()`) on the raw holding prices, and then added a secondary `fillna(1.0)` on the price relatives. This guarantees that missing data is mathematically treated as a 0% return for that day, completely stopping the NaN poisoning."
